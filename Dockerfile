# Multi-stage build to reduce final image size
FROM node:18-bullseye-slim as base

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv lsof bash ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 1: Install Python dependencies
FROM base as python-deps
COPY backend/requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Install Node dependencies  
FROM base as node-deps
COPY package*.json ./
#TODO separate dev/prod
RUN npm ci --no-audit --progress=false

# Final stage
FROM base as final
COPY --from=python-deps /opt/venv /opt/venv
COPY --from=node-deps /app/node_modules ./node_modules

# Copy application code
COPY . /app

# Make scripts executable
RUN chmod +x /app/bdev.sh /app/dev.sh /app/run.sh

# Update scripts to use the virtual environment
RUN sed -i 's|venv/bin/activate|/opt/venv/bin/activate|g' /app/bdev.sh

EXPOSE 5001 3000

CMD ["./run.sh"]