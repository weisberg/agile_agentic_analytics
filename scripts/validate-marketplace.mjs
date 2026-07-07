#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { parse as parseYaml } from "yaml";
import {
  AUTHENTICATION_VALUES,
  CLAUDE_MARKETPLACE_PATH,
  CODEX_MARKETPLACE_PATH,
  HEX_COLOR,
  INSTALLATION_VALUES,
  KEBAB_CASE,
  STRICT_SEMVER,
  codexInterface,
  generatedFiles,
  listFiles,
  listSkillFiles,
  pathExists,
  pluginComponents,
  pluginList,
  readCatalog,
  repoPath,
} from "./marketplace-lib.mjs";

const repoRoot = process.cwd();
const errors = [];
const warnings = [];

function add(message) {
  errors.push(message);
}

function addWarn(message) {
  warnings.push(message);
}

// Canonical tool names (see docs/SKILL_FRONTMATTER.md and docs/TOOLS_REFERENCE.md).
// Shared by skill `allowed-tools` and agent `tools`/`disallowedTools`.
const CANONICAL_TOOLS = new Set([
  "Read",
  "Write",
  "Edit",
  "Bash",
  "Glob",
  "Grep",
  "LSP",
  "NotebookEdit",
  "WebFetch",
  "WebSearch",
  "AskUserQuestion",
  "Skill",
  "Agent",
  "TodoWrite",
  "Monitor",
]);

// MCP server tools are allowed via their canonical `mcp__<server>__<tool>` form.
function isCanonicalTool(name) {
  return CANONICAL_TOOLS.has(name) || /^mcp__[A-Za-z0-9_-]+/.test(name);
}

// Documented skill frontmatter keys: loader-recognized + repo-convention +
// known-deprecated (docs/SKILL_FRONTMATTER.md). Keys outside this set WARN.
const DOCUMENTED_SKILL_KEYS = new Set([
  // Tier 1 — loader-recognized
  "name",
  "description",
  "allowed-tools",
  "disable-model-invocation",
  // Tier 2 — repo-convention metadata
  "triggers",
  "mutating",
  "version",
  // Tier 3 — deprecated but documented (removed on next edit; `tools` also errors)
  "writes_pages",
  "writes_to",
  "preamble-tier",
  "interactive",
  "benefits-from",
  "category",
  "priority",
  "depends_on",
  "feeds_into",
  "tools",
]);

// Plugin-agent frontmatter allowlist (docs/SKILL_FRONTMATTER.md).
const AGENT_ALLOWED_FIELDS = new Set([
  "name",
  "description",
  "model",
  "effort",
  "maxTurns",
  "tools",
  "disallowedTools",
  "skills",
  "memory",
  "background",
  "isolation",
]);
// Fields silently ignored when loaded from a plugin — hard error to declare them.
const AGENT_FORBIDDEN_FIELDS = new Set(["hooks", "mcpServers", "permissionMode"]);

// Normalize a tool declaration (YAML list OR comma-separated string) to a list.
function normalizeToolList(value) {
  if (value === undefined || value === null) {
    return [];
  }
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean);
  }
  return String(value)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

async function readJson(relativePath) {
  try {
    return JSON.parse(await readFile(repoPath(repoRoot, relativePath), "utf8"));
  } catch (error) {
    add(`${relativePath}: invalid or unreadable JSON (${error.message})`);
    return null;
  }
}

function expect(condition, message) {
  if (!condition) {
    add(message);
  }
}

function arraysEqual(left, right) {
  return left.length === right.length && left.every((item, index) => item === right[index]);
}

function validateHttpsUrl(value, fieldPath) {
  if (value === undefined) {
    return;
  }
  expect(typeof value === "string" && value.startsWith("https://"), `${fieldPath} must be an absolute https:// URL.`);
}

