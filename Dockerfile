# Base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libxrender1 \
    libxext6 \
    libxtst6 \
    x11-apps \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    mpich \
    petsc-dev \
    gfortran \
    freefem++ \
    && rm -rf /var/lib/apt/lists/*

# Install Conda for managing Python dependencies like FEniCSx, detecting architecture
RUN if [ "$(uname -m)" = "aarch64" ]; then \
        curl -o /tmp/miniconda.sh -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh; \
    else \
        curl -o /tmp/miniconda.sh -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh; \
    fi \
    && chmod +x /tmp/miniconda.sh \
    && /tmp/miniconda.sh -b -p /opt/conda \
    && rm /tmp/miniconda.sh

# Update PATH to include conda binaries
ENV PATH="/opt/conda/bin:${PATH}"

# Copy environment.yml (for Conda dependencies) and install dependencies
COPY environment.yaml /app/environment.yaml
RUN conda env create -f /app/environment.yaml

# Activate conda environment and set it as default
ENV CONDA_DEFAULT_ENV=fenicsx-env
ENV PATH="/opt/conda/envs/fenicsx-env/bin:${PATH}"

# Copy the rest of the application code
COPY . /app

# Set environment variable for Qt (for PyQt5 usage)
ENV QT_X11_NO_MITSHM=1

# Expose port if necessary (for Flask or Dash app)
EXPOSE 5000

# Use JSON format for CMD
CMD ["python", "main.py"]
