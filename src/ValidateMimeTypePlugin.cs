// ---------------------------------------------------------------------------
// ValidateMimeTypePlugin.cs
// FSI Agent Governance — Zone 3 Server-Side MIME Validation Plugin
//
// Dataverse pre-validation plugin that inspects file uploads (annotations)
// for magic-byte signature compliance. Helps meet FINRA 4511 and SEC 17a-4
// requirements by providing defense-in-depth file type validation in
// Enterprise Managed (Zone 3) environments.
//
// Control: 1.25 — MIME Type Restrictions
// Version: 1.0.0
// ---------------------------------------------------------------------------

using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Xrm.Sdk;

namespace FsiAgentGovernance.Plugins
{
    /// <summary>
    /// Dataverse pre-validation plugin that validates file attachments (annotations)
    /// against a configurable MIME type allowlist and blocked executable signature list.
    /// <para>
    /// Registered on the <c>Create</c> message for the <c>annotation</c> (Note) entity
    /// at the pre-validation stage (stage 10). Reads file content from <c>documentbody</c>
    /// (Base64-encoded) and the declared <c>mimetype</c> field.
    /// </para>
    /// <para>
    /// Validation steps:
    /// <list type="number">
    ///   <item>File size guard — rejects files exceeding <c>maxFileSizeBytes</c>.</item>
    ///   <item>Blocked signature scan — compares leading bytes against known executable headers.</item>
    ///   <item>Allowlist check — verifies the declared MIME type is in the allowed set.</item>
    ///   <item>Magic-byte consistency — for types with known signatures, confirms the header matches.</item>
    ///   <item>OpenXML deep inspection — for DOCX/XLSX/PPTX, verifies PK header and <c>[Content_Types].xml</c>.</item>
    /// </list>
    /// </para>
    /// <para>
    /// Configuration is loaded from the plugin step's secure or unsecure configuration
    /// string, which should contain the full MimeConfig.json content.
    /// </para>
    /// </summary>
    public class ValidateMimeTypePlugin : IPlugin
    {
        // ─── Configuration ─────────────────────────────────────────────────
        private readonly MimeValidationConfig _config;

