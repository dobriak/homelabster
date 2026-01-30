/**
 * Image storage utilities
 */

import { promises as fs } from 'fs';
import path from 'path';
import crypto from 'crypto';

const IMAGES_DIR = path.join(process.cwd(), '..', 'userdata', 'images');

/**
 * Ensures the images directory exists
 */
async function ensureImagesDir(): Promise<void> {
  try {
    await fs.mkdir(IMAGES_DIR, { recursive: true });
  } catch (error) {
    console.error('Failed to create images directory:', error);
    throw new Error('Failed to initialize images directory');
  }
}

/**
 * Generates a unique filename for an uploaded image
 */
function generateFilename(originalFilename: string): string {
  const timestamp = Date.now();
  const hash = crypto.randomBytes(8).toString('hex');
  const ext = path.extname(originalFilename);
  return `${timestamp}-${hash}${ext}`;
}

/**
 * Saves an uploaded image file
 * @returns The path to access the image (e.g., /api/images/filename.png)
 */
export async function saveImage(file: File): Promise<string> {
  await ensureImagesDir();

  const filename = generateFilename(file.name);
  const filepath = path.join(IMAGES_DIR, filename);

  const buffer = Buffer.from(await file.arrayBuffer());
  await fs.writeFile(filepath, buffer);

  return `/api/images/${filename}`;
}

/**
 * Reads an image file
 */
export async function readImage(filename: string): Promise<Buffer> {
  const filepath = path.join(IMAGES_DIR, filename);

  try {
    return await fs.readFile(filepath);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      throw new Error('Image not found');
    }
    throw error;
  }
}

/**
 * Deletes an image file
 */
export async function deleteImage(filename: string): Promise<void> {
  const filepath = path.join(IMAGES_DIR, filename);

  try {
    await fs.unlink(filepath);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      // File doesn't exist, which is fine
      return;
    }
    throw error;
  }
}

/**
 * Gets the content type for an image file
 */
export function getImageContentType(filename: string): string {
  const ext = path.extname(filename).toLowerCase();

  switch (ext) {
    case '.png':
      return 'image/png';
    case '.jpg':
    case '.jpeg':
      return 'image/jpeg';
    case '.svg':
      return 'image/svg+xml';
    default:
      return 'application/octet-stream';
  }
}
