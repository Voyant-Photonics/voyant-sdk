# Quickstart Guide

This guide will help you verify your Voyant API installation by building and running a simple example.

## Building the Examples

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

## Running the Basic Client Example

The basic client example (`voyant_client_basic`) by default connects to
a local stream of simulated Voyant LiDAR sensor data
and displays the incoming data stream.

You can run the example with:

```bash
./bin/voyant_client_basic
```

### Simulating a Device

To test the API without connecting a device,
you can simulate a data stream from another terminal.

> Remember: You can access a running docker container from another terminal with:
>
> ```bash
> docker exec -it voyant-sdk-container bash
> ```

```bash
# Run the mock stream with the network configuration expected by the example
voyant_points_mock_stream multicast --bind-addr 127.0.0.1:0 --group-addr 224.0.0.0:4444
```

You will see a rapid stream indicating data is being sent:

```bash
Sent message 1405 for frame 1 (range: 5.10m)
Sent message 1406 for frame 1 (range: 5.10m)
Sent message 1407 for frame 1 (range: 5.10m)
Sent message 1408 for frame 1 (range: 5.10m)
```

### Check the output

If properly configured, your basic client will display a stream of received full LiDAR frames:

{% raw %}

```bash
###############
Received frame:
Header{message type:2, device id:MDL-000, frame idx:35, stamp:1691391379.087802875, proto version:0.0.2, api version:0.0.2, fw version:0.0.2, hdl version:0.0.34}
Config{ len: 0 }
Points[24384] {{idx:6238209,ts:163840,pos:[43.984,0.193966,11.0427],v:1.22985,snr:12.3234,refl:0,noise:34.0003,min_snr:-0.00802298,drop reason:1},...}
```

{% endraw %}

#### Debugging

If you don't see the expected output, try running (outside the docker container):

```bash
sudo ip route add 224.0.0.0/24 dev lo
```

And restart your examples.

## Understanding the Output

The example output shows:

- **Header**: Information about the frame, device, and versions
- **Config**: Any configuration settings (empty in this example)
- **Points**: An array of point data with position, velocity, signal-to-noise ratio, and other metrics

## Next Steps

Now that you've confirmed your installation works:

1. Explore the [pre-packaged tools](../tools/README.md) to understand what functionality is available
2. Try the [example applications](../examples/README.md) to learn how to use the API
3. Begin developing your own applications with the Voyant API

For more advanced usage, refer to the [API documentation](../api/README.md).
