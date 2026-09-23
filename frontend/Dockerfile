# syntax=docker/dockerfile:1

# ---------- Stage 1: build ----------
FROM node:20-slim AS builder

WORKDIR /build

# Vite inlines VITE_* env vars into the bundle at build time.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# ---------- Stage 2: runtime (static serve via nginx) ----------
FROM nginx:1.27-alpine AS runtime

COPY --from=builder /build/dist /usr/share/nginx/html
COPY infra/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]
