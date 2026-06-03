import { access, readFile } from "node:fs/promises";
import path from "node:path";
import { parse as parseYaml } from "yaml";

export const CATALOG_PATH = "marketplace.yaml";
export const CLAUDE_MARKETPLACE_PATH = ".claude-plugin/marketplace.json";
export const CODEX_MARKETPLACE_PATH = ".agents/plugins/marketplace.json";

export const INSTALLATION_VALUES = new Set(["NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"]);
export const AUTHENTICATION_VALUES = new Set(["ON_INSTALL", "ON_USE"]);
export const KEBAB_CASE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
export const STRICT_SEMVER =
  /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$/;
export const HEX_COLOR = /^#[0-9A-Fa-f]{6}$/;

const OPTIONAL_COMPONENT_PATHS = {
  agents: { field: "agents", path: "agents", manifestPath: "./agents/" },
  apps: { field: "apps", path: ".app.json", manifestPath: "./.app.json" },
  commands: { field: "commands", path: "commands", manifestPath: "./commands/" },
  hooks: { field: "hooks", path: "hooks/hooks.json", manifestPath: "./hooks/hooks.json" },
  lsp: { field: "lspServers", path: ".lsp.json", manifestPath: "./.lsp.json" },
  mcp: { field: "mcpServers", path: ".mcp.json", manifestPath: "./.mcp.json" },
  skills: { field: "skills", path: "skills", manifestPath: "./skills/" },
};

export class MarketplaceError extends Error {
  constructor(errors) {
    super(errors.join("\n"));
    this.name = "MarketplaceError";
    this.errors = errors;
  }
}

export function repoPath(repoRoot, relativePath) {
  return path.join(repoRoot, relativePath);
}

export function toPosix(value) {
  return value.split(path.sep).join("/");
}

export async function pathExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

export function jsonText(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

export async function readCatalog(repoRoot = process.cwd()) {
  const catalogFile = repoPath(repoRoot, CATALOG_PATH);
  const raw = await readFile(catalogFile, "utf8");
  const catalog = parseYaml(raw);
  await validateCatalog(catalog, repoRoot);
  return catalog;
}

export function normalizedAuthor(plugin, catalog) {
  const fallback = catalog.defaults?.author ?? catalog.marketplace?.owner ?? {};
  const author = plugin.author ?? fallback;
  if (typeof author === "string") {
    return { name: author };
  }
  return cleanObject({
    name: author.name ?? fallback.name,
    email: author.email ?? fallback.email,
    url: author.url ?? fallback.url,
  });
}

export function cleanObject(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) => (isPlainObject(item) || Array.isArray(item) ? cleanObject(item) : item))
      .filter((item) => item !== undefined && item !== null && item !== "");
  }

  if (!isPlainObject(value)) {
    return value;
  }

  const cleaned = {};
  for (const [key, item] of Object.entries(value)) {
    if (item === undefined || item === null || item === "") {
      continue;
    }
    const cleanedItem = cleanObject(item);
    if (Array.isArray(cleanedItem) && cleanedItem.length === 0) {
      cleaned[key] = cleanedItem;
      continue;
    }
    if (isPlainObject(cleanedItem) && Object.keys(cleanedItem).length === 0) {
      continue;
    }
    cleaned[key] = cleanedItem;
  }
  return cleaned;
}

export function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function pluginList(catalog) {
  return catalog.plugins ?? [];
}

export function pluginCategory(plugin, catalog) {
  return plugin.category ?? catalog.defaults?.category ?? "Developer Tools";
}

export function pluginLicense(plugin, catalog) {
  return plugin.license ?? catalog.defaults?.license ?? "MIT";
}

export function pluginRepository(plugin, catalog) {
  return plugin.repository ?? catalog.marketplace?.repository;
}

export function pluginComponents(plugin) {
  return {
    skills: true,
    ...(plugin.components ?? {}),
  };
}

