'use client';

import React, { useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const token = searchParams.get('token');
  const email = searchParams.get('email');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (!email || !token) {
      setError('Missing email or token. Please request a new password reset.');
      setIsLoading(false);
      return;
    }

    try {
      console.log('Sending reset password request:', { token, email, password });
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          token,
          email,
          password
        }),
      });

      const data = await response.json();
      console.log('Reset password response:', data);

      if (!response.ok) {
        console.error('Reset password failed:', data);
        throw new Error(data.error || 'Failed to reset password');
      }

      setSuccess('Password has been reset successfully. Redirecting to login...');
      setTimeout(() => {
        router.push('/login');
      }, 2000);
    } catch (err) {
      console.error('Reset password error details:', err);
      setError(err instanceof Error ? err.message : 'Failed to reset password');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token || !email) {
    return (
      <div className="text-center text-red-500">
        Invalid or missing reset token or email. Please request a new password reset.
        <div className="mt-4">
          <Link href="/forgot-password" className="text-[#8B4513] hover:text-[#5C2D0C]">
            Go to Forgot Password
          </Link>
        </div>
      </div>
    );
  }

  return (
    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
      <div>
        <label htmlFor="password" className="block text-gray-700">New Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          required
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="confirmPassword" className="block text-gray-700">Confirm New Password</label>
        <input
          id="confirmPassword"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          required
          disabled={isLoading}
        />
      </div>

      {error && (
        <div className="text-red-500 text-sm bg-red-50 p-3 rounded-md">
          {error}
        </div>
      )}

      {success && (
        <div className="text-green-500 text-sm bg-green-50 p-3 rounded-md">
          {success}
        </div>
      )}

      <button
        type="submit"
        className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-[#0B4A0B] hover:bg-[#083708] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        disabled={isLoading}
      >
        {isLoading ? 'Resetting Password...' : 'Reset Password'}
      </button>
    </form>
  );
}

export default function ResetPassword() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F4FFF4] p-4">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-[#8B4513] mb-2">Reset Password</h1>
          <p className="text-gray-600">Enter your new password</p>
        </div>

        <Suspense fallback={
          <div className="text-center text-gray-600">
            Loading...
          </div>
        }>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  );
} 