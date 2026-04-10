import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import AuthLayout from '@/app/(auth)/layout';

vi.mock('next-themes', () => ({
  useTheme: () => ({ setTheme: vi.fn() }),
}));

describe('AuthLayout', () => {
  it('renders children', () => {
    render(<AuthLayout><div>Login form</div></AuthLayout>);
    expect(screen.getByText('Login form')).toBeInTheDocument();
  });

  it('renders the theme toggle button', () => {
    render(<AuthLayout><div>Login form</div></AuthLayout>);
    expect(screen.getByRole('button', { name: /toggle theme/i })).toBeInTheDocument();
  });
});