        /// <summary>
        /// Initializes a new instance of the <see cref="ValidateMimeTypePlugin"/> class.
        /// Configuration is loaded from the secure configuration string first; if empty,
        /// falls back to the unsecure configuration string.
        /// </summary>
        /// <param name="unsecureConfiguration">Unsecure configuration string (MimeConfig.json content).</param>
        /// <param name="secureConfiguration">Secure configuration string (MimeConfig.json content, preferred).</param>
        /// <exception cref="InvalidPluginExecutionException">
        /// Thrown when no valid configuration is provided or the JSON is malformed.
        /// </exception>
        public ValidateMimeTypePlugin(string unsecureConfiguration, string secureConfiguration)
        {
            var configJson = !string.IsNullOrWhiteSpace(secureConfiguration)
                ? secureConfiguration
                : unsecureConfiguration;

            if (string.IsNullOrWhiteSpace(configJson))
            {
                throw new InvalidPluginExecutionException(
                    "MIME validation plugin configuration is missing. " +
                    "Provide MimeConfig.json content in the plugin step secure or unsecure configuration.");
            }

            try
            {
                _config = JsonSerializer.Deserialize<MimeValidationConfig>(configJson,
                    new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
            }
            catch (JsonException ex)
            {
                throw new InvalidPluginExecutionException(
                    $"MIME validation plugin configuration is invalid JSON: {ex.Message}");
            }

            if (_config == null)
            {
                throw new InvalidPluginExecutionException(
                    "MIME validation plugin configuration deserialized to null.");
            }
        }

        /// <summary>
        /// Entry point for the Dataverse plugin execution pipeline.
        /// Validates the annotation file attachment against configured MIME restrictions.
        /// </summary>
        /// <param name="serviceProvider">The service provider for obtaining Dataverse services.</param>
        /// <exception cref="InvalidPluginExecutionException">
        /// Thrown when the file fails validation and enforcement mode is <c>Block</c>.
        /// </exception>
        public void Execute(IServiceProvider serviceProvider)
        {
            // ─── Obtain services ───────────────────────────────────────────
            var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
            var tracingService = (ITracingService)serviceProvider.GetService(typeof(ITracingService));

            var correlationId = context.CorrelationId;
            tracingService.Trace("[FSI-MIME] Plugin invoked. CorrelationId={0}", correlationId);

            // ─── Validate execution context ────────────────────────────────
            if (context.MessageName != "Create" || context.PrimaryEntityName != "annotation")
            {
                tracingService.Trace("[FSI-MIME] Skipping — not a Create on annotation.");
                return;
            }

            if (!(context.InputParameters["Target"] is Entity target))
            {
                tracingService.Trace("[FSI-MIME] Skipping — Target is not an Entity.");
                return;
            }

            // ─── Extract file data ─────────────────────────────────────────
            var documentBody = target.GetAttributeValue<string>("documentbody");
            var declaredMimeType = target.GetAttributeValue<string>("mimetype");
            var fileName = target.GetAttributeValue<string>("filename") ?? "(unknown)";

            if (string.IsNullOrEmpty(documentBody))
            {
                tracingService.Trace("[FSI-MIME] No documentbody — skipping validation for '{0}'.", fileName);
                return;
            }

            tracingService.Trace("[FSI-MIME] Validating file '{0}', declared MIME='{1}'. CorrelationId={2}",
                fileName, declaredMimeType ?? "(none)", correlationId);

            // ─── Decode file bytes ─────────────────────────────────────────
            byte[] fileBytes;
            try
            {
                fileBytes = Convert.FromBase64String(documentBody);
            }
            catch (FormatException ex)
            {
                HandleViolation(tracingService,
                    $"File '{fileName}' contains invalid Base64 content: {ex.Message}",
                    correlationId);
                return;
            }

            // ─── Step 1: File size guard ───────────────────────────────────
            if (_config.MaxFileSizeBytes > 0 && fileBytes.Length > _config.MaxFileSizeBytes)
            {
                HandleViolation(tracingService,
                    $"File '{fileName}' ({fileBytes.Length:N0} bytes) exceeds the maximum allowed " +
                    $"size of {_config.MaxFileSizeBytes:N0} bytes for Zone {_config.Zone}.",
                    correlationId);
                return;
            }

            tracingService.Trace("[FSI-MIME] File size OK: {0:N0} bytes.", fileBytes.Length);

            // ─── Read header bytes ─────────────────────────────────────────
            var headerLength = Math.Min(fileBytes.Length, 16);
            var headerBytes = new byte[headerLength];
            Array.Copy(fileBytes, headerBytes, headerLength);

            // ─── Step 2: Blocked signature scan ────────────────────────────
            if (_config.BlockedSignatures != null)
            {
                foreach (var blocked in _config.BlockedSignatures)
                {
                    var sigBytes = ParseHexString(blocked.MagicBytes);
                    if (sigBytes != null && StartsWithBytes(headerBytes, sigBytes))
                    {
                        HandleViolation(tracingService,
                            $"File '{fileName}' matches blocked signature '{blocked.Name}'. " +
                            $"This file type is not permitted in Zone {_config.Zone} environments. " +
                            "Contact your administrator if you believe this is in error.",
                            correlationId);
                        return;
                    }
                }
            }

            tracingService.Trace("[FSI-MIME] No blocked signatures detected.");

            // ─── Step 3: Allowlist check ───────────────────────────────────
            if (string.IsNullOrEmpty(declaredMimeType))
            {
                HandleViolation(tracingService,
                    $"File '{fileName}' has no declared MIME type. " +
                    $"All uploads in Zone {_config.Zone} require an explicit MIME type declaration.",
                    correlationId);
                return;
            }

            var allowedEntry = _config.AllowedTypes?
                .FirstOrDefault(t => string.Equals(t.MimeType, declaredMimeType,
                    StringComparison.OrdinalIgnoreCase));

            if (allowedEntry == null)
            {
                HandleViolation(tracingService,
                    $"MIME type '{declaredMimeType}' for file '{fileName}' is not in the " +
                    $"Zone {_config.Zone} allowed list. Review the allowed types configuration " +
                    "or contact your administrator.",
                    correlationId);
                return;
            }

            tracingService.Trace("[FSI-MIME] MIME type '{0}' is in the allowlist.", declaredMimeType);

            // ─── Step 4: Magic-byte consistency ────────────────────────────
            if (allowedEntry.MagicBytes != null)
            {
                var expectedSignatures = allowedEntry.GetMagicByteArrays();
                if (expectedSignatures.Count > 0)
                {
                    var matchFound = expectedSignatures.Any(sig => StartsWithBytes(headerBytes, sig));
                    if (!matchFound)
                    {
                        HandleViolation(tracingService,
                            $"File '{fileName}' declares MIME type '{declaredMimeType}' but its " +
                            "content header does not match the expected magic bytes for that type. " +
                            "The file may have been renamed or corrupted.",
                            correlationId);
                        return;
                    }

                    tracingService.Trace("[FSI-MIME] Magic bytes match for '{0}'.", declaredMimeType);
                }
            }
            else
            {
                // Text-based types: validate absence of binary content
                if (IsTextBasedType(declaredMimeType))
                {
                    var checkLength = Math.Min(fileBytes.Length, 8192);
                    if (ContainsBinaryContent(fileBytes, checkLength))
                    {
                        HandleViolation(tracingService,
                            $"File '{fileName}' declares text MIME type '{declaredMimeType}' " +
                            "but contains binary content. The file may have been mislabeled.",
                            correlationId);
                        return;
                    }

                    tracingService.Trace("[FSI-MIME] Text content validation passed.");
                }
            }

            // ─── Step 5: OpenXML deep inspection ───────────────────────────
            if (IsOpenXmlType(declaredMimeType))
            {
                if (!ValidateOpenXmlStructure(fileBytes, tracingService, fileName))
                {
                    HandleViolation(tracingService,
                        $"File '{fileName}' declares OpenXML MIME type '{declaredMimeType}' " +
                        "but does not contain a valid Office Open XML structure " +
                        "(missing [Content_Types].xml). The file may be corrupted or mislabeled.",
                        correlationId);
                    return;
                }

                tracingService.Trace("[FSI-MIME] OpenXML structure validated for '{0}'.", fileName);
            }

            tracingService.Trace("[FSI-MIME] Validation PASSED for '{0}'. CorrelationId={1}",
                fileName, correlationId);
        }

        // ═══════════════════════════════════════════════════════════════════
        // Violation Handling
        // ═══════════════════════════════════════════════════════════════════

        /// <summary>
        /// Handles a validation violation based on the configured enforcement mode.
        /// In <c>Block</c> mode, throws <see cref="InvalidPluginExecutionException"/>.
        /// In <c>LogOnly</c> mode, writes a trace warning and allows the operation.
        /// </summary>
        /// <param name="tracingService">Dataverse tracing service for logging.</param>
        /// <param name="message">Descriptive violation message.</param>
        /// <param name="correlationId">Correlation ID for trace integration.</param>
        private void HandleViolation(ITracingService tracingService, string message, Guid correlationId)
        {
            var fullMessage = $"[FSI-MIME] VIOLATION: {message} (CorrelationId={correlationId})";

            tracingService.Trace(fullMessage);

            if (string.Equals(_config.EnforcementMode, "Block", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidPluginExecutionException(message);
            }

            // LogOnly mode — record but allow
            tracingService.Trace("[FSI-MIME] EnforcementMode=LogOnly — upload permitted despite violation.");
        }

        // ═══════════════════════════════════════════════════════════════════
        // Byte Comparison Helpers
        // ═══════════════════════════════════════════════════════════════════

        /// <summary>
        /// Parses a space-separated hex string (e.g., "4D 5A") into a byte array.
        /// Returns null if the input is null or empty.
        /// </summary>
        private static byte[] ParseHexString(string hex)
        {
            if (string.IsNullOrWhiteSpace(hex))
                return null;

            var parts = hex.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            var bytes = new byte[parts.Length];

            for (var i = 0; i < parts.Length; i++)
            {
                bytes[i] = Convert.ToByte(parts[i], 16);
            }

            return bytes;
        }

        /// <summary>
        /// Checks whether <paramref name="data"/> starts with the specified <paramref name="prefix"/> bytes.
        /// </summary>
        private static bool StartsWithBytes(byte[] data, byte[] prefix)
        {
            if (data == null || prefix == null || data.Length < prefix.Length)
                return false;

            for (var i = 0; i < prefix.Length; i++)
            {
                if (data[i] != prefix[i])
                    return false;
            }

            return true;
        }

        /// <summary>
        /// Determines whether the declared MIME type is a text-based type
        /// that should be validated for absence of binary content.
        /// </summary>
        private static bool IsTextBasedType(string mimeType)
        {
            return mimeType != null &&
                   (mimeType.StartsWith("text/", StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Checks the first <paramref name="length"/> bytes for binary content.
        /// A byte is considered binary if it is a control character (0x00-0x08, 0x0E-0x1F)
        /// excluding common text control characters (TAB, LF, CR).
        /// </summary>
        private static bool ContainsBinaryContent(byte[] data, int length)
        {
            for (var i = 0; i < length && i < data.Length; i++)
            {
                var b = data[i];
                if (b < 0x09 || (b > 0x0D && b < 0x20))
                {
                    // Allow NULL (0x00) only if it's a UTF-16 BOM pattern
                    if (b == 0x00 && i == 0 && data.Length > 1 && (data[1] == 0xFE || data[1] == 0xFF))
                        continue;

                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Determines whether the MIME type is an OpenXML type requiring deep inspection.
        /// </summary>
        private static bool IsOpenXmlType(string mimeType)
        {
            if (string.IsNullOrEmpty(mimeType))
                return false;

            return mimeType.StartsWith(
                "application/vnd.openxmlformats-officedocument.",
                StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// Validates that the file bytes represent a valid Office Open XML structure
        /// by verifying the PK zip header and the presence of <c>[Content_Types].xml</c>.
        /// </summary>
        /// <param name="fileBytes">The complete file bytes.</param>
        /// <param name="tracingService">Tracing service for diagnostic output.</param>
        /// <param name="fileName">File name for trace messages.</param>
        /// <returns><c>true</c> if the structure is valid; otherwise <c>false</c>.</returns>
        private static bool ValidateOpenXmlStructure(byte[] fileBytes, ITracingService tracingService, string fileName)
        {
            try
            {
                using var stream = new MemoryStream(fileBytes);
                using var archive = new ZipArchive(stream, ZipArchiveMode.Read);

                var hasContentTypes = archive.Entries
                    .Any(e => string.Equals(e.FullName, "[Content_Types].xml",
                        StringComparison.OrdinalIgnoreCase));

                if (!hasContentTypes)
                {
                    tracingService.Trace("[FSI-MIME] OpenXML check: [Content_Types].xml not found in '{0}'.", fileName);
                }

                return hasContentTypes;
            }
            catch (InvalidDataException)
            {
                tracingService.Trace("[FSI-MIME] OpenXML check: File '{0}' is not a valid ZIP archive.", fileName);
                return false;
            }
            catch (Exception ex)
            {
                tracingService.Trace("[FSI-MIME] OpenXML check failed for '{0}': {1}", fileName, ex.Message);
                return false;
            }
        }

        // ═══════════════════════════════════════════════════════════════════
        // Configuration Model
        // ═══════════════════════════════════════════════════════════════════

        /// <summary>
        /// Root configuration model deserialized from MimeConfig.json.
        /// </summary>
        private class MimeValidationConfig
        {
            [JsonPropertyName("version")]
            public string Version { get; set; }

            [JsonPropertyName("enforcementMode")]
            public string EnforcementMode { get; set; }

            [JsonPropertyName("maxFileSizeBytes")]
            public long MaxFileSizeBytes { get; set; }

            [JsonPropertyName("zone")]
            public int Zone { get; set; }

            [JsonPropertyName("allowedTypes")]
            public List<AllowedType> AllowedTypes { get; set; }

            [JsonPropertyName("blockedSignatures")]
            public List<BlockedSignature> BlockedSignatures { get; set; }
        }

        /// <summary>
        /// Represents an allowed MIME type entry with expected magic bytes.
        /// </summary>
        private class AllowedType
        {
            [JsonPropertyName("mimeType")]
            public string MimeType { get; set; }

            [JsonPropertyName("extensions")]
            public List<string> Extensions { get; set; }

            /// <summary>
            /// Magic bytes value — may be a single hex string or a JSON array of hex strings.
            /// Stored as <see cref="JsonElement"/> to handle both cases.
            /// </summary>
            [JsonPropertyName("magicBytes")]
            public JsonElement? MagicBytes { get; set; }

            [JsonPropertyName("description")]
            public string Description { get; set; }

            /// <summary>
            /// Resolves the <see cref="MagicBytes"/> property into a list of byte arrays,
            /// handling both single-string and array-of-strings JSON representations.
            /// </summary>
            public List<byte[]> GetMagicByteArrays()
            {
                var result = new List<byte[]>();

                if (MagicBytes == null || MagicBytes.Value.ValueKind == JsonValueKind.Null)
                    return result;

                if (MagicBytes.Value.ValueKind == JsonValueKind.String)
                {
                    var bytes = ParseHexString(MagicBytes.Value.GetString());
                    if (bytes != null) result.Add(bytes);
                }
                else if (MagicBytes.Value.ValueKind == JsonValueKind.Array)
                {
                    foreach (var element in MagicBytes.Value.EnumerateArray())
                    {
                        if (element.ValueKind == JsonValueKind.String)
                        {
                            var bytes = ParseHexString(element.GetString());
                            if (bytes != null) result.Add(bytes);
                        }
                    }
                }

                return result;
            }
        }

        /// <summary>
        /// Represents a blocked executable signature (magic bytes to reject).
        /// </summary>
        private class BlockedSignature
        {
            [JsonPropertyName("name")]
            public string Name { get; set; }

            [JsonPropertyName("magicBytes")]
            public string MagicBytes { get; set; }

            [JsonPropertyName("description")]
            public string Description { get; set; }
        }
    }
}
