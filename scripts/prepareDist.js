import fs from "node:fs/promises";
import path from "node:path";

const distDir = path.join(process.cwd(), "dist");
const assetsSourceDir = path.join(process.cwd(), "assets");
const assetsTargetDir = path.join(distDir, "assets");
const rootFilesToCopy = ["robots.txt", "sitemap.xml", "CNAME"];
const cleanOnly = process.argv.includes("--clean-only");

async function main() {
  await fs.rm(distDir, { recursive: true, force: true });

  if (cleanOnly) {
    return;
  }

  await fs.mkdir(distDir, { recursive: true });
  await copyAssetsExcludingImages(assetsSourceDir, assetsTargetDir);
  await copyRootFiles();
}

async function copyAssetsExcludingImages(sourceDir, targetDir) {
  let entries;

  try {
    entries = await fs.readdir(sourceDir, { withFileTypes: true });
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return;
    }
    throw error;
  }

  await fs.mkdir(targetDir, { recursive: true });

  for (const entry of entries) {
    if (entry.name === "images") {
      continue;
    }

    const sourcePath = path.join(sourceDir, entry.name);
    const targetPath = path.join(targetDir, entry.name);

    if (entry.isDirectory()) {
      await copyAssetsExcludingImages(sourcePath, targetPath);
      continue;
    }

    if (entry.isFile()) {
      await fs.copyFile(sourcePath, targetPath);
    }
  }
}

async function copyRootFiles() {
  for (const filename of rootFilesToCopy) {
    const sourcePath = path.join(process.cwd(), filename);
    const targetPath = path.join(distDir, filename);

    try {
      await fs.copyFile(sourcePath, targetPath);
    } catch (error) {
      if (!error || error.code !== "ENOENT") {
        throw error;
      }
    }
  }
}

main().catch((error) => {
  console.error("Error preparing dist directory:", error);
  process.exit(1);
});
