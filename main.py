import pygame
import os
import random
import time

# set root window
WIDTH, HEIGHT = 800, 600
root = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Shooter')

# load and scale files
# background file
background_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'background.png')), (WIDTH, HEIGHT))

# ship files
player_ship_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'player_ship.png')), (120, 120))
enemy_ship_green_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'enemy_ship_green.png')), (65, 75))
enemy_ship_red_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'enemy_ship_red.png')), (62, 75))
enemy_ship_blue_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'enemy_ship_blue.png')), (62, 75))
charger_ship_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'charger.png')), (200, 100))

# laser files
laser_player_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'laser_smp.png')), (15, 30))
laser_green_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'laser_green.png')), (12, 22))
laser_red_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'laser_red.png')), (12, 22))
laser_blue_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'laser_blue.png')), (12, 22))
laser_charger_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'laser_1.png')), (17, 30))

# collision file
collision_file = pygame.transform.scale(
    pygame.image.load(os.path.join('images', 'collision.png')), (150, 150))

# global params
game_is_over = False
level = 1
lives = 5
score = 0
FPS = 100
LEVEL = 5

# other params
pygame.font.init()
main_font = pygame.font.SysFont('comicsans', 50)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

tuple_files = {
    'player': (player_ship_file, laser_player_file),
    'red': (enemy_ship_red_file, laser_red_file),
    'blue': (enemy_ship_blue_file, laser_blue_file),
    'green': (enemy_ship_green_file, laser_green_file),
    'charger': (charger_ship_file, laser_charger_file)
}

player_init_x = int((WIDTH - player_ship_file.get_width()) / 2)
player_init_y = int(HEIGHT - player_ship_file.get_height())
charger_init_x = int((WIDTH - charger_ship_file.get_width()) / 2)
charger_init_y = -250
player_move_by = 5
enemy_move_by = 1
laser_move_by = 2
laser_gap_player = 200
laser_gap_charger = 1350
charger_move_left = True
incoming_message = 0

clock = pygame.time.Clock()


# laser class
class Laser:
    def __init__(self, x, y, image_file):
        self.x = x
        self.y = y
        self.image_file = image_file
        self.mask = pygame.mask.from_surface(self.image_file)

    def move(self, vel):
        self.y += vel

    def is_off_screen(self):
        return self.y < 0 or self.y > HEIGHT

    def draw(self, window):
        window.blit(self.image_file, (self.x, self.y))


