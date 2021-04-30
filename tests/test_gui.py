from qt_func_grapher.widget import GrapherWidget


class TestInputValidation:
    def test_error_reporting(self, qtbot):
        window = GrapherWidget()
        window.resize(800, 600)
        window.show()
        window.activateWindow()

        qtbot.addWidget(window)

        window.from_line_edit.clear()
        qtbot.keyClicks(window.from_line_edit, "not a number")

        assert window.error_label.text() == "lower_limit is not a valid number"
