import pygame
import random
import sys
from pygame.locals import *

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
SPACESHIP_SPEED = 5
ASTEROID_SPEED = 2
CRYSTAL_SPEED = 2
SPACESHIP_HIT_LIMIT = 3
TOTAL_CRYSTALS = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)



def main():
    global SPACESHIP_IMAGE, ASTEROID_IMAGE, CRYSTAL_IMAGE, DISPLAY_SURF, CLOCK
    SPACESHIP_IMAGE = pygame.image.load("spaceship.png")
    ASTEROID_IMAGE = pygame.image.load("asteroid.png")
    CRYSTAL_IMAGE = pygame.image.load("energy_crystal.png")
    SPACESHIP_IMAGE = pygame.transform.scale(SPACESHIP_IMAGE, (50, 50))
    ASTEROID_IMAGE = pygame.transform.scale(ASTEROID_IMAGE, (50, 50))
    CRYSTAL_IMAGE = pygame.transform.scale(CRYSTAL_IMAGE, (30, 30))
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Space Scavenger")
    CLOCK = pygame.time.Clock()

    pygame.init()
    background_music = "background_music.wav"
    clash_sound = pygame.mixer.Sound("clash_sound.wav")
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.play(-1)
    font = pygame.font.SysFont(None, 36)
    stars = create_stars()
    display_welcome_screen()
    spaceship = initialize_spaceship()
    asteroids = []
    crystals = create_energy_crystals()
    score = 0
    asteroid_timer = 0
    difficulty_timer = 0
    asteroid_speed = ASTEROID_SPEED
    asteroid_size = (50, 50)
    while True:
        DISPLAY_SURF.fill(BLACK)
        draw_stars(stars)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        asteroid_timer += 1
        if asteroid_timer >= 30:
            asteroids.append(create_asteroid(asteroid_speed, asteroid_size))
            asteroid_timer = 0
        difficulty_timer += 1
        if difficulty_timer >= FPS * 10:
            asteroid_speed *= 1.20
            asteroid_size = (int(asteroid_size[0] * 1.20), int(asteroid_size[1] * 1.20))
            difficulty_timer = 0
        keys = pygame.key.get_pressed()
        move_spaceship(spaceship, keys)
        draw_spaceship(spaceship)
        for asteroid in asteroids[:]:
            move_asteroid(asteroid)
            draw_asteroid(asteroid)
            if asteroid["rect"].top > WINDOW_HEIGHT:
                asteroids.remove(asteroid)
            if asteroid["rect"].colliderect(spaceship["rect"]):
                pygame.mixer.Sound.play(clash_sound)
                spaceship["hit_count"] += 1
                asteroids.remove(asteroid)
        for crystal in crystals[:]:
            draw_crystal(crystal)
            if crystal["rect"].colliderect(spaceship["rect"]):
                score += 1
                crystals.remove(crystal)
        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"Hits: {spaceship['hit_count']}/{SPACESHIP_HIT_LIMIT}", font, WHITE, 10, 40)
        if score == TOTAL_CRYSTALS:
            display_end_screen("Victory", font)
        if spaceship["hit_count"] >= SPACESHIP_HIT_LIMIT:
            display_end_screen("GAME OVER!", font)
        pygame.display.flip()
        CLOCK.tick(FPS)
    pygame.quit()
    sys.exit()


def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    DISPLAY_SURF.blit(surface, rect)

def create_stars():
    stars = []
    for _ in range(50):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT)
        size = random.randint(1, 3)
        stars.append((x, y, size, size))
    return stars

def draw_stars(stars):
    for star in stars:
        pygame.draw.rect(DISPLAY_SURF, WHITE, star)

def initialize_spaceship():
    return {
        "image": SPACESHIP_IMAGE,
        "rect": SPACESHIP_IMAGE.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 70)),
        "speed": SPACESHIP_SPEED,
        "hit_count": 0
    }

def move_spaceship(spaceship, keys):
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        spaceship["rect"].x -= spaceship["speed"]
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        spaceship["rect"].x += spaceship["speed"]
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        spaceship["rect"].y -= spaceship["speed"]
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        spaceship["rect"].y += spaceship["speed"]
    spaceship["rect"].x = max(0, min(spaceship["rect"].x, WINDOW_WIDTH - spaceship["rect"].width))
    spaceship["rect"].y = max(0, min(spaceship["rect"].y, WINDOW_HEIGHT - spaceship["rect"].height))

def draw_spaceship(spaceship):
    DISPLAY_SURF.blit(spaceship["image"], spaceship["rect"])

def create_asteroid(speed, size):
    return {
        "image": pygame.transform.scale(ASTEROID_IMAGE, size),
        "rect": ASTEROID_IMAGE.get_rect(center=(random.randint(0, WINDOW_WIDTH), -50)),
        "speed": speed
    }

def move_asteroid(asteroid):
    asteroid["rect"].y += asteroid["speed"]

def draw_asteroid(asteroid):
    DISPLAY_SURF.blit(asteroid["image"], asteroid["rect"])

def create_energy_crystals():
    crystals = []
    for _ in range(TOTAL_CRYSTALS):
        x = random.randint(0, WINDOW_WIDTH - 30)
        y = random.randint(0, WINDOW_HEIGHT - 30)
        crystals.append({"image": CRYSTAL_IMAGE, "rect": CRYSTAL_IMAGE.get_rect(center=(x, y))})
    return crystals

def draw_crystal(crystal):
    DISPLAY_SURF.blit(crystal["image"], crystal["rect"])

def display_end_screen(message, font):
    DISPLAY_SURF.fill(BLACK)
    draw_text(message, font, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20, center=True)
    pygame.draw.rect(DISPLAY_SURF, WHITE, (WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 20, 150, 40))
    draw_text("Play Again", font, BLACK, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40, center=True)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (WINDOW_WIDTH // 2 - 75 <= mouse_x <= WINDOW_WIDTH // 2 + 75 and
                        WINDOW_HEIGHT // 2 + 20 <= mouse_y <= WINDOW_HEIGHT // 2 + 60):
                    main()

def display_welcome_screen():
    font = pygame.font.SysFont(None, 72)
    button_font = pygame.font.SysFont(None, 36)
    DISPLAY_SURF.fill(BLACK)
    draw_text("Space Scavenger", font, WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50, center=True)
    pygame.draw.rect(DISPLAY_SURF, WHITE, (WINDOW_WIDTH // 2 - 75, WINDOW_HEIGHT // 2 + 20, 150, 40))
    draw_text("Play", button_font, BLACK, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40, center=True)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (WINDOW_WIDTH // 2 - 75 <= mouse_x <= WINDOW_WIDTH // 2 + 75 and
                        WINDOW_HEIGHT // 2 + 20 <= mouse_y <= WINDOW_HEIGHT // 2 + 60):
                    return


if __name__ == "__main__":
    main()
