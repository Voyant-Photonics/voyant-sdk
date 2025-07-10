FROM ubuntu:latest

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    apt-utils \
    tcpdump \
    build-essential \
    python3 \
    cmake \
    curl \
    g++ \
    pkg-config \
    jq \
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
RUN mkdir -p ./debian && \
    LATEST_RELEASE_URL=$(curl -s https://api.github.com/repos/Voyant-Photonics/voyant-sdk/releases/latest | jq -r '.assets[].browser_download_url') && \
    for url in $LATEST_RELEASE_URL; do \
        wget -P ./debian/ $url; \
    done && \
    apt-get update && \
    dpkg -i debian/voyant-api*.deb && \
    rm -rf ./debian


CMD ["bash"]
