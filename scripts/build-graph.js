const fs = require("fs");
const path = require("path");

const WIKILINK_RE = /\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g;
const WIKI_DIR = process.env.WIKI_DIR || "wiki";
const OUT_DIR = "dist";

function findMdFiles(dir) {
  const results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...findMdFiles(full));
    } else if (entry.name.endsWith(".md")) {
      results.push(full);
    }
  }
  return results;
}

function extractTitle(content, filePath) {
  const match = content.match(/^#\s+(.+)$/m);
  if (match) return match[1].trim();
  return path.basename(filePath, ".md").replace(/-/g, " ");
}

function stripFrontmatter(content) {
  const m = content.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/);
  if (m) return content.slice(m[0].length).trim();
  return content.trim();
}

function extractFrontmatterField(content, field) {
  const m = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return null;
  const line = m[1].split(/\r?\n/).find((l) => l.startsWith(field + ":"));
  if (!line) return null;
  return line.slice(field.length + 1).trim().replace(/^['"]|['"]$/g, "") || null;
}

function parseLogEntries(wikiDir) {
  const logPath = path.join(wikiDir, "log.md");
  if (!fs.existsSync(logPath)) return [];
  const content = fs.readFileSync(logPath, "utf-8");
  const entries = [];
  const re = /##\s+\[([^\]]+)\]\s+([^|]+)\|\s*(.+)/g;
  let match;
  while ((match = re.exec(content)) !== null) {
    entries.push({ time: match[1].trim(), type: match[2].trim(), message: match[3].trim() });
  }
  return entries;
}

const wikiPrefix = WIKI_DIR.replace(/\\/g, "/").replace(/\/$/, "") + "/";

function resolveLink(target, allFiles) {
  const withMd = target.endsWith(".md") ? target : target + ".md";
  const candidates = allFiles.map((f) => f.replace(/\\/g, "/"));

  if (candidates.includes(withMd)) return withMd;

  const withWiki = wikiPrefix + withMd;
  if (candidates.includes(withWiki)) return withWiki;

  const subdirs = ["entities", "concepts", "sources", "synthesis"];
  for (const sub of subdirs) {
    const candidate = wikiPrefix + sub + "/" + withMd;
    if (candidates.includes(candidate)) return candidate;
  }

  const basename = withMd.split("/").pop();
  const found = candidates.find((p) => p.endsWith("/" + basename) || p === basename);
  if (found) return found;

  return null;
}

function relDir(filePath) {
  const rel = filePath.replace(/\\/g, "/");
  const inner = rel.startsWith(wikiPrefix) ? rel.slice(wikiPrefix.length) : rel;
  const first = inner.split("/")[0];
  return inner.includes("/") ? first : "wiki";
}

const files = findMdFiles(WIKI_DIR);
const nodes = [];
const edges = [];

for (const file of files) {
  const content = fs.readFileSync(file, "utf-8");
  const relPath = file.replace(/\\/g, "/");
  const dir = relDir(relPath);
  nodes.push({ id: relPath, title: extractTitle(content, file), dir, body: stripFrontmatter(content), created: extractFrontmatterField(content, "created"), updated: extractFrontmatterField(content, "updated") });

  let match;
  const re = new RegExp(WIKILINK_RE.source, "g");
  while ((match = re.exec(content)) !== null) {
    const resolved = resolveLink(match[1], files.map((f) => f.replace(/\\/g, "/")));
    if (resolved) {
      edges.push({ source: relPath, target: resolved });
    }
  }
}

const activity = parseLogEntries(WIKI_DIR);
fs.mkdirSync(OUT_DIR, { recursive: true });
fs.writeFileSync(
  path.join(OUT_DIR, "graph.json"),
  JSON.stringify({ nodes, edges, activity }, null, 2)
);
console.log("Graph: " + nodes.length + " nodes, " + edges.length + " edges, " + activity.length + " log entries → dist/graph.json");