export function codexPolicy(plugin, catalog) {
  const defaults = catalog.defaults ?? {};
  return {
    installation: plugin.codex?.installation ?? plugin.installPolicy ?? defaults.installPolicy ?? "AVAILABLE",
    authentication: plugin.codex?.authentication ?? plugin.authPolicy ?? defaults.authPolicy ?? "ON_INSTALL",
  };
}

export function codexInterface(plugin, catalog) {
  const defaults = catalog.defaults ?? {};
  const codexDefaults = defaults.codex?.interface ?? {};
  const codex = plugin.codex?.interface ?? {};
  const author = normalizedAuthor(plugin, catalog);
  const category = pluginCategory(plugin, catalog);
  const homepage = plugin.homepage ?? pluginRepository(plugin, catalog);

  return cleanObject({
    displayName: plugin.displayName,
    shortDescription: codex.shortDescription ?? plugin.description,
    longDescription: codex.longDescription ?? plugin.description,
    developerName: codex.developerName ?? codexDefaults.developerName ?? author.name,
    category,
    capabilities: plugin.capabilities ?? [],
    websiteURL: homepage,
    privacyPolicyURL: codex.privacyPolicyURL,
    termsOfServiceURL: codex.termsOfServiceURL,
    brandColor: codex.brandColor ?? codexDefaults.brandColor ?? defaults.brandColor,
    defaultPrompt: plugin.defaultPrompt ?? [],
    composerIcon: codex.composerIcon,
    logo: codex.logo,
    screenshots: codex.screenshots,
  });
}

export async function validateCatalog(catalog, repoRoot = process.cwd()) {
  const errors = [];

  if (!isPlainObject(catalog)) {
    throw new MarketplaceError(["marketplace.yaml must parse to an object."]);
  }

  if (!isPlainObject(catalog.marketplace)) {
    errors.push("marketplace.yaml must define marketplace metadata.");
  } else {
    if (!KEBAB_CASE.test(catalog.marketplace.name ?? "")) {
      errors.push("marketplace.name must be lowercase kebab-case.");
    }
    if (!catalog.marketplace.displayName) {
      errors.push("marketplace.displayName is required.");
    }
    if (!catalog.marketplace.description) {
      errors.push("marketplace.description is required.");
    }
    if (catalog.marketplace.version && !STRICT_SEMVER.test(String(catalog.marketplace.version))) {
      errors.push("marketplace.version must be strict semver when present.");
    }
  }

  if (!Array.isArray(catalog.plugins) || catalog.plugins.length === 0) {
    errors.push("plugins must contain at least one plugin.");
  }

  const seen = new Set();
  for (const [index, plugin] of (catalog.plugins ?? []).entries()) {
    const prefix = `plugins[${index}]`;
    if (!isPlainObject(plugin)) {
      errors.push(`${prefix} must be an object.`);
      continue;
    }

    const name = plugin.name ?? "";
    if (!KEBAB_CASE.test(name)) {
      errors.push(`${prefix}.name must be lowercase kebab-case.`);
    }
    if (name.length > 64) {
      errors.push(`${prefix}.name must be no longer than 64 characters.`);
    }
    if (seen.has(name)) {
      errors.push(`${prefix}.name duplicates another plugin.`);
    }
    seen.add(name);

    const expectedPath = `plugins/${name}`;
    if (plugin.path !== expectedPath) {
      errors.push(`${prefix}.path must equal ${expectedPath}.`);
    }
    if (hasPathTraversal(plugin.path)) {
      errors.push(`${prefix}.path must not traverse outside the marketplace root.`);
    }

    const pluginDir = repoPath(repoRoot, plugin.path ?? expectedPath);
    if (!(await pathExists(pluginDir))) {
      errors.push(`${prefix}.path does not exist: ${plugin.path}.`);
    }

    if (!plugin.displayName) {
      errors.push(`${prefix}.displayName is required.`);
    }
    if (!plugin.description) {
      errors.push(`${prefix}.description is required.`);
    }
    if (plugin.version && !STRICT_SEMVER.test(String(plugin.version))) {
      errors.push(`${prefix}.version must be strict semver when present.`);
    }

    const policy = codexPolicy(plugin, catalog);
    if (!INSTALLATION_VALUES.has(policy.installation)) {
      errors.push(`${prefix}.codex.installation must be one of ${Array.from(INSTALLATION_VALUES).join(", ")}.`);
    }
    if (!AUTHENTICATION_VALUES.has(policy.authentication)) {
      errors.push(`${prefix}.codex.authentication must be one of ${Array.from(AUTHENTICATION_VALUES).join(", ")}.`);
    }

    const components = pluginComponents(plugin);
    for (const [component, enabled] of Object.entries(components)) {
      if (!Object.hasOwn(OPTIONAL_COMPONENT_PATHS, component)) {
        errors.push(`${prefix}.components.${component} is not supported by the renderer.`);
        continue;
      }
      if (!enabled) {
        continue;
      }
      const componentInfo = OPTIONAL_COMPONENT_PATHS[component];
      const componentPath = repoPath(pluginDir, componentInfo.path);
      if (!(await pathExists(componentPath))) {
        errors.push(`${prefix}.components.${component} is true but ${plugin.path}/${componentInfo.path} does not exist.`);
      }
      if (component === "skills") {
        const skillFiles = await listSkillFiles(pluginDir);
        if (skillFiles.length === 0) {
          errors.push(`${prefix}.components.skills is true but no skills/*/SKILL.md files were found.`);
        }
      }
      if (component === "agents") {
        const agentFiles = await listFiles(pluginDir, "agents", ".md");
        if (agentFiles.length === 0) {
          errors.push(`${prefix}.components.agents is true but no agents/*.md files were found.`);
        }
      }
    }

    for (const candidate of collectRelativePaths(plugin)) {
      if (hasPathTraversal(candidate)) {
        errors.push(`${prefix} contains a relative path that traverses outside the marketplace root: ${candidate}.`);
      }
    }
  }

  if (errors.length) {
    throw new MarketplaceError(errors);
  }
}

