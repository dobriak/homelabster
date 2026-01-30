/**
 * Data layer for reading/writing settings.json
 * Uses atomic writes to prevent data corruption
 */

import { promises as fs } from 'fs';
import path from 'path';
import type { AppData, Tile, Settings } from '@/types';

const DATA_DIR = path.join(process.cwd(), '..', 'userdata', 'config');
const DATA_FILE = path.join(DATA_DIR, 'settings.json');

/**
 * Ensures the data directory exists
 */
async function ensureDataDir(): Promise<void> {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true });
  } catch (error) {
    console.error('Failed to create data directory:', error);
    throw new Error('Failed to initialize data directory');
  }
}

/**
 * Reads the entire app data from settings.json
 */
export async function readAppData(): Promise<AppData> {
  try {
    await ensureDataDir();
    const data = await fs.readFile(DATA_FILE, 'utf-8');
    return JSON.parse(data) as AppData;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      // File doesn't exist, return default data
      const defaultData: AppData = {
        version: '1.0.0',
        tiles: [],
        settings: {
          theme: 'system',
          siteName: 'Homelabster',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      };
      await writeAppData(defaultData);
      return defaultData;
    }
    console.error('Failed to read app data:', error);
    throw new Error('Failed to read application data');
  }
}

/**
 * Writes app data to settings.json using atomic write
 */
export async function writeAppData(data: AppData): Promise<void> {
  try {
    await ensureDataDir();
    const tempFile = DATA_FILE + '.tmp';
    await fs.writeFile(tempFile, JSON.stringify(data, null, 2), 'utf-8');
    await fs.rename(tempFile, DATA_FILE);
  } catch (error) {
    console.error('Failed to write app data:', error);
    throw new Error('Failed to save application data');
  }
}

/**
 * Gets all tiles, sorted by order
 */
export async function getTiles(): Promise<Tile[]> {
  const data = await readAppData();
  return data.tiles.sort((a, b) => a.order - b.order);
}

/**
 * Gets a single tile by ID
 */
export async function getTileById(id: string): Promise<Tile | null> {
  const data = await readAppData();
  return data.tiles.find((tile) => tile.id === id) || null;
}

/**
 * Creates a new tile
 */
export async function createTile(tile: Omit<Tile, 'id' | 'createdAt' | 'updatedAt'>): Promise<Tile> {
  const data = await readAppData();

  const newTile: Tile = {
    ...tile,
    id: crypto.randomUUID(),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  data.tiles.push(newTile);
  await writeAppData(data);

  return newTile;
}

/**
 * Updates an existing tile
 */
export async function updateTile(id: string, updates: Partial<Omit<Tile, 'id' | 'createdAt' | 'updatedAt'>>): Promise<Tile | null> {
  const data = await readAppData();
  const index = data.tiles.findIndex((tile) => tile.id === id);

  if (index === -1) {
    return null;
  }

  data.tiles[index] = {
    ...data.tiles[index],
    ...updates,
    updatedAt: new Date().toISOString(),
  };

  await writeAppData(data);
  return data.tiles[index];
}

/**
 * Deletes a tile by ID
 */
export async function deleteTile(id: string): Promise<boolean> {
  const data = await readAppData();
  const initialLength = data.tiles.length;

  data.tiles = data.tiles.filter((tile) => tile.id !== id);

  if (data.tiles.length === initialLength) {
    return false;
  }

  await writeAppData(data);
  return true;
}

/**
 * Gets application settings
 */
export async function getSettings(): Promise<Settings> {
  const data = await readAppData();
  return data.settings;
}

/**
 * Updates application settings
 */
export async function updateSettings(updates: Partial<Omit<Settings, 'createdAt' | 'updatedAt'>>): Promise<Settings> {
  const data = await readAppData();

  data.settings = {
    ...data.settings,
    ...updates,
    updatedAt: new Date().toISOString(),
  };

  await writeAppData(data);
  return data.settings;
}
