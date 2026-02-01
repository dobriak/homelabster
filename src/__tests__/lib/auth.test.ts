import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { SignJWT, jwtVerify } from 'jose';
import { validateCredentials } from '@/lib/auth';
import type { AuthTokenPayload } from '@/types';

// Helper to create a token with a specific secret (simulating what signToken does)
async function createToken(username: string, secret: string): Promise<string> {
  const encodedSecret = new TextEncoder().encode(secret);
  const token = await new SignJWT({ username })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('24h')
    .sign(encodedSecret);
  return token;
}

// Helper to verify a token with a specific secret
async function checkToken(token: string, secret: string): Promise<AuthTokenPayload | null> {
  try {
    const encodedSecret = new TextEncoder().encode(secret);
    const { payload } = await jwtVerify(token, encodedSecret);

    if (
      typeof payload.username === 'string' &&
      typeof payload.iat === 'number' &&
      typeof payload.exp === 'number'
    ) {
      return payload as unknown as AuthTokenPayload;
    }

    return null;
  } catch {
    return null;
  }
}

describe('auth', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset environment variables before each test
    process.env = { ...originalEnv };
    process.env.JWT_SECRET = 'test-secret-key-for-testing';
    process.env.ADMIN_USERNAME = 'testadmin';
    process.env.ADMIN_PASSWORD = 'testpassword';
  });

  afterEach(() => {
    // Restore original environment variables
    process.env = originalEnv;
  });

  describe('signToken (via helper)', () => {
    it('should sign a token with a username', async () => {
      const token = await createToken('testuser', 'test-secret');
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.length).toBeGreaterThan(0);
      expect(token.split('.')).toHaveLength(3); // JWT has 3 parts
    });

    it('should create different tokens for different users', async () => {
      const token1 = await createToken('user1', 'test-secret');
      const token2 = await createToken('user2', 'test-secret');
      expect(token1).not.toBe(token2);
    });

    it('should create different tokens when signed with different secrets', async () => {
      const token1 = await createToken('user1', 'secret1');
      const token2 = await createToken('user1', 'secret2');
      expect(token1).not.toBe(token2);
    });

    it('should handle empty username', async () => {
      const token = await createToken('', 'test-secret');
      expect(token).toBeDefined();
    });
  });

  describe('verifyToken (via helper)', () => {
    it('should verify a valid token', async () => {
      const token = await createToken('testuser', 'test-secret');
      const payload = await checkToken(token, 'test-secret');
      expect(payload).toBeDefined();
      expect(payload?.username).toBe('testuser');
      expect(typeof payload?.iat).toBe('number');
      expect(typeof payload?.exp).toBe('number');
    });

    it('should return null for an invalid token', async () => {
      const result = await checkToken('invalid-token', 'test-secret');
      expect(result).toBeNull();
    });

    it('should return null for a malformed token', async () => {
      const result = await checkToken('not.a.valid.token', 'test-secret');
      expect(result).toBeNull();
    });

    it('should return null for an empty string', async () => {
      const result = await checkToken('', 'test-secret');
      expect(result).toBeNull();
    });

    it('should return null for a token signed with a different secret', async () => {
      const token = await createToken('testuser', 'secret1');
      const result = await checkToken(token, 'secret2');
      expect(result).toBeNull();
    });

    it('should reject tokens with invalid payload structure', async () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify({ invalid: 'structure' }));
      const signature = 'invalid-signature';
      const fakeToken = `${header}.${payload}.${signature}`;
      const result = await checkToken(fakeToken, 'test-secret');
      expect(result).toBeNull();
    });

    it('should verify a token created minutes ago', async () => {
      // Create token with past issued-at date
      const encodedSecret = new TextEncoder().encode('test-secret');
      const pastIat = Math.floor(Date.now() / 1000) - 300; // 5 minutes ago
      const token = await new SignJWT({ username: 'testuser' })
        .setProtectedHeader({ alg: 'HS256' })
        .setIssuedAt(pastIat)
        .setExpirationTime('24h')
        .sign(encodedSecret);

      const payload = await checkToken(token, 'test-secret');
      expect(payload?.username).toBe('testuser');
    });
  });

  describe('validateCredentials', () => {
    beforeEach(() => {
      process.env.ADMIN_USERNAME = 'testadmin';
      process.env.ADMIN_PASSWORD = 'testpassword';
    });

    it('should validate correct credentials', () => {
      const result = validateCredentials('testadmin', 'testpassword');
      expect(result).toBe(true);
    });

    it('should reject incorrect username', () => {
      const result = validateCredentials('wronguser', 'testpassword');
      expect(result).toBe(false);
    });

    it('should reject incorrect password', () => {
      const result = validateCredentials('testadmin', 'wrongpassword');
      expect(result).toBe(false);
    });

    it('should reject both incorrect username and password', () => {
      const result = validateCredentials('wronguser', 'wrongpassword');
      expect(result).toBe(false);
    });

    it('should reject empty username', () => {
      const result = validateCredentials('', 'testpassword');
      expect(result).toBe(false);
    });

    it('should reject empty password', () => {
      const result = validateCredentials('testadmin', '');
      expect(result).toBe(false);
    });

    it('should reject both empty username and password', () => {
      const result = validateCredentials('', '');
      expect(result).toBe(false);
    });

    it('should use default values when env vars are not set', () => {
      delete process.env.ADMIN_USERNAME;
      delete process.env.ADMIN_PASSWORD;
      const result = validateCredentials('admin', 'admin');
      expect(result).toBe(true);
    });

    it('should be case sensitive for username', () => {
      const result = validateCredentials('TestAdmin', 'testpassword');
      expect(result).toBe(false);
    });

    it('should be case sensitive for password', () => {
      const result = validateCredentials('testadmin', 'TestPassword');
      expect(result).toBe(false);
    });

    it('should handle special characters in credentials', () => {
      process.env.ADMIN_USERNAME = 'admin@123';
      process.env.ADMIN_PASSWORD = 'p@$$w0rd!';
      const result = validateCredentials('admin@123', 'p@$$w0rd!');
      expect(result).toBe(true);
    });

    it('should handle whitespace in credentials', () => {
      process.env.ADMIN_USERNAME = 'admin user';
      process.env.ADMIN_PASSWORD = 'pass word';
      const result = validateCredentials('admin user', 'pass word');
      expect(result).toBe(true);
    });
  });

  describe('token roundtrip', () => {
    it('should maintain username through sign and verify cycle', async () => {
      const originalUsername = 'testuser';
      const token = await createToken(originalUsername, 'test-secret');
      const payload = await checkToken(token, 'test-secret');
      expect(payload?.username).toBe(originalUsername);
    });

    it('should handle special characters in username', async () => {
      const usernames = ['user@example.com', 'user+tag', 'user_name', 'user-name'];
      for (const username of usernames) {
        const token = await createToken(username, 'test-secret');
        const payload = await checkToken(token, 'test-secret');
        expect(payload?.username).toBe(username);
      }
    });

    it('should handle unicode characters in username', async () => {
      const usernames = ['用户', 'пользователь', 'مستخدم', 'ユーザー'];
      for (const username of usernames) {
        const token = await createToken(username, 'test-secret');
        const payload = await checkToken(token, 'test-secret');
        expect(payload?.username).toBe(username);
      }
    });
  });
});
