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
    libwayland-dev \
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
        jq -r '.assets[] | select(.name | endswith(".tar.gz")) | .browser_download_url' | head -n 1) && \
    if [ -z "$TARBALL_URL" ]; then echo "No .tar.gz asset found in latest release" >&2; exit 1; fi && \
    wget -O /tmp/voyant-api.tar.gz "$TARBALL_URL" && \
    mkdir -p /tmp/voyant-api-extract && \
    tar -xzf /tmp/voyant-api.tar.gz -C /tmp/voyant-api-extract && \
    API_DEB=$(find /tmp/voyant-api-extract -name "voyant-api_*${ARCH}.deb" | head -n 1) && \
    DEV_DEB=$(find /tmp/voyant-api-extract -name "voyant-api-dev_*${ARCH}.deb" | head -n 1) && \
    if [ -z "$API_DEB" ] || [ -z "$DEV_DEB" ]; then echo "Required .deb packages for ARCH=$ARCH not found" >&2; exit 1; fi && \
    apt-get install -y "$API_DEB" "$DEV_DEB" && \
    apt-get clean && \
    rm -rf /tmp/voyant-api.tar.gz /tmp/voyant-api-extract /var/lib/apt/lists/*

# Install Python API
RUN pip3 install voyant-api --break-system-packages

CMD ["bash"]