function normalizeManifestPath(value) {
  return String(value ?? "")
    .replace(/^\.\//, "")
    .replace(/\/$/, "");
}

function validatePluginRelativePath(pluginDir, value, expected, fieldPath) {
  const normalized = normalizeManifestPath(value);
  expect(normalized === expected, `${fieldPath} must resolve to ${expected}.`);
  expect(!path.isAbsolute(normalized) && !normalized.split(/[\\/]/).includes(".."), `${fieldPath} must stay inside the plugin root.`);
  return pathExists(repoPath(pluginDir, normalized));
}

function extractFrontmatter(text, filePath) {
  const lines = text.split(/\r?\n/);
  if (lines[0] !== "---") {
    add(`${filePath}: missing YAML frontmatter.`);
    return null;
  }
  const end = lines.findIndex((line, index) => index > 0 && line === "---");
  if (end < 0) {
    add(`${filePath}: unterminated YAML frontmatter.`);
    return null;
  }
  try {
    const frontmatter = parseYaml(lines.slice(1, end).join("\n"));
    if (!frontmatter || typeof frontmatter !== "object" || Array.isArray(frontmatter)) {
      add(`${filePath}: frontmatter must be a YAML object.`);
      return null;
    }
    return frontmatter;
  } catch (error) {
    add(`${filePath}: invalid YAML frontmatter (${error.message}).`);
    return null;
  }
}

// Resolve a relative reference against the citing file's directory, then (for
// `references/` and `scripts/` citations) against the plugin root, matching how
// skills cite plugin-level references and scripts.
async function referenceResolves(fileDir, pluginDir, target) {
  if (await pathExists(path.resolve(fileDir, target))) {
    return true;
  }
  if (/^(references|scripts)\//.test(target) && (await pathExists(path.resolve(pluginDir, target)))) {
    return true;
  }
  return false;
}

function isReferenceCandidate(target) {
  if (/^https?:|^mailto:|^#|^\$\{/.test(target)) {
    return false;
  }
  return /^\.\.?\//.test(target) || /^references\//.test(target) || /^scripts\//.test(target);
}

// Verify relative markdown links and backtick-quoted relative file paths resolve
// on disk; warn on hardcoded `plugins/<name>/` repo paths (cache-safety guard).
async function validateReferences(filePath, text, pluginDir) {
  const relativeFile = path.relative(repoRoot, filePath);
  const fileDir = path.dirname(filePath);
  const seen = new Set();

  const linkRe = /\[[^\]]*\]\(([^)]+)\)/g;
  let match;
  while ((match = linkRe.exec(text)) !== null) {
    const target = match[1].split(/\s+/)[0].replace(/#.*$/, "");
    if (!isReferenceCandidate(target) || seen.has(`L:${target}`)) {
      continue;
    }
    seen.add(`L:${target}`);
    if (!(await referenceResolves(fileDir, pluginDir, target))) {
      add(`${relativeFile}: markdown link target does not resolve: ${target}`);
    }
  }

  const tickRe = /`([^`]+)`/g;
  while ((match = tickRe.exec(text)) !== null) {
    const target = match[1].trim();
    const looksLikePath = /^\.\.?\//.test(target) || /^references\//.test(target) || /^scripts\//.test(target);
    const hasFileExtension = /\.(py|md|json|jsonl|sh|ya?ml|txt|csv)$/.test(target);
    if (!looksLikePath || !hasFileExtension || target.includes(" ") || seen.has(`T:${target}`)) {
      continue;
    }
    seen.add(`T:${target}`);
    if (!(await referenceResolves(fileDir, pluginDir, target))) {
      add(`${relativeFile}: referenced path does not resolve: ${target}`);
    }
  }

  // Cache-safety guard: hardcoded repo paths break marketplace-installed plugins,
  // which run from a cache. WARN (not error) — some are legitimate repo-run prose.
  const hardcodedRe = /\bplugins\/[a-z0-9][a-z0-9-]*\/(?:skills|agents|scripts|bin|references)\//g;
  const hardcoded = new Set();
  while ((match = hardcodedRe.exec(text)) !== null) {
    hardcoded.add(match[0]);
  }
  for (const hit of hardcoded) {
    addWarn(`${relativeFile}: hardcoded repo path in body may break cache installs: ${hit} (prefer \${CLAUDE_PLUGIN_ROOT}/)`);
  }
}

// Validate a single skill's frontmatter beyond the base required-field checks.
function validateSkillFrontmatter(relativeSkillPath, dirName, frontmatter) {
  // (a) `tools` is an agent-only field; on a skill it is a silent no-op.
  if (Object.hasOwn(frontmatter, "tools")) {
    add(`${relativeSkillPath}: 'tools' is an agent-only field and is invalid on a skill; use 'allowed-tools'.`);
  }

  // (b) every allowed-tools value must be canonical.
  if (frontmatter["allowed-tools"] !== undefined) {
    for (const tool of normalizeToolList(frontmatter["allowed-tools"])) {
      if (!isCanonicalTool(tool)) {
        add(`${relativeSkillPath}: allowed-tools contains non-canonical tool '${tool}' (see docs/SKILL_FRONTMATTER.md).`);
      }
    }
  }

  // (c) warn on frontmatter keys outside the documented spec.
  for (const key of Object.keys(frontmatter)) {
    if (!DOCUMENTED_SKILL_KEYS.has(key)) {
      addWarn(`${relativeSkillPath}: undocumented frontmatter key '${key}' (see docs/SKILL_FRONTMATTER.md).`);
    }
  }

  // (d) name must match the skill directory.
  if (frontmatter.name !== undefined && String(frontmatter.name) !== dirName) {
    add(`${relativeSkillPath}: frontmatter.name '${frontmatter.name}' must match skill directory '${dirName}'.`);
  }
}

// Validate plugin agent frontmatter (plugins/<plugin>/agents/*.md).
async function validateAgents(pluginDir) {
  for (const agentFile of await listFiles(pluginDir, "agents", ".md")) {
    const relativeAgentPath = path.relative(repoRoot, agentFile);
    const text = await readFile(agentFile, "utf8");
    const frontmatter = extractFrontmatter(text, relativeAgentPath);
    if (!frontmatter) {
      continue;
    }

    expect(Boolean(frontmatter.name), `${relativeAgentPath}: frontmatter.name is required.`);
    expect(Boolean(frontmatter.description), `${relativeAgentPath}: frontmatter.description is required.`);

    for (const key of Object.keys(frontmatter)) {
      if (AGENT_FORBIDDEN_FIELDS.has(key)) {
        add(`${relativeAgentPath}: '${key}' is not supported on plugin agents and is silently ignored — remove it.`);
      } else if (!AGENT_ALLOWED_FIELDS.has(key)) {
        add(`${relativeAgentPath}: unsupported agent frontmatter field '${key}' (see docs/SKILL_FRONTMATTER.md).`);
      }
    }

    for (const field of ["tools", "disallowedTools"]) {
      if (frontmatter[field] === undefined) {
        continue;
      }
      for (const tool of normalizeToolList(frontmatter[field])) {
        if (!isCanonicalTool(tool)) {
          add(`${relativeAgentPath}: ${field} contains non-canonical tool '${tool}' (see docs/SKILL_FRONTMATTER.md).`);
        }
      }
    }

    await validateReferences(agentFile, text, pluginDir);
  }
}

async function validateGeneratedFiles(catalog) {
  for (const file of generatedFiles(catalog)) {
    const actualPath = repoPath(repoRoot, file.path);
    let actual = "";
    try {
      actual = await readFile(actualPath, "utf8");
    } catch {
      add(`${file.path}: generated file is missing.`);
      continue;
    }
    if (actual !== file.text) {
      add(`${file.path}: generated file is stale; run npm run render.`);
    }
    if (/\bTODO\b/.test(actual)) {
      add(`${file.path}: generated files must not contain TODO placeholders.`);
    }
  }
}

function validateClaudeMarketplace(catalog, marketplace) {
  const expectedNames = pluginList(catalog).map((plugin) => plugin.name);
  expect(marketplace?.name === catalog.marketplace.name, `${CLAUDE_MARKETPLACE_PATH}: name must match marketplace.yaml.`);
  expect(marketplace?.metadata?.pluginRoot === "./plugins", `${CLAUDE_MARKETPLACE_PATH}: metadata.pluginRoot is required.`);
  const pluginNames = marketplace?.plugins?.map((plugin) => plugin.name) ?? [];
  expect(arraysEqual(pluginNames, expectedNames), `${CLAUDE_MARKETPLACE_PATH}: plugin order must match marketplace.yaml.`);

  for (const entry of marketplace?.plugins ?? []) {
    expect(entry.source === `./plugins/${entry.name}`, `${CLAUDE_MARKETPLACE_PATH}: ${entry.name}.source must be ./plugins/${entry.name}.`);
    expect(entry.version === undefined, `${CLAUDE_MARKETPLACE_PATH}: ${entry.name} must not duplicate plugin manifest version.`);
  }
}

function validateCodexMarketplace(catalog, marketplace) {
  const expectedNames = pluginList(catalog).map((plugin) => plugin.name);
  expect(marketplace?.name === catalog.marketplace.name, `${CODEX_MARKETPLACE_PATH}: name must match marketplace.yaml.`);
  expect(marketplace?.interface?.displayName === catalog.marketplace.displayName, `${CODEX_MARKETPLACE_PATH}: interface.displayName must match marketplace.yaml.`);
  const pluginNames = marketplace?.plugins?.map((plugin) => plugin.name) ?? [];
  expect(arraysEqual(pluginNames, expectedNames), `${CODEX_MARKETPLACE_PATH}: plugin order must match marketplace.yaml.`);

  for (const entry of marketplace?.plugins ?? []) {
    expect(entry.source?.source === "local", `${CODEX_MARKETPLACE_PATH}: ${entry.name}.source.source must be local.`);
    expect(entry.source?.path === `./plugins/${entry.name}`, `${CODEX_MARKETPLACE_PATH}: ${entry.name}.source.path must be ./plugins/${entry.name}.`);
    expect(INSTALLATION_VALUES.has(entry.policy?.installation), `${CODEX_MARKETPLACE_PATH}: ${entry.name}.policy.installation is invalid.`);
    expect(AUTHENTICATION_VALUES.has(entry.policy?.authentication), `${CODEX_MARKETPLACE_PATH}: ${entry.name}.policy.authentication is invalid.`);
    expect(Boolean(entry.category), `${CODEX_MARKETPLACE_PATH}: ${entry.name}.category is required.`);
  }
}

async function validatePlugin(catalog, plugin) {
  const pluginDir = repoPath(repoRoot, plugin.path);
  const claudePath = `${plugin.path}/.claude-plugin/plugin.json`;
  const codexPath = `${plugin.path}/.codex-plugin/plugin.json`;
  const claudeManifest = await readJson(claudePath);
  const codexManifest = await readJson(codexPath);

  if (!claudeManifest || !codexManifest) {
    return;
  }

  expect(claudeManifest.name === plugin.name, `${claudePath}: name must match marketplace.yaml.`);
  expect(codexManifest.name === plugin.name, `${codexPath}: name must match marketplace.yaml.`);
  expect(claudeManifest.version === codexManifest.version, `${plugin.name}: Claude and Codex manifest versions must match.`);
  expect(claudeManifest.description === codexManifest.description, `${plugin.name}: Claude and Codex manifest descriptions must match.`);

  const allowedCodexFields = new Set([
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
  ]);
  for (const key of Object.keys(codexManifest)) {
    expect(allowedCodexFields.has(key), `${codexPath}: unsupported Codex manifest field ${key}.`);
  }

  for (const key of ["name", "version", "description", "author", "skills", "interface"]) {
    expect(codexManifest[key] !== undefined && codexManifest[key] !== "", `${codexPath}: missing required field ${key}.`);
  }

  expect(STRICT_SEMVER.test(codexManifest.version ?? ""), `${codexPath}: version must be strict semver.`);
  expect(typeof codexManifest.author === "object" && Boolean(codexManifest.author?.name), `${codexPath}: author.name is required.`);

  if (pluginComponents(plugin).skills) {
    expect(await validatePluginRelativePath(pluginDir, codexManifest.skills, "skills", `${codexPath}: skills`), `${codexPath}: skills path does not exist.`);
  }

  if (codexManifest.apps) {
    expect(await validatePluginRelativePath(pluginDir, codexManifest.apps, ".app.json", `${codexPath}: apps`), `${codexPath}: apps path does not exist.`);
  }
  if (codexManifest.mcpServers) {
    expect(await validatePluginRelativePath(pluginDir, codexManifest.mcpServers, ".mcp.json", `${codexPath}: mcpServers`), `${codexPath}: mcpServers path does not exist.`);
  }

  const expectedInterface = codexInterface(plugin, catalog);
  const interfaceFields = ["displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"];
  for (const key of interfaceFields) {
    expect(codexManifest.interface?.[key] !== undefined, `${codexPath}: interface.${key} is required.`);
  }
  expect(codexManifest.interface?.displayName === expectedInterface.displayName, `${codexPath}: interface.displayName must match marketplace.yaml.`);
  expect(Array.isArray(codexManifest.interface?.capabilities), `${codexPath}: interface.capabilities must be an array.`);
  expect(Array.isArray(codexManifest.interface?.defaultPrompt), `${codexPath}: interface.defaultPrompt must be an array.`);
  if (codexManifest.interface?.brandColor) {
    expect(HEX_COLOR.test(codexManifest.interface.brandColor), `${codexPath}: interface.brandColor must use #RRGGBB.`);
  }
  validateHttpsUrl(codexManifest.interface?.websiteURL, `${codexPath}: interface.websiteURL`);
  validateHttpsUrl(codexManifest.interface?.privacyPolicyURL, `${codexPath}: interface.privacyPolicyURL`);
  validateHttpsUrl(codexManifest.interface?.termsOfServiceURL, `${codexPath}: interface.termsOfServiceURL`);

  for (const assetField of ["composerIcon", "logo"]) {
    const assetPath = codexManifest.interface?.[assetField];
    if (assetPath) {
      expect(await validatePluginRelativePath(pluginDir, assetPath, normalizeManifestPath(assetPath), `${codexPath}: interface.${assetField}`), `${codexPath}: interface.${assetField} path does not exist.`);
    }
  }
  for (const [index, screenshot] of (codexManifest.interface?.screenshots ?? []).entries()) {
    expect(await validatePluginRelativePath(pluginDir, screenshot, normalizeManifestPath(screenshot), `${codexPath}: interface.screenshots[${index}]`), `${codexPath}: interface.screenshots[${index}] path does not exist.`);
  }

  for (const skillFile of await listSkillFiles(pluginDir)) {
    const relativeSkillPath = path.relative(repoRoot, skillFile);
    const dirName = path.basename(path.dirname(skillFile));
    const text = await readFile(skillFile, "utf8");
    const frontmatter = extractFrontmatter(text, relativeSkillPath);
    if (!frontmatter) {
      continue;
    }
    expect(Boolean(frontmatter.name), `${relativeSkillPath}: frontmatter.name is required.`);
    expect(Boolean(frontmatter.description), `${relativeSkillPath}: frontmatter.description is required.`);
    expect(KEBAB_CASE.test(String(frontmatter.name)), `${relativeSkillPath}: frontmatter.name must be lowercase kebab-case.`);
    expect(frontmatter["disable-model-invocation"] !== undefined, `${relativeSkillPath}: disable-model-invocation is required for shared Codex skills.`);
    validateSkillFrontmatter(relativeSkillPath, dirName, frontmatter);
    await validateReferences(skillFile, text, pluginDir);
  }

  await validateAgents(pluginDir);
}

async function main() {
  const catalog = await readCatalog(repoRoot);
  await validateGeneratedFiles(catalog);

  const claudeMarketplace = await readJson(CLAUDE_MARKETPLACE_PATH);
  const codexMarketplace = await readJson(CODEX_MARKETPLACE_PATH);
  if (claudeMarketplace) {
    validateClaudeMarketplace(catalog, claudeMarketplace);
  }
  if (codexMarketplace) {
    validateCodexMarketplace(catalog, codexMarketplace);
  }

  for (const plugin of pluginList(catalog)) {
    await validatePlugin(catalog, plugin);
  }

  if (warnings.length > 0) {
    console.warn(`marketplace validation warnings (${warnings.length}):`);
    for (const warning of warnings) {
      console.warn(`- ${warning}`);
    }
  }

  if (errors.length > 0) {
    console.error(`marketplace validation failed (${errors.length} issue${errors.length === 1 ? "" : "s"}):`);
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log(`marketplace validation passed (${pluginList(catalog).length} plugin(s), ${warnings.length} warning(s))`);
}

// Exported for targeted unit tests; the module only runs the full sweep when
// executed directly (not when imported).
export { errors, warnings, validateSkillFrontmatter, validateReferences, validateAgents, extractFrontmatter };

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
