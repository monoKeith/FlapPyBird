import pygame
import sys
from state import State
from resources import ImageResources, SoundResource
from itertools import cycle
from pygame.locals import *
from control import NeatControl

# Initialize pygame
pygame.init()
pygame.display.set_caption('Flappy Bird')
FPS_CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((State.SCREEN_WIDTH, State.SCREEN_HEIGHT))

# Initialize resources
images = ImageResources()
sounds = SoundResource()

# Initialize Game state
state = State(images, sounds)


def get_hit_mask(image):
    """returns a hit-mask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


HIT_MASKS_PIPE = [get_hit_mask(images.pipe[i]) for i in range(2)]
HIT_MASKS_PLAYER = [get_hit_mask(images.player[i]) for i in range(3)]

PLAYER_INDEX_CYCLE = cycle([0, 1, 2, 1])


def show_welcome_animation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    player_index = 0
    # iterator used to change player_index after every 5th iteration
    loop_iter = 0

    player_x = int(State.SCREEN_WIDTH * 0.2)
    player_y = int((State.SCREEN_HEIGHT - images.player[0].get_height()) / 2)

    message_x = int((State.SCREEN_WIDTH - images.message.get_width()) / 2)
    message_y = int(State.SCREEN_HEIGHT * 0.12)

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
                return

        # adjust playery, player_index, base_x
        if (loop_iter + 1) % 5 == 0:
            player_index = next(PLAYER_INDEX_CYCLE)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 4) % base_shift)
        player_shm(player_shm_vals)

        # draw sprites
        SCREEN.blit(images.background, (0, 0))
        SCREEN.blit(images.player[player_index], (player_x, player_y + player_shm_vals['val']))
        SCREEN.blit(images.message, (message_x, message_y))
        SCREEN.blit(images.base, (base_x, State.BASE_Y))

        pygame.display.update()
        FPS_CLOCK.tick(State.FPS)


def main_game():
    player_index = 0
    frame_counter = 0
    bird_initial_y = int((State.SCREEN_HEIGHT - images.player[0].get_height()) / 2)

    base_x = 0
    base_shift = images.base.get_width() - images.background.get_width()

    # add 2 random pipes
    state.add_random_pipe(State.SCREEN_WIDTH + 200)
    state.add_random_pipe(State.SCREEN_WIDTH + 200 + (State.SCREEN_WIDTH / 2))

    dt = FPS_CLOCK.tick(State.FPS) / 1000
    pipe_vel_x = -128 * dt

    for bird in state.birds:
        bird.y = bird_initial_y

    while True:
        control.frame_begin()

        # Only used for testing to control keyboard bird
        keyboard_flap = False

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                keyboard_flap = True

        # birds runs
        for bird in state.birds:

            if bird.dead:
                continue

            if keyboard_flap:
                bird.keyboard_flap = True
            bird.run()

            # check for crash
            crash_check = check_crash(
                {
                    'x': bird.get_x(),
                    'y': bird.get_y(),
                    'index': player_index
                },
                state.upper_pipes, state.lower_pipes)

            if crash_check[0]:
                bird.die()
                if state.alive_bird_count <= 0:
                    return

            # check for score
            player_mid_pos = bird.get_x() + images.player[0].get_width() / 2
            for pipe in state.upper_pipes:
                pipe_mid_pos = pipe['x'] + images.pipe[0].get_width() / 2
                if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                    bird.increase_score()
                    # sounds.point.play()

        # change bird appearance, so its wing flaps 3 times per second
        if (frame_counter + 1) % 3 == 0:
            player_index = next(PLAYER_INDEX_CYCLE)
        frame_counter = (frame_counter + 1) % 30
        base_x = -((-base_x + 100) % base_shift)

        # Update Pipes
        # move pipes to left
        for prev_u_pipe, prev_l_pipe in zip(state.upper_pipes, state.lower_pipes):
            prev_u_pipe['x'] += pipe_vel_x
            prev_l_pipe['x'] += pipe_vel_x
        # add new pipe when first pipe is about to touch left of screen
        if 3 > len(state.upper_pipes) > 0 and 0 < state.upper_pipes[0]['x'] < 5:
            state.add_random_pipe()
        # remove first pipe if its out of the screen
        if len(state.upper_pipes) > 0 and state.upper_pipes[0]['x'] < -images.pipe[0].get_width():
            state.upper_pipes.pop(0)
            state.lower_pipes.pop(0)

        # Refresh screen
        SCREEN.blit(images.background, (0, 0))
        # Pipes
        for prev_u_pipe, prev_l_pipe in zip(state.upper_pipes, state.lower_pipes):
            SCREEN.blit(images.pipe[0], (prev_u_pipe['x'], prev_u_pipe['y']))
            SCREEN.blit(images.pipe[1], (prev_l_pipe['x'], prev_l_pipe['y']))
        # Base
        SCREEN.blit(images.base, (base_x, State.BASE_Y))
        # Score
        show_score(state.get_score())
        # Bird: limit rotation of bird within 20
        for bird in state.birds:
            if bird.dead:
                continue
            visible_rotation = min(bird.rotation, 20)
            player_surface = pygame.transform.rotate(images.player[player_index], visible_rotation)
            SCREEN.blit(player_surface, (bird.get_x(), bird.get_y()))
        # Done
        pygame.display.update()
        control.frame_finish()
        FPS_CLOCK.tick(State.FPS)


def player_shm(player_shm_val):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(player_shm_val['val']) == 8:
        player_shm_val['dir'] *= -1

    if player_shm_val['dir'] == 1:
        player_shm_val['val'] += 1
    else:
        player_shm_val['val'] -= 1


def show_score(score):
    """displays score in center of screen"""
    score_digits = [int(x) for x in list(str(score))]
    total_width = 0  # total width of all numbers to be printed

    for digit in score_digits:
        total_width += images.get_number(digit).get_width()

    x_offset = (State.SCREEN_WIDTH - total_width) / 2

    for digit in score_digits:
        SCREEN.blit(images.get_number(digit), (x_offset, State.SCREEN_HEIGHT * 0.1))
        x_offset += images.get_number(digit).get_width()


def check_crash(player, upper_pipes, lower_pipes):
    """returns True if player collides with base or pipes."""
    player_index = player['index']
    player['w'] = images.player[0].get_width()
    player['h'] = images.player[0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= State.BASE_Y - 1:
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

    for x in range(rect.width):
        for y in range(rect.height):
            if hit_mask_a[x1 + x][y1 + y] and hit_mask_b[x2 + x][y2 + y]:
                return True
    return False


# Initialize neat
control = NeatControl(state, main_game)


def main():
    # Start
    show_welcome_animation()

    control.run()


if __name__ == '__main__':
    main()
