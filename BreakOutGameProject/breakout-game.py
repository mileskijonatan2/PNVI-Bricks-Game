import random
import pygame
import json
import sys
import math
import statistics
from pygame.locals import *

FPS = 40
WINDOWWIDTH = 720
WINDOWHEIGHT = 720
BALLSPEED = 4
PADDLESPEED = 30
BRICKWIDTH = 55
BRICKHEIGHT = 55
GAPSIZE = 10
BOARDWIDTH = 5
BOARDHEIGHT = 5
BALLRADIUS = 6
PADDLEWIDTH = 180
PADDLEHEIGHT = 20
SCORE = 0
assert BOARDWIDTH == BOARDHEIGHT
assert BOARDWIDTH % 2 != 0 and BOARDHEIGHT % 2 != 0
YHEADER = 40
XMARGIN = int((WINDOWWIDTH - ((BOARDWIDTH-1) * (BRICKWIDTH + GAPSIZE) + BRICKWIDTH)) / 2)
YMARGIN = int((WINDOWHEIGHT - ((BOARDHEIGHT-1) * (BRICKHEIGHT + GAPSIZE) + BRICKHEIGHT)) / 2) + YHEADER
PADDLEXMARGIN = 20
PADDLEYMARGIN = 20
DEADLY = False
FIRSTOPEN = True


# game colors
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
BRIGHTORANGE = (255, 180, 100)

BGCOLOR = GRAY
LIGHTBGCOLOR = NAVYBLUE
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE
PADDLECOLOR = BRIGHTORANGE

LEVEL = 1
LIVES = 3

# brick types
N = 'normal'
D = 'deadly'
S = 'speed up'
L = 'lose points'

COLORS = {N: WHITE, D: RED, S: PURPLE, L: CYAN}


def getRandomizedBoard(level=1):
    global BOARDWIDTH, BOARDHEIGHT, XMARGIN, YMARGIN
    BOARDWIDTH = LEVELS[str(level)][4]
    BOARDHEIGHT = LEVELS[str(level)][4]
    XMARGIN = int((WINDOWWIDTH - ((BOARDWIDTH - 1) * (BRICKWIDTH + GAPSIZE) + BRICKWIDTH)) / 2)
    YMARGIN = int((WINDOWHEIGHT - ((BOARDHEIGHT - 1) * (BRICKHEIGHT + GAPSIZE) + BRICKHEIGHT)) / 2) + YHEADER
    num_total = calculate_num_bricks(BOARDWIDTH) # BOARDWIDTH * BOARDHEIGHT
    all_bricks = [None] * num_total

    num_n = LEVELS[str(level)][0]
    num_d = LEVELS[str(level)][1]
    num_s = LEVELS[str(level)][2]
    num_l = LEVELS[str(level)][3]

    all_bricks_type = []
    for _ in all_bricks[:int(len(all_bricks) * num_n)]:
        all_bricks_type.append(N)
    for _ in all_bricks[int(len(all_bricks) * num_n): int(len(all_bricks) * (num_n + num_d))]:
        all_bricks_type.append(D)
    for _ in all_bricks[int(len(all_bricks) * (num_n + num_d)): int(len(all_bricks) * (num_n + num_d + num_s))]:
        all_bricks_type.append(S)
    for _ in all_bricks[int(len(all_bricks) * (num_n + num_d + num_s)):]:
        all_bricks_type.append(L)

    all_bricks = all_bricks_type
    random.shuffle(all_bricks)

    board = []
    median = statistics.median(list(range(BOARDWIDTH)))
    valid_indices = [median]
    for x in range(BOARDWIDTH):
        column = []
        if x <= median:
            additional_boxes = 2 * x
            if additional_boxes:
                valid_indices.insert(0, valid_indices[0] - 1)
                valid_indices.append(valid_indices[-1] + 1)
        else:
            valid_indices.pop()
            valid_indices.pop(0)
        for y in range(BOARDHEIGHT):
            if y in valid_indices:
                column.append({'type': all_bricks[0], 'alive': True})
                del all_bricks[0]
            else:
                column.append({'type': None, 'alive': False})
        board.append(column)
    return board


