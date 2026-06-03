#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import path from "node:path";
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
  listSkillFiles,
  pathExists,
  pluginComponents,
  pluginList,
  readCatalog,
  repoPath,
} from "./marketplace-lib.mjs";

const repoRoot = process.cwd();
const errors = [];

function add(message) {
  errors.push(message);
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
    const text = await readFile(skillFile, "utf8");
    const frontmatter = extractFrontmatter(text, relativeSkillPath);
    if (!frontmatter) {
      continue;
    }
    expect(Boolean(frontmatter.name), `${relativeSkillPath}: frontmatter.name is required.`);
    expect(Boolean(frontmatter.description), `${relativeSkillPath}: frontmatter.description is required.`);
    expect(KEBAB_CASE.test(String(frontmatter.name)), `${relativeSkillPath}: frontmatter.name must be lowercase kebab-case.`);
    expect(frontmatter["disable-model-invocation"] !== undefined, `${relativeSkillPath}: disable-model-invocation is required for shared Codex skills.`);
  }
}

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

if (errors.length > 0) {
  console.error(`marketplace validation failed (${errors.length} issue${errors.length === 1 ? "" : "s"}):`);
  for (const error of errors) {
    console.error(`- ${error}`);
  }
  process.exit(1);
}

console.log(`marketplace validation passed (${pluginList(catalog).length} plugin(s))`);
