import sys

from PySide2 import QtWidgets

from widget import GrapherWidget

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    grapher = GrapherWidget()
    grapher.resize(800, 600)
    grapher.show()
    grapher.activateWindow()
    grapher.raise_()

    sys.exit(app.exec_())
