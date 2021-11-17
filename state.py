
class Bird:

    def __init__(self):
        self.x = 0
        self.y = 0

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

class State:

    def __init__(self):
        self.bird = Bird()
        self.score = 0

    def get_score(self):
        return self.score

    def increase_score(self):
        self.score += 1