def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (BRICKWIDTH + GAPSIZE) + XMARGIN
    top = boxy * (BRICKHEIGHT + GAPSIZE) + YMARGIN
    return (left, top)


def calculate_num_bricks(size):
    total_bricks = 0
    mid = size // 2

    for row in range(size):
        bricks_in_row = size - 2 * abs(mid - row)
        total_bricks += bricks_in_row

    return total_bricks


def drawBoard(mainBoard):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if mainBoard[boxx][boxy]['alive']:
                pygame.draw.rect(DISPLAYSURF, COLORS[mainBoard[boxx][boxy]['type']], (left, top, BRICKWIDTH, BRICKHEIGHT))

def drawPaddles(paddleX, paddleY):
    pygame.draw.rect(DISPLAYSURF, PADDLECOLOR, (PADDLEXMARGIN, paddleY, PADDLEHEIGHT, PADDLEWIDTH))
    pygame.draw.rect(DISPLAYSURF, PADDLECOLOR, (WINDOWWIDTH - PADDLEXMARGIN - PADDLEHEIGHT, paddleY, PADDLEHEIGHT, PADDLEWIDTH))
    pygame.draw.rect(DISPLAYSURF, PADDLECOLOR, (paddleX, PADDLEYMARGIN + YHEADER, PADDLEWIDTH, PADDLEHEIGHT))
    pygame.draw.rect(DISPLAYSURF, PADDLECOLOR, (paddleX, WINDOWHEIGHT - PADDLEYMARGIN - PADDLEHEIGHT, PADDLEWIDTH, PADDLEHEIGHT))


def isLegalState(paddle_x, paddle_y):
    return (paddle_x >= PADDLEXMARGIN and (paddle_x + PADDLEWIDTH) <= (WINDOWWIDTH - PADDLEXMARGIN)
            and paddle_y >= PADDLEYMARGIN + YHEADER and (paddle_y + PADDLEWIDTH) <= (WINDOWHEIGHT - PADDLEYMARGIN))


def isLegalBallState(x, y):
    return (x >= PADDLEXMARGIN + PADDLEHEIGHT and x <= (WINDOWWIDTH - PADDLEXMARGIN - PADDLEHEIGHT)
            and y >= PADDLEYMARGIN + YHEADER + PADDLEHEIGHT and y <= (WINDOWHEIGHT - PADDLEYMARGIN - PADDLEHEIGHT))


def drawBall(posX, posY):
    pygame.draw.circle(DISPLAYSURF, WHITE, (int(posX), int(posY)), BALLRADIUS)


def generateBallPos(brick_center_x, brick_center_y, angle_refinement = False):
    # Randomly choose one of the four paddles
    paddle_choice = random.choice(['left', 'right', 'top', 'bottom'])
    if paddle_choice == 'left':
        x = PADDLEXMARGIN + PADDLEHEIGHT + BALLRADIUS + 5
        y = (PADDLEYMARGIN + YHEADER + WINDOWHEIGHT - PADDLEYMARGIN) / 2
    elif paddle_choice == 'right':
        x = WINDOWWIDTH - PADDLEXMARGIN - PADDLEHEIGHT - BALLRADIUS - 5
        y = (PADDLEYMARGIN + YHEADER + WINDOWHEIGHT - PADDLEYMARGIN) / 2
    elif paddle_choice == 'top':
        x = WINDOWWIDTH / 2
        y = PADDLEYMARGIN + YHEADER + PADDLEHEIGHT + BALLRADIUS + 5
    else:
        x = WINDOWWIDTH / 2
        y = WINDOWHEIGHT - PADDLEYMARGIN - PADDLEHEIGHT - BALLRADIUS - 5
    dx = brick_center_x - x
    dy = brick_center_y - y
    angle = math.atan2(dy, dx)
    if angle_refinement:
        angle += random.uniform(-2, 2) # random.uniform(-0.5, 0.5)
    ball_speed_x = BALLSPEED * math.cos(angle)
    ball_speed_y = BALLSPEED * math.sin(angle)
    ball_speed_x, ball_speed_y = normalizeSpeed(ball_speed_x, ball_speed_y, BALLSPEED)
    return x, y, ball_speed_x, ball_speed_y


