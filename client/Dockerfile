# Use an official Node.js runtime as a parent image
FROM node:20

# Declare Railway-provided env vars as build args (available during build only)
ARG VITE_API_BASE_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ARG VITE_GOOGLE_MAPS_API_KEY

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY pnpm-lock.yaml ./
COPY package.json ./

# Install any needed packages specified in package.json
RUN npm install -g pnpm
RUN pnpm install

# Copy the rest of the application code to the working directory
COPY . .

# Build the React app for production
# Expose Vite env vars to the build step
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY \
    VITE_GOOGLE_MAPS_API_KEY=$VITE_GOOGLE_MAPS_API_KEY
RUN pnpm run build

# Use a lightweight Node.js image to serve static files without nginx
FROM node:20-alpine
WORKDIR /app

# Install a simple static server
RUN npm install -g serve

# Copy built assets from the builder stage
COPY --from=0 /app/dist /app/dist

ENV NODE_ENV=production

# Document default port; Railway will inject PORT at runtime
EXPOSE 80

# Start the static server and honor Railway's injected PORT
CMD ["sh", "-c", "serve -s -l tcp://0.0.0.0:${PORT:-80} /app/dist"]
