import webview

# qwop-related constants
_QWOP_URL = "http://foddy.net/Athletics.html?webgl=true"  # Note that it should be the HTML5 version
_QWOP_WIDTH = 700
_QWOP_HEIGHT = 450


def open_qwop_window():
    """ Opens a webview and loads the HTML5 version of QWOP """
    webview.create_window(title="Totter QWOP Instance", url=_QWOP_URL,
                          width=_QWOP_WIDTH, height=_QWOP_HEIGHT, resizable=False)


def close_qwop_window():
    """ Kills the open webview """
    webview.destroy_window()
