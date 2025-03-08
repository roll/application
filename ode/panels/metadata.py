import json
import sys
from pathlib import Path

from frictionless.resources import TableResource
from frictionless import system

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
        QWidget, QLabel, QVBoxLayout, QHBoxLayout,
        QApplication, QPushButton, QStackedLayout
)
from PySide6.QtWidgets import QTabWidget

from ode.paths import Paths
from ode.panels.tabs import ResourceTab, DialectTab, SchemaTab



STYLE_SHEET = Path("ode/panels/tab-style.qss").read_text()

_RESOURCE_METADATA = {
    "Resource": ["Integrity", "Licenses", "Contributors", "Sources"],
    "Dialect": ["Csv"],
    "Schema": ["Fields", "Foreign Keys"]
}


class FrictionlessResourceMetadataWidget(QWidget):
    def __init__(self, filepath=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QHBoxLayout()

        self.forms = []

        self.filepath = filepath
            #for form in self.forms:
            #    form.populate(self.resource)

        metadata = self.make_metadata()

        # Help
#        help = QWidget()
#        help.setFixedWidth(300)
#        help.setFixedHeight(450)
#        help_layout = QVBoxLayout()
#        help_title = QLabel("HELP")
#        help_title.setFixedHeight(30)
#        help_description = QLabel("This is a long text that will be replaced with the actual help content.")
#        help_description.setWordWrap(True)
#        help_description.setFixedHeight(250)
#        help_learn_more = QPushButton("LEARN MORE")
#        help_layout.addWidget(help_title)
#        help_layout.addWidget(help_description)
#        help_layout.addWidget(help_learn_more)
#        help_layout.addStretch()
#        help.setLayout(help_layout)

        #self.layout.addWidget(tree)
        #self.layout.addLayout(self.forms_layout)
        #self.layout.addWidget(help, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(metadata)
        self.setLayout(self.layout)

    def make_metadata(self):
        metadata_widget = QWidget()
        mainlayout = QVBoxLayout()
        pages_box = QHBoxLayout()
        mainlayout.addLayout(pages_box)
        metadata_widget.setLayout(mainlayout)
        metadata_widget.setStyleSheet(STYLE_SHEET)

        self.pages_layout = QStackedLayout()
        mainlayout.addLayout(self.pages_layout)


        self.resource_page = ResourceTab()
        resource_button = QPushButton(self.resource_page.page)
        resource_button.clicked.connect(self._change_page)
        pages_box.addWidget(resource_button)
        self.forms.extend(self.resource_page.get_forms())
        self.pages_layout.addWidget(self.resource_page)


        self.dialect_page = DialectTab()
        dialect_button = QPushButton(self.dialect_page.page)
        dialect_button.clicked.connect(self._change_page)
        pages_box.addWidget(dialect_button)
        self.forms.extend(self.dialect_page.get_forms())
        self.pages_layout.addWidget(self.dialect_page)

        self.schema_page = SchemaTab()
        schema_button = QPushButton(self.schema_page.page)
        schema_button.clicked.connect(self._change_page)
        pages_box.addWidget(schema_button)
        self.forms.extend(self.schema_page.get_forms())
        self.pages_layout.addWidget(self.schema_page)

        pages_box.addStretch()

        if self.filepath:
            self.resource = self.get_or_create_metadata(self.filepath).get("resource")
            for form in self.forms:
                form.populate(self.resource)

        return metadata_widget

    def _change_page(self):
        button = self.sender().text()

        if button == "Resource":
            self.pages_layout.setCurrentWidget(self.resource_page)

        if button == "Schema":
            self.pages_layout.setCurrentWidget(self.schema_page)

        if button == "Dialect":
            self.pages_layout.setCurrentWidget(self.dialect_page)

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
        metadata_filepath = Paths.get_path_to_metadata_file(filepath)
        metadata = dict()

        if not metadata_filepath.exists():
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

        metadata_filepath = Paths.get_path_to_metadata_file(self.resource.path)
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
