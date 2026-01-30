/**
 * Image serving API route
 */

import { NextResponse } from 'next/server';
import { readImage, getImageContentType } from '@/lib/storage';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const { filename } = await params;

    // Basic security check - prevent directory traversal
    if (filename.includes('..') || filename.includes('/')) {
      return NextResponse.json(
        { error: 'Invalid filename' },
        { status: 400 }
      );
    }

    const buffer = await readImage(filename);
    const contentType = getImageContentType(filename);

    return new NextResponse(new Uint8Array(buffer), {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });
  } catch (error) {
    if (error instanceof Error && error.message === 'Image not found') {
      return NextResponse.json(
        { error: 'Image not found' },
        { status: 404 }
      );
    }

    console.error('Failed to serve image:', error);
    return NextResponse.json(
      { error: 'Failed to serve image' },
      { status: 500 }
    );
  }
}
