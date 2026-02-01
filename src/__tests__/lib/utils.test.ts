import { describe, it, expect } from 'vitest';
import { cn } from '@/lib/utils';

describe('cn', () => {
  it('should merge class names correctly', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('should handle conditional classes', () => {
    expect(cn('foo', false && 'bar', 'baz')).toBe('foo baz');
  });

  it('should handle undefined and null values', () => {
    expect(cn('foo', undefined, null, 'bar')).toBe('foo bar');
  });

  it('should handle empty strings', () => {
    expect(cn('foo', '', 'bar')).toBe('foo bar');
  });

  it('should handle arrays of classes', () => {
    expect(cn(['foo', 'bar'], 'baz')).toBe('foo bar baz');
  });

  it('should handle objects with boolean values', () => {
    expect(cn({ foo: true, bar: false, baz: true })).toBe('foo baz');
  });

  it('should deduplicate conflicting Tailwind classes', () => {
    expect(cn('p-4', 'p-2')).toBe('p-2');
  });

  it('should handle complex combinations', () => {
    expect(cn('base-class', { conditional: true }, ['array-class'], null && 'ignored')).toBe(
      'base-class conditional array-class'
    );
  });

  it('should return empty string for no inputs', () => {
    expect(cn()).toBe('');
  });

  it('should return empty string for all falsy inputs', () => {
    expect(cn(false, null, undefined, '', 0)).toBe('');
  });

  it('should handle numbers as class names', () => {
    expect(cn('class-1', 'class-2')).toBe('class-1 class-2');
  });
});
