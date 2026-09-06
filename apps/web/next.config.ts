import type { NextConfig } from "next";

// BFF shape: the browser only ever talks to this origin. `/api/*` is rewritten to the FastAPI
// service so session cookies and CSRF stay same-origin; server components call API_URL directly.
const apiUrl = process.env.API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  // the dev overlay badge is not part of the product and leaks into design-loop renders
  devIndicators: false,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/:path*` }];
  },
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "9000" },
      { protocol: "http", hostname: "minio", port: "9000" },
    ],
  },
};

export default nextConfig;
