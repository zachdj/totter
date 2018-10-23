""" Functions to process QWOP images and extract game information

"""


def is_game_over(screenshot):
    """ Determines if the game of qwop is over using the provided screenshot

    Args:
        screenshot (Pillow.Image): image of the QWOP game

    Returns:
        bool: True if the game is over, false otherwise

    """
    screenshot.save('test.png')

    return False
