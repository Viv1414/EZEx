FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# -H 0.0.0.0 so the dev server accepts connections from outside the
# container -- by default `next dev` only listens on localhost, which
# would be unreachable through Docker's port mapping.
CMD ["npx", "next", "dev", "-H", "0.0.0.0"]
