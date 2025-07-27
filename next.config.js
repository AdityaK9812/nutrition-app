/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Suppress hydration warnings
  suppressHydrationWarning: true,
  // Optimize form handling
  experimental: {
    // This helps with form handling and reduces hydration mismatches
    optimizeFonts: true,
    optimizeImages: true,
    scrollRestoration: true,
  }
}

module.exports = nextConfig 