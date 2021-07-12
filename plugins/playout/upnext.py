import json

from nebula import *
from nxtools.caspar import CasparCG

class Plugin(PlayoutPlugin):
    """
    This plugin shows "coming up next" information before end of each movie or episode
    using HTML template in CasparCG. It is also possible to broadcast an 3-line information
    (header and two lines) manually. This plugin works with the example-info template available
    in Aveco html-template-builder application (https://github.com/aveco-automation/html-template-builder).

    Finished template can also be downloaded here https://pastebin.com/dZgdBLMJ

    The plugin goes to .nx/scripts/v5/playout/upnext.py, then you whitelist the plugin in the channel
    configuration ("plugins" : ["upnext"]).

    The template goes to the template directory of CasparCG (eg. templates/example-info/example-info.html)

    Any plugin accepting JSON with header, line1 and line2 fields should work, as long you update the
    plugin source to match its name.
    """

    def on_init(self):
        # Use layer 60 for the graphics. self.layer() method then
        # returns "{id_channel}-{id_layer}" string, eg "1-60"
        self.id_layer = 60

        # slots create input widgets in the firefly plugin panel
        # when "action" is triggered, on_command method is called
        # with keyword arguments containing all text data

        self.slots = [
                PlayoutPluginSlot("text", "header"),
                PlayoutPluginSlot("text", "line1"),
                PlayoutPluginSlot("text", "line2"),
                PlayoutPluginSlot("action", "show"),
                PlayoutPluginSlot("action", "hide")
            ]

    def on_command(self, action, **kwargs):
        # in kwargs, we get {"header" : "text", "line1" : "text", "line2" : "text"}
        # and action argument depending on which button was pressed
        # So we dump data to json and escape it for sending using AMCP
        data = json.dumps(kwargs)
        data = data.replace("\"", "\\\"")

        # "show" button was pressed"
        if action == "show":
            self.query(f"CG {self.layer()} ADD 0 example-info/example-info 1 \"{data}\"")
            return True

        # "hide" button was pressed"
        if action == "hide":
            self.query(f"CG {self.layer()} STOP 0")
            return True


    def on_change(self):
        # We want to show "coming up next" information before a movie or episode ends
        # So we check the current_asset's folder and do nothing if it does not match
        # movie (1) or episode (2)
        if self.current_asset["id_folder"] not in [1, 2]:
            self.tasks = []
            return

        # otherwise, we add two tasks. Each method in tasks list will be repetably executed
        # until it returns True. So we can show the graphic at correct time.

        self.tasks = [
            self.show_upnext,
            self.hide_upnext,
        ]


    def show_upnext(self):
        # do nothing until one minute before the end
        if self.position < self.duration - 60:
            return False

        # Get the next event object (assuming we're on time)
        db = DB()
        db.query("SELECT meta FROM events WHERE start > %s ORDER BY start ASC LIMIT 1", [time.time()])
        next_event = Event(meta=db.fetchall()[0][0])
        data = {}
        if next_event["title"]:
            data["line1"] = next_event["title"]

        if next_event["subtitle"]:
            data["line2"] = next_event["subtitle"]

        if not data:
            # Nothing to show. abort
            self.tasks = []
            return True
        data["header"] = "COMING UP NEXT"

        # Escape data and start the graphics.
        data = json.dumps(data)
        data = data.replace("\"", "\\\"")
        self.query(f"CG {self.layer()} ADD 0 example-info/example-info 1 \"{data}\"")
        return True



    def hide_upnext(self):
        # do nothing until 50 secs before the end
        if self.position < self.duration - 50:
            return False

        # Hide graphics 50 seconds before the end
        self.query(f"CG {self.layer()} STOP 0")
        return True
