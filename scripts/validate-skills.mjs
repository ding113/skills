#!/usr/bin/env node
/**
 * The repo gate. Enforces the conventions documented in CLAUDE.md:
 *
 *   - every skill is skills/<bucket>/<name>/ holding SKILL.md + agents/openai.yaml
 *   - buckets come from the known set; engineering/ and writing/ are promoted
 *   - SKILL.md frontmatter: single-line `name` (kebab-case, equal to the folder
 *     name) and `description` (non-empty, ≤ 1024 chars); non-empty body
 *   - user-invoked flags stay in sync between SKILL.md and agents/openai.yaml
 *   - plugin.json ships exactly the promoted set; its version matches package.json
 *   - marketplace.json lists the plugin
 *   - every non-empty bucket has a README.md linking each of its skills
 *   - promoted skills have a top-level README reference and a docs page at
 *     docs/<bucket>/<name>.md; non-promoted skills have neither, and are never
 *     linked directly from the top-level README
 *
 * Run: npm run validate
 */
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const BUCKETS = ["engineering", "writing", "misc", "personal", "in-progress", "deprecated"];
const PROMOTED = new Set(["engineering", "writing"]);
const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;

const errors = [];
const err = (msg) => errors.push(msg);
const abs = (p) => join(ROOT, p);
const exists = (p) => existsSync(abs(p));
const read = (p) => readFileSync(abs(p), "utf8");
const listDirs = (p) =>
  readdirSync(abs(p), { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name);

function parseFrontmatter(raw, file) {
  const lines = raw.split("\n");
  if (lines[0] !== "---") {
    err(`${file}: must start with a \`---\` frontmatter block`);
    return null;
  }
  const close = lines.indexOf("---", 1);
  if (close === -1) {
    err(`${file}: frontmatter never closes`);
    return null;
  }
  const fm = {};
  for (const line of lines.slice(1, close)) {
    if (!line.trim()) continue;
    const m = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!m) {
      err(`${file}: frontmatter must be single-line \`key: value\` pairs, got ${JSON.stringify(line)}`);
      continue;
    }
    fm[m[1]] = m[2].trim();
  }
  fm.__body = lines.slice(close + 1).join("\n").trim();
  return fm;
}

// ---- discover and check every skill ----
const skills = [];
if (!exists("skills")) {
  err("skills/ directory missing");
} else {
  for (const bucket of listDirs("skills")) {
    if (!BUCKETS.includes(bucket)) {
      err(`skills/${bucket}/: unknown bucket (known: ${BUCKETS.join(", ")})`);
      continue;
    }
    const names = listDirs(`skills/${bucket}`);
    if (names.length > 0 && !exists(`skills/${bucket}/README.md`)) {
      err(`skills/${bucket}/README.md missing (every non-empty bucket lists its skills)`);
    }
    for (const name of names) skills.push({ bucket, name, dir: `skills/${bucket}/${name}` });
  }
}

for (const s of skills) {
  const skillMd = `${s.dir}/SKILL.md`;
  if (!exists(skillMd)) {
    err(`${skillMd} missing`);
    continue;
  }
  const fm = parseFrontmatter(read(skillMd), skillMd);
  if (!fm) continue;

  if (!fm.name) err(`${skillMd}: frontmatter \`name\` missing`);
  else {
    if (fm.name !== s.name) err(`${skillMd}: name \`${fm.name}\` ≠ folder name \`${s.name}\``);
    if (!KEBAB.test(fm.name)) err(`${skillMd}: name must be kebab-case`);
  }
  if (!fm.description) err(`${skillMd}: frontmatter \`description\` missing or empty`);
  else if (fm.description.length > 1024) err(`${skillMd}: description over 1024 chars`);
  if (!fm.__body) err(`${skillMd}: body is empty`);
  if (fm["disable-model-invocation"] !== undefined && fm["disable-model-invocation"] !== "true") {
    err(`${skillMd}: \`disable-model-invocation\` must be \`true\` or absent`);
  }

  const yamlPath = `${s.dir}/agents/openai.yaml`;
  if (!exists(yamlPath)) {
    err(`${yamlPath} missing (Codex metadata sits beside every SKILL.md)`);
  } else {
    const yaml = read(yamlPath);
    if (!/display_name:/.test(yaml)) err(`${yamlPath}: interface.display_name missing`);
    if (!/short_description:/.test(yaml)) err(`${yamlPath}: interface.short_description missing`);
    const userInvokedMd = fm["disable-model-invocation"] === "true";
    const userInvokedYaml = /allow_implicit_invocation:\s*false/.test(yaml);
    if (userInvokedMd !== userInvokedYaml) {
      err(
        `${s.dir}: invocation flags out of sync — SKILL.md says ${userInvokedMd ? "user" : "model"}-invoked, ` +
          `openai.yaml says ${userInvokedYaml ? "user" : "model"}-invoked`
      );
    }
  }
}

