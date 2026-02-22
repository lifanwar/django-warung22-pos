# Stage 1: Node.js untuk build Tailwind CSS
FROM node:20-slim AS node-builder

WORKDIR /app

# Copy package files
COPY theme/static_src/package*.json ./theme/static_src/

# Install dependencies
WORKDIR /app/theme/static_src
RUN npm ci

# Copy seluruh project untuk tailwind build
WORKDIR /app
COPY . .

# Build Tailwind CSS
WORKDIR /app/theme/static_src
RUN npm run build


# Stage 2: Python untuk Django
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Copy compiled Tailwind CSS dari stage 1
COPY --from=node-builder /app/theme/static/css/dist /app/theme/static/css/dist

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
