# Voyant Pre-packaged Tools

The `voyant-api` package includes several command-line tools to help you work with Voyant LiDAR sensors. These tools are installed system-wide (or in the provided docker container)
and are available in your PATH after installation.

## Available Tools

> **Pro Tip**: All Voyant tools begin with the prefix `voyant_`. You can discover available tools by typing `voyant_` in your terminal and pressing Tab for auto-completion.

### Core Tools

<!--
TODO: Add back with links once we create a apge-per-tool

- **[voyant_hello_world](hello_world.md)** - Simple example application demonstrating basic Voyant API usage
- **[voyant_points_mock_stream](points_mock_stream.md)** - Generate mock point cloud data for testing and development
- **[voyant_foxglove_bridge](foxglove_bridge.md)** - Connect Voyant data streams to Foxglove Studio for visualization
- **[voyant_logger_binary](logger_binary.md)** - Record sensor data to a binary format file
- **[voyant_logger_mcap](logger_mcap.md)** - Record sensor data to MCAP format for playback directly in Foxglove playback.
  - This uses foxglove protobuf syntax and is **NOT** directly compatible with ROS/ROS2.
  - The conversion from Voyant proto messages -> foxglove protobufs is a lossy conversion and cannot be converted back to binary format.
- **[voyant_playback_check](playback_check.md)** - Playback recorded binary data to verify the integrity
- **[voyant_playback_foxglove](playback_foxglove.md)** - Replay recorded binary data to Foxglove Studio for visualization and analysis
-->

- **voyant_hello_world** - Simple example application demonstrating basic Voyant API usage
- **voyant_points_mock_stream** - Generate mock point cloud data for testing and development
- **voyant_foxglove_bridge** - Connect Voyant data streams to Foxglove Studio for visualization
- **voyant_logger_binary** - Record sensor data to a binary format file
- **voyant_logger_mcap** - Record sensor data to MCAP format for playback directly in Foxglove playback.
  - This uses foxglove protobuf syntax and is **NOT** directly compatible with ROS/ROS2.
  - The conversion from Voyant proto messages -> foxglove protobufs is a lossy conversion and cannot be converted back to binary format.
- **voyant_playback_check** - Playback recorded binary data to verify the integrity
- **voyant_playback_foxglove** - Replay recorded binary data to Foxglove Studio for visualization and analysis

## Common Use Cases

These are some common use cases using the core tools,
with example arguments for running them.

Refer to each tool's detailed documentation for details on configuration options.

### Getting Started

Run the hello world example to verify your installation and basic connectivity:

```bash
voyant_hello_world
```

### Testing With Mock Data

Generate mock point cloud data for testing without a physical sensor:

```bash
voyant_points_mock_stream multicast --bind-addr 127.0.0.1:0 --group-addr 224.0.0.0:4444
```

### Visualizing Live Sensor Data

Connect your sensor and visualize the data with Foxglove Studio:

```bash
voyant_foxglove_bridge multicast --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 127.0.0.1
```

### Recording a Data Session

Record a session from your connected sensor:

```bash
# Record a binary log of voyant proto messages [Recommended]
voyant_logger_binary --output my_recording.bin multicast --bind-addr 0.0.0.0:4444 \
                     --group-addr 224.0.0.0 --interface-addr 127.0.0.1
# Or record directly to MCAP format (foxglove protobufs)
voyant_logger_mcap --output path/to/your/output.mcap multicast --bind-addr 0.0.0.0:4444 \
                   --group-addr 224.0.0.0 --interface-addr 127.0.0.1
```

### Validating Recorded Data

Play back a previously recorded binary logging session to display logged frame information.

```bash
voyant_playback_check --input my_recording.bin --rate 3.0
```

### Replaying Recorded Data

Play back a previously recorded binary logging session to Foxglove Studio:

```bash
voyant_playback_foxglove --input my_recording.bin --loopback
```

> Note: If you recorded straight to mcap format,
you can play those logs back directly in foxglove.

### Converting Data Formats

Coming soon...

## Getting Help

Each tool includes built-in help documentation.
To see usage instructions, command-line options, and examples, use the `--help` flag:

```bash
voyant_foxglove_bridge --help
```

And you will see:

```bash
For command-line usage with subcommands

Usage: voyant_foxglove_bridge [OPTIONS] <COMMAND>

Commands:
  unicast    Configure a unicast UDP receiver
  multicast  Configure a multicast UDP receiver
  help       Print this message or the help of the given subcommand(s)

Options:
      --ws-port <WS_PORT>
          Foxglove WebSocket port [default: 8765]
      --check-interval <CHECK_INTERVAL>
          Interval in milliseconds between checks for new frames [default: 10]
  -h, --help
          Print help
  -V, --version
          Print version
```

You can then get more help on subcommands, e.g.:

```bash
voyant_foxglove_bridge multicast --help
```

This will give details on the `multicast` expected args:

```bash
Configure a multicast UDP receiver

Usage: voyant_foxglove_bridge multicast [OPTIONS] --bind-addr <BIND_ADDR> --group-addr <GROUP_ADDR>

Options:
      --bind-addr <BIND_ADDR>
          Local address to bind to (e.g., "0.0.0.0:4444") Must use the same port that multicast senders are targeting
      --group-addr <GROUP_ADDR>
          Multicast group address to join (e.g., "224.0.0.0") Must be in the valid multicast range (224.0.0.0 to 239.255.255.255)
      --interface-addr <INTERFACE_ADDR>
          Local interface IP address to use for the multicast group Use "0.0.0.0" to use the default interface, or specify a particular interface IP [default: 0.0.0.0]
  -h, --help
          Print help
```

This shows you can run with the following,
if you want to change the default foxglove websocket port
and specify all addresses for the multicast connection:

```bash
voyant_foxglove_bridge --ws-port 1234 multicast --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 127.0.0.1
```

## Next Steps

After familiarizing yourself with these tools, check out the [examples](../examples/README.md) to learn how to integrate Voyant sensors into your own applications.
