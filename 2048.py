# last edited on 27-12-2015 by Miguel Paradinha

"""This is a clone of the popular '2048' online game
which can be played here: https://gabrielecirulli.github.io/2048/
This application supports the addition of new tile sets
via images (in the .png format) named after the numbers they
represent placed on a folder with the package name, on the 'packages' folder"""

import sys
import os
from itertools import product
from random import randrange, choice

import pygame
from pygame.locals import *

from tools import setup, load_package, save_profile, load_profile, tile_gen

def main(profile="default"):
    """Main function that is run to start application"""
    global SCORE, PROFILE

    # run setup, check if everything is alright
    setup()

    # load profile
    PROFILE = load_profile(profile_name=profile)

    # initialize board and score
    board = [[0]*4 for i in range(4)]
    SCORE = 0

    # initialize pygame
    pygame.init()
    fpsClock = pygame.time.Clock()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("x800 - a 2048 clone")

    # back button surface
    back_button = pygame.font.SysFont("monospace", 25).render(" <> Back to menu", 1, PROFILE["text_color"], PROFILE["bg_color"])

    # load default tile set
    tile_set = load_package(PROFILE["tile_set_name"])

    # set first random tile
    board[randrange(4)][randrange(4)] = choice([2, 4])

    # varible to know the state of the game
    game_state = "normal"    

    # main loop
    while True:

        if game_over(board):          
            if pop_up(screen, fpsClock, msg="Play again? (y/n)"):

                # reset game
                board = [[0]*4 for i in range(4)] # reset board
                SCORE = 0 # reset score
                board[randrange(4)][randrange(4)] = choice([2, 4]) # set 1st random tile 
                screen.fill(PROFILE["bg_color"]) # fill with background color

            else:
                terminate()

        elif game_won(board) and game_state != "won+":
            game_state = "won"
            if pop_up(screen, fpsClock, msg="You winner! Continue? (y/n)"):
                game_state = "won+"

            else:

                # reset game
                board = [[0]*4 for i in range(4)] # reset board
                SCORE = 0 # reset score
                board[randrange(4)][randrange(4)] = choice([2, 4]) # set 1st random tile 
                screen.fill(PROFILE["bg_color"]) # fill with background color

        # update best score if needed
        if SCORE > PROFILE["best_score"]: PROFILE["best_score"] = SCORE

        # event loop
        for event in pygame.event.get():
            if event.type == QUIT: terminate()

            # when a key is unpressed move the board
            elif event.type == KEYUP:
                if event.key == K_UP:
                    board = move(board, "UP")

                elif event.key == K_DOWN:
                    board = move(board, "DOWN")

                elif event.key == K_LEFT:
                    board = move(board, "LEFT")

                elif event.key == K_RIGHT:
                    board = move(board, "RIGHT")

            # when the mouse is clicked
            elif event.type == MOUSEBUTTONUP:
                # if button was clicked
                if back_button.get_rect(bottomleft=screen.get_rect().bottomleft).collidepoint(pygame.mouse.get_pos()):
                    terminate(load=True)
        
        screen.fill(PROFILE["bg_color"]) # background color

        # blit the board surface to the center of the screen
        board_surf = get_board_surf(board, tile_set)
        board_pos = board_surf.get_rect(center=screen.get_rect().center)
        screen.blit(board_surf, board_pos)
        
        # get score surface and blit to the top
        score_surf = get_score_surf(SCORE, best=PROFILE["best_score"], msg=PROFILE["score_msg"])
        score_pos = score_surf.get_rect(midbottom=board_pos.midtop)
        screen.blit(score_surf, score_pos)

        # get and blit greetting text and top of score
        greetting_surf = get_user_surf()
        greetting_pos = greetting_surf.get_rect(midbottom=score_pos.midtop)
        screen.blit(greetting_surf, greetting_pos)

        # blit back button surface
        screen.blit(back_button, back_button.get_rect(bottomleft=(screen.get_rect().bottomleft)))
        
        # update screen and game clock
        pygame.display.flip()
        fpsClock.tick(60) # FPS = 60

def terminate(save=True, load=False):
    """Saves data to profile
    Closes pygame and exits the program"""

    # save data
    if save: save_profile(PROFILE, PROFILE["user"])
         
    # close program
    pygame.quit()
    if load:
        
        from gui import StartMenu
        StartMenu().run()
        
    sys.exit()

def game_won(board, limit=2048):
    """Checks if the limit (defaults to 2048) was reached"""

    for row in board:
        for tile in row:
            if tile == limit: return True

    return False

def game_over(board):
    """Checks if there are no more possible moves and if the board is full"""

    # if there is at least one 0 on the board, then it's not game over
    for row in board:
        for num in row:
            if num == 0: return False

    # check if calling move(board, ...) makes a diference
    for direction in ["UP", "DOWN", "LEFT", "DOWN"]:
        if board != move(board, direction, count=False): return False

    # if both tests above do not return False, then it's game over
    return True

