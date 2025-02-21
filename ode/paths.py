import os

from pathlib import Path


class Paths:
    """Utility class to handle relative paths."""
    base = os.path.dirname(__file__)
    assets = os.path.join(base, "assets")

    # This is the Project path where all files are stored and
    # it will be hardcoded to the home folder of the user until
    # we define how to properly handle projects in Open Data Editor.
    PROJECT_PATH = Path.home() / '.opendataeditor/tmp'
    METADATA_PATH = PROJECT_PATH / '.metadata'

    @classmethod
    def asset(cls, filename):
        return os.path.join(cls.assets, filename)

    @classmethod
    def translation(cls, filename):
        return os.path.join(cls.assets, "translations", filename)