export async function listSkillFiles(pluginDir) {
  const skillsDir = repoPath(pluginDir, "skills");
  if (!(await pathExists(skillsDir))) {
    return [];
  }
  const { readdir } = await import("node:fs/promises");
  const entries = await readdir(skillsDir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }
    const skillFile = repoPath(skillsDir, `${entry.name}/SKILL.md`);
    if (await pathExists(skillFile)) {
      files.push(skillFile);
    }
  }
  return files.sort();
}

export async function listFiles(pluginDir, relativeDir, extension) {
  const directory = repoPath(pluginDir, relativeDir);
  if (!(await pathExists(directory))) {
    return [];
  }
  const { readdir } = await import("node:fs/promises");
  const entries = await readdir(directory, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith(extension))
    .map((entry) => repoPath(directory, entry.name))
    .sort();
}

export function generatedFiles(catalog) {
  const files = [
    {
      path: CLAUDE_MARKETPLACE_PATH,
      data: buildClaudeMarketplace(catalog),
    },
    {
      path: CODEX_MARKETPLACE_PATH,
      data: buildCodexMarketplace(catalog),
    },
  ];

  for (const plugin of pluginList(catalog)) {
    files.push({
      path: `${plugin.path}/.claude-plugin/plugin.json`,
      data: buildClaudePluginManifest(plugin, catalog),
    });
    files.push({
      path: `${plugin.path}/.codex-plugin/plugin.json`,
      data: buildCodexPluginManifest(plugin, catalog),
    });
  }

  return files.map((file) => ({
    path: file.path,
    text: jsonText(file.data),
  }));
}

