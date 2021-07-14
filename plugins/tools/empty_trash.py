import shutil
from nebula import *

class Plugin():
    def __init__(self):
        db = DB()
        db.query("SELECT meta FROM assets WHERE status = %s AND media_type = %s", [TRASHED, FILE])

        total_size = 0
        count = 0

        for meta, in db.fetchall():
            asset = Asset(meta=meta, db=db)
            if not os.path.exists(asset.file_path):
                continue

            total_size += asset["file/size"]
            count += 1

            trash_dir = os.path.join(storages[asset["id_storage"]].local_path, ".nx/trash")
            target_path = os.path.join(trash_dir, asset["path"])
            target_dir = os.path.split(target_path)[0]

            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)

            logging.debug(f"Moving {asset.file_path} to {target_path}")
            shutil.move(asset.file_path, target_path)

        logging.info(f"{count} assets of total size of {format_filesize(total_size)} is ready for removal")
