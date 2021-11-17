import random

import pygame
from resources import ImageResources, SoundResource
from pygame.locals import *


class State:
    # Constants
    FPS = 30
    SCREEN_WIDTH = 288
    SCREEN_HEIGHT = 512
    PIPE_GAP_SIZE = 100  # gap between upper and lower part of pipe
    BASE_Y = SCREEN_HEIGHT * 0.79

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
        # Constants
        self.pipe_height = images.pipe[0].get_height()

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

    def add_random_pipe(self, x=0):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gap_y = random.randrange(0, int(State.BASE_Y * 0.6 - State.PIPE_GAP_SIZE))
        gap_y += int(State.BASE_Y * 0.2)

        pipe_x = (State.SCREEN_WIDTH + 10) if x == 0 else x
        self.upper_pipes.append({'x': pipe_x, 'y': gap_y - self.pipe_height})
        self.lower_pipes.append({'x': pipe_x, 'y': gap_y + State.PIPE_GAP_SIZE})


class Bird:
    # down is positive, up is negative
    FLAP_ACC = -9
    ACCELERATION_Y = 1
    VELOCITY_Y_MAX = 10
    ROTATION_SPEED = 3

    def __init__(self, state: State):
        self.height_limit = -2 * state.images.player[0].get_height()
        self.game_state = state
        # Location related
        self.x = int(State.SCREEN_WIDTH * 0.2)
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
        self.simple_reflex_agent()
        # Refresh
        self.refresh_location()

    # A simple reflex agent to automatically flap
    def simple_reflex_agent(self):
        offset_allowance = 35
        pipe_index = 1 if self.game_state.upper_pipes[0]['x'] < self.x - 35 else 0
        y_upper = self.game_state.upper_pipes[pipe_index]['y'] + offset_allowance
        y_lower = self.game_state.lower_pipes[pipe_index]['y'] - offset_allowance

        if self.y >= y_lower:
            # self.log("Agent flap")
            self.flap()


    def keyboard_bird(self):
        # Flap?
        for event in pygame.event.get():
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                self.flap()

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

    def log(self, msg):
        print("[Bird] %s" % msg)
