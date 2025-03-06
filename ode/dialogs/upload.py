import os
import re
import sys
import shutil

from frictionless.resources import FileResource, TableResource

from PySide6.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
        QLabel, QFileDialog, QDialog, QTabWidget, QLineEdit
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ode.paths import Paths


class SelectWidget(QWidget):
    """Widget to render the File/Folder upload buttons."""
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        icon_label = QLabel(self)
        pixmap = QPixmap(icon_path)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label)

        self.select_button = QPushButton()
        layout.addWidget(self.select_button)

        self.setLayout(layout)

    def connect_select_action(self, action):
        self.select_button.clicked.connect(action)


class DataUploadDialog(QDialog):
    """Dialog to Upload File, Folders or URLs.

    The goal of this Dialog is to have an intuitive UX for people to add
    files, folders or URLs. For external URLs we rely on frictionless's
    TableResource to read and write tables hosted in the web or Google
    Spreadsheets.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(500)
        self.setFixedWidth(500)

        main_layout = QVBoxLayout()

        # Centered Image
        image_label = QLabel(self)
        image_label.setFixedHeight(200)
        pixmap = QPixmap(Paths.asset("images/dialog_upload_files.png"))
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(image_label)

        # Tab Widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # From Your Computer Tab
        from_computer_tab = QWidget()
        from_computer_layout = QHBoxLayout()
        from_computer_tab.setLayout(from_computer_layout)

        self.file_select_widget = SelectWidget(Paths.asset("icons/upload-file.png"))
        self.file_select_widget.connect_select_action(self.add_files)
        self.folder_select_widget = SelectWidget(Paths.asset("icons/upload-folder.png"))
        self.folder_select_widget.connect_select_action(self.add_folders)

        from_computer_layout.addWidget(self.file_select_widget)
        from_computer_layout.addWidget(self.folder_select_widget)

        # Add External Data Tab
        external_data_tab = QWidget()
        external_data_layout = QVBoxLayout()
        external_data_tab.setLayout(external_data_layout)

        self.url_label = QLabel()
        self.url_input = QLineEdit()
        self.help_text = QLabel()
        self.help_text.setWordWrap(True)
        self.help_text.setStyleSheet("font-style:italic; font-size: 15px;")
        self.paste_button = QPushButton()
        self.paste_button.clicked.connect(self.load_table_from_url)
        self.error_text = QLabel()
        self.error_text.setWordWrap(True)
        self.error_text.setStyleSheet("color: red; font-style: italic; font-size: 15px;")

        external_data_layout.addWidget(self.url_label)
        external_data_layout.addWidget(self.url_input)
        external_data_layout.addWidget(self.help_text)
        external_data_layout.addWidget(self.paste_button)
        external_data_layout.addWidget(self.error_text)

        # Add Tabs to Tab Widget
        self.tab_widget.addTab(from_computer_tab, "")
        self.tab_widget.addTab(external_data_tab, "")

        self.setLayout(main_layout)

        self.retranslateUI()

    def add_files(self):
        """Copy the selected file to the project path."""
        filters = [
                "All supported files (*.csv *.xlsx *.xls)",
                "Comma Separated Values (*.csv)",
                "Excel 2007-365 (*.xlsx)",
                "Excel 97-2003 (*.xls)",
        ]
        filename, _ = QFileDialog.getOpenFileName(self, filter=";;".join(filters))

        if not filename:
            return

        destination_filepath = Paths.get_unique_destination_filepath(filename)
        shutil.copy(filename, destination_filepath)
        self.accept()

    def add_folders(self):
        """Copy the selected folder and all its content to the project path."""
        source_folder = QFileDialog.getExistingDirectory(self)
        if source_folder:
            folder_name = os.path.basename(source_folder)
            target_folder = os.path.join(Paths.PROJECT_PATH, folder_name)
            shutil.copytree(source_folder, target_folder, dirs_exist_ok=True)
        self.accept()

    def load_table_from_url(self):
        """Load a tabular file from a public URL.

        This method uses frictionless to read a remote URL. Currently we support
        Google Spreadsheets and any other URL pointing to a csv file.
        """
        url = self.url_input.text()
        if not url:
            self.error_text.setText(self.tr("Please paste a valid URL."))
            return
        if not url.startswith(("http://", "https://")):
            self.error_text.setText(self.tr("Please paste a valid URL starting with http:// or https://."))
            return

        table = TableResource(path=url)
        filename = table.name
        if table.format == "gsheets":
            filename = self._read_url_html_title(url)

        destination_filepath = Paths.get_unique_destination_filepath(filename + ".csv")

        try:
            with open(destination_filepath, mode='w') as file:
                table.write(file.name)
            self.accept()
        except Exception:
            error = self.tr("Error: The URL is not associated with a table")
            self.error_text.setText(error)

    def reject(self):
        """Overrides class method to reset the forms when the user close the dialog."""
        self._reset_forms()
        super().reject()

    def accept(self):
        """Override class method to reset forms when successfully uploading a file."""
        self._reset_forms()
        super().accept()

    def _reset_forms(self):
        """Reset inputs and selected tab to initial status.

        We should ensure that everytime the user opens the dialog the state is the initial one.
        """
        self.url_input.setText("")
        self.error_text.setText("")
        self.tab_widget.setCurrentIndex(0)

    def _read_url_html_title(self, url):
        """ Return the title of HTML document.

        We use the `title` attribute of the Google Spreadshet's HTML as name of the file.
        This attribute is the same as the name of the spreadsheet.
        """
        file = FileResource(path=url)
        text = file.read_text(size=10000)
        match = re.search(r"<title>(.*?)</title>", text)
        if match:
            title = match.group(1)
            title = title.rsplit("- Google", 1)[0].strip()
            return f"{title}"
        return "google-sheets"

    def retranslateUI(self):
        """Apply translations to class elements."""
        self.setWindowTitle(self.tr("Upload your data"))
        self.file_select_widget.text_label.setText(self.tr("Add one or more Excel or csv files"))
        self.folder_select_widget.text_label.setText(self.tr("Add one or more folders"))
        self.file_select_widget.select_button.setText(self.tr("Select"))
        self.folder_select_widget.select_button.setText(self.tr("Select"))
        self.url_label.setText(self.tr("Link to the external table: "))
        self.url_input.setPlaceholderText(self.tr("Enter or paste URL"))
        self.help_text.setText(self.tr("Here you can paste links from public Google Sheets and urls from csv files in open data portals and GitHub."))
        self.paste_button.setText(self.tr("Add"))
        self.tab_widget.setTabText(0, self.tr("From Your Computer"))
        self.tab_widget.setTabText(1, self.tr("Add External Data"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = DataUploadDialog()
    dialog.exec()
    sys.exit(app.exec())
