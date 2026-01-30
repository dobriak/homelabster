/**
 * Core data types for Homelabster
 */

export interface Tile {
  id: string;
  name: string;
  url: string;
  description?: string;
  icon?: string;
  createdAt: string;
  updatedAt: string;
  order: number;
}

export interface Settings {
  theme: 'light' | 'dark' | 'system';
  siteName: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppData {
  version: string;
  tiles: Tile[];
  settings: Settings;
}

export interface AuthTokenPayload {
  username: string;
  iat: number;
  exp: number;
}

export interface ApiError {
  error: string;
  details?: unknown;
}

export interface ApiSuccess<T = unknown> {
  success: true;
  data: T;
}
