import { describe, it, expect } from 'vitest';
import { z } from 'zod';
import {
  tileSchema,
  settingsSchema,
  loginSchema,
  imageUploadSchema,
  type TileFormData,
  type SettingsFormData,
  type LoginFormData,
} from '@/lib/validation';

describe('tileSchema', () => {
  const validTile = {
    name: 'Test Service',
    url: 'https://example.com',
    description: 'A test service',
    icon: '/icon.png',
    order: 0,
  };

  it('should validate a valid tile', () => {
    const result = tileSchema.safeParse(validTile);
    expect(result.success).toBe(true);
  });

  it('should accept a tile without optional fields', () => {
    const minimalTile = {
      name: 'Test Service',
      url: 'https://example.com',
      order: 1,
    };
    const result = tileSchema.safeParse(minimalTile);
    expect(result.success).toBe(true);
  });

  it('should reject a tile with empty name', () => {
    const invalidTile = { ...validTile, name: '' };
    const result = tileSchema.safeParse(invalidTile);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Name is required');
    }
  });

  it('should reject a tile with name exceeding 100 characters', () => {
    const invalidTile = { ...validTile, name: 'a'.repeat(101) };
    const result = tileSchema.safeParse(invalidTile);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Name must be less than 100 characters');
    }
  });

  it('should reject a tile with invalid URL', () => {
    const invalidTile = { ...validTile, url: 'not-a-url' };
    const result = tileSchema.safeParse(invalidTile);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Must be a valid URL');
    }
  });

  it('should reject a tile with description exceeding 500 characters', () => {
    const invalidTile = { ...validTile, description: 'a'.repeat(501) };
    const result = tileSchema.safeParse(invalidTile);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Description must be less than 500 characters');
    }
  });

  it('should reject a tile with negative order', () => {
    const invalidTile = { ...validTile, order: -1 };
    const result = tileSchema.safeParse(invalidTile);
    expect(result.success).toBe(false);
  });

  it('should reject a tile with non-integer order', () => {
    const invalidTile = { ...validTile, order: 1.5 };
    const result = tileSchema.safeParse(invalidTile);
    expect(result.success).toBe(false);
  });
});

describe('settingsSchema', () => {
  const validSettings = {
    theme: 'dark' as const,
    siteName: 'My Homelab',
  };

  it('should validate valid settings', () => {
    const result = settingsSchema.safeParse(validSettings);
    expect(result.success).toBe(true);
  });

  it('should accept all valid theme values', () => {
    const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system'];
    themes.forEach((theme) => {
      const result = settingsSchema.safeParse({ ...validSettings, theme });
      expect(result.success).toBe(true);
    });
  });

  it('should reject empty site name', () => {
    const invalidSettings = { ...validSettings, siteName: '' };
    const result = settingsSchema.safeParse(invalidSettings);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Site name is required');
    }
  });

  it('should reject site name exceeding 100 characters', () => {
    const invalidSettings = { ...validSettings, siteName: 'a'.repeat(101) };
    const result = settingsSchema.safeParse(invalidSettings);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Site name must be less than 100 characters');
    }
  });

  it('should reject invalid theme value', () => {
    const invalidSettings = { ...validSettings, theme: 'invalid' };
    const result = settingsSchema.safeParse(invalidSettings);
    expect(result.success).toBe(false);
  });
});

describe('loginSchema', () => {
  const validLogin = {
    username: 'admin',
    password: 'password123',
  };

  it('should validate valid login credentials', () => {
    const result = loginSchema.safeParse(validLogin);
    expect(result.success).toBe(true);
  });

  it('should reject empty username', () => {
    const invalidLogin = { ...validLogin, username: '' };
    const result = loginSchema.safeParse(invalidLogin);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Username is required');
    }
  });

  it('should reject empty password', () => {
    const invalidLogin = { ...validLogin, password: '' };
    const result = loginSchema.safeParse(invalidLogin);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('Password is required');
    }
  });

  it('should reject missing username', () => {
    const invalidLogin = { password: 'test' };
    const result = loginSchema.safeParse(invalidLogin);
    expect(result.success).toBe(false);
  });

  it('should reject missing password', () => {
    const invalidLogin = { username: 'test' };
    const result = loginSchema.safeParse(invalidLogin);
    expect(result.success).toBe(false);
  });
});

describe('imageUploadSchema', () => {
  const createMockFile = (filename: string, size: number, type: string): File => {
    const blob = new Blob(['a'.repeat(size)], { type });
    return new File([blob], filename, { type });
  };

  it('should validate a valid PNG file under 5MB', () => {
    const file = createMockFile('image.png', 1024, 'image/png');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(true);
  });

  it('should validate a valid JPEG file under 5MB', () => {
    const file = createMockFile('image.jpg', 1024, 'image/jpeg');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(true);
  });

  it('should validate a valid SVG file under 5MB', () => {
    const file = createMockFile('image.svg', 1024, 'image/svg+xml');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(true);
  });

  it('should reject a file larger than 5MB', () => {
    const file = createMockFile('large.png', 5 * 1024 * 1024 + 1, 'image/png');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('File size must be less than 5MB');
    }
  });

  it('should reject non-image file types', () => {
    const file = createMockFile('document.pdf', 1024, 'application/pdf');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('File must be PNG, JPG, or SVG');
    }
  });

  it('should reject a GIF file (not in allowed types)', () => {
    const file = createMockFile('image.gif', 1024, 'image/gif');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe('File must be PNG, JPG, or SVG');
    }
  });

  it('should reject a WebP file (not in allowed types)', () => {
    const file = createMockFile('image.webp', 1024, 'image/webp');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(false);
  });

  it('should handle exactly 5MB file', () => {
    const file = createMockFile('exact.png', 5 * 1024 * 1024, 'image/png');
    const result = imageUploadSchema.safeParse({ file });
    expect(result.success).toBe(true);
  });
});
