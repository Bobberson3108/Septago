import arcade
from engine import Engine

SCREEN_WIDTH = 885
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Septago"

PIECE_RADIUS = 20
SPOT_RADIUS = int(PIECE_RADIUS*1.2)

MARGIN_PERCENT = 0.25

SPOT_START_X = (SCREEN_WIDTH - (9)*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT) + 18*3)//2
SPOT_START_Y = SCREEN_HEIGHT - (SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT)

START_X = SPOT_START_X + (4)*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT) + 18
START_Y = 150

class Piece(arcade.SpriteCircle):
    def __init__(self, player):
        self.player = player
        colour = arcade.color.BLACK if player == 1 else arcade.color.WHITE

        super().__init__(PIECE_RADIUS, colour)

class Spot(arcade.SpriteCircle):
    def __init__(self, board_index, *args):
        self.board_index = board_index
        
        super().__init__(*args)

class PentagoWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.color.CHARLESTON_GREEN)
        self.held_piece = None
        self.engine = Engine()

        self.placed = False
        self.selected_quadrant = None

        print(self.engine.game_state())

    def set_piece_to_play(self):
        self.piece_to_play = Piece(player=self.engine.next_player)
        self.piece_to_play.position = (START_X, START_Y)
    
    def setup(self):
        self.set_piece_to_play()
        self.board_pieces = arcade.SpriteList()
        self.debug_text = []

    
        # for i in range(3):
        #     for j in range(9):
        #         piece1 = Piece(player=1)
        #         piece1.position = (START_X + j*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT), START_Y + i*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT))

        #         self.player1_pieces.append(piece1)

        #         piece2 = Piece(player=2)
        #         piece2.position = (START_X + (7+j)*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT), START_Y + i*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT))

        #         self.player2_pieces.append(piece2)
        
        self.spot_list = arcade.SpriteList()

        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        spot = Spot((i+l*3, k*3+j), SPOT_RADIUS, arcade.csscolor.DARK_SLATE_GREY)
                        spot.position = SPOT_START_X + (i+3*l)*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT) + 18*l, SPOT_START_Y - (j+3*k)*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT) - 18*k
                        self.debug_text.append(arcade.Text(f"{spot.board_index}", spot.center_x, spot.center_y))

                        self.spot_list.append(spot)

                        # spot = Spot((5-i, k*3 + j), SPOT_RADIUS, arcade.csscolor.DARK_SLATE_GREY)
                        # spot.position = SCREEN_WIDTH - (SPOT_START_X + i*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT)), SPOT_START_Y - (j+3*k)*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT) - 18*k

                        # self.spot_list.append(spot)
                        self.debug_text.append(arcade.Text(f"{spot.board_index}", spot.center_x, spot.center_y))

    def get_spot_by_index(self, i, j):
        for spot in self.spot_list:
            if spot.board_index == (i, j):
                return spot

        raise ValueError("SPOT NOT FOUND")

    def place_board(self):
        self.board_pieces.clear()
        for i, row in enumerate(self.engine.board):
            for j, player in enumerate(row):
                if player:
                    spot = self.get_spot_by_index(i, j)
                    piece = Piece(player)
                    piece.position = spot.position

                    self.board_pieces.append(piece)

    def on_draw(self):
        self.clear()

        self.spot_list.draw()
        self.board_pieces.draw()
        self.piece_to_play.draw()

        # for text in self.debug_text:
        #     text.draw()


    def on_mouse_press(self, x, y, button, key_modifiers):
        if self.piece_to_play.collides_with_point((x,y)):
            self.held_piece = self.piece_to_play
            self.held_piece_original_position = self.held_piece.position

    def on_mouse_release(self, x, y, button, modifiers):
        if self.held_piece == None:
            return
        
        spot, _ = arcade.get_closest_sprite(self.held_piece, self.spot_list)
        
        if arcade.check_for_collision(self.held_piece, spot) and not self.engine.board[spot.board_index]:
            self.held_piece.position = spot.center_x, spot.center_y
            self.placed_piece = self.held_piece
            self.placed = True
            self.place_index = spot.board_index
        else:
            self.held_piece.position = self.held_piece_original_position
        
        self.held_piece = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.held_piece:
            self.held_piece.center_x += dx
            self.held_piece.center_y += dy
    
    def on_key_press(self, key, modifiers):
        if not self.placed:
            return
        
        keyboard_keys = [arcade.key.KEY_1,arcade.key.KEY_2,arcade.key.KEY_3,arcade.key.KEY_4,arcade.key.KEY_5,arcade.key.KEY_6,arcade.key.KEY_7,arcade.key.KEY_8,arcade.key.KEY_9]
        numpad_keys = [arcade.key.NUM_0,arcade.key.NUM_1,arcade.key.NUM_2,arcade.key.NUM_3,arcade.key.NUM_4,arcade.key.NUM_5,arcade.key.NUM_6,arcade.key.NUM_7,arcade.key.NUM_8,arcade.key.NUM_9]
        if key in keyboard_keys:
            self.selected_quadrant = keyboard_keys.index(key) + 1
        elif key in numpad_keys:
            self.selected_quadrant = numpad_keys.index(key) + 1
        else:
            if self.selected_quadrant != None:
                if key == arcade.key.C:
                    self.selected_direction = "CLOCKWISE"
                elif key == arcade.key.A:
                    self.selected_direction = "ANTICLOCKWISE"
                else:
                    return

                self.engine.move(self.place_index, self.selected_quadrant, self.selected_direction)
                self.place_board()

                self.placed = False
                self.selected_quadrant = None
                self.set_piece_to_play()

                print(self.engine.game_state())





def main():
    window = PentagoWindow()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()