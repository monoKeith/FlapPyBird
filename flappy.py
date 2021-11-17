import pygame
import random
import sys
from state import State
from resources import ImageResources, SoundResource
from itertools import cycle
from pygame.locals import *

# Constants
FPS = 30
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
PIPE_GAP_SIZE = 100  # gap between upper and lower part of pipe
BASE_Y = SCREEN_HEIGHT * 0.79

try:
    xrange
except NameError:
    xrange = range

# Initialize Game state
state = State()

# Initialize pygame
pygame.init()
pygame.display.set_caption('Flappy Bird')
FPS_CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize resources
images = ImageResources()
sounds = SoundResource()


def get_hit_mask(image):
    """returns a hit-mask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


HIT_MASKS_PIPE = [get_hit_mask(images.pipe[i]) for i in range(2)]
HIT_MASKS_PLAYER = [get_hit_mask(images.player[i]) for i in range(3)]


def main():
    while True:
        # select random resources
        images.random_background()
        images.random_player()
        images.random_pipe()

        movement_info = show_welcome_animation()
        crash_info = main_game(movement_info)
        show_game_over_screen(crash_info)


def show_welcome_animation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    player_index = 0
    player_index_gen = cycle([0, 1, 2, 1])
    # iterator used to change player_index after every 5th iteration
    loop_iter = 0

    player_x = int(SCREEN_WIDTH * 0.2)
    player_y = int((SCREEN_HEIGHT - images.player[0].get_height()) / 2)

    message_x = int((SCREEN_WIDTH - images.message.get_width()) / 2)
    message_y = int(SCREEN_HEIGHT * 0.12)

    base_x = 0
    # amount by which base can maximum shift to left
    base_shift = images.base.get_width() - images.background.get_width()

    # player shm for up-down motion on welcome screen
    player_shm_vals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                sounds.wing.play()
                return {
                    'player_y': player_y + player_shm_vals['val'],
                    'base_x': base_x,
                    'player_index_gen': player_index_gen,
                }

        # adjust playery, player_index, base_x
        if (loop_iter + 1) % 5 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 4) % base_shift)
        player_shm(player_shm_vals)

        # draw sprites
        SCREEN.blit(images.background, (0, 0))
        SCREEN.blit(images.player[player_index], (player_x, player_y + player_shm_vals['val']))
        SCREEN.blit(images.message, (message_x, message_y))
        SCREEN.blit(images.base, (base_x, BASE_Y))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def main_game(movement_info):
    player_index = 0
    loop_iter = 0
    player_index_gen = movement_info['player_index_gen']
    player_x, state.bird.y = int(SCREEN_WIDTH * 0.2), movement_info['player_y']

    base_x = movement_info['base_x']
    base_shift = images.base.get_width() - images.background.get_width()

    # get 2 new pipes to add to upper_pipes lower_pipes list
    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    # list of upper pipes
    upper_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': new_pipe1[0]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': new_pipe2[0]['y']},
    ]

    # list of lowerpipe
    lower_pipes = [
        {'x': SCREEN_WIDTH + 200, 'y': new_pipe1[1]['y']},
        {'x': SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), 'y': new_pipe2[1]['y']},
    ]

    dt = FPS_CLOCK.tick(FPS) / 1000
    pipe_vel_x = -128 * dt

    # player velocity, max velocity, downward acceleration, acceleration on flap
    player_vel_y = -9  # player's velocity along Y, default same as player_flapped
    player_max_vel_y = 10  # max vel along Y, max descend speed
    player_min_vel_y = -8  # min vel along Y, max ascend speed
    player_acc_y = 1  # players downward acceleration
    player_rot = 45  # player's rotation
    player_vel_rot = 3  # angular speed
    player_rot_thr = 20  # rotation threshold
    player_flap_acc = -9  # players speed on flapping
    player_flapped = False  # True when player flaps

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if state.bird.get_y() > -2 * images.player[0].get_height():
                    player_vel_y = player_flap_acc
                    player_flapped = True
                    sounds.wing.play()

        # check for crash here
        crash_check = check_crash(
            {
                'x': state.bird.get_x(),
                'y': state.bird.get_y(),
                'index': player_index
            },
            upper_pipes, lower_pipes)

        if crash_check[0]:
            return {
                'y': state.bird.get_y(),
                'groundCrash': crash_check[1],
                'base_x': base_x,
                'upper_pipes': upper_pipes,
                'lower_pipes': lower_pipes,
                'score': state.score,
                'player_vel_y': player_vel_y,
                'player_rot': player_rot
            }

        # check for score
        player_mid_pos = state.bird.get_x() + images.player[0].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + images.pipe[0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                state.increase_score()
                sounds.point.play()

        # player_index base_x change
        if (loop_iter + 1) % 3 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 100) % base_shift)

        # rotate the player
        if player_rot > -90:
            player_rot -= player_vel_rot

        # player's movement
        if player_vel_y < player_max_vel_y and not player_flapped:
            player_vel_y += player_acc_y
        if player_flapped:
            player_flapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            player_rot = 45

        player_height = images.player[player_index].get_height()
        state.bird.y += min(player_vel_y, BASE_Y - state.bird.get_y() - player_height)

        # move pipes to left
        for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
            u_pipe['x'] += pipe_vel_x
            l_pipe['x'] += pipe_vel_x

        # add new pipe when first pipe is about to touch left of screen
        if 3 > len(upper_pipes) > 0 and 0 < upper_pipes[0]['x'] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # remove first pipe if its out of the screen
        if len(upper_pipes) > 0 and upper_pipes[0]['x'] < -images.pipe[0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # draw sprites
        SCREEN.blit(images.background, (0, 0))

        for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(images.pipe[0], (u_pipe['x'], u_pipe['y']))
            SCREEN.blit(images.pipe[1], (l_pipe['x'], l_pipe['y']))

        SCREEN.blit(images.base, (base_x, BASE_Y))
        # print score so player overlaps the score
        show_score(state.get_score())

        # Player rotation has a threshold
        visible_rot = player_rot_thr
        if player_rot <= player_rot_thr:
            visible_rot = player_rot

        player_surface = pygame.transform.rotate(images.player[player_index], visible_rot)
        SCREEN.blit(player_surface, (state.bird.get_x(), state.bird.get_y()))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def show_game_over_screen(crash_info):
    """crashes the player down and shows gameover image"""
    score = crash_info['score']
    player_x = SCREEN_WIDTH * 0.2
    player_y = crash_info['y']
    player_height = images.player[0].get_height()
    player_vel_y = crash_info['player_vel_y']
    player_acc_y = 2
    player_rot = crash_info['player_rot']
    player_vel_rot = 7

    basex = crash_info['base_x']

    upper_pipes, lower_pipes = crash_info['upper_pipes'], crash_info['lower_pipes']

    # play hit and die sounds
    sounds.hit.play()
    if not crash_info['groundCrash']:
        sounds.die.play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y + player_height >= BASE_Y - 1:
                    return

        # player y shift
        if player_y + player_height < BASE_Y - 1:
            player_y += min(player_vel_y, BASE_Y - player_y - player_height)

        # player velocity change
        if player_vel_y < 15:
            player_vel_y += player_acc_y

        # rotate only when it's a pipe crash
        if not crash_info['groundCrash']:
            if player_rot > -90:
                player_rot -= player_vel_rot

        # draw sprites
        SCREEN.blit(images.background, (0, 0))

        for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(images.pipe[0], (u_pipe['x'], u_pipe['y']))
            SCREEN.blit(images.pipe[1], (l_pipe['x'], l_pipe['y']))

        SCREEN.blit(images.base, (basex, BASE_Y))
        show_score(score)

        player_surface = pygame.transform.rotate(images.player[1], player_rot)
        SCREEN.blit(player_surface, (player_x, player_y))
        SCREEN.blit(images.game_over, (50, 180))

        FPS_CLOCK.tick(FPS)
        pygame.display.update()


def player_shm(player_shm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(player_shm['val']) == 8:
        player_shm['dir'] *= -1

    if player_shm['dir'] == 1:
        player_shm['val'] += 1
    else:
        player_shm['val'] -= 1


def get_random_pipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gap_y = random.randrange(0, int(BASE_Y * 0.6 - PIPE_GAP_SIZE))
    gap_y += int(BASE_Y * 0.2)
    pipe_height = images.pipe[0].get_height()
    pipe_x = SCREEN_WIDTH + 10

    return [
        {'x': pipe_x, 'y': gap_y - pipe_height},  # upper pipe
        {'x': pipe_x, 'y': gap_y + PIPE_GAP_SIZE},  # lower pipe
    ]


def show_score(score):
    """displays score in center of screen"""
    score_digits = [int(x) for x in list(str(score))]
    total_width = 0  # total width of all numbers to be printed

    for digit in score_digits:
        total_width += images.get_number(digit).get_width()

    x_offset = (SCREEN_WIDTH - total_width) / 2

    for digit in score_digits:
        SCREEN.blit(images.get_number(digit), (x_offset, SCREEN_HEIGHT * 0.1))
        x_offset += images.get_number(digit).get_width()


def check_crash(player, upper_pipes, lower_pipes):
    """returns True if player collides with base or pipes."""
    player_index = player['index']
    player['w'] = images.player[0].get_width()
    player['h'] = images.player[0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASE_Y - 1:
        return [True, True]
    else:

        player_rect = pygame.Rect(player['x'], player['y'], player['w'], player['h'])
        pipe_w = images.pipe[0].get_width()
        pipe_h = images.pipe[0].get_height()

        for uPipe, lPipe in zip(upper_pipes, lower_pipes):
            # upper and lower pipe rects
            u_pipe_rect = pygame.Rect(uPipe['x'], uPipe['y'], pipe_w, pipe_h)
            l_pipe_rect = pygame.Rect(lPipe['x'], lPipe['y'], pipe_w, pipe_h)

            # player and upper/lower pipe hit-masks
            p_hit_mask = HIT_MASKS_PLAYER[player_index]
            u_hit_mask = HIT_MASKS_PIPE[0]
            l_hit_mask = HIT_MASKS_PIPE[1]

            # if bird collided with upipe or lpipe
            u_collide = pixel_collision(player_rect, u_pipe_rect, p_hit_mask, u_hit_mask)
            l_collide = pixel_collision(player_rect, l_pipe_rect, p_hit_mask, l_hit_mask)

            if u_collide or l_collide:
                return [True, False]

    return [False, False]


def pixel_collision(rect1, rect2, hit_mask_a, hit_mask_b):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hit_mask_a[x1 + x][y1 + y] and hit_mask_b[x2 + x][y2 + y]:
                return True
    return False


if __name__ == '__main__':
    main()
