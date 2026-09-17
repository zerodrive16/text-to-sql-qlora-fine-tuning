# Create the Dockerfile image

# Using the python version 3.12
FROM python:3.12-slim 

# Get the uv astral dependency 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# working directory 
WORKDIR /app

# Get dependencies files first 
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project 

# application code 
COPY . . 
RUN uv sync --frozen --no-dev

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

RUN useradd --create-home appuser && chown -R appuser:appuser /app 
USER appuser 

EXPOSE 8000 

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]




    
