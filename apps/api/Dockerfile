# Loan Avengers API Dockerfile
# Multi-stage build for optimal image size

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 1: Builder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM python:3.11-slim AS builder

# Install uv for fast, reliable Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies into virtual environment
# uv creates and manages the venv automatically
RUN uv sync --frozen --no-dev

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Stage 2: Runtime
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Disable uv cache in production
    UV_NO_CACHE=1 \
    # Use system Python (no need for venv in container)
    UV_SYSTEM_PYTHON=1 \
    # API configuration
    APP_DEBUG=false \
    APP_LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    # Required for healthchecks
    curl \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from builder
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

# Create non-root user for security
RUN useradd -m -u 1000 apiuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=apiuser:apiuser /app/.venv /app/.venv

# Copy application code
COPY --chown=apiuser:apiuser loan_avengers ./loan_avengers

# Switch to non-root user
USER apiuser

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "loan_avengers.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
