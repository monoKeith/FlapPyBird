import pygame
from resources import ImageResources, SoundResource
from pygame.locals import *


class Bird:
    # down is positive, up is negative
    FLAP_ACC = -9
    ACCELERATION_Y = 1
    VELOCITY_Y_MAX = 10
    ROTATION_SPEED = 3

    def __init__(self, state):
        self.height_limit = -2 * state.images.player[0].get_height()
        self.game_state = state

        # Location related
        self.x = 0
        self.y = 0
        self.rotation = 45
        self.velocity_y = -9
        # If bird flapped in current frame
        self.flapped = False

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_velocity_y(self):
        return self.velocity_y

    # gets call every frame
    def run(self):
        # Flap?
        for event in pygame.event.get():
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                self.flap()
        # Refresh
        self.refresh_location()

    # Flap
    def flap(self):
        if self.y > self.height_limit:
            self.game_state.sounds.wing.play()
            self.velocity_y = Bird.FLAP_ACC
            self.flapped = True

    # Update location every frame
    def refresh_location(self):
        # Rotate
        if self.rotation > -90:
            self.rotation -= Bird.ROTATION_SPEED
        # Height of bird drop
        if self.velocity_y < Bird.VELOCITY_Y_MAX and not self.flapped:
            self.velocity_y += Bird.ACCELERATION_Y
        # Flap update
        if self.flapped:
            self.rotation = 45
            self.flapped = False


class State:

    def __init__(self, images: ImageResources, sounds: SoundResource):
        # Resources
        self.images = images
        self.sounds = sounds
        # Vars
        self.score = 0
        self.upper_pipes = []
        self.lower_pipes = []
        self.initialize()
        self.bird = Bird(self)

    def initialize(self):
        # Random UI theme
        self.images.random_background()
        self.images.random_player()
        self.images.random_pipe()
        # Reset vars
        self.score = 0
        self.upper_pipes = []
        self.lower_pipes = []

    def get_score(self):
        return self.score

    def increase_score(self):
        self.score += 1
