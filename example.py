import sys

try:
    from .PyWebWinUI3 import MainWindow, loadPage, Notice
except ImportError:
    from PyWebWinUI3 import MainWindow, loadPage, Notice

if __name__ == "__main__":
    # app = MainWindow("PyWebWinUI3", "http://localhost:3000/#dashboard", "debug" in sys.argv)
    app = MainWindow("PyWebWinUI3", "./PyWebWinUI3/FrontEnd/dist/index.html#dashboard", "debug" in sys.argv)

    app.addSettings(loadPage("Settings.xaml"))
    app.addPage(loadPage("Dashboard.xaml"))
    app.addPage(loadPage("Test.xaml"))

    app.setValue("system.version", "1.0.0")
    app.setValue("system.latest", "1.0.0")

    app.setValue("test.textType", "default")
    app.setValue("test.textContent", "This is Text With URL")
    app.setValue("test.textUrl", "https://haruna5718.dev")

    app.setValue("test.inputType", "text")
    app.setValue("test.InputText", "Input")
    app.setValue("test.input", "This is Input")

    app.setValue("test.buttonType", "click")
    app.setValue("test.buttonUrl", "https://haruna5718.dev")
    app.setValue("test.button", False)

    app.setValue("test.selectText", "Select")
    app.setValue("test.select", "option1")

    app.setValue("test.sliderType", "horizontal")
    app.setValue("test.slider", 20)

    app.setValue("test.progress", 20)
    app.setValue("test.progressType", "progress")

    app.setValue("test.switchAligin", "right")
    app.setValue("test.switch", False)

    app.setValue("test.checkType", "two")
    app.setValue("test.checkAligin", "right")
    app.setValue("test.checkd", 0)

    app.setValue("test.radioAligin", "right")
    app.setValue("test.radio", "option1")

    app.setValue("test.image", "https://crac.kro.kr/Haruna.png")

    app.setValue("test.webview", "https://crac.kro.kr")

    app.setValue("test.if", True)

    app.setValue("test.repeat", 3)

    app.setValue("test.state", Notice.Attention)
    app.setValue("test.badge", 1)

    app.setValue("test.noticeType", Notice.Information)
    app.setValue("test.noticeTitle", "Title")
    app.setValue("test.noticeDescription", "Description")

    app.events["setValue"].append(["test.noticeCreate",lambda k,v: app.notice(app.values["test.noticeType"],app.values["test.noticeTitle"],app.values["test.noticeDescription"])])
    app.events["setValue"].append(["test.noticeSample",lambda k,v: app.notice(Notice.Information,"Title","This is sample information notice")])
    app.events["setValue"].append(["test.noticeSample",lambda k,v: app.notice(Notice.Success,"Title","This is sample success notice")])
    app.events["setValue"].append(["test.noticeSample",lambda k,v: app.notice(Notice.Warning,"Title","This is sample warning notice")])
    app.events["setValue"].append(["test.noticeSample",lambda k,v: app.notice(Notice.Error,"Title","This is sample error notice")])

    app.start()