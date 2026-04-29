#!/usr/bin/env node
/**
 * update-personas.mjs
 *
 * Re-emits persona JSON fixtures from the SPA's exportJSON() whenever the
 * framework version advances. Personas live in tests/e2e/fixtures/personas/
 * and are driven by tests/e2e/fixtures/personas/manifest.json (each entry
 * provides the persona name plus the answer set to apply before exporting).
 *
 * SCAFFOLD STATUS:
 *   tests/e2e/fixtures/personas/ does not exist yet (Phase C work). This
 *   script is wired up so that as soon as that directory + manifest land,
 *   regenerating fixtures is a single command. Until then it warns and
 *   exits 0.
 *
 * Usage:
 *   node scripts/update-personas.mjs
 */
import { readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..");
const PERSONAS_DIR = join(repoRoot, "tests", "e2e", "fixtures", "personas");
const PERSONAS_MANIFEST = join(PERSONAS_DIR, "manifest.json");
const CONTROLS_MANIFEST = join(repoRoot, "assessment", "manifest", "controls.json");
const VERSION_JSON = join(repoRoot, "version.json");

function readFrameworkVersion() {
  if (existsSync(VERSION_JSON)) {
    try {
      const v = JSON.parse(readFileSync(VERSION_JSON, "utf8"));
      if (v && (v.frameworkVersion || v.version)) {
        return v.frameworkVersion || v.version;
      }
    } catch (e) {
      console.warn(`warn: could not parse ${VERSION_JSON}: ${e.message}`);
    }
  }
  if (existsSync(CONTROLS_MANIFEST)) {
    try {
      const m = JSON.parse(readFileSync(CONTROLS_MANIFEST, "utf8"));
      // controls.json is currently a bare array; check for wrapper objects too.
      if (m && !Array.isArray(m) && (m.frameworkVersion || m.version)) {
        return m.frameworkVersion || m.version;
      }
    } catch (e) {
      console.warn(`warn: could not parse ${CONTROLS_MANIFEST}: ${e.message}`);
    }
  }
  return "unknown";
}

/**
 * Boot the SPA in jsdom and return { window, exportJSON, applyAnswers }.
 * Mirrors the boot pattern in tests/spa/export-shape.test.mjs. Implementation
 * is intentionally deferred until the persona harness lands so we don't pin
 * the boot helper to a stale shape.
 */
async function bootSPA() {
  throw new Error("bootSPA() not yet wired — implement against tests/spa/export-shape.test.mjs once personas land.");
}

async function regeneratePersona(personaFile, answers) {
  const { exportJSON, applyAnswers } = await bootSPA();
  applyAnswers(answers);
  const exported = exportJSON();
  writeFileSync(personaFile, JSON.stringify(exported, null, 2) + "\n", "utf8");
  const touched = exported && exported._computedScores && exported._computedScores.perControl
    ? Object.keys(exported._computedScores.perControl).length
    : 0;
  return touched;
}

async function main() {
  const frameworkVersion = readFrameworkVersion();
  console.log(`Framework version: ${frameworkVersion}`);

  if (!existsSync(PERSONAS_DIR)) {
    console.warn(
      "Personas directory not yet created (Phase C scaffold pending). " +
      "Script ready for use once personas land."
    );
    process.exit(0);
  }

  if (!existsSync(PERSONAS_MANIFEST)) {
    console.warn(
      `No persona manifest at ${PERSONAS_MANIFEST}. ` +
      "Script ready for use once personas land."
    );
    process.exit(0);
  }

  const manifest = JSON.parse(readFileSync(PERSONAS_MANIFEST, "utf8"));
  const personas = Array.isArray(manifest) ? manifest : (manifest.personas || []);
  if (!personas.length) {
    console.warn("Persona manifest is empty. Nothing to regenerate.");
    process.exit(0);
  }

  const existing = new Set(
    readdirSync(PERSONAS_DIR).filter(f => f.endsWith(".json") && f !== "manifest.json")
  );

  let failed = 0;
  for (const p of personas) {
    const name = p.name || p.id;
    const file = join(PERSONAS_DIR, p.file || `${name}.json`);
    if (!existing.has(p.file || `${name}.json`)) {
      console.warn(`${name}: target file not present yet — will be created`);
    }
    try {
      const touched = await regeneratePersona(file, p.answers || {});
      console.log(`${name}: updated (controls touched: ${touched})`);
    } catch (e) {
      failed += 1;
      console.error(`${name}: FAILED — ${e.message}`);
    }
  }

  if (failed > 0) {
    console.error(`update-personas: ${failed} persona(s) failed.`);
    process.exit(1);
  }
  console.log("update-personas: all personas re-emitted successfully.");
}

main().catch(err => {
  console.error("update-personas: fatal:", err);
  process.exit(1);
});
