import sys
from pathlib import Path
import logging

try:
    from ..pywebwinui3.core import MainWindow, Status
except ImportError:
    sys.path.append(str(Path(__file__).parent.parent))
    from pywebwinui3.core import MainWindow, Status

if __name__ == "__main__":
    pywebviewLogger = logging.getLogger("pywebview")
    [pywebviewLogger.removeHandler(i) for i in pywebviewLogger.handlers[:]]
    pywebviewLogger.setLevel(logging.NOTSET)
    pywebviewLogger.propagate = True

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s | %(asctime)s | %(name)-30s | %(message)s",
        datefmt="%H:%M:%S"
    )

    app = MainWindow("PyWebWinUI3")

    app.addSettings("Settings.xaml")
    app.addPage("Dashboard.xaml")
    app.addPage("test.xaml")

    app.values["test_disabled"] = False

    app.values["test_textType"] = "default"
    app.values["test_textContent"] = "This is Text With URL"
    app.values["test_textUrl"] = "https://haruna5718.dev"

    app.values["test_inputType"] = "text"
    app.values["test_InputText"] = "Input"
    app.values["test_input"] = "This is Input"

    app.values["test_buttonType"] = "click"
    app.values["test_buttonUrl"] = "https://haruna5718.dev"
    app.values["test_button"] = False

    app.values["test_selectText"] = "Select"
    app.values["test_select"] = "option1"

    app.values["test_sliderType"] = "horizontal"
    app.values["test_slider"] = 20

    app.values["test_progress"] = 20
    app.values["test_progressType"] = "progress"

    app.values["test_switchAlign"] = "right"
    app.values["test_switch"] = False

    app.values["test_checkType"] = "two"
    app.values["test_checkAlign"] = "right"
    app.values["test_checkd"] = 0

    app.values["test_radioAlign"] = "right"
    app.values["test_radio"] = "option1"

    app.values["test_image"] = "https://crac.kro.kr/Haruna.png"

    app.values["test_webview"] = "https://crac.kro.kr"

    app.values["test_if"] = True

    app.values["test_repeat"] = 3

    app.values["test_state"] = ""
    app.values["test_badge"] = 1

    app.values["test_noticeType"] = Status.Attention
    app.values["test_noticeTitle"] = "Title"
    app.values["test_noticeDescription"] = "Description"

    @app.onValueChange("test_noticeSample")
    def notiveSample(*_):
        app.notice(Status.Attention,"Title","This is sample information notice")
        app.notice(Status.Success,"Title","This is sample success notice")
        app.notice(Status.Caution,"Title","This is sample warning notice")
        app.notice(Status.Critical,"Title","This is sample error notice")

    @app.onValueChange("test_noticeCreate")
    def notiveCreate(*_):
        app.notice(app.values["test_noticeType"],app.values["test_noticeTitle"],app.values["test_noticeDescription"])

    app.start("debug" in sys.argv)