FROM python:3.13-slim

# Install build dependencies for packages like sentencepiece
# Use apt-get for Debian-based images like python:slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY tests ./tests
COPY pytest.ini ./
COPY README.md ./


RUN pip install --upgrade pip
RUN pip install .


# CMD ["python", "src/main.py"]
