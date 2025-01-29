FROM --platform=linux/amd64 gradescope/autograder-base:latest

ARG LOCAL_TEST=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    firefox \
    xvfb \
    libasound2 \
    libdbus-glib-1-2 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libxcb1 \
    libxkbcommon0

# Install Python dependencies
RUN pip install playwright pytest-playwright

# Install Firefox browser for Playwright
RUN playwright install firefox
RUN playwright install-deps firefox

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY source /autograder/source
COPY submission /autograder/sample_submission

RUN if [ "${LOCAL_TEST}" = "true" ]; then \
    cp -r /autograder/sample_submission /autograder/submission/; \
    fi

# Copy your test files and scripts
RUN cd /autograder/source && cp run_autograder /autograder/run_autograder

# Make run_autograder executable
RUN chmod +x /autograder/run_autograder

# Create necessary directories
RUN mkdir -p /autograder/results

RUN pip install python-dotenv certifi itsdangerous

ENV API_KEY=KWoh0ZOSGPfB52ArjG99w6pxO16VU6Pc
