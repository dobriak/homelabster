/**
 * Login API route - validates credentials and issues JWT token
 */

import { NextResponse } from 'next/server';
import { loginSchema } from '@/lib/validation';
import { validateCredentials, signToken } from '@/lib/auth';
import type { ApiError } from '@/types';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { username, password } = loginSchema.parse(body);

    // Validate credentials
    if (!validateCredentials(username, password)) {
      return NextResponse.json(
        { error: 'Invalid username or password' } as ApiError,
        { status: 401 }
      );
    }

    // Sign JWT token
    const token = await signToken(username);

    // Create response with cookie
    const response = NextResponse.json({ success: true });
    response.cookies.set('auth-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24, // 24 hours
      path: '/',
    });

    return response;
  } catch (error) {
    if (error instanceof Error && 'issues' in error) {
      // Zod validation error
      return NextResponse.json(
        { error: 'Invalid request data' } as ApiError,
        { status: 400 }
      );
    }

    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Authentication failed' } as ApiError,
      { status: 500 }
    );
  }
}