def normalizeSpeed(ball_speed_x, ball_speed_y, target_speed):
    magnitude = math.sqrt(ball_speed_x ** 2 + ball_speed_y ** 2)
    if magnitude == 0:
        return ball_speed_x, ball_speed_y
    scale = target_speed / magnitude
    return ball_speed_x * scale, ball_speed_y * scale


def check_bricks_collision(mainBoard, posX, posY, ball_speed_x, ball_speed_y):
    global SCORE, DEADLY, BALLSPEED
    brick_center_x = XMARGIN + (BOARDWIDTH * (BRICKWIDTH + GAPSIZE)) / 2
    brick_center_y = YMARGIN + (BOARDHEIGHT * (BRICKHEIGHT + GAPSIZE)) / 2
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            if not mainBoard[boxx][boxy]['alive']:
                continue
            left, top = leftTopCoordsOfBox(boxx, boxy)
            brick_rect = pygame.Rect(left, top, BRICKWIDTH, BRICKHEIGHT)
            ball_rect = pygame.Rect(posX - BALLRADIUS, posY - BALLRADIUS, BALLRADIUS * 2, BALLRADIUS * 2)
            if brick_rect.colliderect(ball_rect):
                # Calculate new direction toward brick field center
                dx = brick_center_x - posX
                dy = brick_center_y - posY
                angle = math.atan2(dy, dx)
                # Add slight randomness to avoid repetitive paths
                angle += random.uniform(-5, 5) # random.uniform(0, 5)
                ball_speed_x = BALLSPEED * math.cos(angle)
                ball_speed_y = BALLSPEED * math.sin(angle)
                # ball_speed_x, ball_speed_y = normalizeSpeed(ball_speed_x, ball_speed_y, BALLSPEED)
                mainBoard[boxx][boxy]['alive'] = False
                if mainBoard[boxx][boxy]['type'] == N:
                    SCORE += 1
                elif mainBoard[boxx][boxy]['type'] == D:
                    DEADLY = True
                elif mainBoard[boxx][boxy]['type'] == L:
                    SCORE -= 1
                elif mainBoard[boxx][boxy]['type'] == S:
                    BALLSPEED = min(BALLSPEED * 1.2, 10)
                return True, ball_speed_x, ball_speed_y
    return False, ball_speed_x, ball_speed_y


def check_paddles_collision(paddleX, paddleY, posX, posY, ball_speed_x, ball_speed_y):
    v1 = pygame.Rect(PADDLEXMARGIN, paddleY, PADDLEHEIGHT, PADDLEWIDTH)
    v2 = pygame.Rect(WINDOWWIDTH - PADDLEXMARGIN - PADDLEHEIGHT, paddleY, PADDLEHEIGHT, PADDLEWIDTH)
    h1 = pygame.Rect(paddleX, PADDLEYMARGIN + YHEADER, PADDLEWIDTH, PADDLEHEIGHT)
    h2 = pygame.Rect(paddleX, WINDOWHEIGHT - PADDLEYMARGIN - PADDLEHEIGHT, PADDLEWIDTH, PADDLEHEIGHT)
    ball_rect = pygame.Rect(posX - BALLRADIUS, posY - BALLRADIUS, BALLRADIUS * 2, BALLRADIUS * 2)

    if v1.colliderect(ball_rect):
        ball_speed_x = -ball_speed_x
        ball_speed_y += random.uniform(-1, 1)
        return True, ball_speed_x, ball_speed_y
    elif v2.colliderect(ball_rect):
        ball_speed_x = -ball_speed_x
        ball_speed_y += random.uniform(-1, 1)
        return True, ball_speed_x, ball_speed_y
    elif h1.colliderect(ball_rect):
        ball_speed_y = -ball_speed_y
        ball_speed_x += random.uniform(-1, 1)
        return True, ball_speed_x, ball_speed_y
    elif h2.colliderect(ball_rect):
        ball_speed_y = -ball_speed_y
        ball_speed_x += random.uniform(-1, 1)
        return True, ball_speed_x, ball_speed_y
    return False, ball_speed_x, ball_speed_y


