import pygame
import random
import os
import time
from pygame import mixer

# Initialize the pygame
pygame.init()

# Background music
mixer.music.load(os.path.join("assets", "background.wav"))
mixer.music.play(-1)# -1 to loop it

WIDTH, HEIGHT = 750, 750
# Create the game window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# Title of window
pygame.display.set_caption("Yannick's Space Invader")

# Load images
red_spaceship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
green_spaceship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
blue_spaceship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# player ship
player_ship = pygame.image.load(os.path.join("assets", "space-invaders-ship.png"))

# Lasers
red_lasers = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
green_lasers = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blue_lasers = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_lasers = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Backgorund
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (HEIGHT, WIDTH))


# Abstract ship class to inherit from later
class Ship:
    COOLDOWN = 2

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None # to draw ship
        self.laser_img = None # to draw laser
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, velo, obj):
        self.cooldown()
        # for each laser that's been shot move it downwards
        for laser in self.lasers:
            laser.move(velo)
            # check if the laser off screen
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            # otherwise check if it has collided with the player, decrease the health and remove the laser
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    # cooldown counter before another laser can be shot
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    # shooting function
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    # getting width of the ship image
    def get_width(self):
        return self.ship_img.get_width()

    # getting the height of the ship image
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health) # using the same attributes of the ship class
        self.ship_img = player_ship
        self.laser_img = yellow_lasers
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, velo, objs):
        self.cooldown()
        # for each laser that's been shot move it upwards
        for laser in self.lasers:
            laser.move(velo)
            # check if the laser off screen
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
            # otherwise check if it has collided with the player, decrease the health and remove the laser
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    # function to tell us if laser is not on the screen
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    # tells us if the laser collides with an object
    def collision(self, obj):
        return collide(self, obj) # returns the value of the collide function



class Enemy(Ship):
    # mapping images to strings according to their colour
    colour_map = {
                 "red" : (red_spaceship, red_lasers),
                 "green": (green_spaceship, green_lasers),
                 "blue": (blue_spaceship, blue_lasers)
                 }
    COOLDOWN = 30

    def __init__(self, x, y, colour, health=100):
        super().__init__(x, y, health)# inheriting the attributes from the ship class
        # taking out the images based on the colour that was called
        self.ship_img, self.laser_img = self.colour_map[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)

    # moving the enemy downwards
    def move(self, velocity):
        self.y += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    # distance between the two objects
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    # determining if the mask of each object are overlapping based on their offsets
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
    # if they overlap it'll return a tuple (x,y) point of intersection


# Game Loop
def main():
    running = True
    FPS = 60
    level = 0
    lives = 10
    # Using pygame fonts
    main_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    wave_length = 5
    enemy_velocity = 8

    laser_velocity = 15
    player_velocity = 25
    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        # draw background
        WIN.blit(bg, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10,10)) # drawing top right
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) # drawing top left

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        pygame.display.update()

    while running:
        clock.tick(FPS)
        redraw_window()


        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        # if we've lost count for three seconds then quit the game
        if lost:
            if lost_count > FPS * 2:
                running = False
            else:
                continue

        # spawning the enemies
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            # spawning the enemies so they come randomly at different heights
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, 100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed() # returns a dict of all keys. tells you wether they are pressed or not at the current time
        if keys[pygame.K_a] and player.x - player_velocity > 0: # left key pressed
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH: # right key pressed
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0: # up key pressed
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() + 15 < HEIGHT: # down key pressed
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            # if enemy collides with the player decrement player health
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            # if enemy reaches the end of the screen decrement player health
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_velocity, enemies)

# Making main menu
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    running = True
    while running:
        # drawing the welcoming screen
        WIN.blit(bg, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    quit()

main_menu()
