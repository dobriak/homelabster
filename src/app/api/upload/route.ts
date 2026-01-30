/**
 * Image upload API route
 */

import { NextResponse } from 'next/server';
import { saveImage } from '@/lib/storage';
import { verifyToken } from '@/lib/auth';
import type { ApiError } from '@/types';

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

    const formData = await request.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' } as ApiError,
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/svg+xml'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Invalid file type. Only PNG, JPG, and SVG are allowed.' } as ApiError,
        { status: 400 }
      );
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      return NextResponse.json(
        { error: 'File size must be less than 5MB' } as ApiError,
        { status: 400 }
      );
    }

    const url = await saveImage(file);

    return NextResponse.json({ url });
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Failed to upload image' } as ApiError,
      { status: 500 }
    );
  }
}
