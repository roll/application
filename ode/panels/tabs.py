import json

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
        QWidget, QHBoxLayout, QStackedLayout,
        QPushButton, QTabWidget, QVBoxLayout,
        QLabel, QFormLayout, QMessageBox,
        QListWidget, QComboBox, QLineEdit,
        QSpinBox, QScrollArea, QBoxLayout,
        QGridLayout
)

from ode.paths import Paths


stylesheet = Path("ode/panels/tab-style.qss").read_text()



class LicensesForm(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.insertSpacing(0, 30)
        self.licenses = self.get_list_of_licenses()
        # License selection
        self.license_list = QComboBox()
        self.license_list.addItems([lic["title"] for lic in self.licenses])

        licenses = QLabel("Licenses")
        layout.addWidget(licenses)
        licenses.setStyleSheet(
                "font-size: 28px; font-weight: 545; color: black;"
        )
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

        layout.addStretch()
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

        form_layout = QVBoxLayout()

        label_layout = QHBoxLayout()
        layout = QFormLayout()
        form_layout.addLayout(label_layout)
        form_layout.addLayout(layout)

        label = QLabel("SingleField")
        label_layout.addWidget(label)

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

        form_layout.addStretch()
        self.setLayout(form_layout)

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
        self.form_layout = QVBoxLayout()

        # TODO
        # Add search bar and "Add field" button to
        # label layout as they're on the same level
        self.label_layout = QHBoxLayout()
        self.container_layout = QVBoxLayout()
        self.form_layout.addLayout(self.label_layout)
        self.form_layout.addLayout(self.container_layout)

        label = QLabel("Fields")
        self.label_layout.addWidget(label)

        self.container_widget.setLayout(self.form_layout)
        self.scroll_area.setWidget(self.container_widget)
        self.field_forms = []

        self.form_layout.addStretch()
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

        form_layout = QVBoxLayout()
        form_layout.insertSpacing(0, 30)

        label_layout = QHBoxLayout()
        layout = QGridLayout()
        form_layout.addLayout(label_layout)
        form_layout.addLayout(layout)

        label = QLabel("Schema")
        label_layout.addWidget(label)
        label.setStyleSheet(
                "font-size: 28px; font-weight: 545; color: black;"
        )

        name_label = QLabel("Name")
        self.name = QLineEdit()
        self.name.setEnabled(False)
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name, 1, 0)

        primary_key_label = QLabel("Primary Key")
        self.primary_key = QComboBox()
        self.primary_key.setEnabled(False)
        layout.addWidget(primary_key_label, 0, 1)
        layout.addWidget(self.primary_key, 1, 1)

        title_label = QLabel("Title")
        self.title = QLineEdit()
        self.title.setEnabled(False)
        layout.addWidget(title_label, 2, 0)
        layout.addWidget(self.title, 3, 0)

        missing_values_label = QLabel("Missing Values")
        self.missing_values = QLineEdit()
        self.missing_values.setEnabled(False)
        layout.addWidget(missing_values_label, 2, 1)
        layout.addWidget(self.missing_values, 3, 1)

        description_label = QLabel("Description")
        self.description = QLineEdit()
        self.description.setEnabled(False)
        layout.addWidget(description_label, 4, 0)
        layout.addWidget(self.description, 5, 0)

        form_layout.addStretch()
        self.setLayout(form_layout)

    def populate(self, resource):
        # TODO: Implement, logic of Schema is not well defined
        pass


class IntegrityForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        form_layout = QVBoxLayout()
        form_layout.insertSpacing(0, 30)


        layout = QGridLayout()
        label_layout = QHBoxLayout()
        form_layout.addLayout(label_layout)
        form_layout.addLayout(layout)

        label = QLabel("Integrity")
        label_layout.addWidget(label)
        label.setStyleSheet(
                "font-size: 28px; font-weight: 545; color: black;"
        )

        hash_label = QLabel("Hash")
        self.hash = QLineEdit()
        layout.addWidget(hash_label, 0, 0)
        layout.addWidget(self.hash, 1, 0)

        field_label = QLabel("Fields")
        self.fields = QSpinBox()
        layout.addWidget(field_label, 0, 1)
        layout.addWidget(self.fields, 1, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(0, 1)

        bytes_label = QLabel("Bytes")
        self.bytes_field = QSpinBox()
        layout.addWidget(bytes_label, 2, 0)
        layout.addWidget(self.bytes_field, 3, 0)

        rows_label = QLabel("Rows")
        self.rows = QSpinBox()
        layout.addWidget(rows_label, 2, 1)
        layout.addWidget(self.rows, 3, 1)

        form_layout.addStretch()
        self.setLayout(form_layout)

    def populate(self, resource):
        self.hash.setText(resource.hash)
        self.fields.setValue(resource.fields)
        self.bytes_field.setValue(resource.bytes)
        self.rows.setValue(resource.rows)


class ResourceForm(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form_layout = QVBoxLayout()
        self.form_layout.insertSpacing(0, 30)

        self.label_layout = QHBoxLayout()
        self.layout = QGridLayout()
        self.form_layout.addLayout(self.label_layout)
        self.form_layout.addLayout(self.layout)

        self.label = QLabel("Resource")
        self.label_layout.addWidget(self.label)
        self.label.setStyleSheet(
                "font-size: 28px; font-weight: 545; color: black;"
        )

        name_label = QLabel("Name")
        self.name = QLineEdit()
        self.layout.addWidget(name_label, 0, 0)
        self.layout.addWidget(self.name, 1, 0)

        path_label = QLabel("Path")
        self.path = QLineEdit()
        self.path.setEnabled(False)
        self.layout.addWidget(path_label, 0, 1)
        self.layout.addWidget(self.path, 1, 1)

        type_label = QLabel("Type")
        self.types = QComboBox()
        self.types.addItems(["file", "text", "json", "table"])
        self.layout.addWidget(type_label, 2, 0)
        self.layout.addWidget(self.types, 3, 0)

        scheme_label = QLabel("Scheme")
        format_label = QLabel("Format")
        label_box = QHBoxLayout()
        label_box.addWidget(scheme_label)
        label_box.addWidget(format_label)
        self.layout.addLayout(label_box, 2, 1)

        self.scheme = QLineEdit()
        self.format = QLineEdit()
        hbox = QHBoxLayout()
        hbox.addWidget(self.scheme)
        hbox.addWidget(self.format)
        self.layout.addLayout(hbox, 3, 1, Qt.AlignmentFlag.AlignHCenter)

        format_rect = self.layout.cellRect(3, 2)
        format_rect.moveLeft(10)

        title_label = QLabel("Title")
        self.title = QLineEdit()
        self.layout.addWidget(title_label, 4, 0)
        self.layout.addWidget(self.title, 5, 0)

        mediatype_label = QLabel("Media Type")
        self.mediatype = QLineEdit()
        self.layout.addWidget(mediatype_label, 4, 1)
        self.layout.addWidget(self.mediatype, 5, 1)

        description_label = QLabel("Description")
        self.description = QLineEdit()
        self.layout.addWidget(description_label, 6, 0)
        self.layout.addWidget(self.description, 7, 0)

        encoding_label = QLabel("Encoding")
        self.encoding = QLineEdit()
        self.layout.addWidget(encoding_label, 6, 1)
        self.layout.addWidget(self.encoding, 7, 1)

        self.form_layout.addStretch()
        self.setLayout(self.form_layout)

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



class ResourceTab(QWidget):
    def __init__(self, **kwargs):
        super().__init__()

        self.page = self.tr("Resource")

        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)

        self.buttonlayout = QVBoxLayout()
        self.buttonlayout.setSpacing(10)
        self.forms = QStackedLayout()

        self.mainlayout.addLayout(self.buttonlayout)
        self.mainlayout.addLayout(self.forms)

        self.buttonlayout.setContentsMargins(30, 40, 50, 0)

        self.default_button = QPushButton("Default")
        self.resource_form = ResourceForm()
        self.buttonlayout.addWidget(self.default_button)
        self.default_button.clicked.connect(self.switch_form)
        self.forms.addWidget(self.resource_form)

        self.integrity_button = QPushButton("Integrity")
        self.integrity_form = IntegrityForm()
        self.buttonlayout.addWidget(self.integrity_button)
        self.integrity_button.clicked.connect(self.switch_form)
        self.forms.addWidget(self.integrity_form)

        self.licenses_button = QPushButton("Licenses")
        self.licenses_form = LicensesForm()
        self.buttonlayout.addWidget(self.licenses_button)
        self.licenses_button.clicked.connect(self.switch_form)
        self.forms.addWidget(self.licenses_form)

        self.contributors_button = QPushButton("Contributors")
        #self.contributors_form = ContributorsForm()
        self.buttonlayout.addWidget(self.contributors_button)
        self.contributors_button.clicked.connect(self.switch_form)
        #self.forms.addWidget(self.contributors_form)

        self.sources_button = QPushButton("Sources")
        #self.sources_form = SourcesForm()
        self.buttonlayout.addWidget(self.sources_button)
        self.sources_button.clicked.connect(self.switch_form)
        #self.forms.addWidget(self.sources_form)

        self.buttonlayout.addStretch()
        self.setStyleSheet(stylesheet)

    def get_forms(self):
        return [
                self.resource_form,
                self.integrity_form,
                self.licenses_form
        ]

    def switch_form(self):
        """Set the index of the Forms Stacked Layout to match the selected form."""
        # This order is the order in which we add the forms to the stacked layout in the
        # __init__ method. We could implement something more fancy but life is too short
        # to make complex stuff.
        button = self.sender().text()

        if button == "Default":
            self.forms.setCurrentWidget(self.resource_form)
        if button == "Integrity":
            self.forms.setCurrentWidget(self.integrity_form)
        if button == "Licenses":
            self.forms.setCurrentWidget(self.licenses_form)


class DialectTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page = self.tr("Dialect")

        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)

        self.buttonlayout = QVBoxLayout()
        self.forms = QStackedLayout()
        self.mainlayout.addLayout(self.buttonlayout)
        self.mainlayout.addLayout(self.forms)

        self.buttonlayout.setContentsMargins(30, 40, 50, 0)
        self.buttonlayout.setSpacing(10)

        self.default_button = QPushButton("Default")
        #self.default_form = DialectForm()
        self.buttonlayout.addWidget(self.default_button)
        self.default_button.clicked.connect(self.switch_form)
        #self.forms.addWidget(self.default_form)

        self.csv_button = QPushButton("Csv")
        #self.csv_form = CsvForm()
        self.buttonlayout.addWidget(self.csv_button)
        self.csv_button.clicked.connect(self.switch_form)
        #self.forms.addWidget(self.csv_form)

        self.buttonlayout.addStretch()
        self.setStyleSheet(stylesheet)

    def get_forms(self):
        # Add csv_form when it's available
        #return [self.default_form]
        return []

    def switch_form(self):
        """Set the index of the Forms Stacked Layout to match the selected form."""
        # This order is the order in which we add the forms to the stacked layout in the
        # __init__ method. We could implement something more fancy but life is too short
        # to make complex stuff.
        pass
       # button = self.sender().text()

       # if button == "Default":
       #     self.forms.setCurrentWidget(self.default_form)
       # if button == "Integrity":
       #     self.forms.setCurrentWidget(self.integrity_form)
       # if button == "Licenses":
       #     self.forms.setCurrentWidget(self.licenses_form)


class SchemaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.page = self.tr("Schema")

        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)

        self.buttonlayout = QVBoxLayout()
        self.forms = QStackedLayout()
        self.mainlayout.addLayout(self.buttonlayout)
        self.mainlayout.addLayout(self.forms)

        self.buttonlayout.setContentsMargins(30, 40, 50, 0)
        self.buttonlayout.setSpacing(10)

        self.default_button = QPushButton("Default")
        self.default_form = SchemaForm()

        self.forms.addWidget(self.default_form)
        self.buttonlayout.addWidget(self.default_button)
        self.default_button.clicked.connect(self.switch_form)

        self.fields_button =  QPushButton("Fields")
        self.fields_form = FieldsForm()
        self.fields_button.clicked.connect(self.switch_form)
        self.buttonlayout.addWidget(self.fields_button)
        self.forms.addWidget(self.fields_form)

        self.foreign_keys_button =  QPushButton("Foreign Keys")
        #self.foreign_keys_form = ForeignKeysForm()
        self.foreign_keys_button.clicked.connect(self.switch_form)
        self.buttonlayout.addWidget(self.foreign_keys_button)
        #self.forms.addWidget(self.foreign_keys_form)

        self.buttonlayout.addStretch()
        self.setStyleSheet(stylesheet)

    def get_forms(self):
        # Add other forms when they're available
        return [self.default_form, self.fields_form]

    def switch_form(self):
        """Set the index of the Forms Stacked Layout to match the selected form."""
        # This order is the order in which we add the forms to the stacked layout in the
        # __init__ method. We could implement something more fancy but life is too short
        # to make complex stuff.
        button = self.sender().text()

        if button == "Default":
            self.forms.setCurrentWidget(self.default_form)
        if button == "Fields":
            self.forms.setCurrentWidget(self.fields_form)
        #if button == "Licenses":
        #    self.forms.setCurrentWidget(self.licenses_form)
