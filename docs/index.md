---
layout: default
title: Voyant SDK
nav_order: 1
---
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

## Licensing

The **[`voyant-sdk`](https://github.com/Voyant-Photonics/voyant-sdk)** repository contains example code for interacting with Voyant Photonics device drivers.

### License Information

- **Example Code**: All example code in this repository is licensed under the [MIT License](https://github.com/Voyant-Photonics/voyant-sdk/blob/main/LICENSE).
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
