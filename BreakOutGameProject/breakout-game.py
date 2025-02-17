import random, pygame, sys
from pygame.locals import *

FPS = 60 # frames per second, the general speed of the program
WINDOWWIDTH = 700 # size of window's width in pixels
WINDOWHEIGHT = 500 # size of windows' height in pixels
BALLSPEEDX = 2 # speed of the ball along x-axis
BALLSPEEDY = 2 # speed of the ball along y-axis
PADDLESPEED = 10 # speed of paddles
BRICKWIDTH = 40 # size of brick width in pixels
BRICKHEIGHT = 20 # size of brick height in pixels
GAPSIZE = 10 # size of gap between bricks in pixels
BOARDWIDTH = 8 # number of columns of bricks
BOARDHEIGHT = 5 # number of rows of icons
BALLRADIUS = int(BRICKHEIGHT / 2)
PADDLEWIDHT = 180
PADDLEHEIGHT = 20
SCORE = 0
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0
YHEADER = 40
XMARGIN = int((WINDOWWIDTH - ((BOARDWIDTH-1) * (BRICKWIDTH + GAPSIZE) + BRICKWIDTH)) / 2)
YMARGIN = int((WINDOWHEIGHT - ((BOARDHEIGHT-1) * (BRICKHEIGHT + GAPSIZE) + BRICKHEIGHT)) / 2) + YHEADER
PADDLEXMARGIN = 20
PADDLEYMARGIN = 20
DEALDY = False


#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

LEVEL = 1
# Bricks types: N (normal), D(deadly), S(speed up), L(lose points)
N = 'normal'
D = 'deadly'
S = 'speed up'
L = 'lose points'

COLORS = {N: WHITE, D: RED, S: PURPLE, L: GRAY}

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def getRandomizedBoard():
    # Get a list of all 4 types of tiles with randomly given positions.
    all_bricks = []
    num_n, num_d, num_s, num_l = 0, 0, 0, 0
    num_total = BOARDWIDTH * BOARDHEIGHT
    all_bricks = [None] * num_total

    if LEVEL == 1:
        num_n = 0.7
        num_d = 0.1
        num_s = 0.1
        num_l = 0.1

    all_bricks_type = []
    for el in all_bricks[:int(len(all_bricks) * num_n)]:
        all_bricks_type.append(N)

    for el in all_bricks[int(len(all_bricks) * num_n): int(len(all_bricks) * (num_n + num_d))]:
        all_bricks_type.append(D)

    for el in all_bricks[int(len(all_bricks) * (num_n + num_d)): int(len(all_bricks) * (num_n + num_d + num_s))]:
        all_bricks_type.append(S)

    for el in all_bricks[int(len(all_bricks) * (num_n + num_d + num_s)):]:
        all_bricks_type.append(L)

    all_bricks = all_bricks_type

    random.shuffle(all_bricks)  # randomize the order of the bricks list

    # Create the board data structure, with randomly placed bricks as keys and their state (True) as value.
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append({'type': all_bricks[0], 'alive': True})
            del all_bricks[0]  # remove the bricks as we assign them
        board.append(column)
    return board


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BRICKWIDTH + GAPSIZE) + XMARGIN
    top = boxy * (BRICKHEIGHT + GAPSIZE) + YMARGIN
    return (left, top)


def drawBoard(mainBoard):
    # Draws all the boxes in their covered or revealed state.
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if mainBoard[boxx][boxy]['alive']:
                # Draw a brick.
                pygame.draw.rect(DISPLAYSURF, COLORS[mainBoard[boxx][boxy]['type']], (left, top, BRICKWIDTH, BRICKHEIGHT))


def drawPaddles(paddleX, paddleY):
    # Draw the two y-axis paddles
    pygame.draw.rect(DISPLAYSURF, BLUE, (PADDLEXMARGIN, paddleY, PADDLEHEIGHT, PADDLEWIDHT))
    pygame.draw.rect(DISPLAYSURF, BLUE, (WINDOWWIDTH - PADDLEXMARGIN - PADDLEHEIGHT, paddleY, PADDLEHEIGHT, PADDLEWIDHT))

    # Draw the two x-axis paddles
    pygame.draw.rect(DISPLAYSURF, BLUE, (paddleX, PADDLEYMARGIN + YHEADER, PADDLEWIDHT, PADDLEHEIGHT))
    pygame.draw.rect(DISPLAYSURF, BLUE, (paddleX, WINDOWHEIGHT - PADDLEYMARGIN - PADDLEHEIGHT, PADDLEWIDHT, PADDLEHEIGHT))


def isLegalState(paddle_x, paddle_y):
    return (paddle_x >= PADDLEXMARGIN and (paddle_x + PADDLEWIDHT) <= (WINDOWWIDTH - PADDLEXMARGIN)
            and paddle_y >= PADDLEYMARGIN + YHEADER and (paddle_y + PADDLEWIDHT) <= (WINDOWHEIGHT - PADDLEYMARGIN))

def isLegalBallState(x, y):
    return (x >= PADDLEXMARGIN + PADDLEHEIGHT / 2 and x <= (WINDOWWIDTH - PADDLEXMARGIN + PADDLEHEIGHT / 2)
            and y >= PADDLEYMARGIN + YHEADER + PADDLEHEIGHT / 2 and y <= (WINDOWHEIGHT - PADDLEYMARGIN + PADDLEHEIGHT / 2))

