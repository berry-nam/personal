# ── Dev stage ─────────────────────────────────────────────────────────────────
FROM node:22-alpine AS dev

WORKDIR /app
COPY . .
RUN npm install
CMD ["npx", "vite", "--host", "0.0.0.0"]

# ── Build stage ───────────────────────────────────────────────────────────────
FROM dev AS build
RUN npx vite build

# ── Production stage (nginx) ──────────────────────────────────────────────────
FROM nginx:1.27-alpine AS prod

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
