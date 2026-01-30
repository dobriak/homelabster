/**
 * Settings API route - GET and PUT operations
 */

import { NextResponse } from 'next/server';
import { getSettings, updateSettings } from '@/lib/data';
import { settingsSchema } from '@/lib/validation';
import { verifyToken } from '@/lib/auth';
import type { ApiError } from '@/types';

/**
 * GET /api/settings - Get application settings
 */
export async function GET() {
  try {
    const settings = await getSettings();
    return NextResponse.json(settings);
  } catch (error) {
    console.error('Failed to get settings:', error);
    return NextResponse.json(
      { error: 'Failed to fetch settings' } as ApiError,
      { status: 500 }
    );
  }
}

/**
 * PUT /api/settings - Update application settings
 * Requires authentication
 */
export async function PUT(request: Request) {
  try {
    // Check authentication
    const token = request.headers.get('cookie')?.match(/auth-token=([^;]+)/)?.[1];
    if (!token || !(await verifyToken(token))) {
      return NextResponse.json(
        { error: 'Unauthorized' } as ApiError,
        { status: 401 }
      );
    }

    const body = await request.json();
    const validatedData = settingsSchema.parse(body);

    const updatedSettings = await updateSettings(validatedData);

    return NextResponse.json(updatedSettings);
  } catch (error) {
    if (error instanceof Error && 'issues' in error) {
      return NextResponse.json(
        { error: 'Validation failed', details: error } as ApiError,
        { status: 400 }
      );
    }

    console.error('Failed to update settings:', error);
    return NextResponse.json(
      { error: 'Failed to update settings' } as ApiError,
      { status: 500 }
    );
  }
}