def drawBall(posX, posY):
    pygame.draw.circle(DISPLAYSURF, WHITE, (posX, posY), BALLRADIUS)

def generateBallPos():
    range1_x = range(PADDLEXMARGIN + PADDLEHEIGHT + BALLRADIUS * 2, XMARGIN - BALLRADIUS * 2 + 1)
    range2_x = range(WINDOWWIDTH - XMARGIN + BALLRADIUS * 2, WINDOWWIDTH - PADDLEXMARGIN - PADDLEHEIGHT + 1 - BALLRADIUS * 2 + 1)
    range1_y = range(PADDLEYMARGIN + PADDLEHEIGHT + YHEADER + BALLRADIUS * 2, YMARGIN + YHEADER + 1 - BALLRADIUS * 2 + 1)
    range2_y = range(WINDOWWIDTH-YMARGIN + BALLRADIUS * 2, WINDOWHEIGHT - PADDLEYMARGIN - PADDLEHEIGHT - BALLRADIUS * 2 + 1)

    return random.choice(list(range1_x) + list(range2_x)), random.choice(list(range1_y) + list(range2_y)) # return x and y of ball

def check_bricks_collision(mainBoard, posX, posY):
    global SCORE, DEADLY, BALLSPEEDX, BALLSPEEDY
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if mainBoard[boxx][boxy]['alive']:
                if pygame.Rect(left, top, BRICKWIDTH, BRICKHEIGHT).colliderect(pygame.Rect(posX - BALLRADIUS, posY - BALLRADIUS, BALLRADIUS * 2, BALLRADIUS * 2)):
                    mainBoard[boxx][boxy]['alive'] = False
                    if mainBoard[boxx][boxy]['type'] == N:
                        SCORE += 1
                    elif mainBoard[boxx][boxy]['type'] == D:
                        DEADLY = True
                    elif mainBoard[boxx][boxy]['type'] == L:
                        SCORE -= 1
                    elif mainBoard[boxx][boxy]['type'] == S:
                        BALLSPEEDX *= 1.5
                        BALLSPEEDY *= 1.5
                    return True

def check_paddles_collision(paddleX, paddleY, posX, posY):
    v1 = pygame.Rect(PADDLEXMARGIN, paddleY, PADDLEHEIGHT, PADDLEWIDHT)
    v2 = pygame.Rect(WINDOWWIDTH - PADDLEXMARGIN - PADDLEHEIGHT, paddleY, PADDLEHEIGHT, PADDLEWIDHT)
    h1 = pygame.Rect(paddleX, PADDLEYMARGIN + YHEADER, PADDLEWIDHT, PADDLEHEIGHT)
    h2 = pygame.Rect(paddleX, WINDOWHEIGHT - PADDLEYMARGIN - PADDLEHEIGHT, PADDLEWIDHT, PADDLEHEIGHT)
    ball = pygame.Rect(posX - BALLRADIUS, posY - BALLRADIUS, BALLRADIUS * 2, BALLRADIUS * 2)
    return v1.collidepoint((posX, posY)) or v2.collidepoint((posX, posY)) or h1.collidepoint((posX, posY)) or h2.collidepoint((posX, posY))

def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    DISPLAYSURF.blit(surface, rect)


def display_end_screen(message, font):
    DISPLAYSURF.fill(BGCOLOR)
    draw_text(message, font, WHITE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 - 20, center=True)
    pygame.draw.rect(DISPLAYSURF, WHITE, (WINDOWWIDTH // 2 - 75, WINDOWHEIGHT // 2 + 20, 150, 40))
    draw_text("Play Again", font, NAVYBLUE, WINDOWWIDTH // 2, WINDOWHEIGHT // 2 + 40, center=True)
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

def main():
    global FPSCLOCK, DISPLAYSURF, BALLSPEEDX, BALLSPEEDY, SCORE, DEALDY
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    pygame.display.set_caption('Bricks Breaker')

    font = pygame.font.SysFont(None, 36)

    bricksBorad = getRandomizedBoard()

    paddle_x = (PADDLEXMARGIN + (WINDOWWIDTH - PADDLEXMARGIN)) // 2 - (PADDLEWIDHT/2)
    paddle_y = (PADDLEYMARGIN + (WINDOWHEIGHT - PADDLEYMARGIN)) // 2 - (PADDLEHEIGHT/2)

    ball_pos_x, ball_pos_y = generateBallPos()

    DISPLAYSURF.fill(BGCOLOR)

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(bricksBorad)
        drawPaddles(paddle_x, paddle_y)
        drawBall(ball_pos_x, ball_pos_y)
        draw_text(f'Score: {SCORE}', font, WHITE, PADDLEXMARGIN, PADDLEYMARGIN)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

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

        if check_bricks_collision(bricksBorad, ball_pos_x, ball_pos_y) or check_paddles_collision(paddle_x, paddle_y, ball_pos_x, ball_pos_y):
            if random.randint(0, 1) > 0.5:
                BALLSPEEDX = -BALLSPEEDX
            else:
                BALLSPEEDY = -BALLSPEEDY

        ball_pos_x += BALLSPEEDX
        ball_pos_y += BALLSPEEDY

        if not isLegalBallState(ball_pos_x, ball_pos_y) or DEALDY:
            display_end_screen('You scored', font)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    main()