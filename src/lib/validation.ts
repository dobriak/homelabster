/**
 * Zod validation schemas for Homelabster
 */

import { z } from 'zod';

/**
 * Tile validation schema
 */
export const tileSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  url: z.string().url('Must be a valid URL'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  icon: z.string().optional(),
  order: z.number().int().min(0).default(0),
});

export type TileFormData = z.infer<typeof tileSchema>;

/**
 * Settings validation schema
 */
export const settingsSchema = z.object({
  theme: z.enum(['light', 'dark', 'system']).default('system'),
  siteName: z.string().min(1, 'Site name is required').max(100, 'Site name must be less than 100 characters'),
});

export type SettingsFormData = z.infer<typeof settingsSchema>;

/**
 * Login validation schema
 */
export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Image upload validation
 */
export const imageUploadSchema = z.object({
  file: z.instanceof(File)
    .refine((file) => file.size <= 5 * 1024 * 1024, 'File size must be less than 5MB')
    .refine(
      (file) => ['image/png', 'image/jpeg', 'image/svg+xml'].includes(file.type),
      'File must be PNG, JPG, or SVG'
    ),
});
