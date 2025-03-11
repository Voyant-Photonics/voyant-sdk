# Voyant API Examples

This repository contains minimal examples for testing the Voyant API with installed Debian packages.

We package two debian packages that are always available at
[voyant-sdk/releases/latest](https://github.com/Voyant-Photonics/voyant-sdk/releases/latest).

- `voyant-api`: For binaries, command line utilities, etc.
- `voyant-api-dev`: Header files, static libraries, etc.
  - Depends on `voyant-api`

The `voyant-api` package is all you need to:

- connect to your sensor
- stream, record, and visualize data
- configure your sensor (Coming Soon...)

The `voyant-api-dev` package exists for the developer community and enables:

- Building and running the examples contained in this repository
- Developing your own C++ applications that process Voyant LiDAR data

## Prerequisites

To use the voyant packages, you have two options:

- Run through our provided Docker container (recommended)
- Install the voyant debian packages on your native system
  - Requires Ubuntu 22.04
  - Additional OS support coming soon...

### Clone this repository

You should start with cloning this repository:

```bash
git clone https://github.com/Voyant-Photonics/voyant-sdk.git
```

### Docker instructions

The recommended approach is to build the examples in our provided docker container,
which installs all dependencies for you and provides cross-platform support.

Please follow the [Docker - Get started](https://docs.docker.com/get-started/)
documentation for installation.

You can then build and run the [Voyant SDK docker container](/docker/Dockerfile):

> NOTE: These commands represent the commands on linux based systems.
> Other operating systems may have slightly different commands.

Build the container:

```bash
cd voyant-sdk/
docker build -t voyant-sdk-container -f docker/Dockerfile .
```

Run the container:

```bash
docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash
```

> If you wish to open a second terminal accessing the running docker container:
>
> ```bash
> docker exec -it voyant-sdk-container bash
> ```

### Native installation

If you wish to install on your native system,
you will need to install and manage all dependencies.

#### Dependencies

We have a dependency on Cap'n Proto for our message encoding.

Install Cap'n Proto from source following the **Installation: Unix** > **From Release Tarball** instructions
found at [Cap'n Proto](https://capnproto.org/install.html).

> At the time of writing, these instructions were:
>
> ```bash
> curl -O https://capnproto.org/capnproto-c++-1.1.0.tar.gz
> tar zxf capnproto-c++-1.1.0.tar.gz
> cd capnproto-c++-1.1.0
> ./configure
> make -j6 check
> sudo make install
> ```

#### Voyant packages

In a clean directory, download the latest `voyant-api` & `voyant-api-dev` debian packages,
included in the latest release found at
[voyant-sdk/releases/latest](https://github.com/Voyant-Photonics/voyant-sdk/releases/latest).

Then install with:

```bash
sudo apt update
sudo apt install voyant-api*.deb
```

## Using the pre-packaged tools

There a number of commandline tools packaged in `voyant-api`.

> Pro tip: The executables packaged in `voyant-api` all begin with `voyant_`.
> Once you have the package installed, you can check what tools are available
> by typing `voyant_` in the terminal and seeing the options that show when
> you hit the `tab` key (assuming you have tab complete).

The instructions for running each example can be displayed by using the `--help` flag.
For example, you can see the required and optional command line arguments
for the `voyant_foxglove_bridge` tool with:

```bash
voyant_foxglove_bridge --help
```

### Instructions for packaged tools

Coming soon...

## Using the developer API

For using the developer API, you can develop your own `C++` applications that use the Voyant
static libraries and header files.

The best place to start is by testing your ability to build and run the examples contained in this repository.

### Building the Examples

To build the examples:

```bash
cd voyant-sdk/
mkdir -p build
cd build
cmake ..
make
```

The built executables will be in the `build/bin` directory.

### Running the Examples

You can then run the compiled binary example:

```bash
./bin/voyant_client_basic
```

### How to see the headers

You can find the header files included in `voyant-api-dev` installed at `/usr/include/voyant_api/`.
