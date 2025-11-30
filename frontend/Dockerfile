# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files from the frontend folder (build context is repo root)
COPY frontend/package*.json ./

# Install dependencies: prefer `npm ci` when a lockfile exists, otherwise fall back to `npm install`.
RUN if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then \
      npm ci; \
    else \
      npm install; \
    fi

# Copy source code from frontend directory
COPY frontend/ ./

# Accept a build-time API base so Vite embeds correct API URL into built assets.
# Default to '/api' if not provided.
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build for production (CI-friendly: run `build:ci` to skip local type-checking)
RUN npm run build:ci

# Production stage
FROM nginx:alpine

# Copy custom nginx config (from repo root context -> frontend/nginx.conf)
# When the build context is the repository root, reference the file with the frontend/ prefix.
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
