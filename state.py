import random
from enum import Enum

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
    BIRD_COUNT = 2

    def __init__(self, images: ImageResources, sounds: SoundResource):
        # Resources
        self.images = images
        self.sounds = sounds
        # Vars
        self.score = 0
        self.upper_pipes = []
        self.lower_pipes = []
        self.initialize()
        # Constants
        self.pipe_height = images.pipe[0].get_height()
        # Bird
        self.birds = [Bird(self, BirdParam(BirdParam.Type.SELF)), Bird(self, BirdParam(BirdParam.Type.KEYBOARD))]
        self.alive_bird_count = State.BIRD_COUNT


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

    def record_score(self, score):
        self.score = max(self.score, score)

    def a_bird_die(self):
        self.alive_bird_count -= 1

    def add_random_pipe(self, x=0):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gap_y = random.randrange(0, int(State.BASE_Y * 0.6 - State.PIPE_GAP_SIZE))
        gap_y += int(State.BASE_Y * 0.2)

        pipe_x = (State.SCREEN_WIDTH + 10) if x == 0 else x
        self.upper_pipes.append({'x': pipe_x, 'y': gap_y - self.pipe_height})
        self.lower_pipes.append({'x': pipe_x, 'y': gap_y + State.PIPE_GAP_SIZE})


class BirdParam:

    class Type(Enum):
        KEYBOARD = 1
        SELF = 2

    def __init__(self, type: Type):
        self.type = type


class Bird:
    # down is positive, up is negative
    FLAP_ACC = -9
    ACCELERATION_Y = 1
    VELOCITY_Y_MAX = 10
    ROTATION_SPEED = 3
    HEIGHT = 24

    def __init__(self, state: State, param: BirdParam):
        self.height_limit = -2 * state.images.player[0].get_height()
        self.game_state = state
        self.param = param
        # Location related
        self.x = int(State.SCREEN_WIDTH * 0.2)
        self.y = 0
        self.rotation = 45
        self.velocity_y = -9
        # If bird flapped in current frame
        self.flapped = False
        # Score
        self.score = 0
        self.dead = False
        # Keyboard flap parameter for testing only!
        self.keyboard_flap = False

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_velocity_y(self):
        return self.velocity_y

    def is_dead(self):
        return self.dead

    # gets call every frame
    def run(self):
        if self.param.type is BirdParam.Type.SELF:
            self.stupid_reflex_agent()
        elif self.param.type is BirdParam.Type.KEYBOARD:
            self.keyboard_bird()
        # Refresh
        self.refresh_location()

    # A very very simple reflex agent to automatically flap
    def stupid_reflex_agent(self):
        offset_allowance = 35
        pipe_index = 1 if self.game_state.upper_pipes[0]['x'] < self.x - 40 else 0
        y_upper = self.game_state.upper_pipes[pipe_index]['y'] + offset_allowance
        y_lower = self.game_state.lower_pipes[pipe_index]['y'] - offset_allowance

        if self.y >= y_lower:
            # self.log("Agent flap")
            self.flap()

    def keyboard_bird(self):
        # Flap?
        if self.keyboard_flap:
            self.flap()
            self.keyboard_flap = False

    # When a bird hit the pipe, this function will be called
    def die(self):
        print("this bird died")
        self.dead = True
        self.game_state.a_bird_die()

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
        self.y += min(self.velocity_y, int(State.BASE_Y - self.y - Bird.HEIGHT))
        # Flap update
        if self.flapped:
            self.rotation = 45
            self.flapped = False

    def log(self, msg):
        print("[Bird] %s" % msg)

    def increase_score(self):
        self.score += 1
        self.game_state.record_score(self.score)