def pop_up(screen, fpsClock, msg="(y/n)"):
    """Display a pop up message at the center of the screen with the string 'msg'.
    Returns True if user presses the 'y' key and False if the 'n' key is pressed"""

    text_surf = pygame.font.SysFont("monospace", 30).render(msg, 1, PROFILE["text_color"], PROFILE["bg_color"])

    # menu loop
    while True:

        for event in pygame.event.get():
            if event.type == QUIT: terminate()

            elif event.type == KEYUP:
                if event.key == K_y:
                    return True

                elif event.key == K_n:
                    return False

        screen.blit(text_surf, text_surf.get_rect(center=screen.get_rect().center))

        # update screen and game clock
        pygame.display.flip()
        fpsClock.tick(60) # FPS = 60

def move(board, direction, count=True):
    """Returns a new version of the board after collapsing all the rows
    and collumns in the right fashion, according to the direction argument.
    score is incremented with the formed numbers"""
    
    if direction == "UP":
        new_board = transpose([list(reversed(collapsed(list(reversed(row)), count))) for row in transpose(board)])

    elif direction == "DOWN":
        new_board = transpose([collapsed(row, count) for row in transpose(board)])

    elif direction == "LEFT":
        new_board = [list(reversed(collapsed(list(reversed(row)), count))) for row in board]

    elif direction == "RIGHT":
        new_board = [collapsed(row, count) for row in board]

    if board != new_board:
        insert_random(new_board)

    return new_board

def insert_random(board):
    """Places, if possible a new tile on the board.
    Does NOT return a new board list"""

    empty_tiles = [(x, y) for x, y in product(list(range(4)), repeat=2) if board[y][x] == 0]
    if empty_tiles != []: # same as 'if len(empty_tiles) > 0:'

        x, y = choice(empty_tiles)
        board[y][x] = choice([2, 4])

def transpose(board):
    """Return the transposed version of the board matrix
    Transposition is done just like in normal algebra"""
    
    trans = [[0]*4 for _ in range(len(board))]
    for i, j in product(list(range(4)), repeat=2):
        trans[j][i] = board[i][j]

    return trans
    
def collapsed(lst, count=True):
    """Returns the row list in 'collapsed' form
    This always collapses to the right, so change the entry accordingly
    e.g. collapsed([4, 0, 2, 2]) -> [0, 0, 4, 4]"""
    global SCORE

    row = [x for x in lst] # copy lst to row

    # 'push' the numbers to the right
    row = push_to_right(row)
    
    if row[2] == row[3]:
        row[2], row[3] = 0, row[2] + row[3] # add the two together and place on row[3]
        if count: SCORE += row[3]

        if row[0] == row[1]:
            row[0], row[1] = 0, row[0] + row[1] # add the two together and place on row[1]
            if count: SCORE += row[1]

    elif row[1] == row[2]:
        row[1], row[2] = 0, row[1] + row[2] # add the two together and place on row[2]
        if count: SCORE += row[2]

    elif row[0] == row[1]:
        row[0], row[1] = 0, row[0] + row[1] # add the two together and place on row[1]
        if count: SCORE += row[1]

    # 'push' again
    row = push_to_right(row)

    return row

def push_to_right(lst):
    """Helper function for collapsed function.
    Pushes all entries of row the farthest to the right as possible
    Returns a new row list
    e.g. push_to_right([4, 0, 2, 0]) -> [0, 0, 4, 2]"""
    
    row = [x for x in lst]
    
    for _ in range(len(row) - 1):
        for i in range(len(row) - 1):
            if row[i + 1] == 0:
                row[i], row[i + 1] = row[i + 1], row[i]

    return row

def get_user_surf(msg="Hi there {}"):
    """Returns the text surface for blitting using the provided message"""

    return pygame.font.SysFont("monospace", 25).render(msg.format(PROFILE["user"]), 1, PROFILE["text_color"], PROFILE["bg_color"])

def get_score_surf(score, msg="Score: {}", best=""):
    """Returns the text surface for blitting using the provided message"""
    global SCORE

    return pygame.font.SysFont("monospace", 25).render(msg.format(SCORE, best), 1, PROFILE["text_color"], PROFILE["bg_color"])

def get_board_surf(board, img_dict):
    """Returns a pygame Surface of the board to use for blitting afterwards"""

    board_surf = pygame.Surface((410, 410))
    board_surf.fill(PROFILE["board_color"])

    for x in range(4):
        for y in range(4):

            try:
                board_surf.blit(img_dict[board[y][x]], (4 + 102*x,4 + 102*y))

            # if the number is bigger than 2048 create the needed tile surface
            except KeyError:

                # get the new tile surface using tile_gen function from tools module at tools.py
                # and blit to the board like the other tiles
                board_surf.blit(tile_gen(board[y][x]), (4 + 102*x,4 + 102*y))

    return board_surf
    
if __name__ == "__main__":
    main()