// ---- stray SKILL.md files (wrong depth) ----
if (exists("skills")) {
  (function walk(dir) {
    for (const e of readdirSync(abs(dir), { withFileTypes: true })) {
      if (e.name === "node_modules" || e.name.startsWith(".")) continue;
      const p = `${dir}/${e.name}`;
      if (e.isDirectory()) walk(p);
      else if (e.name === "SKILL.md" && !/^skills\/[^/]+\/[^/]+\/SKILL\.md$/.test(p)) {
        err(`${p}: SKILL.md outside the skills/<bucket>/<name>/ layout`);
      }
    }
  })("skills");
}

// ---- manifests ----
let pkg, plugin, market;
try { pkg = JSON.parse(read("package.json")); } catch (e) { err(`package.json: ${e.message}`); }
try { plugin = JSON.parse(read(".claude-plugin/plugin.json")); } catch (e) { err(`.claude-plugin/plugin.json: ${e.message}`); }
try { market = JSON.parse(read(".claude-plugin/marketplace.json")); } catch (e) { err(`.claude-plugin/marketplace.json: ${e.message}`); }

const pluginSkills = (plugin?.skills ?? []).map((p) => p.replace(/^\.\//, "").replace(/\/+$/, ""));
if (pkg && plugin && plugin.version !== pkg.version) {
  err(`version drift: package.json ${pkg.version} ≠ plugin.json ${plugin.version} (bump both together)`);
}
if (plugin && market && !(market.plugins ?? []).some((p) => p.name === plugin.name)) {
  err(`marketplace.json: no plugin entry named \`${plugin.name}\``);
}
for (const p of pluginSkills) {
  const m = p.match(/^skills\/([^/]+)\/([^/]+)$/);
  if (!m) {
    err(`plugin.json skills entry \`${p}\` is not skills/<bucket>/<name>`);
    continue;
  }
  if (!PROMOTED.has(m[1])) err(`plugin.json ships \`${p}\` from a non-promoted bucket`);
  if (!exists(`${p}/SKILL.md`)) err(`plugin.json skills entry \`${p}\` has no SKILL.md`);
}

// ---- READMEs and docs pages ----
let readme = "";
if (exists("README.md")) readme = read("README.md");
else err("README.md missing");

for (const s of skills) {
  const bucketReadmePath = `skills/${s.bucket}/README.md`;
  if (exists(bucketReadmePath) && !read(bucketReadmePath).includes(`./${s.name}/SKILL.md`)) {
    err(`${bucketReadmePath}: no entry linking ./${s.name}/SKILL.md`);
  }
  const inPlugin = pluginSkills.includes(s.dir);
  const docsPage = `docs/${s.bucket}/${s.name}.md`;
  const readmeLink = `./skills/${s.bucket}/${s.name}/SKILL.md`;
  if (PROMOTED.has(s.bucket)) {
    if (!inPlugin) err(`${s.dir}: promoted but missing from plugin.json's skills array`);
    if (!exists(docsPage)) err(`${s.dir}: promoted but ${docsPage} missing`);
    if (!readme.includes(readmeLink)) err(`README.md: no reference linking ${readmeLink}`);
  } else {
    if (inPlugin) err(`${s.dir}: non-promoted but listed in plugin.json`);
    if (exists(docsPage)) err(`${docsPage}: docs page for a non-promoted skill`);
    if (readme.includes(readmeLink)) {
      err(`README.md: links non-promoted ${readmeLink} directly (point at skills/${s.bucket}/README.md instead)`);
    }
  }
}

// ---- verdict ----
if (errors.length) {
  console.error(`✗ gate failed with ${errors.length} problem${errors.length === 1 ? "" : "s"}:\n`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
const promoted = skills.filter((s) => PROMOTED.has(s.bucket)).length;
console.log(`✓ ${skills.length} skill${skills.length === 1 ? "" : "s"} validated (${promoted} promoted, ${skills.length - promoted} not promoted)`);
