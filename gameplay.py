import pyfiglet # -->fonts
import string
import numpy as np
import random
import os 
import time

class Battleships:
    def __init__(self):
        self.clear_screen() 

        self.GREEN = "\033[92m" 
        self.RED = "\033[91m" 
        self.YELLOW = "\033[93m" 
        self.BLUE = "\033[94m" 
        self.MAGENTA = "\033[95m" 
        self.RESET = "\033[0m" # reset to default color

        # welcome message
        print(f"{self.BLUE}{pyfiglet.figlet_format("Battle Ships!")}{self.RESET}")

        # exit possibility
        print(f"To exit and close the game at any time, please press {self.YELLOW}Ctrl + C{self.RESET}.")
        print()

        # get and display player name
        self.player_name = input("Type in your player name: ").strip()  
        if not self.player_name:
            self.player_name = "Anonymous"  # default name if no input is given

        # clear screen after getting player name
        self.clear_screen()

        print(f"{self.GREEN}{pyfiglet.figlet_format(f"Ahoi {self.player_name}!", font = "slant")}{self.RESET}")
        time.sleep(0.5) # wait some time

        # vars
        self.grid_size = 0
        self.matrix = None
        self.no_of_ships = 0
        self.columns = {} # for translation 
        self.column_i = None
        self.player_ships_amount_game = 0
        self.enemy_ships_amount_game = 0
        self.enemy_rm_strat_memory = []
        self._render_hit_map_dict = {
            1:f"{self.MAGENTA}{self.player_name[0]}{self.RESET}", # player ships, first letter of player name 
            3:f"{self.RED}!{self.RESET}", 
            2:f"{self.GREEN}X{self.RESET}",
            -2:f"{self.BLUE}O{self.RESET}",
            0:f"{self.BLUE}~{self.RESET}",
        } # for rendering the map 

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear') # clear screen --> for windows and unix

    def game_intro_message(self):
        # game play message
        print(f"It's the year 5318008 and you {self.player_name} are the navy admiral of the Chocolate Chip nation.")
        print("All but one fleet have lost their battles...")
        time.sleep(0.5) 
        print()
        print(f"It is up to the one and only admiral {self.player_name} to place and attack ships in right waters.")
        print("All will be lost if you fail to win this cookie monster war!!")
        time.sleep(0.5) 
        print()
        input("Press enter to continue...")

        self.clear_screen() 

        print()
        print(f"As admiral {self.player_name} you must select the grid size of the final battle...")
        print()
        time.sleep(0.5) 

        while True:
            self.grid_size = self._handle_int_input("Type in the amount of rows (min 2, max 26): ")
            if 2 <= self.grid_size <= 26:
                break
            print("Invalid input. Please enter a number between 2 and 26.")

        print()
        print(f"Your selected grid size: {self.grid_size}x{self.grid_size}")
        print()

        self.column_i = list(string.ascii_uppercase)[:self.grid_size] 
        time.sleep(0.5) # wait some time (for drama...)

    def _handle_int_input(self, message): 
        while True:
            try:
                user_input = float(input(message).strip().upper())
                if user_input.is_integer():
                    return int(user_input)
                print("Please enter a whole number (e.g. 1 or 1.0) no fractions!")
            except ValueError:
                print("Invalid input. Please enter a whole int number.")

    def generate_zero_matrix(self):
        self.matrix = np.zeros((self.grid_size, self.grid_size), dtype=int)

    def render_player_field(self):
        print(pyfiglet.figlet_format(f"Battlefield", font = "bubble")) 

        row_zero = f"-- " 
        for no, i in enumerate(self.column_i):
            row_zero = row_zero + i + " "
            self.columns[i] = no
        
        print(row_zero) # render row_zero

        for i, z in enumerate(self.column_i): 
            if i < 10:
                current_row = f"0{i} "
            elif i >= 10:
                current_row = f"{i} "
            for y in range(len(self.column_i)):
                # render logic: try to render player ships, ..., if enemy ship hit detected, render enemy ship
                try:
                    current_row = current_row + self._render_hit_map_dict[self.matrix[y,i]] + " " # seems kinda dirty --> maybe find cleaner solution later 
                except:
                    current_row = current_row + f"{self.BLUE}~{self.RESET}" + " "
            print(current_row)
        print()

    def _x_input_validation(self, x): # function to check if x input is valid
        if x in self.columns:
            return True
        else:
            return False
    
    def _y_input_validation(self, y, las_row): # function to check if y input is valid
        if 0 <= y <= las_row:
            return True
        else:
            return False

    def player_select_ships(self):
        self.render_player_field()
        self.no_of_ships = round(self.grid_size / 2)
        self.player_ships_amount_game = self.no_of_ships
        last_col = string.ascii_uppercase[self.grid_size - 1]
        last_row = self.grid_size - 1

        print(f"Please select your ships' positions. Total ships to allocate: {self.no_of_ships}")

        for i in range(self.no_of_ships):
            while True:
                # Get and validate X coordinate
                x = input(f"X coordinate of ship number {i+1}: Choose a letter between A and {last_col}: ").strip().upper()
                if not self._x_input_validation(x):
                    print("Invalid X coordinate!")
                    continue

                # Get and validate Y coordinate
                y = self._handle_int_input(f"Y coordinate of ship number {i+1}: Enter a number between 0 and {last_row}: ")
                if not self._y_input_validation(y, last_row):
                    print("Invalid Y coordinate!")
                    continue

                # Convert coordinates
                x_index = self.columns[x]
                y_index = int(y)

                # Check if the ship is already placed at that location
                if self.matrix[x_index, y_index] == 1:
                    print("Ship already placed there, please select another coordinate.")
                    print()
                    continue 

                # Place the ship
                self.matrix[x_index, y_index] = 1
                break  

            self.clear_screen()
            self.render_player_field()

        input("Ships placed successfully, press enter to continue...")
        self.clear_screen()

    def _check_hit(self, x, y, player):
        if self.matrix[x,y] == player:
            return True
        elif self.matrix[x,y] != player:
            return False

    def enemy_select_ships(self): # integrating smart select (not selecting where a ship is already placed)
        self.enemy_ships_amount_game = self.no_of_ships # init ships amount 
        for i in range(self.no_of_ships):
            x = random.randint(0, self.grid_size-1)
            y = random.randint(0, self.grid_size-1)

            overlap_player = self._check_hit(x,y,1)
            if overlap_player == False:
                self.matrix[x,y] = -1
            elif overlap_player == True:
                while True:
                    x = random.randint(0, self.grid_size - 1)
                    y = random.randint(0, self.grid_size - 1)
                    if self._check_hit(x,y,1) == False:
                        self.matrix[x,y] = -1
                        break
                    else:
                        pass

    def player_select_attack(self):
        print("Select your attack coordinates")
        last_col = string.ascii_uppercase[self.grid_size-1] # variable for the last column letter
        last_row = self.grid_size - 1 # variable for the last row number
        
        # X coordinate validation loop
        while True:
            x = input(f"X attack coordinate: Choose a letter between A and {last_col}: ").strip().upper()
            if self._x_input_validation(x):
                break
            print(f"Invalid X coordinate!!!")
        
        # Y coordinate validation loop
        while True:
            y = self._handle_int_input(f"Y attack coordinate: Please enter a number between 0 and {last_row}: ")
            if self._y_input_validation(y, last_row):
                break
            print(f"Invalid Y coordinate!!!")
        
        return x, y

    def enemie_select_attack_rmStrat(self): 
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if (x, y) not in self.enemy_rm_strat_memory:
                self.enemy_rm_strat_memory.append((x, y))
                return x, y

    def battle_game_round(self):
        # attack
        px, py = self.player_select_attack()
        ex, ey = self.enemie_select_attack_rmStrat()

        input("Attacks selected successfully, press enter to check results...")
        print()

        # check hits
        ph = self._check_hit(self.columns[px], int(py), -1) # this could be done more efficiently 
        sh = self._check_hit(self.columns[px], int(py), 1) # check if player hit self
        eh = self._check_hit(ex, ey, 1)
        
        if ph == True: 
            self.matrix[self.columns[px], int(py)] = 2
            self.enemy_ships_amount_game -= 1
            print(f"Good job admiral {self.player_name} you have hit an enemy ship!")
            print()

        if eh == True:
            self.matrix[ex, ey] = 3
            self.player_ships_amount_game -= 1
            print(f"UUUUUFFF! Admiral {self.player_name} you have been hit!")
            print()

        if sh == True:
            self.matrix[self.columns[px], int(py)] = 3
            self.player_ships_amount_game -= 1
            print(f"Admiral {self.player_name}, you have hit your own ship! You are a disgrace to the navy!")
            print()
        elif ph == False:
            self.matrix[self.columns[px], int(py)] = -2
            print(f"Admiral {self.player_name}, missed shot. You've hit empty waters!")
            print()

        input("Press enter to continue...") 
        self.clear_screen() 
    
    def battle_game_play(self): 
        print(f"{self.MAGENTA}{pyfiglet.figlet_format("Battle start!")}{self.RESET}")
        input("Press enter to start the battle...") 
        self.clear_screen()

        while True:
            if self.player_ships_amount_game == 0 or self.enemy_ships_amount_game == 0:
                break   
            self.render_player_field()
            self.battle_game_round()

        self.render_player_field()
        
        if self.player_ships_amount_game > self.enemy_ships_amount_game:
            print(f"{self.GREEN}{pyfiglet.figlet_format("Victory!")}{self.RESET}")
            print("Congratulations you've won!!")
        elif self.player_ships_amount_game < self.enemy_ships_amount_game:
            print(f"{self.RED}{pyfiglet.figlet_format("Defeat!")}{self.RESET}")
            print("All ships are lost... You and only you alone have failed, your nation is doomed...")
        else:
            print(f"{self.YELLOW}{pyfiglet.figlet_format("Draw!")}{self.RESET}")
            print(f"As the smoke clears, Admiral {self.player_name}, both navies drift in silence.")
            print("Cookies are crumbling, fuel is low, and the sea tastes vaguely of chocolate chips...")
            print("No victor today — only legends.")
            print("The Cookie Monster War ends in a bitter, buttery draw.")
        print()
        input("Press enter to restart the game...") 