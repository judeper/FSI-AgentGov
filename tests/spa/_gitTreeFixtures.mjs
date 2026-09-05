import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const apiRoot = "https://api.github.com/repos/judeper/FSI-AgentGov";

export function git(...args) {
  return execFileSync("git", args, { cwd: repoRoot, maxBuffer: 128 * 1024 * 1024 });
}

export function readGitTree(ref = "HEAD", includeTrees = false) {
  return git("ls-tree", "-r", ...(includeTrees ? ["-t"] : []), "-z", "--full-tree", ref)
    .toString("utf8").split("\0").filter(Boolean).map(record => {
      const tab = record.indexOf("\t");
      const [mode, type, sha] = record.slice(0, tab).split(" ");
      return { path: record.slice(tab + 1), mode, type, sha };
    });
}

export function readGitIndex() {
  return git("ls-files", "--stage", "-z").toString("utf8").split("\0").filter(Boolean)
    .map(record => {
      const tab = record.indexOf("\t");
      const [mode, sha, stage] = record.slice(0, tab).split(" ");
      if (stage !== "0") throw new Error("fixture index has unresolved stages");
      return { path: record.slice(tab + 1), mode, type: mode === "160000" ? "commit" : "blob", sha };
    });
}

export function gitObjectId(type, bytes) {
  return createHash("sha1").update(`${type} ${bytes.length}\0`).update(bytes).digest("hex");
}

export function fixtureBlob(path, bytes, mode = "100644") {
  const content = Buffer.from(bytes);
  return { path, mode, type: "blob", sha: gitObjectId("blob", content), size: content.length };
}

// Match Git's tree serialization, including directory ordering and binary object IDs.
export function githubTreeResponse(leaves) {
  const directories = new Map([["", new Map()]]);
  for (const entry of leaves.filter(entry => entry.type !== "tree")) {
    const parts = entry.path.split("/");
    for (let count = 1; count < parts.length; count += 1) {
      const path = parts.slice(0, count).join("/");
      if (!directories.has(path)) directories.set(path, new Map());
    }
    const parent = parts.slice(0, -1).join("/");
    directories.get(parent).set(parts.at(-1), { ...entry, name: parts.at(-1) });
  }
  const tree = [...leaves.filter(entry => entry.type !== "tree")];
  let rootSha;
  for (const path of [...directories.keys()].sort((a, b) => b.split("/").length - a.split("/").length || b.length - a.length)) {
    const children = [...directories.get(path).values()].sort((a, b) =>
      Buffer.compare(Buffer.from(a.name + (a.type === "tree" ? "/" : "")),
        Buffer.from(b.name + (b.type === "tree" ? "/" : ""))));
    const bytes = Buffer.concat(children.map(entry =>
      Buffer.concat([Buffer.from(`${entry.mode.replace(/^0/, "")} ${entry.name}\0`), Buffer.from(entry.sha, "hex")])));
    const sha = gitObjectId("tree", bytes);
    if (!path) { rootSha = sha; continue; }
    const parts = path.split("/");
    const entry = { path, mode: "040000", type: "tree", sha };
    tree.push(entry);
    directories.get(parts.slice(0, -1).join("/")).set(parts.at(-1), { ...entry, name: parts.at(-1) });
  }
  return {
    sha: rootSha,
    url: `${apiRoot}/git/trees/${rootSha}`,
    truncated: false,
    tree: tree.sort((a, b) => Buffer.compare(Buffer.from(a.path), Buffer.from(b.path))).map(entry => ({
      ...entry,
      url: `${apiRoot}/git/${entry.type === "tree" ? "trees" : "blobs"}/${entry.sha}`,
    })),
  };
}
