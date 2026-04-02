FROM python:3.12 AS base

LABEL maintainer="Ferdinand Berger <ferdy@berger-em.de>" \
      description="Personal Zoo - visit: https://personal-zoo.com"

WORKDIR /app

# Settings for ARM7 (needs Rust for some packages)
FROM base AS base-arm
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
COPY . ./

# Settings for amd64
FROM base AS base-amd64
COPY . ./

# Settings for arm64
FROM base AS base-arm64
COPY . ./

# Main build process
FROM base-${TARGETARCH}
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Run migrations and start with gunicorn
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn pzoo.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
