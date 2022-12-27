import arcade
from engine import Engine

SCREEN_WIDTH = 885
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Pentago"

PIECE_RADIUS = 30
SPOT_RADIUS = int(PIECE_RADIUS*1.2)

MARGIN_PERCENT = 0.25

START_X = PIECE_RADIUS + PIECE_RADIUS*MARGIN_PERCENT
START_Y = PIECE_RADIUS + PIECE_RADIUS*MARGIN_PERCENT

SPOT_START_X = 230 #START_X + 3*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT)
SPOT_START_Y = SCREEN_HEIGHT - (SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT)

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
    
    def setup(self):
        self.player1_pieces = arcade.SpriteList()
        self.player2_pieces = arcade.SpriteList()
        self.board_pieces = arcade.SpriteList()
        self.debug_text = []

        for i in range(3):
            for j in range(6):
                piece1 = Piece(player=1)
                piece1.position = (START_X + j*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT), START_Y + i*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT))

                self.player1_pieces.append(piece1)

                piece2 = Piece(player=2)
                piece2.position = (START_X + (7+j)*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT), START_Y + i*(PIECE_RADIUS*2 + PIECE_RADIUS*MARGIN_PERCENT))

                self.player2_pieces.append(piece2)
        
        self.spot_list = arcade.SpriteList()

        for i in range(3):
            for j in range(3):
                for k in range(2):
                    spot = Spot((i, k*3 + j), SPOT_RADIUS, arcade.csscolor.DARK_SLATE_GREY)
                    spot.position = SPOT_START_X + i*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT), SPOT_START_Y - (j+3*k)*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT) - 18*k
                    self.debug_text.append(arcade.Text(f"{spot.board_index}", spot.center_x, spot.center_y))

                    self.spot_list.append(spot)

                    spot = Spot((5-i, k*3 + j), SPOT_RADIUS, arcade.csscolor.DARK_SLATE_GREY)
                    spot.position = SCREEN_WIDTH - (SPOT_START_X + i*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT)), SPOT_START_Y - (j+3*k)*(SPOT_RADIUS*2 + SPOT_RADIUS*MARGIN_PERCENT) - 18*k

                    self.spot_list.append(spot)
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
        self.player1_pieces.draw()
        self.player2_pieces.draw()

        # for text in self.debug_text:
        #     text.draw()
        
    def pull_to_top(self, piece):
        if piece.player == 1:
            self.player1_pieces.remove(piece)
            self.player1_pieces.append(piece)
        else:
            self.player2_pieces.remove(piece)
            self.player2_pieces.append(piece)

    def on_mouse_press(self, x, y, button, key_modifiers):
        if self.placed:
            return

        if self.engine.next_player == 1:
            pieces = arcade.get_sprites_at_point((x,y), self.player1_pieces)
        else:
            pieces = arcade.get_sprites_at_point((x,y), self.player2_pieces)

        if len(pieces) > 0:
            self.held_piece = pieces[-1]
            self.held_piece_original_position = self.held_piece.position
            self.pull_to_top(self.held_piece)

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
        
        if key == arcade.key.KEY_1 or key==arcade.key.NUM_1:
            self.selected_quadrant = 1
        elif key == arcade.key.KEY_2 or key==arcade.key.NUM_2:
            self.selected_quadrant = 2
        elif key == arcade.key.KEY_3 or key==arcade.key.NUM_3:
            self.selected_quadrant = 3
        elif key == arcade.key.KEY_4 or key==arcade.key.NUM_4:
            self.selected_quadrant = 4
        else:
            if self.selected_quadrant != None:
                if key == arcade.key.C:
                    self.selected_direction = "CLOCKWISE"
                elif key == arcade.key.A:
                    self.selected_direction = "ANTICLOCKWISE"
                else:
                    return

                if self.engine.next_player == 1:
                    self.player1_pieces.remove(self.placed_piece)
                else:
                    self.player2_pieces.remove(self.placed_piece)
                self.engine.move(self.place_index, self.selected_quadrant, self.selected_direction)
                self.place_board()

                self.placed = False
                self.selected_quadrant = None

                print(self.engine.game_state())





def main():
    window = PentagoWindow()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()