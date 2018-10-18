""" Instance of QWOP loaded in a webview

"""

import webview

QWOP_URL = "http://foddy.net/Athletics.html?webgl=true"  # Note that it should be the HTML version


class QwopInstance:
    def __init__(self):
        pass

    def start(self):
        webview.create_window(title="Totter QWOP Instance",
                              url="http://foddy.net/Athletics.html?webgl=true",
                              width=700,
                              height=450,
                              resizable=False)
