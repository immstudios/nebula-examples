Importing media
===============

Watchfolders
------------

The easiest way to import media files to nebula is to use watchfolders. 
That way, new assets are created automatically for each file uploaded to 
a defined directory. To use watchfolders, use a single instance of the `watch`
service. Service configuration may contain one or more watchfolders.

```xml
<service>
    <folder id_storage="1" path="media.dir/movies"/>
    <folder id_storage="2" path="media.dir/episodes"/>
</service>
```
Folder tag attributes:

- `id_storage` (required)
- `path` (required)
- `id_folder` (default 12 - Incoming)
- `recursive` (default True)
- `hidden` (default False) - Ignore dotfiles
- `quarantine_time` (default 10)
- `case_sensitive_exts` (default False)

It is also possible to execute a script to add/modify the metadata of the new asset:

```xml
<service>
  <folder id_storage="1" path="media.dir" recursive="1" id_folder="1">
    <post>
<![CDATA[
import shortuuid
asset["id/main"] = shortuuid.uuid()
]]>
    </post>
  </folder>
</service>
```

If you are using watchfolders, a media file (quite obviously) must exist prior to the creation of the asset.

Manual asset creation
---------------------

Nebula also supports the opposite method: Create an asset first using the web interface 
or Firefly and enforce the user to fill all required metadata before they are able to upload the file. 
This can be done using an asset validation plugin: 

Create a file on your first storage `.nx/scripts/v5/validator/asset.py` and create a script similar to the following:

```python

from nx.plugins import ValidatorPlugin
from nx.core.enum import ContentType, MediaType


class Plugin(ValidatorPlugin):
    def validate(self, asset):

        if not asset["title"]:
            # Return string with an error message in case metadata is incorrect
            return "Title is required"

        if len(asset["title"]) > 255:
            return "Title must be 255 characters or less"

        if not asset.id:
            # This is a new asset, so we save it first to get its ID
            asset.save() 

            # The file is expected in the media.dir directory and must be named by asset ID.
            path = f"media.dir/{asset.id}.mxf"

            asset["id_storage"] = 1
            asset["path"] = path
            asset["content_type"] = ContentType.VIDEO
            asset["media_type"] = MediaType.FILE
        
        return asset
```

The validate methodr returns the modified instance of the asset or a string with an error message.


When the asset is created, Nebula expects the file at the specified location 
and after it's uploaded, it pairs automatically, and its technical metadata is extracted.

This method is useful if you need to schedule clips for broadcasting before they are created: 
you just enter the expected duration during the asset creation and then use this offline asset in your rundown. 
When the file arrives, Nebula just marks the asset as online and updates the duration according to the actual value.


### Future validators

Nebula 6 (now in alpha) uses a slightly different validators, which are more pythonic:

```python

import nebula

from nebula.enum import ContentType, MediaType, ObjectStatus
from nebula.exceptions import ValidationException

from typing import Any
from enum import IntEnum


class Folder(IntEnum):
    MOVIE = 1
    EPISODE = 2
    STORY = 3
    SONG = 4
    FILL = 5
    TRAILER = 6
    JINGLE = 7
    GRAPHIC = 8
    COMMERCIAL = 9
    TELESHOPPING = 10
    DATASET = 11
    INCOMING = 12
    SERIE = 13


async def validate(
    asset: nebula.Asset, # Original asset (or an empty asset to be modified)
    meta: dict[str, Any], # Form data
    connection: nebula.DB, # Database connection object (with a running transaction)
    user: nebula.User, # The user performing the update
) -> None:
    """Validate the asset.

    The validator runs in a transaction, so at any point you can raise
    an exception to abort the transaction.
    """

    asset.patch(meta)

    # Do a simple check to see if all required fields are present.

    if not asset["title"]:
        raise ValidationException("Title is required")

    # We need an asset id to continue, so if it's a new asset,
    # we need to save it first. This will generate an id.
    # Remember that we're in a transaction, so if we raise an exception
    # later, the asset will be rolled back.

    if not asset.id:
        await asset.save()

    # Fill additional fields based on the folder.

    if asset["id_folder"] == Folder.DATASET:
        asset["media_type"] = MediaType.VIRTUAL
        asset["content_type"] = ContentType.TEXT
        asset["status"] = ObjectStatus.ONLINE

    elif asset["id_folder"] == Folder.SERIE:
        asset["media_type"] = MediaType.VIRTUAL
        asset["content_type"] = ContentType.PACKAGE
        asset["status"] = ObjectStatus.ONLINE

        await connection.execute(
            """
            INSERT INTO cs (cs, value, settings)
            VALUES ($1, $2, $3)
            ON CONFLICT (cs, value) DO UPDATE SET settings = $3
            """,
            "urn:site:series",
            str(asset.id),
            {
                "aliases": {"en": asset["title"]},
            },
        )

    else:
        asset["media_type"] = MediaType.FILE
        asset["content_type"] = ContentType.VIDEO
        asset["status"] = ObjectStatus.OFFLINE
        asset["id/main"] = f"{asset.id:06x}"

        subdir = Folder(asset["id_folder"]).name.lower() + "s"
        asset["id_storage"] = 1
        asset["path"] = f"media.dir/{subdir}/{asset['id/main']}.mxf"

    # We're done, all changes made to the asset will be saved
    # outside of this function, so we don't need to call save()
    # or return anything.

```
