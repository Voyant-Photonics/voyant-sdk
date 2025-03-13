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
sudo apt install ./voyant-api*.deb
```

> You can remove the Voyant packages with:
>
> ```bash
> sudo apt remove voyant-api voyant-api-dev
> ```

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

You can develop your own `C++` applications that use the Voyant static libraries and header files.

The best place to start is by testing your ability to build and run the examples contained in this repository.

### Building the Examples

To build the examples:

- From `/workspace/` if building in provided docker container.
- From `voyant-sdk/` if building on native system.

```bash
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

If you are connected to a stream (simulated or from a device),
you will see a stream of received messages similar to:

```bash
###############
Received frame:
Header{message type:2, device id:MDL-000, frame idx:35, stamp:1691391379.087802875, proto version:0.0.2, api version:0.0.2, fw version:0.0.2, hdl version:0.0.34}
Config{ len: 0 }
Points[24384] {{idx:6238209,ts:163840,pos:[43.984,0.193966,11.0427],v:1.22985,snr:12.3234,refl:0,noise:34.0003,min_snr:-0.00802298,drop reason:1},...}
```

### How to see the headers

You can find the header files included in `voyant-api-dev` installed at `/usr/include/voyant_api/`.

## Licensing

This repository contains example code for interacting with Voyant Photonics device drivers.

### License Information

- **Example Code**: All example code in this repository is licensed under the [MIT License](LICENSE).
You are free to use, modify, distribute, and include this example code in both open source and commercial projects.

- **Device Driver**: The Voyant Photonics device driver itself is proprietary software,
distributed as a static library in a Debian package with accompanying header files.
The device driver is **not** covered by the MIT License and is subject to separate licensing terms.

### Using This Code

You are encouraged to:

- Use these examples as starting points for your own applications
- Modify and adapt the examples to suit your needs
- Share your improvements with the community

When using the example code, please retain the copyright notices at the top of each file.

### Questions

If you have any questions about licensing or usage of either the examples or the device driver,
please contact us at Voyant Photonics, Inc.
