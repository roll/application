import json
from pathlib import Path

from frictionless.resources import TableResource
from frictionless import system

from ode.paths import Paths


def migrate_metadata_store():
    """Migrates all the metadata information to separated files.

    Previously ODE stored the Frictionless metadata and other info of
    every file in a single "records" dictionary stored in a metadata.json.
    This created several issues like: custom logic to deduplicate file names,
    a third database to link files with records, etc.

    We will now store metadata on independent files under a `.metadata` folder.
    Each file will have the same name of the original file with a `metadata.json` append.
    We will also mimic the folder structure.
    """
    new_metadata_dir = Paths.PROJECT_PATH / '.metadata/'
    if new_metadata_dir.exists():
        print(".metadata folder exist. Skipping migration...")
        return
    new_metadata_dir.mkdir()

    # Path to the original metadata.json file
    metadata_file_path = Paths.PROJECT_PATH / '.opendataeditor/metadata.json'
    if not metadata_file_path.exists():
        print("There is no current metadata.json file to migrate. Skipping migration...")
        return

    with open(metadata_file_path, 'r') as file:
        metadata = json.load(file)

    records = metadata['record']

    for _, record_data in records.items():
        path = record_data['path']
        try:
            # Infer Frictionless Statistics, it is mandatory for the newest version of ODE.
            with system.use_context(trusted=True):
                resource = TableResource(record_data.get("resource"))
                # Patch the original resource path with the absolute path to the file.
                resource.path = str(Paths.PROJECT_PATH / path)
                resource.infer(stats=True)
                record_data["resource"] = resource.to_descriptor()
        except Exception as e:
            # This should happen only if the user did file/metadata editing outside ODE.
            print(f"Error when creating TableResource: {e}")
            continue

        # Set metadata file name as <filename>.json
        # Example: my-file.csv -> my-file.json
        # Example: subfolder/my-file.csv -> subfolder/my-file.json
        filename = path.rsplit(".", 1)[0]
        metadata_filename = str(new_metadata_dir / filename) + ".json"

        # Ensure the directory structure exists
        # Example: if we are migrating a file located in a subfolder, we need to create
        # it before the json.dump file.
        Path(metadata_filename).parent.mkdir(parents=True, exist_ok=True)

        with open(metadata_filename, 'w') as json_file:
            json.dump(record_data, json_file, indent=4)

    print("Migration completed successfully!")
