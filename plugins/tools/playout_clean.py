"""
This plugin deletes playout media, which haven't been used for more than 3 months
and aren't scheduled for playback.
"""

from nebula import *

def get_scheduled(id_channel, db=False):
    db = db or DB()
    db.query("""
        SELECT DISTINCT(i.id_asset)
        FROM
            items AS i,
            events AS e
        WHERE
            e.id_channel = %s
        AND e.start > %s
        AND e.id_magic = i.id_bin
        """,
        [ id_channel, time.time() - (90*24*3600) ]
    )

    return [i[0] for i in db.fetchall()]


def latest_run(id_asset, id_channel, db):
    db.query("SELECT r.start FROM asrun AS r, items AS i WHERE r.id_channel = %s AND r.id_item = i.id AND i.id_asset = %s ORDER BY start DESC LIMIT 1 ", [id_channel, id_asset])
    try:
        return db.fetchall()[0][0]
    except IndexError:
        return 0


def clear():
    db = DB()

    for id_channel in config["playout_channels"]:
        logging.info(f"Cleaning {config['playout_channels'][id_channel]['title']} storage")
        scheduled_assets = get_scheduled(id_channel, db)
        db.query(f"SELECT meta FROM assets WHERE meta->>'playout_status/{id_channel}' IS NOT NULL")
        i = 0
        s = 0
        for meta, in db.fetchall():
            asset = Asset(meta=meta, db=db)

            if asset.id in scheduled_assets:
                continue
            i+=1

            s += asset[f"playout_status/{id_channel}"]["size"]
            logging.debug(f"Removing {asset.get_playout_full_path(id_channel)}. Last aired {format_time(latest_run(asset.id, id_channel, db))}")

            os.remove(asset.get_playout_full_path(id_channel))
            del(asset.meta[f"playout_status/{id_channel}"])
            asset.save()

        logging.info(f"Removed {i} {config['playout_channels'][id_channel]['title']} playout media files. {format_filesize(s) or '0 bytes'} freed.")


class Plugin(WorkerPlugin):
    def __init__(self):
        clear()
