# Exceptional fast-uri 3.1.7 dependency artifact

This directory is a narrowly reviewed supply-chain exception, **not** a general
vendoring convention. `fast-uri` 3.1.7 contains security fixes needed by Ajv
8.20.0, but the compatible 3.1.7 package was not available from the npm
registry on September 4, 2026. GitHub-generated source archives were rejected
because GitHub can regenerate their compression bytes, invalidating lockfile
integrity even when the Git tree is unchanged.

The 43,760-byte `fast-uri-3.1.7.tgz` is committed as an ordinary Git blob so a
clean install does not depend on a mutable or regenerable external archive.
`package.json` declares the repo-relative artifact as a development-dependency
anchor and uses npm's `$fast-uri` override reference only for Ajv's transitive
edge. This is required because npm resolves a literal local-file override from
the dependent package directory and otherwise produces an invalid clean
install. `package-lock.json` retains Ajv's `fast-uri: ^3.0.1` dependency edge,
the package identity `fast-uri@3.1.7`, the repo-relative `file:` URI, and the
tarball's SHA-512 SRI. The anchor does not add a second package copy.

## Why this mechanism

- The upstream v3.1.7 GitHub release has no first-party package asset; its
  automatic source links have the same regeneration risk as codeload.
- Git LFS is not configured in this repository or available in its verified
  local toolchain. Introducing it for a 43,760-byte file would add a second
  availability boundary without reducing review risk.
- No external release or artifact host was created. The reviewed bytes travel
  with the checkout and are protected by Git object identity plus the lockfile
  and policy hashes.

## Reviewed provenance

| Field | Value |
|---|---|
| Upstream repository | `https://github.com/fastify/fast-uri.git` |
| Package | `fast-uri@3.1.7` |
| License | BSD-3-Clause (`package/LICENSE` in the tarball) |
| Upstream commit | `412e40abd4eb8beabfb952d80abf949a2baf27a3` |
| Upstream tree | `a1ec2b29b5d2493a9ba4d2de480a062b08f72558` |
| Upstream tracked files | 46 |
| npm package files | 44 |
| Artifact SHA-256 | `3fa380284be4ecbf471c1dbb8c5da6f517c95f54279f88c2037985d03fdc6d92` |
| Artifact SHA-512 | `74ebd95738dd65dcfba6177dbfa8c26f0c6b056ddf2ba9fc45cd02b5d98ce1bba6ccc9f1cb005886ea61e89f35f51470fe4bbeacb6de9707ccba792dbb35551e` |
| npm SRI | `sha512-dOvZVzjdZdz7phd9v6jCbwxrBW3fK6n8Rc0CtdmM4bumzMnxywBYhuph6J819RRw/ku+rLbelwfMunktuzVVHg==` |

`provenance.json` is the included-file manifest. It records each package path,
size, mode, and SHA-256. The source tree has 46 tracked files; npm's pack rules
intentionally omit `.gitignore` and `.npmrc`, yielding the exact 44-file
package set. Every packaged entry is a regular, non-executable file with
canonical ownership and timestamps. There are no links, unsafe paths,
executable `bin` entries, or install/pack lifecycle scripts.

## Deterministic reconstruction

Run from the repository root in PowerShell. Keep scratch data inside the
gitignored `maintainers-local/` path.

```powershell
$commit = '412e40abd4eb8beabfb952d80abf949a2baf27a3'
$tree = 'a1ec2b29b5d2493a9ba4d2de480a062b08f72558'
$scratch = 'maintainers-local\tmp\fast-uri-3.1.7'
$source = Join-Path $scratch 'source'
$pack1 = Join-Path $scratch 'pack-1'
$pack2 = Join-Path $scratch 'pack-2'

Remove-Item -Recurse -Force $scratch -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $source,$pack1,$pack2 | Out-Null
git init --quiet $source
git -C $source remote add origin https://github.com/fastify/fast-uri.git
git -C $source fetch --quiet --depth=1 origin $commit
git -C $source checkout --quiet --detach FETCH_HEAD

if ((git -C $source rev-parse HEAD) -ne $commit) { throw 'commit mismatch' }
if ((git -C $source rev-parse 'HEAD^{tree}') -ne $tree) { throw 'tree mismatch' }

npm pack $source --ignore-scripts --pack-destination $pack1 --json
npm pack $source --ignore-scripts --pack-destination $pack2 --json

$a = (Resolve-Path (Join-Path $pack1 'fast-uri-3.1.7.tgz')).Path
$b = (Resolve-Path (Join-Path $pack2 'fast-uri-3.1.7.tgz')).Path
if (-not [Linq.Enumerable]::SequenceEqual(
  [IO.File]::ReadAllBytes($a),
  [IO.File]::ReadAllBytes($b)
)) { throw 'npm pack was not byte-deterministic' }

Get-FileHash $a -Algorithm SHA256
Get-FileHash $a -Algorithm SHA512
npm run verify:dependency-artifacts -- --source $source
```

The reviewed reconstruction used Node 24.19.0 and npm 11.17.0. Both independent
`npm pack --ignore-scripts` runs produced identical bytes and the hashes above;
npm 10.8.2 independently reproduced those same bytes for the Node 20 CI line.
Before replacing the committed artifact, regenerate `provenance.json` from the
`npm pack --json` file list and the verified Git blobs, inspect the exact
packlist, update the hard-coded reviewed hashes in
`scripts/verify-fast-uri-artifact.mjs`, then run:

```powershell
npm ci
npm run verify:dependency-artifacts
npm run verify:vendor-runtime
npm test
```

## Removal condition

Remove this exception as one reviewed change when an official byte-stable npm
registry artifact provides a patched version compatible with Ajv's supported
dependency range. Before removal, verify registry integrity and provenance,
Ajv compatibility, the six security regressions, the full repository suite,
and the post-install dependency graph. Delete the local tarball, provenance,
override, and policy gate together. Do not copy this pattern to another
dependency merely for convenience.
