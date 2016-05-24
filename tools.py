#last edited on 27-12-2015 by Miguel Paradinha

"""This module contains some tools to be used by the main script
at 2048.py. Can be used to check if default image dictionary is presente
and create one if necessary. Handles saving and loading of settings"""

import os
import sys

import pygame
from pygame.locals import *

def setup():
    """Run tests and make sure eveything needed is present at the right place"""

    pygame.init() # initialize pygame

    ensure_default_package()

    ensure_default_profile()

def ensure_default_package():
    """Checks if the default image folder exists, and if it is usable.
    Creates a new one if it is missing"""

    pkg_folder = os.path.join(os.getcwd(), "packages")
    pkg_path = os.path.join(pkg_folder, "default")

    if not os.path.isdir(pkg_folder):
        os.mkdir(pkg_folder) # create packages folder
    if not os.path.isdir(pkg_path):
        os.mkdir(pkg_path)

    # get the missing tiles if directory exists and is incomplete
    missing = []
    for tile_num in [0] + [2**x for x in range(1, 12)]:
        if not os.path.exists(os.path.join(pkg_path, "{}.png".format(tile_num))):
            missing.append(tile_num)

    for tile in missing:

        # if tile 0 is missing save as grey tile
        if tile == 0:

            tile_surf = pygame.Surface((96, 96))
            tile_surf.fill((130, 130, 130))
            pygame.image.save(tile_surf, os.path.join(pkg_path, "{}.png".format(tile)))
            continue # move on to next iteration of for loop AKA next tile

        # save image as a .png
        pygame.image.save(tile_gen(tile), os.path.join(pkg_path, "{}.png".format(tile)))

def ensure_default_profile():
    """Checks if the default profile exists and is complete, if not creates a new one"""

    profile_path = os.path.join(os.getcwd(), "profiles")

    default_profile = {"user": "default",
                       "bg_color": (255, 255, 255),
                       "board_color": (255, 255, 255),
                       "text_color": (0, 0, 0),
                       "best_score": 0,
                       "games_won": 0,
                       "games_played": 0,
                       "tile_set_name": "default",
                       "score_msg": "Score: {}    Best: {}"}

    # if folder does not exists create new folder and file
    if not os.path.exists(profile_path):

        # create folder
        os.mkdir(profile_path)

        # save default dictionary
        save_profile(default_profile, "default")

    elif not os.path.exists(os.path.join(profile_path, "default.txt")):
        save_profile(default_profile, "default")

    elif load_profile() != default_profile:
        save_profile(default_profile, "default")

def save_profile(data, profile_name):
    """Saves the data dictionary to the folder at 'profiles//profile_name.txt' """

    profile_path = os.path.join(os.getcwd(), "profiles", profile_name)

    with open("{}.txt".format(profile_path), "w") as pf:
        for k in sorted(data.keys()):
            pf.write("{}={}\n".format(k, repr(data[k])))

def load_profile(profile_name="default"):
    """Returns a dictionary representing the profile save at 'profiles//profile_name.txt'"""

    profile_path = os.path.join(os.getcwd(), "profiles", profile_name)

    with open("{}.txt".format(profile_path), "r") as pf:
        data = [line for line in pf.read().split("\n") if line]

    if profile_name != "default":
        df = load_profile()

    else:
        df = {}

    # get a dictionary from the pairs in the file
    pf = dict([tuple(line.split("=")) for line in data])

    # set each setting to its correct type
    pf = {key: eval(value) for key, value in list(pf.items())}

    for k in list(df.keys()):

        # if there are atributtes missing set them to the default ones
        if k not in list(pf.keys()): pf[k] = df[k] # add to pf

        # if they are the wrong type, e.g should be tuple and is integer, use default instead
        elif type(df[k]) != type(pf[k]): pf[k] = df[k]

    return pf

def load_package(package_name="default"):
    """Returns a dict that where the keys are the powers of two,
    and the values are the corresponding pygame.Surface object"""

    pkg_path = os.path.join(os.getcwd(), "packages", package_name)

    if package_name != "default":
        images = load_package()

    else:
        images = {}

    for img in os.listdir(pkg_path):

        if img != "desktop.ini": #ignore 'desktop.ini' file created by google drive
            images[int(img.replace(".png", ""))] = pygame.image.load(os.path.join(pkg_path, img))

    return images

def tile_gen(number, font_size=45, tile_color=(139, 71, 93)):
    """Generates and returns the pygame surface corresponding to the tile with this number"""

    tile_surf = pygame.Surface((96, 96))

    # make the numbers smaller if needed
    while pygame.font.SysFont("monospace", font_size).size(str(number))[0] > 92:
        font_size -= 1

    tile_text = pygame.font.SysFont("monospace", font_size).render(str(number), 1, (255, 255, 255), tile_color)

    tile_surf.fill(tile_color)
    # blit text at center of tile
    tile_surf.blit(tile_text, (tile_text.get_rect(center=tile_surf.get_rect().center)))

    return tile_surf

def preview(profile):
    """Runs a mini window displaying a small version of the board with the given profile"""

    # setup pygame variables
    pygame.init()
    screen = pygame.display.set_mode((160, 160))
    pygame.display.set_caption("x800 - board preview")
    fpsClock = pygame.time.Clock()

    # get mini board surface
    board = pygame.Surface((110, 110))
    board.fill(profile["board_color"])

    # get 0 tile surface for blitting
    tile = load_package(package_name=profile["tile_set_name"])[0]

    # get text surface
    text = pygame.font.SysFont("monospace", 20).render("TEXT", 1, profile["text_color"], profile["bg_color"])

    while True:

        screen.fill(profile["bg_color"])

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        # blit 0 tile at center of the board
        board.blit(tile, tile.get_rect(center=board.get_rect().center))

        # blit board at center of the screen
        screen.blit(board, board.get_rect(center=screen.get_rect().center))

        # blit text on top of the board
        screen.blit(text, text.get_rect(midbottom=board.get_rect(center=screen.get_rect().center).midtop))

        # update screen and clock
        pygame.display.flip()
        fpsClock.tick(60)

if __name__ == "__main__":
    # if module is run on it's own, do the setup checks
    setup()
