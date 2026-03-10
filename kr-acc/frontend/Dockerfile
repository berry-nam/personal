FROM node:22-alpine AS base

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

CMD ["npx", "vite", "--host", "0.0.0.0"]

FROM base AS dev
CMD ["npx", "vite", "--host", "0.0.0.0"]
