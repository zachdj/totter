""" Functions to process QWOP images and extract game information """

import collections
import pytesseract

# colors will be considered identical if the Euclidean distance between them is less than this epsilon
_COLOR_EQUALITY_EPSILON = 5
_GOLD_MEDAL_POSITION = (180, 235)  # position of the gold ribbon in the game-over screen
_GOLD_MEDAL_COLOR = (255, 255, 0)  # color in the center of the gold ribbon in the game over screen

# box for the current distance measure at the top of the window
_CURRENT_DISTANCE_BOX = (225, 125, 460, 160)  # left, upper, right, lower
# box for the text in the game-over box
_FINAL_DISTANCE_BOX = (200, 255, 481, 387)


def _colors_equal(color1, color2):
    sq_distance = 0
    for idx, val in enumerate(color1):
        sq_distance += (val - color2[idx])**2

    return sq_distance < _COLOR_EQUALITY_EPSILON**2


class ImageProcessor(object):
    def __init__(self, buffer_size=0):
        """ Initialize an ImageProcessor

        `ImageProcessor`s analyze QWOP screenshots and use visual features to determine how far the player has run
        and if the game has ended.

        The game ends if the game-over screen appears, or if the distance achieved has stayed the same for the last
         `buffer_size` frames.

        Args:
            buffer_size (int):
                number of identical-distance frames before game_over becomes true.
                If this is zero, then the stagnation check will not be performed.
        """
        self.latest = None
        self.current_distance = 0
        self.game_over = False
        self.buffer_size = buffer_size
        self.historical_distances = collections.deque(maxlen=buffer_size)

    def reset(self):
        self.latest = None
        self.current_distance = 0
        self.game_over = False

    def update(self, screenshot):
        self.latest = screenshot
        # determine distance run so far
        distance_screenshot = screenshot.crop(_CURRENT_DISTANCE_BOX).convert(mode='L')  # convert to greyscale
        distance_text = pytesseract.image_to_string(distance_screenshot)  # should be something like 'x metres'
        tokens = distance_text.split()
        if len(tokens) > 1:
            try:
                self.current_distance = float(tokens[0])  # try to parse the first token as a number
                self.historical_distances.append(self.current_distance)
            except ValueError:
                pass

        # determine if the game is over
        # check if the game over screen is up
        self.game_over = _colors_equal(self.latest.getpixel(_GOLD_MEDAL_POSITION), _GOLD_MEDAL_COLOR)
        # check if the game has "stagnated" (distance hasn't changed in the last buffer_size checks)
        if 0 < self.buffer_size <= len(self.historical_distances):
            self.game_over = all(dist == self.historical_distances[0] for dist in self.historical_distances) or self.game_over

    def is_game_over(self):
        return self.game_over

    def get_final_distance(self):
        text_screenshot = self.latest.crop(_FINAL_DISTANCE_BOX).convert(mode='L')
        # filter out everything except the distance text (which is pure white)
        text_screenshot = text_screenshot.point(lambda pixel: 0 if _colors_equal((pixel,), (255, )) else 255)
        text = pytesseract.image_to_string(text_screenshot)
        tokens = text.split()
        try:
            distance_value_idx = tokens.index('metres') - 1  # the distance will preceed the word 'metres'
            distance = float(tokens[distance_value_idx])
            # detect if there's a serious mismatch between observed and final distances
            # this helps make the distance-finding mechanism robust against tesseract errors
            if abs(distance - self.current_distance) > 1:
                return min(distance, self.current_distance)
            else:
                return distance
        except ValueError:
            # 'metres' not found in the list of tokens.  Defer to top-of-window distance
            return self.current_distance


