from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QTableView


class ErrorTitle(QWidget):
    """Widget to display the error type and count."""

    def __init__(self, title, count):
        super().__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(title)
        errors = QLabel(str(count), objectName="errors")

        layout.addWidget(title)
        layout.addWidget(errors)
        layout.addStretch()

        self.setLayout(layout)

        self.setStyleSheet("""
            QLabel#errors {
              background: red;
              color: #FFF;
              padding: 2px 2px;
              border-style: outset;
              border-width: 1px;
              border-radius: 4px;
              border-color: red;
            }
        """)


class ErrorReport(QWidget):
    """Widget to show errors detected by frictionless.

    This widget will be use in the Errors view for every type of error that
    frictionless validate finds. It display the title, description and table
    preview for a specific type of error.

    The error argument is a list of Frictionless errors object of the same type
    of error.
    """

    def __init__(self, errors, model, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = ErrorTitle(errors[0].title, len(errors))
        self.description = QLabel(errors[0].description)
        font = self.description.font()
        font.setPointSize(12)
        self.description.setFont(font)
        self.description.setWordWrap(True)

        self.table = QTableView()
        self.table.setModel(model)

        # Since we are reusing the FrictionlessTableModel lets display only
        # the rows with errors by hiding all rows without errors.
        rowsWithErrors = [self._get_error_row_number(e) for e in errors]
        totalRows = range(model.rowCount())
        rowsToHide = list(set(totalRows) - set(rowsWithErrors))
        for row_number in rowsToHide:
            self.table.hideRow(row_number)

        vbox = QVBoxLayout()
        vbox.addWidget(self.title)
        vbox.addWidget(self.description)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def _get_error_row_number(self, error):
        """Return the row number from the Error object

        Errors objects in frictionless-py do not have a consistent API. This method
        encapsulates the logic to retrieve them. It also moves from 1-index to 0-index.
        """
        if error.type == 'blank-label':
            result = error.row_numbers[0] - 1
        elif error.type == 'source-error':
            # SourceError means file cannot be read. We do not display a table.
            result = 0
        else:
            result = error.row_number - 1
        return result


class ErrorsWidget(QWidget):
    """ Widget to dynamically show errors reports. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QVBoxLayout()

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    def add_error(self, errors, model):
        """Adds a single ErrorReport to the widget.

        This method should be called when reading and validating a
        tabular file. It is currently triggered when the user clicks on
        a file in the FileTreeNavigator
        """
        errorReport = ErrorReport(errors, model)
        self.layout.addWidget(errorReport)

    def remove_all_errors(self):
        """" Removes all the ErrorReports that have been added to this widget. """
        while (self.layout.count() != 0):
            errorReport = self.layout.takeAt(0)
            errorReport.widget().deleteLater()

    def retranslateUI(self):
        self.label.setText(self.tr("No errors to show."))
