import json
import sys
from pathlib import Path

from frictionless.resources import TableResource
from frictionless import system

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
        QWidget, QLabel, QVBoxLayout, QHBoxLayout, QStackedLayout, QApplication, QPushButton,
        QSpinBox, QMessageBox, QScrollArea
)
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QListWidget
from PySide6.QtWidgets import QFormLayout, QLineEdit, QComboBox

from ode.paths import Paths

_RESOURCE_METADATA = {
    "Resource": ["Integrity", "Licenses", "Contributors", "Sources"],
    "Dialect": ["Csv"],
    "Schema": ["Fields", "Foreign Keys"]
}


class LicensesForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.licenses = self.get_list_of_licenses()
        # License selection
        self.license_list = QComboBox()
        self.license_list.addItems([lic["title"] for lic in self.licenses])
        layout.addWidget(QLabel("Available Licenses:"))
        layout.addWidget(self.license_list)

        # Buttons to add/remove licenses
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # Selected licenses
        self.selected_licenses = QListWidget()
        layout.addWidget(QLabel("Selected Licenses:"))
        layout.addWidget(self.selected_licenses)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_license)
        self.remove_button.clicked.connect(self.remove_license)

        self.setLayout(layout)

    def add_license(self):
        """Add a license to the list of selected licenses."""
        license_title = self.license_list.currentText()
        # Check for duplicates
        if not any(license_title == self.selected_licenses.item(i).text() for i in range(self.selected_licenses.count())):
            self.selected_licenses.addItem(license_title)
        else:
            QMessageBox.warning(self, "Duplicate", "This license is already added.")

    def remove_license(self):
        selected_item = self.selected_licenses.currentItem()
        if selected_item:
            self.selected_licenses.takeItem(self.selected_licenses.row(selected_item))
        else:
            QMessageBox.warning(self, "No Selection", "Please select a license to remove.")

    def get_list_of_licenses(self):
        """Reads a list of licenses from an asset file.

        Each license in an object specified by the Datapackage standard.

        Example:
        {
          "name": "AGPL-3.0",
          "path": "https://opensource.org/licenses/AGPL-3.0",
          "title": "GNU Affero General Public License v3"
        }
        """
        result = []
        with open(Paths.asset("licenses.json")) as file:
            result = json.load(file)
        return result

    def get_selected_licenses(self):
        """Returns the list of selected licenses.

        This will be used to set the license field of the resource when saving the metadata.
        """
        selected = []
        for index in range(self.selected_licenses.count()):
            title = self.selected_licenses.item(index).text()
            license_obj = filter(lambda lic: lic["title"] == title, self.licenses)
            selected.extend(license_obj)
        return selected

    def populate(self, resource):
        for lic in resource.licenses:
            self.selected_licenses.addItem(lic["title"])


class SingleFieldForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QFormLayout()
        self.name = QLineEdit()
        layout.addRow("Name: ", self.name)
        self.types = QComboBox()
        self.types.addItems([
            "any", "array", "boolean", "date", "datetime", "duration",
            "geojson", "geopoint", "integer", "number", "string", "object",
            "time", "year", "yearmonth"
        ])
        layout.addRow("Type: ", self.types)
        self.title = QLineEdit()
        layout.addRow("Title: ", self.title)
        self.description = QLineEdit()
        layout.addRow("Description: ", self.description)
        self.missing_values = QLineEdit()
        self.missing_values.setEnabled(False)
        layout.addRow("Missing Values: ", self.missing_values)
        self.rdf_type = QLineEdit()
        layout.addRow("RDF Type: ", self.rdf_type)
        self.setLayout(layout)

    def populate(self, field):
        self.name.setText(field.name)
        self.types.setCurrentText(field.type)
        self.title.setText(field.title)
        self.description.setText(field.description)
        # self.missing_values.setText(field.missing_values)
        self.rdf_type.setText(field.rdf_type)


