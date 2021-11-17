import sys
import pygame
import random

PATH_PREFIX_IMG = "assets/sprites"
PATH_PREFIX_SOUND = "assets/audio"

# list of backgrounds
BACKGROUNDS_LIST = (
    '%s/background-day.png' % PATH_PREFIX_IMG,
    '%s/background-night.png' % PATH_PREFIX_IMG,
)

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        '%s/redbird-upflap.png' % PATH_PREFIX_IMG,
        '%s/redbird-midflap.png' % PATH_PREFIX_IMG,
        '%s/redbird-downflap.png' % PATH_PREFIX_IMG,
    ),
    # blue bird
    (
        '%s/bluebird-upflap.png' % PATH_PREFIX_IMG,
        '%s/bluebird-midflap.png' % PATH_PREFIX_IMG,
        '%s/bluebird-downflap.png' % PATH_PREFIX_IMG,
    ),
    # yellow bird
    (
        '%s/yellowbird-upflap.png' % PATH_PREFIX_IMG,
        '%s/yellowbird-midflap.png' % PATH_PREFIX_IMG,
        '%s/yellowbird-downflap.png' % PATH_PREFIX_IMG,
    ),
)

# list of pipes
PIPES_LIST = (
    '%s/pipe-green.png' % PATH_PREFIX_IMG,
    '%s/pipe-red.png' % PATH_PREFIX_IMG,
)


class ImageResources:

    def __init__(self):
        # numbers sprites for score display
        self.numbers = []
        for number in range(0, 10):
            path = "%s/%d.png" % (PATH_PREFIX_IMG, number)
            self.numbers.append(pygame.image.load(path).convert_alpha())

        # game over sprite
        self.game_over = pygame.image.load("%s/gameover.png" % PATH_PREFIX_IMG).convert_alpha()

        # message sprite for welcome screen
        self.message = pygame.image.load("%s/message.png" % PATH_PREFIX_IMG).convert_alpha()

        # base (ground) sprite
        self.base = pygame.image.load("%s/base.png" % PATH_PREFIX_IMG).convert_alpha()

        # Initialize a random background
        self.random_background()

        # select random player sprites
        self.random_player()

        # select random pipe
        self.random_pipe()

    def get_number(self, number):
        return self.numbers[number]

    def random_background(self):
        self.background = pygame.image.load(random.choice(BACKGROUNDS_LIST)).convert()

    def random_player(self):
        random_player = random.choice(PLAYERS_LIST)
        self.player = (
            pygame.image.load(random_player[0]).convert_alpha(),
            pygame.image.load(random_player[1]).convert_alpha(),
            pygame.image.load(random_player[2]).convert_alpha(),
        )

    def random_pipe(self):
        random_pipe_img = random.choice(PIPES_LIST)
        self.pipe = (
            pygame.transform.flip(pygame.image.load(random_pipe_img).convert_alpha(), False, True),
            pygame.image.load(random_pipe_img).convert_alpha(),
        )


class SoundResource:

    def __init__(self):

        ext = '.wav' if 'win' in sys.platform else '.ogg'

        self.die = pygame.mixer.Sound('%s/die%s' % (PATH_PREFIX_SOUND, ext))

        self.hit = pygame.mixer.Sound('%s/hit%s'% (PATH_PREFIX_SOUND, ext))

        self.point = pygame.mixer.Sound('%s/point%s' % (PATH_PREFIX_SOUND, ext))

        self.swoosh = pygame.mixer.Sound('%s/swoosh%s' % (PATH_PREFIX_SOUND, ext))

        self.wing = pygame.mixer.Sound('%s/wing%s' % (PATH_PREFIX_SOUND, ext))

