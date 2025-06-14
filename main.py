from gameplay import Battleships 

def main():
    while True:
        #gameplay 
        game1 = Battleships() # create class Instanz --> also initiates game
        game1.game_intro_message() 
        game1.generate_zero_matrix() # our battlefield 
        game1.render_player_field() 
        input("Press enter to continue...")
        game1.clear_screen() 
        game1.player_select_ships()
        game1.enemy_select_ships()
        game1.battle_game_play()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame interrupted. Exiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Exiting the game due to an error.")