class FieldsForm(QWidget):
    """Widget to dynamically display the field forms.

    This is a tricky widget since it has to dinamycally add/remove field forms
    inside a QScrollArea when we navigate between resources.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_widget.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container_widget)
        self.field_forms = []

        self.setStyleSheet("QScrollArea {border: none;}")

    def remove_forms(self):
        for form in self.field_forms:
            self.container_layout.removeWidget(form)
            form.deleteLater()
        self.field_forms = []

    def populate(self, resource):
        if self.field_forms:
            self.remove_forms()
        for field in resource.schema.fields:
            form = SingleFieldForm()
            form.populate(field)
            self.field_forms.append(form)
            self.container_layout.addWidget(form)

    def resizeEvent(self, event):
        """Ensure the QScrollArea resizes to fit the parent layout.

        I couldn't find a better way to rezise the QScrollArea to always fit
        the parent container. QScrollArea seems to have a particular behaviour
        related to sizes, specially on widgets that adds childrens dynamically:
        https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QScrollArea.html#size-hints-and-layouts
        """
        super().resizeEvent(event)
        self.scroll_area.setGeometry(self.rect())


class SchemaForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QFormLayout()
        self.name = QLineEdit()
        self.name.setEnabled(False)
        layout.addRow("Name: ", self.name)
        self.primary_key = QComboBox()
        self.primary_key.setEnabled(False)
        layout.addRow("Primary Key: ", self.primary_key)
        self.title = QLineEdit()
        self.title.setEnabled(False)
        layout.addRow("Title: ", self.title)
        self.missing_values = QLineEdit()
        self.missing_values.setEnabled(False)
        layout.addRow("Missing Values: ", self.missing_values)
        self.description = QLineEdit()
        self.description.setEnabled(False)
        layout.addRow("Description: ", self.description)
        self.setLayout(layout)

    def populate(self, resource):
        # TODO: Implement, logic of Schema is not well defined
        pass


class IntegrityForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QFormLayout()

        self.hash = QLineEdit()
        layout.addRow("Hash: ", self.hash)
        self.fields = QSpinBox()
        layout.addRow("Fields: ", self.fields)
        self.bytes_field = QSpinBox()
        layout.addRow("Bytes: ", self.bytes_field)
        self.rows = QSpinBox()
        layout.addRow("Rows: ", self.rows)

        self.setLayout(layout)

    def populate(self, resource):
        self.hash.setText(resource.hash)
        self.fields.setValue(resource.fields)
        self.bytes_field.setValue(resource.bytes)
        self.rows.setValue(resource.rows)


class ResourceForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QFormLayout()

        self.name = QLineEdit()
        self.layout.addRow("Name: ", self.name)
        self.path = QLineEdit()
        self.path.setEnabled(False)
        self.layout.addRow("Path: ", self.path)
        self.types = QComboBox()
        self.types.addItems(["file", "text", "json", "table"])
        self.layout.addRow("Type: ", self.types)
        self.scheme = QLineEdit()
        self.layout.addRow("Scheme: ", self.scheme)
        self.format = QLineEdit()
        self.layout.addRow("Format: ", self.format)
        self.title = QLineEdit()
        self.layout.addRow("Title: ", self.title)
        self.mediatype = QLineEdit()
        self.layout.addRow("Media Type: ", self.mediatype)
        self.description = QLineEdit()
        self.layout.addRow("Description: ", self.description)
        self.encoding = QLineEdit()
        self.layout.addRow("Encoding: ", self.encoding)

        self.setLayout(self.layout)

    def populate(self, resource):
        """Populates all the form fields with the values of the resource"""
        self.name.setText(resource.name)
        self.path.setText(resource.path)
        self.title.setText(resource.title)
        self.types.setCurrentText(resource.type)
        self.mediatype.setText(resource.mediatype)
        self.description.setText(resource.description)
        self.encoding.setText(resource.encoding)
        self.scheme.setText(resource.scheme)
        self.format.setText(resource.format)


class FrictionlessResourceMetadataWidget(QWidget):
    def __init__(self, filepath=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QHBoxLayout()

        # Sidebar menu
        tree = QTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setFixedWidth(350)
        items = []
        for key, values in _RESOURCE_METADATA.items():
            item = QTreeWidgetItem([key])
            for value in values:
                child = QTreeWidgetItem([value])
                item.addChild(child)
            items.append(item)
        tree.insertTopLevelItems(0, items)
        tree.expandAll()
        tree.clicked.connect(self.switch_form)

        # Metadata Forms
        self.forms_layout = QStackedLayout()
        self.forms = [
            ResourceForm(), IntegrityForm(), LicensesForm(), SchemaForm(), FieldsForm(),
        ]
        for form in self.forms:
            self.forms_layout.addWidget(form)
        if filepath:
            self.resource = self.get_or_create_metadata(filepath).get("resource")
            for form in self.forms:
                form.populate(self.resource)

        # Help
        help = QWidget()
        help.setFixedWidth(300)
        help.setFixedHeight(450)
        help_layout = QVBoxLayout()
        help_title = QLabel("HELP")
        help_title.setFixedHeight(30)
        help_description = QLabel("This is a long text that will be replaced with the actual help content.")
        help_description.setWordWrap(True)
        help_description.setFixedHeight(250)
        help_learn_more = QPushButton("LEARN MORE")
        help_layout.addWidget(help_title)
        help_layout.addWidget(help_description)
        help_layout.addWidget(help_learn_more)
        help_layout.addStretch()
        help.setLayout(help_layout)

        self.layout.addWidget(tree)
        self.layout.addLayout(self.forms_layout)
        self.layout.addWidget(help, alignment=Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

    def switch_form(self, index):
        """Set the index of the Forms Stacked Layout to match the selected form."""
        # This order is the order in which we add the forms to the stacked layout in the
        # __init__ method. We could implement something more fancy but life is too short
        # to make complex stuff.
        form = index.data()
        if form == 'Resource':
            self.forms_layout.setCurrentIndex(0)
        elif form == "Integrity":
            self.forms_layout.setCurrentIndex(1)
        elif form == "Licenses":
            self.forms_layout.setCurrentIndex(2)
        elif form == "Schema":
            self.forms_layout.setCurrentIndex(3)
        elif form == "Fields":
            self.forms_layout.setCurrentIndex(4)

    def _get_path_to_metadata_file(self, filepath):
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
        filepath = Path(filepath)
        relative_path = filepath.parent.relative_to(Paths.PROJECT_PATH)
        metadata_path = Paths.METADATA_PATH / relative_path
        metadata_filepath = metadata_path / (filepath.stem + '.json')
        return metadata_filepath

    def get_or_create_metadata(self, filepath):
        """Get or create a metadata object for the Resource.

        Metadata is a dict containing the Frictionless Metadata plus other metadata
        that ODE could require.

        Example:
        {
          "resource": "{...frictionless descriptor...}"
          "custom_ode_metadata": "custom_ode_metadata_value"
        }
        """
        metadata_filepath = self._get_path_to_metadata_file(filepath)
        metadata = dict()

        if not metadata_filepath.exists():
            print("Metadata file not found. Creating and empty one.")
            metadata_filepath.parent.mkdir(parents=True, exist_ok=True)
            with system.use_context(trusted=True):
                resource = TableResource(filepath)
                resource.infer(stats=True)
            with open(metadata_filepath, "w") as f:
                # Resource is not serializable, converting to dict before writing.
                metadata["resource"] = resource.to_descriptor()
                json.dump(metadata, f)
            # We want to return a Frictionless object, so we are plugging it back.
            metadata["resource"] = resource
            return metadata

        with open(metadata_filepath) as file:
            metadata = json.load(file)

        with system.use_context(trusted=True):
            resource = TableResource(metadata["resource"])
            resource.infer(stats=True)
            metadata["resource"] = resource

        return metadata

    def populate_all_forms(self, filepath):
        """Populates the form with the content of the descriptor."""
        self.resource = self.get_or_create_metadata(filepath).get("resource")
        for form in self.forms:
            form.populate(self.resource)

    def save_metadata_to_descriptor_file(self):
        """Collects all data from all forms and save the descriptor.

        descriptor is the name that frictionless give to the json file that
        stores all the Resource metadata.
        """
        for form in self.forms:
            if isinstance(form, ResourceForm):
                self.resource.name = form.name.text()
                self.resource.path = form.path.text()
                self.resource.title = form.title.text()
                self.resource.types = form.types.currentText()
                self.resource.mediatype = form.mediatype.text()
                self.resource.description = form.description.text()
                self.resource.encoding = form.encoding.text()
                self.resource.scheme = form.scheme.text()
                self.resource.format = form.format.text()
            elif isinstance(form, IntegrityForm):
                self.resource.hash = form.hash.text()
                self.resource.fields = form.fields.value()
                self.resource.bytes = form.bytes_field.value()
                self.resource.rows = form.rows.value()
            elif isinstance(form, SchemaForm):
                # SchemaForm
                # self.resource.schema.name = form.name.text()
                # self.resource.schema.title = form.title.text()
                # self.resource.schema.primary_key = form.primary_key.currentText()
                # self.resource.schema.missing_values = form.missing_values.text()
                # self.resource.schema.description = form.description.text()
                pass
            elif isinstance(form, FieldsForm):
                for i, field_form in enumerate(form.field_forms):
                    field = self.resource.schema.fields[i]
                    field.name = field_form.name.text()
                    # field type cannot be updated directly, we need to use set_field_type
                    self.resource.schema.set_field_type(field.name, field_form.types.currentText())
                    field.title = field_form.title.text()
                    field.description = field_form.description.text()
                    # field.missing_values = field_form.missing_values.text()
                    field.rdf_type = field_form.rdf_type.text()
            elif isinstance(form, LicensesForm):
                self.resource.licenses = form.get_selected_licenses()

        metadata_filepath = self._get_path_to_metadata_file(self.resource.path)
        metadata = self.get_or_create_metadata(self.resource.path)
        metadata["resource"] = self.resource.to_descriptor()
        with open(metadata_filepath, "w") as f:
            print(f"Saving metadata {metadata_filepath}")
            json.dump(metadata, f)


if __name__ == "__main__":
    app = QApplication([])
    metadata = FrictionlessResourceMetadataWidget(filepath="./data/valid.csv")
    metadata.showMaximized()
    metadata.show()
    sys.exit(app.exec())
