import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/signup', '/forgot-password'];
  
  // Skip middleware for API routes
  if (pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  // For client-side routes, let the client handle authentication
  if (pathname !== '/login' && pathname !== '/signup') {
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}; 