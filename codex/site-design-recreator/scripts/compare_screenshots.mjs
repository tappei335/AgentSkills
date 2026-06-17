#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const usage = `Usage:
  node compare_screenshots.mjs <expected-image> <actual-image> [options]

Options:
  --out <path>          Write a red diff PNG.
  --threshold <0-255>   Per-channel pixel threshold. Default: 10.
  --fail-over <ratio>   Exit 2 when diff ratio exceeds this value. Default: 0.005.
  --allow-size-mismatch Compare different-sized images using the larger canvas.
  --help               Show this help.
`;

function parseArgs(argv) {
  const args = {
    expected: null,
    actual: null,
    out: null,
    threshold: 10,
    failOver: 0.005,
    allowSizeMismatch: false,
    help: false,
  };

  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") {
      args.help = true;
    } else if (arg === "--out") {
      args.out = argv[++i];
    } else if (arg === "--threshold") {
      args.threshold = Number(argv[++i]);
    } else if (arg === "--fail-over") {
      args.failOver = Number(argv[++i]);
    } else if (arg === "--allow-size-mismatch") {
      args.allowSizeMismatch = true;
    } else if (arg.startsWith("--")) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      positional.push(arg);
    }
  }

  [args.expected, args.actual] = positional;
  return args;
}

function mimeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "image/png";
}

function dataUrl(filePath) {
  return `data:${mimeFor(filePath)};base64,${fs.readFileSync(filePath, "base64")}`;
}

function validateArgs(args) {
  if (args.help) return;
  if (!args.expected || !args.actual) {
    throw new Error("expected-image and actual-image are required");
  }
  if (!Number.isFinite(args.threshold) || args.threshold < 0 || args.threshold > 255) {
    throw new Error("--threshold must be a number from 0 to 255");
  }
  if (!Number.isFinite(args.failOver) || args.failOver < 0 || args.failOver > 1) {
    throw new Error("--fail-over must be a ratio from 0 to 1");
  }
  for (const filePath of [args.expected, args.actual]) {
    if (!fs.existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  validateArgs(args);

  if (args.help) {
    process.stdout.write(usage);
    return;
  }

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    throw new Error("The Playwright package is required. Install it in the target project with `npm install -D playwright`.");
  }

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    const result = await page.evaluate(
      async ({ expectedUrl, actualUrl, threshold, makeDiff }) => {
        function loadImage(src) {
          return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => reject(new Error(`Failed to load image: ${src.slice(0, 64)}...`));
            img.src = src;
          });
        }

        function imageDataFor(img, width, height) {
          const canvas = document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          const context = canvas.getContext("2d", { willReadFrequently: true });
          context.clearRect(0, 0, width, height);
          context.drawImage(img, 0, 0);
          return context.getImageData(0, 0, width, height);
        }

        const [expected, actual] = await Promise.all([loadImage(expectedUrl), loadImage(actualUrl)]);
        const width = Math.max(expected.naturalWidth, actual.naturalWidth);
        const height = Math.max(expected.naturalHeight, actual.naturalHeight);
        const expectedData = imageDataFor(expected, width, height).data;
        const actualData = imageDataFor(actual, width, height).data;
        const diffCanvas = document.createElement("canvas");
        diffCanvas.width = width;
        diffCanvas.height = height;
        const diffContext = diffCanvas.getContext("2d");
        const diff = diffContext.createImageData(width, height);

        let diffPixels = 0;
        let totalDelta = 0;
        let maxDelta = 0;

        for (let i = 0; i < expectedData.length; i += 4) {
          const dr = Math.abs(expectedData[i] - actualData[i]);
          const dg = Math.abs(expectedData[i + 1] - actualData[i + 1]);
          const db = Math.abs(expectedData[i + 2] - actualData[i + 2]);
          const da = Math.abs(expectedData[i + 3] - actualData[i + 3]);
          const delta = Math.max(dr, dg, db, da);
          const pixelChanged = delta > threshold;

          maxDelta = Math.max(maxDelta, delta);
          totalDelta += (dr + dg + db + da) / 4;
          if (pixelChanged) diffPixels += 1;

          if (pixelChanged) {
            diff.data[i] = 255;
            diff.data[i + 1] = 0;
            diff.data[i + 2] = 0;
            diff.data[i + 3] = 255;
          } else {
            const gray = Math.round((expectedData[i] + expectedData[i + 1] + expectedData[i + 2]) / 3);
            diff.data[i] = gray;
            diff.data[i + 1] = gray;
            diff.data[i + 2] = gray;
            diff.data[i + 3] = 80;
          }
        }

        diffContext.putImageData(diff, 0, 0);
        const totalPixels = width * height;
        return {
          expectedWidth: expected.naturalWidth,
          expectedHeight: expected.naturalHeight,
          actualWidth: actual.naturalWidth,
          actualHeight: actual.naturalHeight,
          canvasWidth: width,
          canvasHeight: height,
          dimensionMismatch: expected.naturalWidth !== actual.naturalWidth || expected.naturalHeight !== actual.naturalHeight,
          diffPixels,
          totalPixels,
          diffRatio: diffPixels / totalPixels,
          averageDelta: totalDelta / totalPixels,
          maxDelta,
          diffPng: makeDiff ? diffCanvas.toDataURL("image/png") : null,
        };
      },
      {
        expectedUrl: dataUrl(args.expected),
        actualUrl: dataUrl(args.actual),
        threshold: args.threshold,
        makeDiff: Boolean(args.out),
      },
    );

    if (args.out && result.diffPng) {
      fs.mkdirSync(path.dirname(args.out), { recursive: true });
      fs.writeFileSync(args.out, Buffer.from(result.diffPng.split(",", 2)[1], "base64"));
    }

    const printable = { ...result };
    delete printable.diffPng;
    console.log(JSON.stringify(printable, null, 2));

    const failedSize = result.dimensionMismatch && !args.allowSizeMismatch;
    if (failedSize || result.diffRatio > args.failOver) {
      process.exitCode = 2;
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
