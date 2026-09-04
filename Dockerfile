# Use an official Python runtime as a parent image
FROM python:3.14.7-alpine

#add gettext
RUN apk add --no-cache gettext

LABEL org.opencontainers.image.source=https://github.com/potentialInc/enterMong-backend
#EXPOSE 8000
# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set DJANGO_SETTINGS_MODULE to your project's settings module
ENV DJANGO_SETTINGS_MODULE=core.settings

# Set the working directory in the container
WORKDIR /app

# Copy dependency metadata first for better build cache behavior.
COPY pyproject.toml uv.lock /app/

# Install uv
RUN pip install uv

RUN uv pip install twisted[tls,http2] --system

# Install runtime dependencies from lockfile without installing local project as a package.
RUN uv sync --locked --no-dev --no-install-project --system

# Copy the full application after dependencies are installed.
COPY . /app



# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# RUN echo 'appuser ALL=(ALL) NOPASSWD: ALL' >  /etc/sudoers.d/appuser
RUN chmod +x entrypoint.sh

USER appuser

# Set the entrypoint script as the default command to execute when the container starts
ENTRYPOINT ["sh", "entrypoint.sh"]