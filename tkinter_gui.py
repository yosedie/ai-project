import tkinter as tk
from tkinter import messagebox

class MacananGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Macanan Game")
        
        # Game board configuration
        self.board_size = 5
        self.cell_size = 80
        self.canvas = tk.Canvas(self.root, width=self.board_size * self.cell_size, 
                              height=self.board_size * self.cell_size)
        self.canvas.pack(pady=10)
        
        # Define restricted movement positions (gray cells)
        self.restricted_positions = {
            (1,0), (3,0),  # Row 0
            (0,1), (2,1), (4,1),  # Row 1
            (1,2), (3,2),  # Row 2
            (0,3), (2,3), (4,3),  # Row 3
            (1,4), (3,4)  # Row 4
        }
        
        # Add status label
        self.status_label = tk.Label(root, text="Start game - Macan's turn", font=('Arial', 12))
        self.status_label.pack(pady=5)
        
        # Add restart button
        self.restart_button = tk.Button(root, text="Restart Game", command=self.restart_game)
        self.restart_button.pack(pady=5)
        
        self.reset_game()
        self.draw_board()
        
        self.canvas.bind("<Button-1>", self.handle_click)
        self.selected_piece = None

    def is_valid_move(self, old_row, old_col, new_row, new_col):
        if self.board[new_row][new_col] is not None:
            return False

        # Get current and target positions
        current_pos = (old_row, old_col)
        target_pos = (new_row, new_col)

        # Calculate differences
        row_diff = abs(new_row - old_row)
        col_diff = abs(new_col - old_col)

        # If moving from a restricted (gray) position
        if current_pos in self.restricted_positions:
            # Only allow orthogonal moves (up, down, left, right)
            return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
        
        # If in a white position, allow moves in any direction
        return row_diff <= 1 and col_diff <= 1

    def draw_board(self):
        # Draw the basic grid
        for i in range(self.board_size):
            for j in range(self.board_size):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                # Use gray for restricted movement positions
                fill_color = "lightgray" if (i,j) in self.restricted_positions else "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

    # Rest of the code remains the same as before
    def reset_game(self):
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.turn = "macan"
        self.macan_count = 0
        self.uwong_count = 0
        self.macan_positions = []
        self.selected_piece = None
        self.macan_can_move = False
        self.status_label.config(text="Start game - Macan's turn")

    def restart_game(self):
        self.reset_game()
        self.redraw_board()

    def handle_click(self, event):
        row = event.y // self.cell_size
        col = event.x // self.cell_size

        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return

        if self.macan_can_move:
            self.handle_mixed_phase(row, col)
        else:
            self.handle_placement(row, col)

    def can_capture(self, old_row, old_col, new_row, new_col):
        if self.board[new_row][new_col] is not None:
            return False

        # For horizontal captures
        if old_row == new_row:
            min_col = min(old_col, new_col)
            max_col = max(old_col, new_col)
            if max_col - min_col == 3:  # Must be exactly 2 spaces apart
                uwong_count = 0
                for col in range(min_col + 1, max_col):
                    if self.board[old_row][col] == "uwong":
                        uwong_count += 1
                    elif self.board[old_row][col] == "macan":
                        return False
                return uwong_count == 2

        # For vertical captures
        elif old_col == new_col:
            min_row = min(old_row, new_row)
            max_row = max(old_row, new_row)
            if max_row - min_row == 3:  # Must be exactly 2 spaces apart
                uwong_count = 0
                for row in range(min_row + 1, max_row):
                    if self.board[row][old_col] == "uwong":
                        uwong_count += 1
                    elif self.board[row][old_col] == "macan":
                        return False
                return uwong_count == 2

        # For diagonal captures
        elif abs(new_row - old_row) == abs(new_col - old_col) and abs(new_row - old_row) == 3:
            row_step = 1 if new_row > old_row else -1
            col_step = 1 if new_col > old_col else -1
            
            # Check the two spaces between start and end positions
            uwong_count = 0
            check_row = old_row + row_step
            check_col = old_col + col_step
            
            for _ in range(2):  # Check two spaces
                if self.board[check_row][check_col] == "uwong":
                    uwong_count += 1
                elif self.board[check_row][check_col] == "macan":
                    return False
                check_row += row_step
                check_col += col_step
                
            return uwong_count == 2

        return False

    def capture_uwong(self, old_row, old_col, new_row, new_col):
        # For horizontal captures
        if old_row == new_row:
            min_col = min(old_col, new_col)
            max_col = max(old_col, new_col)
            for col in range(min_col + 1, max_col):
                self.board[old_row][col] = None

        # For vertical captures
        elif old_col == new_col:
            min_row = min(old_row, new_row)
            max_row = max(old_row, new_row)
            for row in range(min_row + 1, max_row):
                self.board[row][old_col] = None

        # For diagonal captures
        elif abs(new_row - old_row) == abs(new_col - old_col):
            row_step = 1 if new_row > old_row else -1
            col_step = 1 if new_col > old_col else -1
            
            check_row = old_row + row_step
            check_col = old_col + col_step
            
            for _ in range(2):  # Clear two spaces
                self.board[check_row][check_col] = None
                check_row += row_step
                check_col += col_step

        # Move the Macan
        self.move_piece(old_row, old_col, new_row, new_col)

    def handle_mixed_phase(self, row, col):
        if self.turn == "macan":
            if self.selected_piece is None:
                if self.board[row][col] == "macan":
                    self.selected_piece = (row, col)
                    self.highlight_piece(row, col)
            else:
                self.handle_macan_movement(row, col)
        else:  # Uwong's turn
            if self.board[row][col] is None and self.uwong_count < 8:
                self.place_piece(row, col, "uwong")
                self.uwong_count += 1
                self.turn = "macan"
                self.status_label.config(text="Macan's turn")
            elif self.selected_piece is None and self.board[row][col] == "uwong":
                self.selected_piece = (row, col)
                self.highlight_piece(row, col)
            elif self.selected_piece is not None:
                self.handle_uwong_movement(row, col)

    def handle_placement(self, row, col):
        if self.board[row][col] is not None:
            return

        if self.turn == "macan" and self.macan_count < 2:
            self.place_piece(row, col, "macan")
            self.macan_positions.append((row, col))
            self.macan_count += 1
            self.turn = "uwong"
            self.status_label.config(text="Uwong's turn to place")
            
        elif self.turn == "uwong" and self.uwong_count < 2:
            self.place_piece(row, col, "uwong")
            self.uwong_count += 1
            if self.uwong_count < 2:
                self.turn = "macan" if self.macan_count < 2 else "uwong"
                self.status_label.config(text=f"{'Macan' if self.turn == 'macan' else 'Uwong'}'s turn to place")
        
        if self.macan_count == 2 and self.uwong_count == 2:
            self.macan_can_move = True
            self.turn = "macan"
            self.status_label.config(text="Macan's turn to move")

    def handle_macan_movement(self, row, col):
        old_row, old_col = self.selected_piece
        
        if self.is_valid_move(old_row, old_col, row, col):
            self.move_piece(old_row, old_col, row, col)
            self.turn = "uwong"
            self.status_label.config(text="Uwong's turn")
        elif self.can_capture(old_row, old_col, row, col):
            self.capture_uwong(old_row, old_col, row, col)
            self.turn = "uwong"
            self.status_label.config(text="Uwong's turn")
            
            if self.count_uwong() < 3:
                messagebox.showinfo("Game Over", "Macan wins!")
                self.restart_game()
        
        self.selected_piece = None
        self.redraw_board()

    def handle_uwong_movement(self, row, col):
        old_row, old_col = self.selected_piece
        if self.is_valid_move(old_row, old_col, row, col):
            self.move_piece(old_row, old_col, row, col)
            self.turn = "macan"
            self.status_label.config(text="Macan's turn")
        
        self.selected_piece = None
        self.redraw_board()

    def count_uwong(self):
        count = 0
        for row in self.board:
            count += row.count("uwong")
        return count

    def move_piece(self, old_row, old_col, new_row, new_col):
        piece_type = self.board[old_row][old_col]
        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece_type
        if piece_type == "macan":
            self.macan_positions.remove((old_row, old_col))
            self.macan_positions.append((new_row, new_col))

    def highlight_piece(self, row, col):
        self.redraw_board()
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        self.canvas.create_oval(x - 22, y - 22, x + 22, y + 22, outline="yellow", width=3)

    def place_piece(self, row, col, piece_type):
        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2
        color = "red" if piece_type == "macan" else "blue"
        self.board[row][col] = piece_type
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color)

    def redraw_board(self):
        self.canvas.delete("all")
        self.draw_board()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] is not None:
                    self.place_piece(i, j, self.board[i][j])

if __name__ == "__main__":
    root = tk.Tk()
    game = MacananGame(root)
    root.mainloop()