class Ship:
    def __init__(self, x, y, files):
        self.x = x
        self.y = y
        self.image_file = files[0]
        self.laser_image_file = files[1]
        self.mask = pygame.mask.from_surface(self.image_file)
        self.lasers = []
        self.prev_tick = 0

    def move_lasers(self, vel):
        for laser in self.lasers:
            laser.move(vel)

    def draw(self, window):
        window.blit(self.image_file, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def remove_lasers(self):
        for laser in self.lasers:
            if laser.is_off_screen():
                self.lasers.remove(laser)


# player class
class PlayerShip(Ship):
    def move(self, keys):
        if keys[pygame.K_a] and self.x > 0:
            self.x -= player_move_by
        if keys[pygame.K_d] and self.x < WIDTH - self.image_file.get_width():
            self.x += player_move_by
        if keys[pygame.K_s] and self.y < HEIGHT - self.image_file.get_height():
            self.y += player_move_by
        if keys[pygame.K_w] and self.y > 0:
            self.y -= player_move_by

    def shoot(self, keys):
        if keys[pygame.K_SPACE] and pygame.time.get_ticks() - self.prev_tick >= laser_gap_player:
            x = int(self.x + (self.image_file.get_width() - self.laser_image_file.get_width()) / 2)
            y = self.y
            laser = Laser(x, y, self.laser_image_file)
            self.lasers.append(laser)
            self.prev_tick = pygame.time.get_ticks()


# enemy ship class
class EnemyShip(Ship):
    def move(self):
        self.y += enemy_move_by

    def is_off_screen(self):
        return self.y > HEIGHT - self.image_file.get_height()

    def shoot(self):
        if pygame.time.get_ticks() - self.prev_tick >= random.randrange(3500, 6000):
            x = self.x + int((self.image_file.get_width() - self.laser_image_file.get_width()) / 2)
            y = self.y + int(self.image_file.get_height())
            laser = Laser(x, y, self.laser_image_file)
            self.lasers.append(laser)
            self.prev_tick = pygame.time.get_ticks()


class Charger(Ship):
    def __init__(self, x, y, files):
        super().__init__(x, y, files)
        self.health = 100
        self.max_down = HEIGHT / 2 - 200
        self.max_left = 10
        self.max_right = WIDTH - self.image_file.get_width() - 10

    def move_down(self, vel):
        self.y += vel

    def move_left(self, vel):
        if self.x >= self.max_left:
            self.x -= vel

    def move_right(self, vel):
        if self.x <= self.max_right:
            self.x += vel

    def shoot(self):
        if pygame.time.get_ticks() - self.prev_tick >= laser_gap_charger:
            x = self.x + int((self.image_file.get_width() - self.laser_image_file.get_width()) / 2)
            y = self.y + int(self.image_file.get_height())
            laser_m = Laser(x, y, self.laser_image_file)
            laser_l = Laser(x-30, y, self.laser_image_file)
            laser_r = Laser(x+30, y, self.laser_image_file)
            self.lasers.append(laser_m)
            self.lasers.append(laser_l)
            self.lasers.append(laser_r)
            self.prev_tick = pygame.time.get_ticks()


# player ship and enemies
player = PlayerShip(player_init_x, player_init_y, tuple_files['player'])
enemies = []
charger = Charger(charger_init_x, charger_init_y, tuple_files['charger'])


# function to create enemies list
def create_enemies():
    enemy_list = []
    for i in range(level * 1):
        x = random.randrange(10, WIDTH - 50)
        y = random.randrange(-600, -100)
        enemy_object = EnemyShip(x, y, tuple_files[random.choice(['red', 'blue', 'green'])])
        enemy_list.append(enemy_object)
    return enemy_list


# function to check collision
def collides(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def boss_fight():
    global charger_move_left, lives, score

    if charger.x == charger.max_left:
        charger_move_left = False
    if charger.x == charger.max_right:
        charger_move_left = True

    if charger.y <= charger.max_down:
        charger.move_down(enemy_move_by)
    elif charger_move_left:
        charger.move_left(enemy_move_by)
    else:
        charger.move_right(enemy_move_by)

    charger.shoot()
    charger.move_lasers(laser_move_by)
    charger.remove_lasers()

    for laser in charger.lasers:
        if collides(player, laser):
            charger.lasers.remove(laser)
            if lives > 0:
                lives -= 1

    for laser in player.lasers:
        if collides(charger, laser):
            player.lasers.remove(laser)
            if charger.health > 0:
                charger.health -= 5

    if collides(charger, player):
        if lives > 0:
            lives -= 1
        if charger.health > 0:
            charger.health -= 5


# function to put items on root window
def put_items():
    global player, enemies, game_is_over, incoming_message
    # put the background
    root.blit(background_file, (0, 0))

    # put all enemy and lasers
    for enemy in enemies:
        enemy.draw(root)

    if level > LEVEL:
        if incoming_message == 0:
            incoming_message = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - incoming_message <= 2000:
            incoming_message_label = main_font.render('Incoming Charger', 1, WHITE)
            x = int((WIDTH - incoming_message_label.get_width()) / 2)
            y = int((HEIGHT - incoming_message_label.get_height()) / 2)
            root.blit(incoming_message_label, (x, y))
        if charger.health > 0:
            charger.draw(root)

    # put the player and lasers
    player.draw(root)

    # put the scoreboard
    lives_label = main_font.render(f'Lives: {lives}', 1, WHITE)
    score_label = main_font.render(f'Score: {score}', 1, WHITE)
    if level <= LEVEL:
        level_label = main_font.render(f'Level: {level}', 1, WHITE)
    else:
        level_label = main_font.render(f'Charger: {charger.health}', 1, WHITE)

    root.blit(lives_label, (10, 10))
    root.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
    root.blit(score_label, (10, lives_label.get_height() + 20))

    # put game over label
    if lives == 0:
        collision_x = int(player.x - (collision_file.get_width() - player.image_file.get_width()) / 2)
        collision_y = int(player.y - (collision_file.get_height() - player.image_file.get_height()) / 2)
        root.blit(collision_file, (collision_x, collision_y))
        game_over_label = main_font.render('Game Over!', 1, WHITE)
        x = int((WIDTH - game_over_label.get_width()) / 2)
        y = int((HEIGHT - game_over_label.get_height()) / 2)
        root.blit(game_over_label, (x, y))
        game_is_over = True

    # put you win label
    if level > LEVEL and lives != 0 and charger.health == 0:
        collision_x = int(charger.x + (charger.image_file.get_width() - collision_file.get_width()) / 2)
        collision_y = int(charger.y - (collision_file.get_height() - charger.image_file.get_height()) / 2)
        root.blit(collision_file, (collision_x, collision_y))
        you_win_label = main_font.render('You Win!', 1, WHITE)
        x = int((WIDTH - you_win_label.get_width()) / 2)
        y = int((HEIGHT - you_win_label.get_height()) / 2)
        root.blit(you_win_label, (x, y))
        game_is_over = True


# driver function
def main():
    pygame.init()
    global lives, score, level, enemies, game_is_over

    while True:
        pygame.display.update()
        clock.tick(FPS)
        put_items()

        # check if quit is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        if game_is_over:
            continue  # freeze the screen

        # move player based on key press
        player.move(pygame.key.get_pressed())  # if
        player.shoot(pygame.key.get_pressed())  # if
        player.move_lasers(-laser_move_by)

        # remove lasers from player
        player.remove_lasers()

        if level > LEVEL:
            boss_fight()
            continue

        # create enemies list
        if not enemies and level <= LEVEL:
            enemies = create_enemies()

        # move and remove all enemy
        for enemy in enemies:
            enemy.move()
            if enemy.is_off_screen():
                enemies.remove(enemy)
                if lives > 0:
                    lives -= 1

        # append lasers to enemy
        for enemy in enemies:
            enemy.shoot()  # if
            enemy.move_lasers(laser_move_by)
            enemy.remove_lasers()  # if

        # collision check player laser to enemy
        for laser in player.lasers:
            for enemy in enemies:
                if collides(enemy, laser):
                    player.lasers.remove(laser)
                    enemies.remove(enemy)
                    score += 5

        # collision check enemy, enemy laser to player
        for enemy in enemies:
            if collides(enemy, player):
                enemies.remove(enemy)
                if lives > 0:
                    lives -= 1
            for laser in enemy.lasers:
                if collides(player, laser):
                    enemy.lasers.remove(laser)
                    if lives > 0:
                        lives -= 1

        if not enemies and level <= LEVEL:
            level += 1


if __name__ == '__main__':
    main()










