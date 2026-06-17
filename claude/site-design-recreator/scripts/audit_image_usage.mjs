#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const usage = `Usage:
  node audit_image_usage.mjs <project-root>

Reports raster/vector asset references that may indicate screenshot-heavy UI reconstruction.
`;

const IMAGE_EXTENSIONS = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"]);
const SOURCE_EXTENSIONS = new Set([".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro"]);
const IGNORE_DIRS = new Set([".git", "node_modules", "dist", "build", ".next", ".nuxt", ".design-reference", ".design-actual", ".design-diff"]);
const RISKY_NAME = /(screen|screenshot|capture|canvas|panel|page|navbar|nav|card|sidebar|toolbar|modal|dialog|full|desktop|mobile|view|viewer)/i;
const RISKY_CODE_PATTERNS = [
  { name: "stretched-background", pattern: /background-size\s*:\s*100%\s+100%/i },
  { name: "object-fill", pattern: /object-fit\s*:\s*fill/i },
  { name: "risky-background-variable", pattern: /background-image\s*:\s*var\(--[^)]*(?:screen|screenshot|capture|canvas|panel|page|desktop|mobile|view|viewer)[^)]*\)/i },
  { name: "risky-background-url", pattern: /background-image\s*:\s*url\([^)]*(?:screen|screenshot|capture|canvas|panel|page|desktop|mobile|view|viewer)[^)]*\)/i },
];

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, files);
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

function relative(root, filePath) {
  return path.relative(root, filePath) || ".";
}

function readImageDimensions(filePath) {
  const buffer = fs.readFileSync(filePath);
  const ext = path.extname(filePath).toLowerCase();

  if (ext === ".png" && buffer.length >= 24 && buffer.toString("ascii", 1, 4) === "PNG") {
    return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
  }

  if ((ext === ".jpg" || ext === ".jpeg") && buffer.length >= 4) {
    let offset = 2;
    while (offset + 9 < buffer.length) {
      if (buffer[offset] !== 0xff) break;
      const marker = buffer[offset + 1];
      const length = buffer.readUInt16BE(offset + 2);
      if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
        return { width: buffer.readUInt16BE(offset + 7), height: buffer.readUInt16BE(offset + 5) };
      }
      offset += 2 + length;
    }
  }

  if (ext === ".webp" && buffer.length >= 30 && buffer.toString("ascii", 0, 4) === "RIFF" && buffer.toString("ascii", 8, 12) === "WEBP") {
    const chunk = buffer.toString("ascii", 12, 16);
    if (chunk === "VP8X" && buffer.length >= 30) {
      return {
        width: 1 + buffer.readUIntLE(24, 3),
        height: 1 + buffer.readUIntLE(27, 3),
      };
    }
    if (chunk === "VP8 " && buffer.length >= 30) {
      return {
        width: buffer.readUInt16LE(26) & 0x3fff,
        height: buffer.readUInt16LE(28) & 0x3fff,
      };
    }
  }

  return { width: null, height: null };
}

function main() {
  const root = process.argv[2];
  if (!root || root === "--help" || root === "-h") {
    process.stdout.write(usage);
    process.exit(root ? 0 : 1);
  }

  const projectRoot = path.resolve(root);
  if (!fs.existsSync(projectRoot) || !fs.statSync(projectRoot).isDirectory()) {
    throw new Error(`Project root is not a directory: ${projectRoot}`);
  }

  const files = walk(projectRoot);
  const assets = files
    .filter((filePath) => IMAGE_EXTENSIONS.has(path.extname(filePath).toLowerCase()))
    .map((filePath) => {
      const stat = fs.statSync(filePath);
      const dimensions = readImageDimensions(filePath);
      const pixels = dimensions.width && dimensions.height ? dimensions.width * dimensions.height : null;
      return {
        path: relative(projectRoot, filePath),
        sizeKb: Math.round(stat.size / 1024),
        ...dimensions,
        pixels,
        riskyName: RISKY_NAME.test(path.basename(filePath)),
      };
    })
    .sort((a, b) => b.sizeKb - a.sizeKb || a.path.localeCompare(b.path));

  const references = [];
  const riskyCode = [];
  const imagePattern = /(?:url\(["']?([^"')]+)["']?\)|src=["']([^"']+)["']|["']([^"']+\.(?:png|jpe?g|webp|gif|svg|avif)(?:\?[^"']*)?)["'])/gi;
  for (const filePath of files) {
    if (!SOURCE_EXTENSIONS.has(path.extname(filePath).toLowerCase())) continue;
    const text = fs.readFileSync(filePath, "utf8");
    const lines = text.split(/\r?\n/);
    for (const match of text.matchAll(imagePattern)) {
      const value = match[1] || match[2] || match[3];
      references.push({
        file: relative(projectRoot, filePath),
        value,
        riskyName: RISKY_NAME.test(value),
      });
    }
    lines.forEach((line, index) => {
      for (const { name, pattern } of RISKY_CODE_PATTERNS) {
        if (pattern.test(line)) {
          riskyCode.push({
            file: relative(projectRoot, filePath),
            line: index + 1,
            pattern: name,
            text: line.trim(),
          });
        }
      }
    });
  }

  const riskyAssets = assets.filter((asset) => asset.riskyName || asset.sizeKb >= 250 || (asset.pixels !== null && asset.pixels >= 500000));
  const riskyReferences = references.filter((reference) => reference.riskyName);

  console.log(JSON.stringify(
    {
      root: projectRoot,
      imageAssetCount: assets.length,
      imageReferenceCount: references.length,
      largestAssets: assets.slice(0, 20),
      riskyAssets,
      riskyReferences,
      riskyCode,
      reviewRequired: riskyAssets.length > 0 || riskyReferences.length > 0 || riskyCode.length > 0,
    },
    null,
    2,
  ));

  if (riskyAssets.length > 0 || riskyReferences.length > 0 || riskyCode.length > 0) {
    process.exitCode = 2;
  }
}

main();
