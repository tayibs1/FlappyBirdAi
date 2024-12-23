import pygame
import neat
import os
import random

# Constants
WIN_WIDTH = 600
WIN_HEIGHT = 800

# Load images
script_dir = os.path.dirname(__file__)
img_dir = os.path.join(script_dir, "imgs")

BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "bird3.png")))
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(img_dir, "bg.png")))

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5 # negative velocity meaning going upwards, positive velocity means going downwards
        self.tick_count = 0 
        self.height = self.y

    # self.tick_count is the frames of the bird moving; every time there is a frame (e.g., 30 frames per second), 
    # every second there are 30 ticks, each tick calculating the displacement of the bird
    def move(self):
        self.tick_count += 1 
        
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2 # calculating displacement; tells us based on velocity how much we are moving up or down
        
        if d >= 16:
            d = 16
        
        if d < 0:
            d -= 2
        
        self.y = self.y + d
        
        if (d < 0) or (self.y < self.height + 50): # when going up, it checks if height is still above the initial height at position 0; if under that position, start to tilt bird
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION # sets it back to 25 degrees if it goes above, to stop it flipping itself
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL # when going downwards, it tilts 90 degrees to simulate the bird diving

    def draw(self, win):
        self.img_count += 1 # keeps track of how many images have been shown
        
        # logic to get flappy bird wings to flap up and down
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2 # doesn't skip image when flapping back up
            
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        # rotates image around the center where bird is located, not from the top-left of the window
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center) 
        win.blit(rotated_image, new_rect.topleft) # rotates img
        
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
# Add the Pipe class for basic drawing functionality.
class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


def draw_window(win, bird):
    # .blit function means .draw, and draws the background img from the top-left
    win.blit(BG_IMG, (0, 0))
    bird.draw(win)
    pygame.display.update()

def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)  # Limit to 30 frames per second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Remove bird.move() to keep it stationary but flapping
        draw_window(win, bird)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main()