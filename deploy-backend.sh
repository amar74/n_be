#!/bin/bash

# Backend deployment script for EC2
echo "🚀 Deploying Megapolis Backend to EC2..."

# Set variables
BACKEND_DIR="/home/ec2-user/megapolis-api"
CONTAINER_NAME="megapolis-backend"
IMAGE_NAME="megapolis-backend"
PORT=8000

# Navigate to backend directory
cd $BACKEND_DIR

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Remove old image to save space
echo "🧹 Cleaning up old images..."
docker image prune -f

# Build new image
echo "🔨 Building backend Docker image..."
docker build -f Dockerfile.production -t $IMAGE_NAME .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed!"
    exit 1
fi

# Run the container
echo "▶️ Starting backend container..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $PORT:8000 \
    --env-file env.production \
    $IMAGE_NAME

# Check if container is running
sleep 5
if docker ps | grep -q $CONTAINER_NAME; then
    echo "✅ Backend container is running!"
    echo "🌐 Backend API available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):$PORT"
    echo "📚 API docs available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):$PORT/docs"
else
    echo "❌ Container failed to start!"
    echo "📋 Container logs:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Show container status
echo "📊 Container status:"
docker ps | grep $CONTAINER_NAME

echo "🎉 Backend deployment complete!"