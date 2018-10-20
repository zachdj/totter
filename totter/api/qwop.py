""" API to load and play games of QWOP """

import webview
import pyautogui
import time
import threading


# constants
_QWOP_URL = "http://foddy.net/Athletics.html?webgl=true"  # Note that it should be the HTML version
_QWOP_HEIGHT = 450
_QWOP_WIDTH = 700


def _open_qwop_window():
    webview.create_window(title="Totter QWOP Instance",
                          url="http://foddy.net/Athletics.html?webgl=true",
                          width=_QWOP_WIDTH,
                          height=_QWOP_HEIGHT,
                          resizable=False)


class QwopRunner:
    def __init__(self, input_delay=10):
        """ Initialize a QwopRunner

        Args:
            input_delay (int): delay in milliseconds before the key_mask will change
        """

        self.input_delay = input_delay * 0.001  # convert ms to seconds
        self._qwop_thread = None
        self.started = False
        self.q_pressed = False
        self.w_pressed = False
        self.o_pressed = False
        self.p_pressed = False

    def start(self):
        # spin up a webview with QWOP
        _qwop_thread = threading.Thread(target=_open_qwop_window)
        _qwop_thread.start()
        self._qwop_thread = _qwop_thread

        # wait until the game has (probably) loaded
        time.sleep(4)
        # the qwop window will always be in the center of the primary monitor
        screen_width, screen_height = pyautogui.size()
        # correct for double-monitor setup
        if screen_width > 1920:
            screen_width = screen_width // 2
        # move the mouse to the qwop window, and click to start the game
        pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=0.25)
        pyautogui.click()
        self.started = True

        # apply the initial key_mask
        self.set_key_mask(q=self.q_pressed, w=self.w_pressed, o=self.o_pressed, p=self.p_pressed)

    def stop(self):
        self.set_key_mask(q=False, w=False, o=False, p=False)
        self.started = False
        webview.destroy_window()
        self._qwop_thread.join()

    def set_key_mask(self, q=False, w=False, o=False, p=False):
        """ Sets which keys are currently down

        Delays between key_mask setting are controlled by the `input_delay` parameter

        Args:
            q (bool): True if q should be pressed
            w (bool): True if w should be pressed
            o (bool): True if o should be pressed
            p (bool): True if p should be pressed

        Returns: None

        """
        time.sleep(self.input_delay)
        if self.started:
            # press the keys that need to be pressed
            if q and not self.q_pressed:
                pyautogui.keyDown('q')
            if w and not self.w_pressed:
                pyautogui.keyDown('w')
            if o and not self.o_pressed:
                pyautogui.keyDown('o')
            if p and not self.p_pressed:
                pyautogui.keyDown('p')

            # release the keys that need to be released
            if not q and self.q_pressed:
                pyautogui.keyUp('q')
            if not w and self.w_pressed:
                pyautogui.keyUp('w')
            if not o and self.o_pressed:
                pyautogui.keyUp('o')
            if not p and self.p_pressed:
                pyautogui.keyUp('p')

        # update the masks
        self.q_pressed = q
        self.w_pressed = w
        self.o_pressed = o
        self.p_pressed = p
