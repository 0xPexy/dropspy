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

RUN pip install --upgrade pip
RUN pip install .

COPY scripts ./scripts
COPY prompts ./prompts
COPY data ./data
COPY pytest.ini ./
COPY README.md ./

CMD ["python", "src/main.py"]