def draw_text(text1, text2, font, color, x, y, center=False):
    surface = font.render(text1, True, color)
    rect = surface.get_rect()
    surface2 = font.render(text2, True, color)
    rect2 = surface2.get_rect()

    rect.topleft = (x, y)
    rect2.topleft = (WINDOWWIDTH - x - 100, y)
    DISPLAYSURF.blit(surface, rect)
    DISPLAYSURF.blit(surface2, rect2)

def draw_text_end_screen(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    rect.center = (x, y)
    DISPLAYSURF.blit(surface, rect)


def display_end_screen(message, font):
    global SCORE, LEVEL, FPS
    DISPLAYSURF.fill(BGCOLOR)
    font1 = pygame.font.SysFont('Comic Sans MS', 36)
    font2 = pygame.font.SysFont(None, 26)
    font3 = pygame.font.SysFont('Comic Sans MS', 26)
    draw_text_end_screen(f"{message}", font1, WHITE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 60)
    draw_text_end_screen(f"Score: {SCORE}", font2, WHITE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 20)
    pygame.draw.rect(DISPLAYSURF, WHITE, (WINDOWWIDTH // 2 - 75, WINDOWHEIGHT // 2 + 20, 150, 40))
    if message == "You Won This Level!":
        draw_text_end_screen("Next Level", font3, NAVYBLUE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 + 40)
        LEVEL += 1
        FPS += 10
    else:
        draw_text_end_screen("Play Again", font3, NAVYBLUE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 + 40)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (WINDOWWIDTH // 2 - 75 <= mouse_x <= WINDOWWIDTH // 2 + 75 and
                        WINDOWHEIGHT // 2 + 20 <= mouse_y <= WINDOWHEIGHT // 2 + 60):
                    main()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def display_start_screen():
    global FIRSTOPEN
    DISPLAYSURF.fill(BGCOLOR)
    font1 = pygame.font.SysFont('Comic Sans MS', 52)
    font2 = pygame.font.SysFont(None, 26)
    font3 = pygame.font.SysFont('Comic Sans MS', 28)
    draw_text_end_screen(f"Bricks Breaker", font1, WHITE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 80)
    draw_text_end_screen(f"Press arrow keys or AWSD keys in order to move the paddles", font2, WHITE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 30)
    draw_text_end_screen(f"Press space to teleport the ball on a random position", font2, WHITE, WINDOWWIDTH // 2,
                         WINDOWHEIGHT // 2 - 10)
    pygame.draw.rect(DISPLAYSURF, WHITE, (WINDOWWIDTH // 2 - 75, WINDOWHEIGHT // 2 + 20, 150, 40))
    draw_text_end_screen("Play", font3, NAVYBLUE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 + 40)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (WINDOWWIDTH // 2 - 75 <= mouse_x <= WINDOWWIDTH // 2 + 75 and
                        WINDOWHEIGHT // 2 + 20 <= mouse_y <= WINDOWHEIGHT // 2 + 60):
                    FIRSTOPEN = False
                    main()
        pygame.display.update()
        FPSCLOCK.tick(FPS)




def main():
    global FPSCLOCK, DISPLAYSURF, BALLSPEED, SCORE, DEADLY, LIVES
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Bricks Breaker')
    font = pygame.font.SysFont(None, 36)
    SCORE = 0
    DEADLY = False
    LIVES = 3
    BALLSPEED = 5
    bricksBoard = getRandomizedBoard(level=LEVEL)
    paddle_x = (PADDLEXMARGIN + (WINDOWWIDTH - PADDLEXMARGIN)) // 2 - (PADDLEWIDTH / 2)
    paddle_y = (PADDLEYMARGIN + (WINDOWHEIGHT - PADDLEYMARGIN)) / 2 - (PADDLEWIDTH / 2)
    ball_pos_x, ball_pos_y, _, _ = generateBallPos(0, 0)
    brick_center_x = XMARGIN + (BOARDWIDTH * (BRICKWIDTH + GAPSIZE)) / 2
    brick_center_y = YMARGIN + (BOARDHEIGHT * (BRICKHEIGHT + GAPSIZE)) / 2
    ball_pos_x, ball_pos_y, ball_speed_x, ball_speed_y = generateBallPos(brick_center_x, brick_center_y)

    if FIRSTOPEN:
        display_start_screen()

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(bricksBoard)
        drawPaddles(paddle_x, paddle_y)
        drawBall(ball_pos_x, ball_pos_y)
        draw_text(f'Score: {SCORE}', f'Lives: {LIVES}', font, WHITE, PADDLEXMARGIN, PADDLEYMARGIN)
        level_message = font.render(f"Level: {LEVEL}", True, WHITE)
        level_message_rect = level_message.get_rect(center=(WINDOWWIDTH // 2, PADDLEYMARGIN + PADDLEYMARGIN//2))
        DISPLAYSURF.blit(level_message, level_message_rect)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                ball_pos_x, ball_pos_y, ball_speed_x, ball_speed_y = generateBallPos(brick_center_x, brick_center_y, angle_refinement=True)


        # Check collisions
        brick_hit, ball_speed_x, ball_speed_y = check_bricks_collision(bricksBoard, ball_pos_x, ball_pos_y,
                                                                       ball_speed_x, ball_speed_y)
        paddle_hit, ball_speed_x, ball_speed_y = check_paddles_collision(paddle_x, paddle_y, ball_pos_x,
                                                                         ball_pos_y, ball_speed_x,
                                                                         ball_speed_y)

        if brick_hit or paddle_hit:
            ball_speed_x, ball_speed_y = normalizeSpeed(ball_speed_x, ball_speed_y, BALLSPEED)

        keys = pygame.key.get_pressed()
        if keys[K_LEFT] or keys[K_a]:
            if isLegalState(paddle_x - PADDLESPEED, paddle_y):
                paddle_x -= PADDLESPEED
        if keys[K_RIGHT] or keys[K_d]:
            if isLegalState(paddle_x + PADDLESPEED, paddle_y):
                paddle_x += PADDLESPEED
        if keys[K_UP] or keys[K_w]:
            if isLegalState(paddle_x, paddle_y - PADDLESPEED):
                paddle_y -= PADDLESPEED
        if keys[K_DOWN] or keys[K_s]:
            if isLegalState(paddle_x, paddle_y + PADDLESPEED):
                paddle_y += PADDLESPEED

        # Check game over or win conditions
        if (not paddle_hit and not isLegalBallState(ball_pos_x, ball_pos_y)) or DEADLY:
            LIVES -= 1
            DEADLY = False
            ball_pos_x, ball_pos_y, ball_speed_x, ball_speed_y = generateBallPos(brick_center_x, brick_center_y, angle_refinement=True)

        if LIVES <= 0:
            message = 'Game Over'
            display_end_screen(message, font)
            break

        if all(not bricksBoard[boxx][boxy]['alive'] for boxx in range(BOARDWIDTH) for boxy in range(BOARDHEIGHT) if bricksBoard[boxx][boxy]['type'] == N):
            message = 'You Won This Level!'
            display_end_screen(message, font)
            break

        # Update ball position
        ball_pos_x += ball_speed_x
        ball_pos_y += ball_speed_y

        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    # Read the levels file
    with open("levels.json", "r") as file:
        LEVELS = json.load(file)

    main()
