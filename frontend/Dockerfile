# ============================================================================
# TrackX — Frontend (Vite/React multi-stage build → Nginx)
# ============================================================================

# ------------------------- BUILD STAGE -------------------------
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies first for better layer caching
COPY package.json package-lock.json* ./
RUN npm install

# Copy source + build static assets
COPY . .
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_WS_URL=/ws/alerts/
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_WS_URL=$VITE_WS_URL

RUN npm run build

# ------------------------- PRODUCTION STAGE -------------------------
FROM nginx:alpine

# Nginx config: serve static assets + reverse-proxy /api/ and /ws/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React bundle
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
