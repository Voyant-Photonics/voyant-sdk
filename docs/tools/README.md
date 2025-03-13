# Voyant Pre-packaged Tools

The `voyant-api` package includes several command-line tools to help you work with Voyant LiDAR sensors. These tools are installed system-wide (or in the provided docker container)
and are available in your PATH after installation.

## Available Tools

> **Pro Tip**: All Voyant tools begin with the prefix `voyant_`. You can discover available tools by typing `voyant_` in your terminal and pressing Tab for auto-completion.

### Core Tools

- **[voyant_foxglove_bridge](foxglove_bridge.md)** - Connect Voyant data streams to Foxglove Studio for visualization
- ... TODO: Add all here



## Common Use Cases

### Visualizing Live Sensor Data

Connect your sensor and visualize the data with Foxglove Studio:

Coming soon...
<!--
```bash
voyant_foxglove_bridge --device-ip 192.168.1.100
```
 -->

### Recording a Data Session

Record a session from your connected sensor:

Coming soon...
<!--
```bash
voyant_recorder --output-file my_recording.vdat
```
-->

### Replaying Recorded Data

Play back a previously recorded session:

Coming soon...
<!--
```bash
voyant_player --input-file my_recording.vdat
```
-->

## Tool Configuration

Refer to each tool's detailed documentation for details on configuration options.

### Getting Help

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
