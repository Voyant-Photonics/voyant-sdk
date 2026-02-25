# Voyant API Examples

This repository contains lightweight and easy to augment examples for testing the Voyant API with installed Debian packages.

Full documentation for using the Voyant SDK, including this repository, is available at:
[voyant-photonics.github.io](https://voyant-photonics.github.io/).

## Instructions

Provided below is a minimal set of instructions designed to simplify the installation process and get the repository up and running on your system quickly. If needed, additional installation and usage instruction is available at:
[voyant-photonics.github.io](https://voyant-photonics.github.io/).

### Clone This Repository

Start by cloning this repository:

```bash
git clone https://github.com/Voyant-Photonics/voyant-sdk.git
```

### Docker Instructions

The recommended approach is to build the examples in our provided docker container,
which installs all dependencies and provides cross-platform support.

Follow the [Install Docker Engine](https://docs.docker.com/engine/install/)
documentation for installation instructions. Please be sure to install Docker Engine, and not Docker Desktop; installing the later prevents the api from functioning.

Once the docker container has been installed, build and run the [Voyant SDK docker container](/docker/Dockerfile):

> NOTE: The commands below represent the commands on linux based systems.
> Performing equivalent operations on other operating systems might require slightly different commands.

Build the container:

```bash
cd voyant-sdk/
docker build -t voyant-sdk-container -f docker/Dockerfile .
```

Run the container:

```bash
docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash
```

> Execute the following command if you wish to open a second terminal accessing the running docker container:
>
> ```bash
> docker exec -it voyant-sdk-container bash
> ```

### Building the C++ Examples

Listed below are all instructions relating to building the provided C++ examples.

```bash
cd [INSERT ONE OF THE TWO OPTIONS BELOW]
```
- `/workspace/` if building in the provided docker container (recommended. See [Docker Instructions](#docker-instructions) for relevant instruction.)
- `voyant-sdk/` if building on native system.

```bash
mkdir -p build
cd build
cmake ..
make
```

The built resulting executables will be located in the `build/bin` directory.

### Running the C++ Examples

Run the compiled binary example:

```bash
./bin/voyant_client_basic
```

If connected to a stream (simulated or from an external device), a feed of received messages similar to the sample below will be displayed.

```bash
###############
Received frame:
Header{message type:2, device id:MDL-000, frame idx:35, stamp:1691391379.087802875, proto version:0.0.2, api version:0.0.2, fw version:0.0.2, hdl version:0.0.34}
Config{ len: 0 }
Points[24384] {{idx:6238209,ts:163840,pos:[43.984,0.193966,11.0427],v:1.22985,snr:12.3234,refl:0,noise:34.0003,min_snr:-0.00802298,drop reason:1},...}
```

### Running the Python Examples

The Python examples require the `voyant-api` package, which is pre-installed in the Docker container. To install it on your native system:

```bash
pip install voyant-api
```

Run a Python example:

```bash
python3 python/examples/client_example.py
```

## Licensing

This repository contains example code for interacting with Voyant Photonics, Inc. device drivers.

### License Information

- **Example Code**: All example code in this repository is licensed under the [MIT License](LICENSE).
You are free to use, modify, distribute, and include this example code in both open source and commercial projects.

- **Device Driver**: The provided device driver is proprietary code (**not** covered by the MIT License), but may be called from your application for the evaluation of Voyant sensors.

### Using This Code

You are encouraged to:

- Use these examples as starting points for custom applications
- Suggest improvements and/or new features.
- Share your improvements and applications with the community

When using the example code, please retain the copyright notices at the top of each file.

### Questions

If you have any questions or feedback about licensing or usage of either the examples or the device driver,
please see our [troubleshooting guide](https://voyant-photonics.github.io/troubleshooting.html) for support options.

We value your experience, and are committed to ironing out any errors or unnecessary difficulties in the code.
