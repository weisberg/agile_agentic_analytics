#!/usr/bin/env node
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { generatedFiles, MarketplaceError, readCatalog, repoPath } from "./marketplace-lib.mjs";

const args = new Set(process.argv.slice(2));
const checkOnly = args.has("--check");
const repoRoot = process.cwd();

try {
  const catalog = await readCatalog(repoRoot);
  const files = generatedFiles(catalog);
  const stale = [];

  for (const file of files) {
    const absolutePath = repoPath(repoRoot, file.path);
    if (checkOnly) {
      let current = "";
      try {
        current = await readFile(absolutePath, "utf8");
      } catch {
        stale.push(`${file.path} (missing)`);
        continue;
      }
      if (current !== file.text) {
        stale.push(file.path);
      }
      continue;
    }

    await mkdir(path.dirname(absolutePath), { recursive: true });
    await writeFile(absolutePath, file.text, "utf8");
  }

  if (checkOnly && stale.length > 0) {
    console.error("Generated marketplace files are stale:");
    for (const filePath of stale) {
      console.error(`- ${filePath}`);
    }
    console.error("Run `npm run render` to refresh them.");
    process.exit(1);
  }

  if (checkOnly) {
    console.log(`render check passed (${files.length} generated files current)`);
  } else {
    console.log(`rendered ${files.length} marketplace file(s)`);
  }
} catch (error) {
  if (error instanceof MarketplaceError) {
    console.error("marketplace catalog validation failed:");
    for (const message of error.errors) {
      console.error(`- ${message}`);
    }
    process.exit(1);
  }
  throw error;
}
