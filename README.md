# Voyant API Examples

This repository contains minimal examples for testing the Voyant API with installed Debian packages.

Full documentation for using the Voyant SDK, including this repository are available at:
[voyant-photonics.github.io](https://voyant-photonics.github.io/).

## Instructions

There are additional installation and usage instructions available at:
[voyant-photonics.github.io](https://voyant-photonics.github.io/).
Here we provide a minimal subset of these.

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

## Licensing

This repository contains example code for interacting with Voyant Photonics device drivers.

### License Information

- **Example Code**: All example code in this repository is licensed under the [MIT License](LICENSE).
You are free to use, modify, distribute, and include this example code in both open source and commercial projects.

- **Device Driver**: The device driver is proprietary (**not** covered my the MIT License), but may be called from your application for the evaluation of Voyant sensors.

### Using This Code

You are encouraged to:

- Use these examples as starting points for your own applications
- Modify and adapt the examples to suit your needs
- Share your improvements with the community

When using the example code, please retain the copyright notices at the top of each file.

### Questions

If you have any questions about licensing or usage of either the examples or the device driver,
please see our [troubleshooting guide](https://voyant-photonics.github.io/troubleshooting.html) for support options.
