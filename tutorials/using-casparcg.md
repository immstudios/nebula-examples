Using CasparCG
==============

Nebula has two drivers for CasparCG playout server. Legacy `casparcg` for Caspar versions
2.06 and 2.07 (not tested with 2.1) and `casparcg2` for the current 2.2+ versions.

The original driver uses unidirectional connection to the server, so from the networking
point of view, you only need to allow TCP connection to the AMCP port (default 5250) of
the playout server from the `play` service instance.

`casparcg2` uses bi-directional communication, so CasparCG needs to connect the `play`
service using specified UDP port (see [Controlling CasparCG from Docker](controlling-casparcg-from-docker.md)
for more details).

Storage
-------

CasparCG has to have its own storage. Primary assets reside on the production storage and Nebula
copies them to the playout storage before broadcasting. This workflow is required since CasparCG
needs to have media file in one directory. Workaroud based on symlinks is now tested and will be
available in the future versions of Nebula with Linux-based playout servers.

Our best practice is to have `media.dir` directory
on the playout server data drive (e.g. `d:\media.dir` on Windows ), then we share the media drive,
so it's accesible as for example `\\playoutserver\playout`

In `casparcg.config` set the `<media-path>` to the local path to the directory.

Then setup a playout storage in Nebula:

```python
data["storages"][2] =  {
    "title"    : "playout",
    "protocol" : "samba",
    "path"     : "//playoutserver/playout",
    "login"    : "nebula",
    "password" : "nebulapass"
}
```

Send to playout
---------------

In order to copy media files to the playout storage, create an action for each physical playout storage.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings>
    <allow_if>True</allow_if>
    <task mode="ffmpeg">
        <param name="filter:a">"loudnorm=I=-23"</param>
        <param name="ar">48000</param>
        <param name="c:v">"copy"</param>
        <param name="c:a">"pcm_s16le"</param>
        <output storage="asset.get_playout_storage(1)" direct="1"><![CDATA[asset.get_playout_path(1)]]></output>
    </task>
</settings>
```

Putting it all together
-----------------------

```python
data["channels"][1] = {
    1 :  [0, {
        "title": "Nebula TV",
        "engine" : "casparcg2",
        "controller_host" : "localhost",   # Hostname or an IP address using which the play service
                                           # can be reached from the HUB
        "controller_port" : 42100,         # Unique port number when more play instances run on the same server
        "caspar_host" : "playoutserver",
        "caspar_port" : 5250,
        "caspar_osc_port" : 6250,
        "caspar_channel" : 1,
        "caspar_feed_layer" : 10,
        "playout_storage" : 2,
        "playout_dir" : "media.dir",
        "playout_container" : "mxf",
        "day_start" : [8, 0],
        "send_action" : 2,                 # ID of the action configured before
        "rundown_accepts": "asset['content_type'] == VIDEO", # Which assets may be used to create items in rundown
        "scheduler_accepts": "asset['id_folder'] in [1, 2]", # Which assets may be used to create events in scheduler
        "fps": 25,
        "live_source" : "DECKLINK 2 FORMAT 1080i5000",
        "plugins": [],
        "solvers": [],
        "meta_set" : [                     # Which metadata may be filled in the event detail
                ("title", {}),
                ("description", {})
            ]
    }]
}
```

PSM Service
-----------

PSM (Playout storage monitor) is a Nebula service which controls sending media filest to the playout
storage automatically based on the schedule. By default it start the job 24 hours before broadcast time.

Only one PSM instance is needed per installation as it handles all configured playout channels.
No further configuration of the service is required.


Related links
-------------

 - [Controlling CasparCG from Docker](controlling-casparcg-from-docker.md)
 - [Remote storages in docker](remote-storages-in-docker.md)
