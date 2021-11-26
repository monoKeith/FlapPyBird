import os

import neat as neat

from state import *


class NeatControl:

    def __init__(self, state: State, game_iteration):
        self.state = state
        self.game_iteration = game_iteration
        local_dir = os.path.dirname(__file__)
        self.config_file = os.path.join(local_dir, 'config-feedforward.txt')

    def run(self):
        """
            runs the NEAT algorithm to train a neural network to play flappy bird.
            :param config_file: location of config file
            :return: None
            """
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    self.config_file)

        # Create the population, which is the top-level object for a NEAT run.
        p = neat.Population(config)

        # Add a stdout reporter to show progress in the terminal.
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        # p.add_reporter(neat.Checkpointer(5))

        # Run for up to 50 generations.
        winner = p.run(self.eval_genomes, 50)

        # show final stats
        print('\nBest genome:\n{!s}'.format(winner))

    def eval_genomes(self, genomes, config):
        # Init
        self.state.initialize(len(genomes))

        self.nets = []
        self.ge = []
        # For each frame the bird survive, fitness + 0.1, for each pipe the bird survive, fitness + 5
        self.current_fitness = 0
        for genome_id, genome in genomes:
            genome.fitness = 0  # start with fitness level of 0
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            self.ge.append(genome)

        # Run one generation (all birds die)
        self.game_iteration()

    def frame_begin(self):
        # Update net for each bird
        for index, net in enumerate(self.nets):
            self.state.birds[index].set_net(net)

    def frame_finish(self):
        # When a bird die, remove corresponding data
        for bird in self.state.birds:
            if bird.dead:
                index = self.state.birds.index(bird)
                self.nets.pop(index)
                self.ge.pop(index)
                self.state.birds.pop(index)
        # Update fitness score
        self.current_fitness += 0.1
        if self.state.is_new_record():
            self.current_fitness += 5
        for genome in self.ge:
            genome.fitness = self.current_fitness
