'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function ResetPassword() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const token = searchParams?.get('token');
  const email = searchParams?.get('email');

  useEffect(() => {
    if (!token || !email) {
      setError('Invalid reset link');
    }
  }, [token, email]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          email,
          password
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to reset password');
      }

      setSuccess('Password has been reset successfully. Redirecting to login...');
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } catch (err) {
      console.error('Reset password error:', err);
      setError(err instanceof Error ? err.message : 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F4FFF4] p-4">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-[#8B4513] mb-2">Reset Password</h1>
          <p className="text-gray-600">Enter your new password</p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6" suppressHydrationWarning>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              New Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              required
              disabled={isLoading || !token || !email}
              minLength={8}
              suppressHydrationWarning
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
              Confirm New Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
              required
              disabled={isLoading || !token || !email}
              minLength={8}
              suppressHydrationWarning
            />
          </div>

          {error && (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded-md" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="text-green-500 text-sm bg-green-50 p-3 rounded-md" role="alert">
              {success}
            </div>
          )}

          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-[#0B4A0B] hover:bg-[#083708] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            disabled={isLoading || !token || !email}
            suppressHydrationWarning
          >
            {isLoading ? 'Resetting Password...' : 'Reset Password'}
          </button>

          <div className="text-center text-sm">
            <Link href="/login" className="text-[#8B4513] hover:text-[#5C2D0C]">
              Back to Login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
} 