# Installation

This guide provides detailed instructions for installing the Voyant API and development packages.

## Installation Options

### Option 1: Docker Installation (Recommended)

The Docker container approach is recommended as it:

- Works across different operating systems
- Includes all dependencies pre-installed
- Provides a consistent development environment

#### Prerequisites (docker)

- Docker installed on your system
  - [Docker installation guide](https://docs.docker.com/get-started/)

#### Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Voyant-Photonics/voyant-sdk.git
   ```

2. **Build the container**:

   ```bash
   cd voyant-sdk/
   docker build -t voyant-sdk-container -f docker/Dockerfile .
   ```

   > **Note**: You can force a rebuild that will update to the latest release by adding the `--no-cache` flag.
   >
   > `docker build --no-cache -t voyant-sdk-container -f docker/Dockerfile .`

3. **Run the container**:

   ```bash
   docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash
   ```

   > **Note**: For Windows or macOS, the `--network host` flag works differently. You might need to adjust networking settings.

4. **Access a running container** (in a new terminal):

   ```bash
   docker exec -it voyant-sdk-container bash
   ```

### Option 2: Native Installation (Ubuntu 22.04)

#### Prerequisites (native)

- Ubuntu 22.04 LTS
- Administrator (sudo) access

#### Install Dependencies

1. **Install Cap'n Proto**:

   ```bash
   curl -O https://capnproto.org/capnproto-c++-1.1.0.tar.gz
   tar zxf capnproto-c++-1.1.0.tar.gz
   cd capnproto-c++-1.1.0
   ./configure
   make -j6 check
   sudo make install
   ```

#### Install Voyant Packages

1. **Download packages** from [voyant-sdk/releases/latest](https://github.com/Voyant-Photonics/voyant-sdk/releases/latest)

2. **Install the packages**:

   ```bash
   sudo apt update
   sudo dpkg -i voyant-api*.deb
   ```

3. **Fix any missing dependencies** (if needed):

   ```bash
   sudo apt --fix-broken install
   ```

#### Clone the repository

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Voyant-Photonics/voyant-sdk.git
   ```

## Verifying Installation

To verify your installation, check that the Voyant tools are available.
You can run:

```bash
voyant_hello_world
```

And you should see something like:

```bash
Welcome to the Voyant Photonics, Inc. API!
You have successfully installed the voyant-api package with:
- Proto version: 0.0.2 (Proto)
- API version:   0.0.2 (API)
```

## Uninstalling

To remove the Voyant packages from a native installation:

```bash
sudo apt remove voyant-api voyant-api-dev
```

For the Docker installation, simply remove the container and image:

```bash
docker rm -f voyant-sdk-container
docker rmi voyant-sdk-container
```

## Next Steps

Once installation is complete, proceed to the [Quickstart Guide](quickstart.md) to verify your setup with a simple example.
