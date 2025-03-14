# UDP Connections Guide

This guide explains how to set up UDP connections between Voyant LiDAR sensors and API tools. Voyant sensors and tools communicate using either unicast or multicast UDP connections.

## Connection Types

### Multicast UDP (Recommended for Sensors)

Multicast is the **primary connection method for Voyant sensors**. This allows multiple receivers to simultaneously connect to a single sensor's data stream, which is ideal for development, debugging, and production deployments.

> **Note:** Voyant sensors currently only support multicast UDP transmission.

### Unicast UDP

Unicast is useful for point-to-point connections, especially during development when using mock data streams or when sending data between your own applications.

## Network Setup for Sensor Connection

Before connecting to a Voyant sensor, you need to configure your network interface:

1. **Identify your network interface** - Use `ip addr` to list all network interfaces

2. **Configure the network interface with a compatible IP address** - The sensor uses the `192.168.1.x` subnet

   ```bash
   sudo ip addr add 192.168.1.100/24 dev YOUR_INTERFACE_NAME
   sudo ip link set YOUR_INTERFACE_NAME up
   ```

   Replace `YOUR_INTERFACE_NAME` with your actual network interface name (e.g., `enxf8ce7234082e`)

3. **Verify the configuration**

   ```bash
   ip addr show YOUR_INTERFACE_NAME
   ```

## Multicast Connection Parameters

Voyant sensors come pre-configured to send data to the following multicast address:

- **Group Address**: 224.0.0.0
- **Port**: 8080

### Receiving Data from a Sensor

To receive data from a sensor using tools like `voyant_foxglove_bridge`, use:

```bash
voyant_foxglove_bridge multicast --bind-addr 0.0.0.0:8080 --group-addr 224.0.0.0 --interface-addr 192.168.1.100
```

### Configuration Options Explained (multicast)

#### For Multicast Receivers

- **`--bind-addr <BIND_ADDR>`**: Local address to bind to (e.g., "0.0.0.0:8080")
  - The IP address is typically "0.0.0.0" to listen on all interfaces
  - The port must match the port used by the sensor (default: 8080)

- **`--group-addr <GROUP_ADDR>`**: Multicast group address to join (e.g., "224.0.0.0")
  - Must be in the valid multicast range (224.0.0.0 to 239.255.255.255)
  - This is the address the sensor sends data to

- **`--interface-addr <INTERFACE_ADDR>`**: Local interface IP address to use for the multicast group
  - Set to your configured IP address (e.g., "192.168.1.100")
  - Using the specific interface ensures proper routing of multicast traffic

#### For Multicast Senders (Development Only)

- **`--bind-addr <BIND_ADDR>`**: Local address to bind to, default is "0.0.0.0:0"
  - Using "0.0.0.0:0" binds to any interface with a random port

- **`--group-addr <GROUP_ADDR>`**: Multicast group address with port (e.g., "224.0.0.0:8080")
  - This is where the data will be sent

- **`--ttl <TTL>`**: Time To Live value (default: 5)
  - Controls how many network hops the packet can traverse (1-255)
  - For local network, 1 is sufficient

## Unicast Connection Parameters

Unicast connections are primarily used during development when sending data between your own applications.

### Configuration Options Explained (unicast)

#### For Unicast Senders

- **`--bind-addr <BIND_ADDR>`**: Local address to bind to, default is "0.0.0.0:0"
  - Using "0.0.0.0:0" binds to any interface with a random port

- **`--target-addr <TARGET_ADDR>`**: Target address to send packets to
  - Format: "ip:port" (e.g., "192.168.1.100:4444")
  - This should be the address where your receiver is listening

#### For Unicast Receivers

- **`--bind-addr <BIND_ADDR>`**: Local address to bind to
  - Must include a specific port (e.g., "0.0.0.0:4444")
  - This is the address and port where the receiver will listen for incoming packets

## Common Use Cases

### Connecting to a Voyant Sensor

1. **Configure your network interface**:

   ```bash
   sudo ip addr add 192.168.1.100/24 dev YOUR_INTERFACE_NAME
   sudo ip link set YOUR_INTERFACE_NAME up
   ```

2. **Run a Voyant tool with multicast receiver configuration**:

   ```bash
   voyant_foxglove_bridge multicast --bind-addr 0.0.0.0:8080 --group-addr 224.0.0.0 --interface-addr 192.168.1.100
   ```

### Testing with Mock Data (Development)

For local development using the mock data generator:

1. **Start the mock data sender**:

   ```bash
   voyant_points_mock_stream multicast --bind-addr 0.0.0.0:0 --group-addr 224.0.0.0:4444
   ```

2. **Run a receiver tool**:

   ```bash
   voyant_foxglove_bridge multicast --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 127.0.0.1
   ```

### Recording Data from a Sensor

To record data from a connected sensor:

```bash
voyant_logger_binary --output my_recording.bin multicast --bind-addr 0.0.0.0:8080 \
                     --group-addr 224.0.0.0 --interface-addr 192.168.1.100
```

## Troubleshooting

### Cannot Connect to Sensor

1. **Verify network interface configuration**:

   ```bash
   ip addr show
   ```

   Ensure your interface has the 192.168.1.x address properly configured.

2. **Check network cables and power** - Ensure the sensor is powered on and properly connected.

3. **Verify multicast routing**:

   ```bash
   ip route get 224.0.0.0
   ```

   This should show the correct interface for multicast routing.

4. **Check for firewall issues**:

   ```bash
   sudo iptables -L
   ```

   Ensure your firewall isn't blocking UDP traffic on the sensor's port.

### Packet Loss or Intermittent Connectivity

1. **Check buffer sizes**:

   ```bash
   sysctl net.core.rmem_max
   sysctl net.core.rmem_default
   ```

   Consider increasing UDP receive buffer sizes:

   ```bash
   sudo sysctl -w net.core.rmem_max=26214400
   sudo sysctl -w net.core.rmem_default=26214400
   ```

2. **Reduce network load** - Ensure your network isn't congested with other traffic.

## Advanced Configuration

For persistent network interface configuration, add the following to `/etc/network/interfaces`:

```bash
auto YOUR_INTERFACE_NAME
iface YOUR_INTERFACE_NAME inet static
    address 192.168.1.100
    netmask 255.255.255.0
```

Alternatively, if using NetworkManager, create a connection profile:

```bash
nmcli con add type ethernet con-name "Voyant" ifname YOUR_INTERFACE_NAME ip4 192.168.1.100/24
nmcli con up "Voyant"
```

## Next Steps

After setting up your UDP connection, proceed to:

- [Visualizing Data](visualization.md) - Learn how to visualize your sensor data
- [Recording Data](recording.md) - Explore options for recording sensor data
- [Data Processing](processing.md) - Process and analyze your sensor data
