import pygame
import neat
import os
import random

pygame.font.init()

# Constants
GEN = 0
WIN_WIDTH = 500
WIN_HEIGHT = 800
FPS = 30  # Frames per second
PIPE_GAP = 200  # Gap between pipes
PIPE_VELOCITY = 5  # Velocity of the pipes
BASE_VELOCITY = 5  # Velocity of the base
JUMP_VELOCITY = -10.5  # Velocity for bird jump
DISPLACEMENT_LIMIT = 16  # Max displacement per tick
ANIMATION_TIME = 5  # Time for each animation frame

# Load images
script_dir = os.path.dirname(__file__)
img_dir = os.path.join(script_dir, "imgs")

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, f"bird{i}.png"))) for i in range(1, 4)
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    """Represents the bird controlled by AI."""

    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = JUMP_VELOCITY
        self.tick_count = 0
        self.height = self.y

    # self.tick_count is the frames of the bird moving; every time there is a frame (e.g., 30 frames per second), 
    # every second there are 30 ticks, each tick calculating the displacement of the bird
    def move(self):
        self.tick_count += 1
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2
        displacement = max(min(displacement, DISPLACEMENT_LIMIT), -DISPLACEMENT_LIMIT - 2)

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:  # when going up, it checks if height is still above the initial height at position 0; if under that position, start to tilt bird
            self.tilt = min(self.MAX_ROTATION, self.tilt + self.ROTATION_VELOCITY)
        else:
            self.tilt = max(-90, self.tilt - self.ROTATION_VELOCITY)  # when going downwards, it tilts 90 degrees to simulate the bird diving

    def draw(self, win):
        self.img_count += 1  # keeps track of how many images have been shown

        # logic to get flappy bird wings to flap up and down
        index = (self.img_count // ANIMATION_TIME) % len(self.IMGS)  # Ensures cycling through images safely
        self.img = self.IMGS[index]

        if self.tilt <= -80:
            self.img = self.IMGS[1]  # Wing flat when diving steeply

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        # rotates image around the center where bird is located, not from the top-left of the window
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)  # rotates img

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = PIPE_GAP
    VEL = PIPE_VELOCITY

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # using masks for collisions (using 2d arrays to store x and y pixel coords of an image 
    # and then the arrays are compared with other objects to see if collisions occur 
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # finds the point of collision where masks overlap
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

class Base:
    VEL = BASE_VELOCITY
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # since base image is too small we need to create two base images move to the left at the same velocity
    # this simulates two base images moving constantly when in reality its two of the same base images in a cycle moving at same speed as the screen
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds, pipes, base, score, gen):
    # .blit function means .draw, and draws the background img from the top-left
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10 , 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    for __, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)  # setting up neural network (giving it the genome, config file)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(FPS)  # Limit to FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(birds) == 0:  # Ensure there are birds before proceeding
            run = False
            break

        pipe_ind = 0
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # for every second the bird is alive it gains 1 fitness; encourages it to stay alive longer rather than just going all the way up or down

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # favors the bird that didn't hit the pipe and passed compared to the bird that collided so that the algorithm can learn faster
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5  # this allows the birds that pass through the pipe to have more fitness favouring birds that pass the pipes
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)

def run(config_path):
    # runs the NEAT algorithm to train a neural network to play flappy bird.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
