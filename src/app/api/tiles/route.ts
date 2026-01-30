/**
 * Tiles API route - GET all tiles, POST create tile
 */

import { NextResponse } from 'next/server';
import { getTiles, createTile } from '@/lib/data';
import { tileSchema } from '@/lib/validation';
import { verifyToken } from '@/lib/auth';
import type { ApiError } from '@/types';

/**
 * GET /api/tiles - Get all tiles
 */
export async function GET() {
  try {
    const tiles = await getTiles();
    return NextResponse.json(tiles);
  } catch (error) {
    console.error('Failed to get tiles:', error);
    return NextResponse.json(
      { error: 'Failed to fetch tiles' } as ApiError,
      { status: 500 }
    );
  }
}

/**
 * POST /api/tiles - Create a new tile
 * Requires authentication
 */
export async function POST(request: Request) {
  try {
    // Check authentication
    const token = request.headers.get('cookie')?.match(/auth-token=([^;]+)/)?.[1];
    if (!token || !(await verifyToken(token))) {
      return NextResponse.json(
        { error: 'Unauthorized' } as ApiError,
        { status: 401 }
      );
    }

    // Parse and validate request body
    const body = await request.json();
    const validatedData = tileSchema.parse(body);

    // Create tile
    const tile = await createTile(validatedData);

    return NextResponse.json(tile, { status: 201 });
  } catch (error) {
    if (error instanceof Error && 'issues' in error) {
      // Zod validation error
      return NextResponse.json(
        { error: 'Validation failed', details: error } as ApiError,
        { status: 400 }
      );
    }

    console.error('Failed to create tile:', error);
    return NextResponse.json(
      { error: 'Failed to create tile' } as ApiError,
      { status: 500 }
    );
  }
}
