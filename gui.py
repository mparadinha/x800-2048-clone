# last edited on 27-12-2015 by Miguel Paradinha

"""This module contains the classes and functions associated with
the start menu where you can:
    - choose an existing profile
    - create a new one"""

import os
import tkinter
from tkinter.constants import *

from importlib import import_module

main_game = import_module("2048")
from tools import setup, load_profile, save_profile, preview

class StartMenu:

    def __init__(self):

        self.root = tkinter.Tk()
        self.root.title("x800 - Start Menu")
        self.path = os.getcwd()
        self.profile_path = os.path.join(self.path, "profiles")
        self.profiles = self.get_profile_list()
        self.pf_to_load = tkinter.StringVar()
        self.pf_to_load.set("default") # set default start value

        # frames
        self.load_frame = tkinter.LabelFrame(self.root, text="1. Load existing profile")
        self.create_frame = tkinter.LabelFrame(self.root, text="2. Create a new profile")
                                        
        # top load frame widgets
        self.profile_options = tkinter.OptionMenu(*(self.load_frame, self.pf_to_load) + tuple(self.profiles))
        self.load_button = tkinter.Button(self.load_frame, text="LOAD PROFILE", command=self.launch_game)
        self.edit_button = tkinter.Button(self.load_frame, text="EDIT PROFILE", command=self.edit_profile)
        self.reset_button = tkinter.Button(self.load_frame, text="RESET SCORE", command=self.reset_profile)

        # create lower frame button
        self.create_button = tkinter.Button(self.create_frame, text="CREATE NEW PROFILE", command=self.create_profile)

    def launch_game(self):
        """Closes app and calls the main function from the 2048.py module to start the game"""
        
        self.root.destroy()
        main_game.main(profile=self.pf_to_load.get())

    def edit_profile(self):
        """Closes app and calls the create menu with the special keyword argument 'load'
        set to the current selected profile"""

        self.root.destroy()
        CreateMenu(load=self.pf_to_load.get()).run()

    def reset_profile(self):
        """Resets the best_score to 0 on the profile file.
        Displays a pop-up informing that the profile has been reset"""

        pf = load_profile(profile_name=self.pf_to_load.get()) # get profile
        pf["best_score"] = 0 # reset score
        save_profile(pf, pf["user"]) # save profile

        # initialize pop up
        pop_up = tkinter.Toplevel()
        pop_up.title("Profile reset")

        # get message to display and pack the widgets
        tkinter.Message(pop_up, text="Profile '{}' has been reset.".format(pf["user"])).pack()
        tkinter.Button(pop_up, text="Dismiss", command=pop_up.destroy).pack()
    
    def get_profile_list(self):
        """Get the list of profiles from the correct directory"""
        
        return [pf.replace(".txt", "") for pf in os.listdir(self.profile_path) if ".txt" in pf]

    def create_profile(self):
        """Function to be called by the 'create new' button"""

        self.root.destroy()
        CreateMenu().run()

    def build(self):
        """Packs the widgets"""
        
        # pack top 'load' frame widgets
        self.load_frame.pack(fill=X, padx=5, pady=5)
        
        self.profile_options.grid(row=0, columnspan=3, sticky=W+E)
        self.load_button.grid(row=1, column=0)
        self.edit_button.grid(row=1, column=1)
        self.reset_button.grid(row=1, column=2)

        # pack lower frame and button widget
        self.create_frame.pack(fill=X, padx=5, pady=5)
        self.create_button.pack()

    def run(self):
        """Starts application"""
        
        self.build()
        self.root.mainloop()

class CreateMenu:
    """Menu used to create a new profile or edit an existing one"""

    def __init__(self, load="default"):

        self.root = tkinter.Tk()
        self.root.title("x800 - Profile creation")
        self.packages_path = os.path.join(os.getcwd(), "packages")

        self.save_button = tkinter.Button(self.root, text="SAVE", command=self.save)
        self.preview_button = tkinter.Button(self.root, text="PREVIEW", command=self.show_preview)

        self.fields = ["user", "tile_set_name", "board_color", "bg_color", "text_color", "score_msg"]
        self.label_text = ["User name",
                           "Tile Set",
                           "Board Color (RGB)",
                           "Background color (RGB)",
                           "Text Color (RGB)",
                           "Score text"]
        
        self.default_profile = load_profile(profile_name=load) # function from tools module

        self.widgets = [] # list containing dictionaries for the entry widgets

        for i, field in enumerate(self.fields):
            df_text_var = tkinter.StringVar(value=repr(self.default_profile[field]).replace("'", ""))
            self.widgets.append({"field": field,
                                 "entry": tkinter.Entry(self.root, justify=LEFT, textvariable=df_text_var),
                                 "label": tkinter.Label(self.root, text=self.label_text[i])})
            
        # gets all folder names from 'packages' directory
        self.tile_set_list = [pkg for pkg in os.listdir(self.packages_path)
                              if os.path.isdir(os.path.join(self.packages_path, pkg))]

        # change the widget for the tile set to have a options menu instead of an entry object
        self.tile_set_var = tkinter.StringVar(value="default")
        self.widgets[1]["entry"] = tkinter.OptionMenu(*(self.root, self.tile_set_var) + tuple(self.tile_set_list))
            
    def get_profile_dict(self):
        """Returns a profile dictionary of the current chossen options
        Serves as helper functions for 'save' and 'show_preview'"""

        return {"user": self.widgets[0]["entry"].get(),
                "tile_set_name": self.tile_set_var.get(),
                "board_color": eval(self.widgets[2]["entry"].get()),
                "bg_color": eval(self.widgets[3]["entry"].get()),
                "text_color": eval(self.widgets[4]["entry"].get()),
                "score_msg": self.widgets[5]["entry"].get()}

    def save(self):
        """Saves profile, exits app and start load menu again"""

        # get dictionary for saving, before destroying application
        self.profile_to_save = self.get_profile_dict()
        
        self.root.destroy()
        
        # save profile
        save_profile(self.profile_to_save, self.profile_to_save["user"])
        
        StartMenu().run()

    def show_preview(self):
        """Calls function preview from the tools module"""

        preview(self.get_profile_dict())

    def build(self):
        """Packs widgets"""

        # put widgets in grid
        for i, widget in enumerate(self.widgets):
            widget["label"].grid(row=i, column=0)
            widget["entry"].grid(row=i, column=1)

        # put the save and preview buttons on the bottom
        self.save_button.grid(row=6, column=0)
        self.preview_button.grid(row=6, column=1)

    def run(self):
        """Starts menu application"""
        
        self.build()
        self.root.mainloop()

if __name__ == "__main__":
    setup() # make sure everything is ok
    StartMenu().run()
