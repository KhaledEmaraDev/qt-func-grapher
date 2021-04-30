import traceback

import numpy as np

from PySide2 import QtCore, QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

from arithmetic_parser import ArithmeticParser
from validator import LimitsValidator


class WorkerSignals(QtCore.QObject):
    """Defines the signals available from a running worker thread."""

    error = QtCore.Signal(tuple)
    data = QtCore.Signal(dict)


class UpdateWorker(QtCore.QRunnable):
    """
    Worker thread for calculating y points to their x counter parts

    Runs in a background thread to avoid delays in processing user events

    ...

    Attributes
    ----------
    parser : ArithmeticParser
        Parser class used to evaluate points
    x : numpy.array
        Value with which to replace the variable x

    Methods
    -------
    run()
        Do the calculations and evaluations in the background
    """

    signals = WorkerSignals()

    def __init__(self, parser, x):
        super(UpdateWorker, self).__init__()
        self.parser = parser
        self.x = x

    @QtCore.Slot()
    def run(self):
        """Do the calculations and evaluations in the background

        The output value is evaluated and signaled back the the Main Thread
        """

        try:
            y = self.parser.evaluate(self.x)

        except ValueError as err:
            self.signals.error.emit((err, traceback.format_exc()))
            return

        self.signals.data.emit(y)


