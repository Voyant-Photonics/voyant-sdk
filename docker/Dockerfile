FROM ubuntu:latest

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    apt-utils \
    build-essential \
    cmake \
    curl \
    g++ \
    pkg-config \
    jq \
    python3 \
    python3-pip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Cap'n Proto from source
WORKDIR /tmp
RUN curl -O https://capnproto.org/capnproto-c++-1.1.0.tar.gz && \
    tar zxf capnproto-c++-1.1.0.tar.gz && \
    cd capnproto-c++-1.1.0 && \
    ./configure && \
    make -j6 && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf capnproto-c++-1.1.0*

# Set working directory
WORKDIR /workspace

# Download and install the latest release packages from GitHub
RUN ARCH=$(dpkg --print-architecture) && \
    TARBALL_URL=$(curl -s https://api.github.com/repos/Voyant-Photonics/voyant-sdk/releases/latest | \
        jq -r '.assets[] | select(.name | endswith(".tar.gz")) | .browser_download_url') && \
    wget -O /tmp/voyant-api.tar.gz "$TARBALL_URL" && \
    tar -xzf /tmp/voyant-api.tar.gz -C /tmp && \
    apt-get update && \
    dpkg -i /tmp/voyant-api-debian-*/voyant-api_*-1_${ARCH}.deb \
            /tmp/voyant-api-debian-*/voyant-api-dev_*-1_${ARCH}.deb && \
    rm -rf /tmp/voyant-api*

# Install Python API
RUN pip3 install voyant-api --break-system-packages

CMD ["bash"]
