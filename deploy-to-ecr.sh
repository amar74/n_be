#!/bin/bash

# ===========================================
# Deploy Backend to AWS ECR
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
ECR_REPOSITORY_NAME="megapolis-api"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying Backend to AWS ECR${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install it with: brew install awscli"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Install it with: brew install docker"
    exit 1
fi

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS credentials verified${NC}"

# Create ECR repository if it doesn't exist
echo -e "${YELLOW}Checking ECR repository...${NC}"
if ! aws ecr describe-repositories --repository-names "$ECR_REPOSITORY_NAME" --region "$AWS_REGION" &> /dev/null; then
    echo -e "${YELLOW}Creating ECR repository: $ECR_REPOSITORY_NAME${NC}"
    aws ecr create-repository \
        --repository-name "$ECR_REPOSITORY_NAME" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true
    echo -e "${GREEN}✓ Repository created${NC}"
else
    echo -e "${GREEN}✓ Repository exists${NC}"
fi

# Get ECR URI
ECR_URI=$(aws ecr describe-repositories \
    --repository-names "$ECR_REPOSITORY_NAME" \
    --region "$AWS_REGION" \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo -e "${GREEN}ECR URI: $ECR_URI${NC}"

# Login to ECR
echo -e "${YELLOW}Logging in to ECR...${NC}"
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "$ECR_URI"

echo -e "${GREEN}✓ Logged in to ECR${NC}"

# Get git commit hash for tagging
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE=$(date +%Y%m%d-%H%M%S)

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build \
    --platform linux/amd64 \
    -t "$ECR_REPOSITORY_NAME:latest" \
    -t "$ECR_REPOSITORY_NAME:$GIT_COMMIT" \
    -t "$ECR_REPOSITORY_NAME:$BUILD_DATE" \
    .

echo -e "${GREEN}✓ Docker image built${NC}"

# Tag images
echo -e "${YELLOW}Tagging images...${NC}"
docker tag "$ECR_REPOSITORY_NAME:latest" "$ECR_URI:latest"
docker tag "$ECR_REPOSITORY_NAME:$GIT_COMMIT" "$ECR_URI:$GIT_COMMIT"
docker tag "$ECR_REPOSITORY_NAME:$BUILD_DATE" "$ECR_URI:$BUILD_DATE"

echo -e "${GREEN}✓ Images tagged${NC}"

# Push to ECR
echo -e "${YELLOW}Pushing images to ECR...${NC}"
docker push "$ECR_URI:latest"
docker push "$ECR_URI:$GIT_COMMIT"
docker push "$ECR_URI:$BUILD_DATE"

echo -e "${GREEN}✓ Images pushed to ECR${NC}"

# Display summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Repository: ${GREEN}$ECR_REPOSITORY_NAME${NC}"
echo -e "Region: ${GREEN}$AWS_REGION${NC}"
echo -e "ECR URI: ${GREEN}$ECR_URI${NC}"
echo -e "Tags pushed:"
echo -e "  - ${GREEN}latest${NC}"
echo -e "  - ${GREEN}$GIT_COMMIT${NC}"
echo -e "  - ${GREEN}$BUILD_DATE${NC}"
echo -e "${GREEN}========================================${NC}"

# Clean up local images (optional)
read -p "Do you want to clean up local Docker images? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cleaning up local images...${NC}"
    docker rmi "$ECR_REPOSITORY_NAME:latest" "$ECR_REPOSITORY_NAME:$GIT_COMMIT" "$ECR_REPOSITORY_NAME:$BUILD_DATE" &> /dev/null || true
    echo -e "${GREEN}✓ Cleanup complete${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Next Steps:${NC}"
echo -e "${GREEN}========================================${NC}"
echo "1. Update your ECS task definition with: $ECR_URI:latest"
echo "2. Update your ECS service to use the new task definition"
echo "3. Or run: aws ecs update-service --cluster YOUR_CLUSTER --service YOUR_SERVICE --force-new-deployment"
echo -e "${GREEN}========================================${NC}"
