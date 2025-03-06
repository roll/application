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

    @classmethod
    def get_path_to_metadata_file(cls, filepath):
        """Returns the path to the metadata file of the given file.

        Metadata is a JSON object that stores Fricionless Metadata and any other
        metadata required by ODE. All metadata files are going to be stored in a
        `.metadata` folder mimicing the file name and the structure of the project
        folder.

        Example 1:
          - File: Paths.PROJECT_FOLDER / 'myfile.csv'
          - Metadata: Paths.PROJECT_FOLDER / '.metadata/myfile.json'

        Example 2 (subfolder):
          - File: Paths.PROJECT_FOLDER / 'subfolder/invalid-file.csv'
          - Metadata: Paths.PROJECT_FOLDER / '.metadata/subfolder/invalid-file.json'
        """
        filepath = Path(filepath) if isinstance(filepath, str) else filepath
        relative_path = filepath.parent.relative_to(cls.PROJECT_PATH)
        metadata_path = cls.METADATA_PATH / relative_path
        metadata_filepath = metadata_path / (filepath.stem + '.json')
        return metadata_filepath

    @classmethod
    def get_unique_destination_filepath(cls, src_filepath, project_path=None):
        """Returns a unique destination_filepath by appending a number if the file already exists.

        If the specified file already exists, the method will generate a new filename by
        appending a number in parentheses to the original name. For example:

          - For a file named 'myfile.csv', if it doesn't exist, it will return 'myfile.csv'.
          - If 'myfile.csv' already exists, it will return 'myfile(1).csv'.
          - If 'myfile(1).csv' also exists, it will return 'myfile(2).csv', and so on.
        """

        src_filepath = Path(src_filepath) if isinstance(src_filepath, str) else src_filepath

        project_path = cls.PROJECT_PATH if project_path is None else project_path
        destination_filepath = Path(project_path) / src_filepath.name

        # If already exists we increment to `filename (n) until we find one not taking
        counter = 1
        while destination_filepath.exists():
            destination_filepath = destination_filepath.with_stem(f"{src_filepath.stem}({counter})")
            counter += 1

        return destination_filepath
