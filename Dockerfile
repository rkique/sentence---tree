# Minimal container that can run both ./bdev.sh (backend) and ./dev.sh (frontend)
# Base on Node image and add Python so both dev scripts can run.
FROM node:18-bullseye-slim

# Install Python, pip, lsof and bash
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      python3 python3-pip python3-venv lsof bash ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project
COPY . /app

# Copy requirements.txt to root for install.sh compatibility
RUN cp backend/requirements.txt . || true

# Ensure scripts are executable
RUN chmod +x /app/bdev.sh /app/dev.sh /app/install.sh || true

# Use install.sh to set up the environment
RUN ./install.sh

# Create a simple runner that starts both scripts and handles signals
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Expose typical dev ports (adjust if your scripts use different ports)
EXPOSE 5001 3000

# Use the runner as the container command
CMD ["/run.sh"]