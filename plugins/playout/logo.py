from nebula import *

class Plugin(PlayoutPlugin):
    def on_init(self):
        self.id_layer = 99
        self.logo = False
        self.slots = [
                PlayoutPluginSlot("action", "show"),
                PlayoutPluginSlot("action", "hide")
            ]
        self.tasks = [
                self.on_change
            ]

    def on_change(self):
        if not self.current_asset and self.current_item and self.current_item["item_role"] == "live":
            return self.show_live()
        elif self.current_asset["id_folder"] in [9, 10]:
            return self.hide()
        else:
            return self.show()

    def on_command(self, action, **kwargs):
        if action == "hide":
            self.hide()
            return True

        if action == "show":
            self.show()
        return True

    def show(self):
        logo = "nxtv-logo"
        if self.query("PLAY {} {} MIX 4".format(self.layer(), logo)):
            logging.info("Switched station logo to {}".format(logo))
            self.logo = logo
            return True
        logging.error("Logo show failed")

    def show_live(self):
        logo = "nxtv-logo-live"
        logging.info("Switching station logo to {}".format(logo))
        if self.query("PLAY {} {} MIX 4".format(self.layer(), logo)):
            self.logo = logo
            return True
        logging.error("Logo show failed")


    def hide(self):
        logo = "EMPTY"
        logging.info("Hiding station logo")
        if self.query("PLAY {} {} MIX 4".format(self.layer(), logo)):
            self.logo = logo
            return True
        logging.error("Logo hide failed")