export function buildClaudeMarketplace(catalog) {
  return cleanObject({
    name: catalog.marketplace.name,
    owner: cleanObject({
      name: catalog.marketplace.owner?.name,
      email: catalog.marketplace.owner?.email,
    }),
    description: catalog.marketplace.description,
    version: String(catalog.marketplace.version),
    metadata: {
      pluginRoot: "./plugins",
    },
    plugins: pluginList(catalog).map((plugin) =>
      cleanObject({
        name: plugin.name,
        source: `./${plugin.path}`,
        displayName: plugin.displayName,
        description: plugin.description,
        author: normalizedAuthor(plugin, catalog),
        homepage: plugin.homepage,
        repository: pluginRepository(plugin, catalog),
        license: pluginLicense(plugin, catalog),
        keywords: plugin.keywords ?? [],
        category: pluginCategory(plugin, catalog),
        defaultEnabled: plugin.claude?.defaultEnabled ?? catalog.defaults?.claude?.defaultEnabled,
        strict: plugin.claude?.strict ?? catalog.defaults?.claude?.strict,
      }),
    ),
  });
}

export function buildCodexMarketplace(catalog) {
  return cleanObject({
    name: catalog.marketplace.name,
    interface: {
      displayName: catalog.marketplace.displayName,
    },
    plugins: pluginList(catalog).map((plugin) => ({
      name: plugin.name,
      source: {
        source: "local",
        path: `./${plugin.path}`,
      },
      policy: codexPolicy(plugin, catalog),
      category: pluginCategory(plugin, catalog),
    })),
  });
}

export function buildClaudePluginManifest(plugin, catalog) {
  const components = pluginComponents(plugin);
  const manifest = {
    name: plugin.name,
    displayName: plugin.displayName,
    version: String(plugin.version),
    description: plugin.description,
    author: normalizedAuthor(plugin, catalog),
    homepage: plugin.homepage,
    repository: pluginRepository(plugin, catalog),
    license: pluginLicense(plugin, catalog),
    keywords: plugin.keywords ?? [],
  };

  if (components.skills) {
    manifest.skills = "./skills/";
  }
  if (components.mcp) {
    manifest.mcpServers = "./.mcp.json";
  }
  if (components.hooks) {
    manifest.hooks = "./hooks/hooks.json";
  }
  if (components.commands) {
    manifest.commands = "./commands/";
  }
  if (components.lsp) {
    manifest.lspServers = "./.lsp.json";
  }
  if (plugin.claude?.userConfig) {
    manifest.userConfig = plugin.claude.userConfig;
  }
  if (plugin.claude?.defaultEnabled ?? catalog.defaults?.claude?.defaultEnabled) {
    manifest.defaultEnabled = plugin.claude?.defaultEnabled ?? catalog.defaults?.claude?.defaultEnabled;
  }

  return cleanObject(manifest);
}

export function buildCodexPluginManifest(plugin, catalog) {
  const components = pluginComponents(plugin);
  const manifest = {
    name: plugin.name,
    version: String(plugin.version),
    description: plugin.description,
    author: normalizedAuthor(plugin, catalog),
    homepage: plugin.homepage,
    repository: pluginRepository(plugin, catalog),
    license: pluginLicense(plugin, catalog),
    keywords: plugin.keywords ?? [],
  };

  if (components.skills) {
    manifest.skills = "./skills/";
  }
  if (components.mcp) {
    manifest.mcpServers = "./.mcp.json";
  }
  if (components.apps) {
    manifest.apps = "./.app.json";
  }

  manifest.interface = codexInterface(plugin, catalog);
  return cleanObject(manifest);
}

export function hasPathTraversal(relativePath) {
  if (!relativePath || typeof relativePath !== "string") {
    return false;
  }
  if (path.isAbsolute(relativePath)) {
    return true;
  }
  return path.normalize(relativePath).split(path.sep).includes("..");
}

function collectRelativePaths(plugin) {
  const paths = [plugin.path];
  const codexInterfaceConfig = plugin.codex?.interface ?? {};
  for (const key of ["composerIcon", "logo"]) {
    if (codexInterfaceConfig[key]) {
      paths.push(codexInterfaceConfig[key]);
    }
  }
  for (const screenshot of codexInterfaceConfig.screenshots ?? []) {
    paths.push(screenshot);
  }
  return paths;
}
