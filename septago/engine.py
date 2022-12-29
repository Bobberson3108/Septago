import numpy as np

def seven_in_a_row(row):
    count = 1
    prev = row[0]
    for x in row[1:]:
        if x==prev:
            count += 1
            if count == 7:
                return x
        else:
            count = 1
        prev = x
    return 0

class Engine:
    def __init__(self, starting_player=1, starting_configuration=None):
        if starting_configuration == None:
            self.board = np.zeros((9,9), dtype=int)
        else:
            self.board = starting_configuration

        self.next_player = starting_player
        self.game_over = False

    def move(self, position, rotation_quadrant, rotation_direction):
        if self.game_over:
            return

        if self.board[position]:
            raise ValueError("Position Taken")

        self.board[position] = self.next_player
        self.rotate(rotation_quadrant, rotation_direction)

        self.change_player()
    
    def rotate(self, quadrant, direction):
        if direction == "CLOCKWISE":
            k = 1
        elif direction == "ANTICLOCKWISE":
            k = 3
        else:
            raise ValueError("Invalid Direction")
        
        quadrant -= 1
        y, x = divmod(quadrant, 3)
        self.board[x*3:(x+1)*3, (y*3):(y+1)*3] = np.rot90(self.board[x*3:(x+1)*3, (y*3):(y+1)*3], k=k)
        # if quadrant == 1:
        #     self.board[:3, 0:3] = np.rot90(self.board[:3, :3], k=k)
        # elif quadrant == 2:
        #     self.board[3:6, 0:3] = np.rot90(self.board[3:, :3], k=k)
        # elif quadrant == 3:
        #     self.board[6:9, 0:3] = np.rot90(self.board[:3, 3:], k=k)
        # elif quadrant == 4:
        #     self.board[0:3:, 3:6] = np.rot90(self.board[3:, 3:], k=k)
        # else:


    def change_player(self):
        if self.next_player == 1:
            self.next_player = 2
        else:
            self.next_player = 1

    def game_state(self):
        for row in self.board:
            winner = seven_in_a_row(row)
            if winner:
                self.game_over = True
                return f"Player {winner} won"
        for column in self.board.T:
            winner = seven_in_a_row(column)
            if winner:
                self.game_over = True
                return f"Player {winner} won"

        for offset in range(-2, 3):
            winner = seven_in_a_row(np.diagonal(self.board, offset))
            if winner:
                self.game_over = True
                return f"Player {winner} won"
        
        flipped_board = np.fliplr(self.board)
        for offset in range(-2, 3):
            winner = seven_in_a_row(np.diagonal(flipped_board, offset))
            if winner:
                self.game_over = True
                return f"Player {winner} won"
        
        if np.count_nonzero(self.board) == 81:
            self.game_over = True
            return "DRAW"
        
        return f"Player {self.next_player}'s turn"
    
    def display(self):
        print(self.game_state())
        line = "  "
        for i in range(9):
            line += str(i)
            line += " "
            # if i == 2 or i == 5:
            #     line += "  "
        print(line)
        for i in range(9):
            line = f'{i} '
            for j in range(9):
                line += str(self.board[j][i])
                line += " "
                # if j == 2 or j == 5:
                #     line += "| "
            print(line)
            # if i == 2 or i == 5:
            #     print("  ----------------------")
                
if __name__=="__main__":
    game = Engine()
    while not game.game_over:
        game.display()
        x, y, quadrant, direction = input("Enter Move: ").split() # Example Move: "3 3 2 A"
        direction = "CLOCKWISE" if direction == "C" else "ANTICLOCKWISE" if direction == "A" else direction
        try:
            game.move((int(x), int(y)), int(quadrant), direction)
        except ValueError as e:
            print(e)
        game.game_state()
    game.display()