class GrapherWidget(QtWidgets.QMainWindow):
    """
    Main Qt Window displaying input UI and output Graphs

    ...

    Attributes
    ----------
    func_combo_box : QComboBox
        ComboBox containing user enterd function
    from_line_edit : QLineEdit
        LineEdit containing user enterd min value
    to_line_edit : QLineEdit
        LineEdit containing user enterd max value
    error_label : QLabel
        Label displaying errors

    Methods
    -------
    refresh()
        Validate and calculate new graph points based on new input
    resultDataCallback()
        Update the graph with data from the worker thread
    notifyErrors()
        Display errors from the worker thread
    """

    def __init__(self):
        super().__init__()
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)

        # Create ComboBox for function input
        self.func_combo_box = QtWidgets.QComboBox()
        self.func_combo_box.setEditable(True)
        self.func_combo_box.addItem("x")
        self.func_combo_box.editTextChanged.connect(self.refresh)
        self._default_text_color = self.func_combo_box.palette().color(
            QtGui.QPalette.Text
        )

        # Create Label for function input
        func_label = QtWidgets.QLabel("Function:")
        func_label.setBuddy(self.func_combo_box)

        # Create LineEdit for the min value
        self.from_line_edit = QtWidgets.QLineEdit("0")
        self.from_line_edit.textChanged.connect(self.refresh)

        # Create Label for the min value
        from_label = QtWidgets.QLabel("From:")
        from_label.setBuddy(self.from_line_edit)

        # Create LineEdit for the max value
        self.to_line_edit = QtWidgets.QLineEdit("10")
        self.to_line_edit.textChanged.connect(self.refresh)

        # Create Label for the max value
        to_label = QtWidgets.QLabel("To:")
        to_label.setBuddy(self.from_line_edit)

        # Create Label for displaying errors
        self.error_label = QtWidgets.QLabel()
        self.error_label.setWordWrap(True)
        error_label_palette = self.error_label.palette()
        error_label_palette.setColor(QtGui.QPalette.Foreground, QtCore.Qt.red)
        self.error_label.setPalette(error_label_palette)

        # Create the input layout
        input_layout = QtWidgets.QGridLayout()
        input_layout.addWidget(func_label, 0, 0, 1, 2)
        input_layout.addWidget(self.func_combo_box, 1, 0, 1, 2)
        input_layout.addWidget(from_label, 2, 0)
        input_layout.addWidget(self.from_line_edit, 3, 0)
        input_layout.addWidget(to_label, 2, 1)
        input_layout.addWidget(self.to_line_edit, 3, 1)
        input_layout.addWidget(self.error_label, 4, 0, 1, 2)
        input_layout.addItem(QtWidgets.QSpacerItem(0, 0), 5, 0, 1, 2)
        input_layout.setRowStretch(5, 1)

        # Create a canvas for matplotlib
        func_figure_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.addToolBar(NavigationToolbar(func_figure_canvas, self))
        self._func_ax = func_figure_canvas.figure.subplots()
        self._func_ax.grid(b=True, which="both", axis="both")
        (self._func_line,) = self._func_ax.plot(np.zeros(0), np.zeros(0))

        # Maerge the input layout and the Canvas
        main_layout = QtWidgets.QHBoxLayout(main_widget)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(func_figure_canvas, 1)

        # Create a thread pool to run the UpdateWorker
        self._thread_pool = QtCore.QThreadPool()

        self.setWindowTitle("Master Micro Grapher")
        self.refresh()

    @QtCore.Slot()
    def refresh(self):
        """Validate and calculate new graph points based on new input"""

        # Disable redraws while updating values to avoid flicker on some
        # systems
        self.setUpdatesEnabled(False)

        # Collect user input
        func = self.func_combo_box.currentText()
        lower_limit = self.from_line_edit.text()
        upper_limit = self.to_line_edit.text()

        # Reset error state
        is_valid = True
        self.error_label.setText("")

        # Create a class to validate min and max valeus
        limit_validator = LimitsValidator(lower_limit, upper_limit)

        # Validate and parse min value
        from_palette = self.from_line_edit.palette()
        from_palette.setColor(
            QtGui.QPalette.Text,
            self._default_text_color,
        )
        try:
            lower_limit = limit_validator.parse(name="lower_limit")
        except ValueError as err:
            from_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
            self.error_label.setText(str(err))
            is_valid = False

        # Validate and parse max value
        to_palette = self.to_line_edit.palette()
        to_palette.setColor(
            QtGui.QPalette.Text,
            self._default_text_color,
        )
        try:
            upper_limit = limit_validator.parse(name="upper_limit")
        except ValueError as err:
            to_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
            self.error_label.setText(str(err))
            is_valid = False

        # Validate limits
        try:
            limit_validator.validate()
        except ValueError as err:
            from_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
            to_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
            self.error_label.setText(str(err))
            is_valid = False

        # Update text color to reflect errors
        self.from_line_edit.setPalette(from_palette)
        self.to_line_edit.setPalette(to_palette)

        # Skip calculations, because of invalid input
        if not is_valid:
            self.setUpdatesEnabled(True)
            return

        # Create a parser class for user enterd function
        arithmetic_parser = ArithmeticParser(func)
        self._x = np.linspace(lower_limit, upper_limit, 501)

        # Validate and parse user ented function as an Expression Tree
        palette = self.func_combo_box.palette()
        try:
            arithmetic_parser.parse()
            palette.setColor(
                QtGui.QPalette.Text,
                self._default_text_color,
            )
        except (SyntaxError, NameError) as err:
            palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
            self.error_label.setText(str(err))
            is_valid = False
        self.func_combo_box.setPalette(palette)

        # Skip calculations, because of invalid input
        if not is_valid:
            self.setUpdatesEnabled(True)
            return

        # Evaluate the Expression Tree in a background thread and conect it to
        # callback functions to update results and display errors
        worker = UpdateWorker(arithmetic_parser, self._x)
        worker.signals.data.connect(self.resultDataCallback)
        worker.signals.error.connect(self.notifyError)
        self._thread_pool.start(worker)

        # Re-enable redrawss
        self.setUpdatesEnabled(True)

    def resultDataCallback(self, y):
        """Update the graph with data from the worker thread"""

        self._func_line.set_data(self._x, y)
        self._func_ax.relim()
        self._func_ax.set_xlim(self._x[0], self._x[-1])
        self._func_ax.autoscale_view(scalex=False, scaley=True)
        self._func_line.figure.canvas.draw()

    def notifyError(self, error):
        """Display errors from the worker thread"""

        err, tb = error
        palette = self.func_combo_box.palette()
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.red)
        self.error_label.setText(str(err))
        self.func_combo_box.setPalette(palette)
