/**
 * Single tile API route - GET, PUT, DELETE operations
 */

import { NextResponse } from 'next/server';
import { getTileById, updateTile, deleteTile } from '@/lib/data';
import { tileSchema } from '@/lib/validation';
import { verifyToken } from '@/lib/auth';
import type { ApiError } from '@/types';

/**
 * GET /api/tiles/[id] - Get a single tile
 */
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const tile = await getTileById(id);

    if (!tile) {
      return NextResponse.json(
        { error: 'Tile not found' } as ApiError,
        { status: 404 }
      );
    }

    return NextResponse.json(tile);
  } catch (error) {
    console.error('Failed to get tile:', error);
    return NextResponse.json(
      { error: 'Failed to fetch tile' } as ApiError,
      { status: 500 }
    );
  }
}

/**
 * PUT /api/tiles/[id] - Update a tile
 * Requires authentication
 */
export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // Check authentication
    const token = request.headers.get('cookie')?.match(/auth-token=([^;]+)/)?.[1];
    if (!token || !(await verifyToken(token))) {
      return NextResponse.json(
        { error: 'Unauthorized' } as ApiError,
        { status: 401 }
      );
    }

    const { id } = await params;
    const body = await request.json();
    const validatedData = tileSchema.parse(body);

    const updatedTile = await updateTile(id, validatedData);

    if (!updatedTile) {
      return NextResponse.json(
        { error: 'Tile not found' } as ApiError,
        { status: 404 }
      );
    }

    return NextResponse.json(updatedTile);
  } catch (error) {
    if (error instanceof Error && 'issues' in error) {
      return NextResponse.json(
        { error: 'Validation failed', details: error } as ApiError,
        { status: 400 }
      );
    }

    console.error('Failed to update tile:', error);
    return NextResponse.json(
      { error: 'Failed to update tile' } as ApiError,
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/tiles/[id] - Delete a tile
 * Requires authentication
 */
export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // Check authentication
    const token = request.headers.get('cookie')?.match(/auth-token=([^;]+)/)?.[1];
    if (!token || !(await verifyToken(token))) {
      return NextResponse.json(
        { error: 'Unauthorized' } as ApiError,
        { status: 401 }
      );
    }

    const { id } = await params;
    const deleted = await deleteTile(id);

    if (!deleted) {
      return NextResponse.json(
        { error: 'Tile not found' } as ApiError,
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to delete tile:', error);
    return NextResponse.json(
      { error: 'Failed to delete tile' } as ApiError,
      { status: 500 }
    );
  }
}
