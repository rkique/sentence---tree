# Multi-stage build to reduce final image size
FROM node:18-bookworm-slim as base

# Install system dependencies including Python 3.11
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv lsof bash ca-certificates curl && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

WORKDIR /app

# Stage 1: Install Node dependencies  
FROM base as node-deps
COPY package*.json ./

# Install ALL dependencies (including devDependencies for Vite)
RUN npm ci --no-audit --no-fund --progress=false && \
    npm cache clean --force

# Final stage
FROM base as final
COPY --from=node-deps /app/node_modules ./node_modules

# Copy application code
COPY . /app

# Create necessary directories
RUN mkdir -p /app/backend/distances

# Create venv and install Python dependencies in final stage
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r /app/backend/requirements.txt && \
    rm -rf /root/.cache/pip

# Make scripts executable
RUN chmod +x /app/bdev.sh /app/dev.sh /app/run.sh


EXPOSE 5001 3000

CMD ["./run.sh"]