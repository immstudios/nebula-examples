# send e-mail notifications using sendgrid
data["settings"]["smtp_host"] = "smtp.sendgrid.net"
data["settings"]["smtp_port"] = 465
data["settings"]["smtp_ssl"] = True
data["settings"]["smtp_user"] = "apikey"
data["settings"]["smtp_pass"] = "sendgrid secret token"

data["settings"]["mail_from"] = "Nebula <support@example.com>"


data["services"] = {
    1  : ["mesg",   "svbcore",         "mesg",     "template/services/mesg.xml",     True, 5],
    2  : ["play",   "svbcore",         "play",     "template/services/play.xml",     True, 5],
    3  : ["broker", "svbwork",         "broker",   None,     True, 5],
    4  : ["psm",    "svbwork",         "psm",      None,     True, 5],
    5  : ["meta",   "svbwork",         "meta1",    "template/services/meta1.xml",     True, 5],
    6  : ["meta",   "svbwork",         "meta2",    "template/services/meta2.xml",     True, 5],
    7  : ["import", "spconv3",         "import",   "template/services/import.xml",    True, 5],
    8  : ["worker", "spconv3",         "injektaz", "template/services/injektaz.xml",  True, 5],
    9  : ["worker", "spconv3",         "vod",      "template/services/vod.xml",       True, 5],
    10 : ["conv",   "spconv3",         "conv1",    None,     True, 5],
    11 : ["conv",   "spconv3",         "conv2",    None,     True, 5],
}

data["actions"] = {
    1 : ["proxy",   "conv", "template/actions/proxy.xml"],
    2 : ["playout", "conv", "template/actions/playout.xml"],
    3 : ["client", "conv", "template/actions/client.xml"],
}


data["storages"] = {
    1 : {
        "title"    : "production",
        "protocol" : "samba",
        "path"     : "//productionstorage/storage",
        "login"    : "nebula",
        "password" : "nebula",
        "samba_version" : "3.0"
    },
    2 : {
        "title"    : "playout",
        "protocol" : "samba",
        "path"     : "//playoutserver/playout",
        "login"    : "nebula",
        "password" : "nebula",
        "samba_version" : "3.0"
    }
}

data["channels"] = {
    1 :  [0, {
        'title': 'Caspar TV',
        'engine' : 'casparcg',
        'controller_host' : 'localhost',
        'controller_port' : 42100,
        'caspar_host' : 'casparcg',
        'caspar_port' : 5250,
        'caspar_channel' : 1,
        'caspar_feed_layer' : 10,
        'playout_storage' : 2,
        'playout_dir' : "media.dir",
        'playout_container' : 'mxf',
        'day_start' : [7, 0],
        'send_action' : 2,
        'rundown_accepts': "asset['content_type'] == VIDEO",
        'scheduler_accepts': "asset['id_folder'] in [1, 2]",
        'fps': 25,
	'live_source' : 'DECKLINK 2 FORMAT 1080i5000',
        'plugins' : ["injektaz", "logo", "templates", "upoutavka", "crawl", "plachty"],
        'solvers' : ["report", "smycka"],
        'meta_set' : [
                ("start", {}),
                ("title", {}),
                ("subtitle", {}),
                ("description", {}),
                ("promoted", {}),
                ("color", {})
            ]
    }]
}
