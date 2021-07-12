# Controlling CasparCG from Docker

Should your `play` service run in Docker and use `casparcg2` engine,
you need to allow bi-directional communication between the service and the playout server.
CasparCG uses OSC protocol to provide information about the current state of playback.
When running in Docker, container has to expose an UDP port Caspar will connect to.

Let's assume there are two `play` services running in a container,
controlling two channels of the same CasparCG server.

Each channel must be configured with unique `controller_port` and `caspar_osc_port` values in the site template:

```python
data["channels"] = {
    1 : [0, {
        'title': 'Channel 1',
        'engine' : 'casparcg2',
        'controller_host' : "playout",
        'controller_port' : 42101,
        'caspar_host' : "IP_ADDRESS_OF_CASPARCG_SERVER",
        'caspar_port' : 5250,
        'caspar_osc_port' : 6251,
        'caspar_channel' : 1,
        # THE REST OF THE CONFIGURATION
        ]
    }],
    2 : [0, {
        'title': 'Channel 2',
        'engine' : 'casparcg2',
        'controller_host' : "playout",
        'controller_port' : 42102,
        'caspar_host' : "IP_ADDRESS_OF_CASPARCG_SERVER",
        'caspar_port' : 5250,
        'caspar_osc_port' : 6252,
        'caspar_channel' : 2,
        # THE REST OF THE CONFIGURATION
    }],
}
```

Then we setup both controllers services to run on the `playout` host:

```python
data["services"][11] = [
    "play",    # Service type
    "playout", # Hostname
    "play1",   # Service name
    "template/services/play1.xml", # Path to config file
    True,      # Automatic restart
    5          # Interval between on_main calls

data["services"][12] = [
    "play",    # Service type
    "playout", # Hostname
    "play1",   # Service name
    "template/services/play2.xml", # Path to config file
    True,      # Automatic restart
    5          # Interval between on_main calls
]
```

And we create configuration files for both services:

```xml
<!-- /opt/nebula-setup/template/services/play1.xml -->
<settings>
    <id_channel>1</id_channel>
</settings>
```

```xml
<!-- /opt/nebula-setup/template/services/play2.xml -->
<settings>
    <id_channel>2</id_channel>
</settings>
```

In the `docker-compose.yml` we setup UDP port forwarding for both ports
we specified in the channels configuration:

```yaml
playout:
    image: nebulabroadcast/nebula-base
    hostname: "playout"
    restart: always
    ports:
        - "6251:6251/udp"
        - "6252:6252/udp"
    # The rest of the configuration
```

And last, in the `casparcg.config` file, we enable sending OSC messages to the host.

```xml
<osc>
  <predefined-clients>
    <predefined-client>
      <address>IP_ADDRESS_OF_DOCKER_HOST</address>
      <port>6251</port>
    </predefined-client>
    <predefined-client>
      <address>IP_ADDRESS_OF_DOCKER_HOST</address>
      <port>6252</port>
    </predefined-client>
  </predefined-clients>
</osc>
```

