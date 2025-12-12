import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";
import { cpus } from "node:os";

const imgSourceDir = path.join(process.cwd(), "src", "images");
const imgTargetDir = path.join(process.cwd(), "assets", "images");

// Limit concurrent operations to number of CPU cores
const CONCURRENCY_LIMIT = cpus().length;

async function copyAndOptimizeImages() {
  const startTime = Date.now();
  let processedCount = 0;
  
  try {
    console.log("🖼️  Starting image optimization...\n");
    
    // Process the main image directory
    const results = await Promise.all([
      copyDirectory(imgSourceDir, imgTargetDir, "images"),
    ]);
    
    processedCount = results.reduce((sum, count) => sum + count, 0);
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    console.log(`\n✨ Optimized ${processedCount} images in ${duration}s`);
  } catch (error) {
    console.error("Error copying and optimizing images:", error);
    process.exit(1);
  }
}

// Process tasks with concurrency limit
async function processConcurrent(tasks, limit) {
  const results = [];
  const executing = [];
  
  for (const task of tasks) {
    const promise = task().then(result => {
      executing.splice(executing.indexOf(promise), 1);
      return result;
    });
    
    results.push(promise);
    executing.push(promise);
    
    if (executing.length >= limit) {
      await Promise.race(executing);
    }
  }
  
  return Promise.all(results);
}

async function copyDirectory(source, target, label = "") {
  await fs.mkdir(target, { recursive: true });
  let entries;
  
  try {
    entries = await fs.readdir(source, { withFileTypes: true });
  } catch (error) {
    if (error && error.code === "ENOENT") {
      return 0;
    }
    throw error;
  }

  // Collect all tasks
  const tasks = [];
  
  for (const entry of entries) {
    const sourcePath = path.join(source, entry.name);
    const targetPath = path.join(target, entry.name);

    if (entry.isDirectory()) {
      tasks.push(async () => {
        const count = await copyDirectory(sourcePath, targetPath, label);
        return count;
      });
    } else if (entry.isFile()) {
      // Only process image files
      if (/\.(png|jpe?g|gif|svg|webp)$/i.test(entry.name)) {
        tasks.push(async () => {
          await optimizeAndCopyImage(sourcePath, targetPath);
          return 1;
        });
      } else {
        // Copy other files directly
        tasks.push(async () => {
          await fs.copyFile(sourcePath, targetPath);
          return 0;
        });
      }
    }
  }
  
  // Process tasks with concurrency limit
  const results = await processConcurrent(tasks, CONCURRENCY_LIMIT);
  const processedCount = results.reduce((sum, count) => sum + count, 0);
  
  if (label && processedCount > 0) {
    // console.log(`📁 Processed ${processedCount} images from ${label}`);
  }
  
  return processedCount;
}

async function optimizeAndCopyImage(sourcePath, targetPath) {
  try {
    const image = sharp(sourcePath);
    const metadata = await image.metadata();
    const ext = path.extname(sourcePath).toLowerCase();

    if (metadata.format === "svg" || metadata.format === "gif") {
      // Copy SVGs and GIFs directly
      await fs.copyFile(sourcePath, targetPath);
    } else {
      // Optimize and save image
      let pipeline = image.resize({ width: 1920, withoutEnlargement: true });
      
      if (ext === '.jpg' || ext === '.jpeg') {
          pipeline = pipeline.jpeg({ quality: 80, mozjpeg: true });
      } else if (ext === '.png') {
          pipeline = pipeline.png({ quality: 80, compressionLevel: 9 });
      } else if (ext === '.webp') {
          pipeline = pipeline.webp({ quality: 80 });
      }
      
      await pipeline.toFile(targetPath);
    }
  } catch (error) {
    console.error(`Error optimizing image ${sourcePath}:`, error);
    // Fallback to copy if optimization fails
    await fs.copyFile(sourcePath, targetPath);
  }
}

// Execute main function
copyAndOptimizeImages();
