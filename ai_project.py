import tkinter as tk
from tkinter import messagebox

class MacananAI:
    def __init__(self, board_size=5):
        self.board_size = board_size
        self.restricted_positions = {
            (1,0), (3,0),  # Row 0
            (0,1), (2,1), (4,1),  # Row 1
            (1,2), (3,2),  # Row 2
            (0,3), (2,3), (4,3),  # Row 3
            (1,4), (3,4)  # Row 4
        }

    def has_valid_moves(self, board, macan_positions):
        """Check if Macan has any valid moves available"""
        for pos in macan_positions:
            row, col = pos
            # Check regular moves
            moves = self.get_valid_moves(board, pos, "macan", macan_positions)
            if moves:
                return True
        return False

    def evaluate_placement(self, board, macan_positions, is_macan_ai):
        """Evaluate board state during placement phase"""
        score = 0
        if is_macan_ai:
            # Prefer central positions for Macan
            for pos in macan_positions:
                row, col = pos
                # Center positions are worth more
                score += (2 - abs(row - 2)) + (2 - abs(col - 2))
                # Avoid restricted positions during placement
                if pos in self.restricted_positions:
                    score -= 3
        else:
            # For Uwong, try to block Macan's movements
            uwong_positions = [(i, j) for i in range(self.board_size) 
                            for j in range(self.board_size) 
                            if board[i][j] == "uwong"]
            for pos in uwong_positions:
                # Position Uwong pieces to restrict Macan movement
                for macan_pos in macan_positions:
                    if abs(pos[0] - macan_pos[0]) + abs(pos[1] - macan_pos[1]) == 1:
                        score += 2
        return score

    def get_placement_moves(self, board):
        """Get all possible placement positions"""
        moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] is None:
                    moves.append((i, j))
        return moves

    def minimax_placement(self, board, macan_positions, depth, alpha, beta, 
                        is_maximizing, is_macan_ai, macan_count, uwong_count):
        """Minimax algorithm for placement phase"""
        if depth == 0:
            return self.evaluate_placement(board, macan_positions, is_macan_ai), None
            
        if is_maximizing:
            best_score = float('-inf')
            best_move = None
            possible_moves = self.get_placement_moves(board)
            
            for move in possible_moves:
                row, col = move
                new_board = [row[:] for row in board]
                new_macan_positions = macan_positions.copy()
                
                if is_macan_ai:
                    new_board[row][col] = "macan"
                    new_macan_positions.append(move)
                    new_macan_count = macan_count + 1
                else:
                    new_board[row][col] = "uwong"
                    new_uwong_count = uwong_count + 1
                
                score, _ = self.minimax_placement(new_board, new_macan_positions, 
                                            depth - 1, alpha, beta, False, 
                                            is_macan_ai, macan_count, uwong_count)
                
                if score > best_score:
                    best_score = score
                    best_move = move
                    
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
                    
            return best_score, best_move
        else:
            best_score = float('inf')
            best_move = None
            possible_moves = self.get_placement_moves(board)
            
            for move in possible_moves:
                row, col = move
                new_board = [row[:] for row in board]
                new_macan_positions = macan_positions.copy()
                
                if not is_macan_ai:
                    new_board[row][col] = "macan"
                    new_macan_positions.append(move)
                    new_macan_count = macan_count + 1
                else:
                    new_board[row][col] = "uwong"
                    new_uwong_count = uwong_count + 1
                
                score, _ = self.minimax_placement(new_board, new_macan_positions, 
                                            depth - 1, alpha, beta, True, 
                                            is_macan_ai, macan_count, uwong_count)
                
                if score < best_score:
                    best_score = score
                    best_move = move
                    
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
                    
            return best_score, best_move

    def get_best_placement(self, board, macan_positions, is_macan_ai, macan_count, uwong_count):
        """Get the best placement move"""
        _, best_move = self.minimax_placement(board, macan_positions, depth=3,
                                            alpha=float('-inf'), beta=float('inf'),
                                            is_maximizing=True, is_macan_ai=is_macan_ai,
                                            macan_count=macan_count, uwong_count=uwong_count)
        return best_move

    def evaluate_board(self, board, macan_positions):
        """
        Evaluate the current board state
        Positive score favors Macan, negative score favors Uwong
        """
        uwong_count = sum(row.count("uwong") for row in board)
        
        # Check if game is won
        if uwong_count < 3:
            return 1000  # Macan wins
        if not self.has_valid_moves(board, macan_positions):
            return -1000  # Uwong wins
            
        # Otherwise evaluate based on piece count and positions
        score = (8 - uwong_count) * 10  # Value each remaining Uwong capture
        
        # Add positional values
        for pos in macan_positions:
            if pos in self.restricted_positions:
                score -= 5  # Penalty for Macan in restricted position
                
        return score

    def get_valid_moves(self, board, pos, piece_type, macan_positions):
        """Return all valid moves for a piece at given position"""
        row, col = pos
        moves = []
        
        # Regular moves
        if pos in self.restricted_positions:
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 4 directions
        else:
            directions = [(0, 1), (1, 1), (1, 0), (1, -1),   # 8 directions
                        (0, -1), (-1, -1), (-1, 0), (-1, 1)]
            
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.board_size and 
                0 <= new_col < self.board_size and 
                board[new_row][new_col] is None):
                moves.append((new_row, new_col))
        
        # Add capture moves for Macan
        if piece_type == "macan":
            capture_moves = self.get_capture_moves(board, pos)
            moves.extend(capture_moves)
            
        return moves

    def get_capture_moves(self, board, pos):
        """Get all possible capture moves for Macan"""
        row, col = pos
        captures = []
        
        # Check horizontal captures
        for col_offset in [-3, 3]:
            new_col = col + col_offset
            if (0 <= new_col < self.board_size and 
                self.can_capture(board, row, col, row, new_col)):
                captures.append((row, new_col))
        
        # Check vertical captures
        for row_offset in [-3, 3]:
            new_row = row + row_offset
            if (0 <= new_row < self.board_size and 
                self.can_capture(board, row, col, new_row, col)):
                captures.append((new_row, col))
        
        # Check diagonal captures
        for row_offset in [-3, 3]:
            for col_offset in [-3, 3]:
                new_row, new_col = row + row_offset, col + col_offset
                if (0 <= new_row < self.board_size and 
                    0 <= new_col < self.board_size and 
                    self.can_capture(board, row, col, new_row, new_col)):
                    captures.append((new_row, new_col))
                    
        return captures

    def can_capture(self, board, old_row, old_col, new_row, new_col):
        """Check if a capture move is valid"""
        if board[new_row][new_col] is not None:
            return False

        # For horizontal captures
        if old_row == new_row:
            min_col = min(old_col, new_col)
            max_col = max(old_col, new_col)
            if max_col - min_col == 3:
                uwong_count = 0
                for col in range(min_col + 1, max_col):
                    if board[old_row][col] == "uwong":
                        uwong_count += 1
                    elif board[old_row][col] == "macan":
                        return False
                return uwong_count == 2

        # Similar logic for vertical and diagonal captures
        # [Keep the existing capture logic from the MacananGame class]
        
        return False

    def minimax(self, board, macan_positions, depth, alpha, beta, is_maximizing, is_macan_ai):
        if depth == 0:
            return self.evaluate_board(board, macan_positions), None
            
        if is_maximizing:
            best_score = float('-inf')
            best_move = None
            
            if is_macan_ai:
                for pos in macan_positions:
                    moves = self.get_valid_moves(board, pos, "macan", macan_positions)
                    for move in moves:
                        # Make move
                        new_board = [row[:] for row in board]
                        new_macan_positions = macan_positions.copy()
                        
                        # Simulate move
                        new_board[pos[0]][pos[1]] = None
                        new_board[move[0]][move[1]] = "macan"
                        new_macan_positions.remove(pos)
                        new_macan_positions.append(move)
                        
                        # Check if this is a capture move
                        if abs(move[0] - pos[0]) == 3 or abs(move[1] - pos[1]) == 3:
                            # Remove captured Uwong pieces
                            if self.can_capture(board, pos[0], pos[1], move[0], move[1]):
                                self._apply_capture(new_board, pos[0], pos[1], move[0], move[1])
                        
                        score, _ = self.minimax(new_board, new_macan_positions, 
                                            depth - 1, alpha, beta, False, is_macan_ai)
                        
                        if score > best_score:
                            best_score = score
                            best_move = (pos, move)
                            
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
            else:
                # Uwong's moves
                uwong_positions = [(i, j) for i in range(self.board_size) 
                                for j in range(self.board_size) 
                                if board[i][j] == "uwong"]
                for pos in uwong_positions:
                    moves = self.get_valid_moves(board, pos, "uwong", macan_positions)
                    for move in moves:
                        new_board = [row[:] for row in board]
                        new_board[pos[0]][pos[1]] = None
                        new_board[move[0]][move[1]] = "uwong"
                        
                        score, _ = self.minimax(new_board, macan_positions, 
                                            depth - 1, alpha, beta, False, is_macan_ai)
                        
                        if score > best_score:
                            best_score = score
                            best_move = (pos, move)
                            
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
                    
            return best_score, best_move
        else:
            # Minimizing player's logic (similar to maximizing but with min instead of max)
            best_score = float('inf')
            best_move = None
            
            if not is_macan_ai:
                for pos in macan_positions:
                    moves = self.get_valid_moves(board, pos, "macan", macan_positions)
                    for move in moves:
                        new_board = [row[:] for row in board]
                        new_macan_positions = macan_positions.copy()
                        
                        # Simulate move
                        new_board[pos[0]][pos[1]] = None
                        new_board[move[0]][move[1]] = "macan"
                        new_macan_positions.remove(pos)
                        new_macan_positions.append(move)
                        
                        if abs(move[0] - pos[0]) == 3 or abs(move[1] - pos[1]) == 3:
                            if self.can_capture(board, pos[0], pos[1], move[0], move[1]):
                                self._apply_capture(new_board, pos[0], pos[1], move[0], move[1])
                        
                        score, _ = self.minimax(new_board, new_macan_positions, 
                                            depth - 1, alpha, beta, True, is_macan_ai)
                        
                        if score < best_score:
                            best_score = score
                            best_move = (pos, move)
                            
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
            else:
                uwong_positions = [(i, j) for i in range(self.board_size) 
                                for j in range(self.board_size) 
                                if board[i][j] == "uwong"]
                for pos in uwong_positions:
                    moves = self.get_valid_moves(board, pos, "uwong", macan_positions)
                    for move in moves:
                        new_board = [row[:] for row in board]
                        new_board[pos[0]][pos[1]] = None
                        new_board[move[0]][move[1]] = "uwong"
                        
                        score, _ = self.minimax(new_board, macan_positions, 
                                            depth - 1, alpha, beta, True, is_macan_ai)
                        
                        if score < best_score:
                            best_score = score
                            best_move = (pos, move)
                            
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
                    
            return best_score, best_move

    def _apply_capture(self, board, old_row, old_col, new_row, new_col):
        """Apply capture move on the board"""
        if old_row == new_row:  # Horizontal capture
            min_col = min(old_col, new_col)
            max_col = max(old_col, new_col)
            for col in range(min_col + 1, max_col):
                board[old_row][col] = None
        elif old_col == new_col:  # Vertical capture
            min_row = min(old_row, new_row)
            max_row = max(old_row, new_row)
            for row in range(min_row + 1, max_row):
                board[row][old_col] = None
        else:  # Diagonal capture
            row_step = 1 if new_row > old_row else -1
            col_step = 1 if new_col > old_col else -1
            row, col = old_row + row_step, old_col + col_step
            for _ in range(2):
                board[row][col] = None
                row += row_step
                col += col_step

    def get_best_move(self, board, macan_positions, is_macan_ai):
        """Get the best move using minimax"""
        _, best_move = self.minimax(board, macan_positions, depth=3, 
                                  alpha=float('-inf'), beta=float('inf'), 
                                  is_maximizing=True, is_macan_ai=is_macan_ai)
        return best_move

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Macanan Game")
        
        # Create main menu frame
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(expand=True, pady=20)
        
        # Title
        title_label = tk.Label(self.menu_frame, text="Macanan Game", font=('Arial', 24, 'bold'))
        title_label.pack(pady=20)
        
        # Menu buttons
        play_as_macan = tk.Button(self.menu_frame, text="Play as Macan", 
                                 command=lambda: self.start_game(1),
                                 width=20, height=2, font=('Arial', 12))
        play_as_macan.pack(pady=10)
        
        play_as_uwong = tk.Button(self.menu_frame, text="Play as Uwong",
                                 command=lambda: self.start_game(2),
                                 width=20, height=2, font=('Arial', 12))
        play_as_uwong.pack(pady=10)
        
        play_1v1 = tk.Button(self.menu_frame, text="1 vs 1",
                            command=lambda: self.start_game(3),
                            width=20, height=2, font=('Arial', 12))
        play_1v1.pack(pady=10)
        
        self.game_frame = None
        self.game = None

    def start_game(self, mode):
        # Hide menu frame
        self.menu_frame.pack_forget()
        
        # Create and show game frame
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(expand=True)
        
        # Create game instance
        self.game = MacananGame(self.game_frame, mode, self.return_to_menu)

    def return_to_menu(self):
        # Destroy game frame
        if self.game_frame:
            self.game_frame.destroy()
        
        # Show menu frame
        self.menu_frame.pack(expand=True)

class MacananGame:
    def __init__(self, parent, mode, return_callback):
        self.parent = parent
        self.mode = mode  # 1: Play as Macan, 2: Play as Uwong, 3: 1v1
        self.ai = MacananAI()
        self.is_ai_turn = False
        self.return_callback = return_callback  
        
        self.board_size = 5
        self.cell_size = 80

        # Add movement rules explanation
        self.game_frame = tk.Frame(parent)
        self.game_frame.pack(pady=10)
        
        # Add legend for movement rules
        # gray_square = tk.Canvas(rules_frame, width=20, height=20)
        # gray_square.grid(row=0, column=0, padx=5)
        # gray_square.create_rectangle(0, 0, 20, 20, fill="lightgray", outline="black")
        
        # gray_label = tk.Label(rules_frame, text="= 4 directions movement (↑→↓←)", font=('Arial', 10))
        # gray_label.grid(row=0, column=1, padx=5, sticky="w")
        
        # white_square = tk.Canvas(rules_frame, width=20, height=20)
        # white_square.grid(row=1, column=0, padx=5)
        # white_square.create_rectangle(0, 0, 20, 20, fill="white", outline="black")
        
        # white_label = tk.Label(rules_frame, text="= 8 directions movement (↑↗→↘↓↙←↖)", font=('Arial', 10))
        # white_label.grid(row=1, column=1, padx=5, sticky="w")
        
        self.canvas = tk.Canvas(self.game_frame, 
                              width=self.board_size * self.cell_size,
                              height=self.board_size * self.cell_size)
        self.canvas.pack(pady=10)
        
        # Rest of the initialization code remains the same
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
        
        # Button frame
        button_frame = tk.Frame(self.game_frame)
        button_frame.pack(pady=5)
        
        # Add restart and quit buttons
        self.restart_button = tk.Button(button_frame, text="Restart Game", 
                                      command=self.restart_game)
        self.restart_button.pack(side=tk.LEFT, padx=5)
        
        self.quit_button = tk.Button(button_frame, text="Back to Menu", 
                                   command=self.return_to_menu)
        self.quit_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_game()
        self.draw_board()

        if self.mode == 2:
            self.parent.after(500, self.make_ai_move)
        
        self.canvas.bind("<Button-1>", self.handle_click)
        self.selected_piece = None

    def make_ai_move(self):
        """Make AI move based on current game state"""
        if self.mode == 1:  # AI plays as Uwong
            if self.uwong_count < 8:  # Placement phase
                best_move = self.ai.get_best_placement(self.board, self.macan_positions, 
                                                    False, self.macan_count, self.uwong_count)
                if best_move:
                    row, col = best_move
                    self.place_piece(row, col, "uwong")
                    self.uwong_count += 1
                    self.turn = "macan"
                    self.status_label.config(text="Macan's turn")
                    
                    if self.uwong_count == 8:
                        self.macan_can_move = True
                        
            elif self.uwong_count == 8:  # Movement phase
                best_move = self.ai.get_best_move(self.board, self.macan_positions, False)
                if best_move:
                    old_pos, new_pos = best_move
                    self.move_piece(old_pos[0], old_pos[1], new_pos[0], new_pos[1])
                    self.turn = "macan"
                    self.status_label.config(text="Macan's turn")
                    
        elif self.mode == 2:  # AI plays as Macan
            if self.macan_count < 2:  # Placement phase
                best_move = self.ai.get_best_placement(self.board, self.macan_positions, 
                                                    True, self.macan_count, self.uwong_count)
                if best_move:
                    row, col = best_move
                    self.place_piece(row, col, "macan")
                    self.macan_positions.append((row, col))
                    self.macan_count += 1
                    self.turn = "uwong"
                    self.status_label.config(text="Uwong's turn")
                    
                    if self.macan_count == 2:
                        self.macan_can_move = True
                        
            elif self.macan_count == 2:  # Movement phase
                best_move = self.ai.get_best_move(self.board, self.macan_positions, True)
                if best_move:
                    old_pos, new_pos = best_move
                    if self.can_capture(old_pos[0], old_pos[1], new_pos[0], new_pos[1]):
                        self.capture_uwong(old_pos[0], old_pos[1], new_pos[0], new_pos[1])
                    else:
                        self.move_piece(old_pos[0], old_pos[1], new_pos[0], new_pos[1])
                    self.turn = "uwong"
                    self.status_label.config(text="Uwong's turn")
        
        self.redraw_board()

    def return_to_menu(self):
        if hasattr(self, 'status_label'):  # Ensure it exists
            self.status_label.destroy() 
        self.game_frame.destroy()
        self.return_callback()

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
                
                # # Determine cell color based on restricted positions
                # fill_color = "lightgray" if (i, j) in self.restricted_positions else "white"
                # self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")
                
                # Determine movement pattern
                if (i, j) not in self.restricted_positions:  # 8-directional movement
                    # Draw diagonal lines (8 directions)
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    self.canvas.create_line(cx, cy, x1, y1, fill="black")  # Top-left
                    self.canvas.create_line(cx, cy, x2, y1, fill="black")  # Top-right
                    self.canvas.create_line(cx, cy, x1, y2, fill="black")  # Bottom-left
                    self.canvas.create_line(cx, cy, x2, y2, fill="black")  # Bottom-right
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                self.canvas.create_line(cx, cy, cx, y1, fill="black")  # Up
                self.canvas.create_line(cx, cy, cx, y2, fill="black")  # Down
                self.canvas.create_line(cx, cy, x1, cy, fill="black")  # Left
                self.canvas.create_line(cx, cy, x2, cy, fill="black")  # Right

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

        if (self.mode == 1 and self.turn == "macan") or \
        (self.mode == 2 and self.turn == "uwong") or \
        self.mode == 3:  # 1v1 mode
            
            if self.macan_can_move:
                if self.turn == "macan":
                    if self.selected_piece is None:
                        if self.board[row][col] == "macan":
                            self.selected_piece = (row, col)
                            self.highlight_piece(row, col)
                    else:
                        if self.selected_piece == (row, col):
                            self.selected_piece = None
                            self.redraw_board()
                        else:
                            old_row, old_col = self.selected_piece
                            if self.is_valid_move(old_row, old_col, row, col) or \
                            self.can_capture(old_row, old_col, row, col):
                                self.handle_macan_movement(row, col)
                                if self.mode == 1:  # If human is Macan, let AI make its move
                                    self.parent.after(500, self.make_ai_move)
                else:  # Uwong's turn
                    if self.uwong_count < 8:  # Still in placement phase
                        if self.board[row][col] is None:
                            self.place_piece(row, col, "uwong")
                            self.uwong_count += 1
                            self.turn = "macan"
                            self.status_label.config(text="Macan's turn")
                            if self.mode == 2:  # If human is Uwong, let AI make its move
                                self.parent.after(500, self.make_ai_move)
                    else:  # Movement phase for Uwong
                        if self.selected_piece is None:
                            if self.board[row][col] == "uwong":
                                self.selected_piece = (row, col)
                                self.highlight_piece(row, col)
                        else:
                            if self.selected_piece == (row, col):
                                self.selected_piece = None
                                self.redraw_board()
                            else:
                                old_row, old_col = self.selected_piece
                                if self.is_valid_move(old_row, old_col, row, col):
                                    self.handle_uwong_movement(row, col)
                                    if self.mode == 2:  # If human is Uwong, let AI make its move
                                        self.parent.after(500, self.make_ai_move)
            else:  # Placement phase
                self.handle_placement(row, col)
                if ((self.mode == 1 and self.turn == "uwong") or 
                    (self.mode == 2 and self.turn == "macan")):
                    self.parent.after(500, self.make_ai_move)

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
        # Check for Macan's available moves at the start of Macan's turn
        if self.turn == "macan" and not self.selected_piece:
            if not self.check_macan_has_moves():
                messagebox.showinfo("Game Over", "Uwong wins! Macan has no valid moves left!")
                self.restart_game()
                return

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

            # Check win conditions
            if not self.check_macan_has_moves():
                messagebox.showinfo("Game Over", "Uwong wins! Macan has no valid moves left!")
                self.restart_game()

    def handle_placement(self, row, col):
        if self.board[row][col] is not None:
            return

        if self.turn == "macan" and self.macan_count < 2:
            self.place_piece(row, col, "macan")
            self.macan_positions.append((row, col))
            self.macan_count += 1
            self.turn = "uwong"
            self.status_label.config(text="Uwong's turn to place")
                
            # Enable movement phase when Macan placement is complete
            if self.macan_count == 2:
                self.macan_can_move = True
                
        elif self.turn == "uwong" and self.uwong_count < 8:
            self.place_piece(row, col, "uwong")
            self.uwong_count += 1
            if self.uwong_count < 8:
                self.turn = "macan" if self.macan_count < 2 else "uwong"
                self.status_label.config(text=f"{'Macan' if self.turn == 'macan' else 'Uwong'}'s turn to place")
            else:
                self.turn = "macan"
                self.status_label.config(text="Macan's turn to move")

    def check_macan_has_moves(self):
        """
        Check if any Macan piece has valid moves available,
        following all movement rules (4-direction on gray, 8-direction on white)
        """
        for macan_pos in self.macan_positions:
            row, col = macan_pos
            current_pos = (row, col)
            
            # First check regular moves based on position type
            if current_pos in self.restricted_positions:
                # On gray square - can only move orthogonally
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
            else:
                # On white square - can move in all 8 directions
                directions = [(0, 1), (1, 1), (1, 0), (1, -1),   # Right, Down-Right, Down, Down-Left
                            (0, -1), (-1, -1), (-1, 0), (-1, 1)] # Left, Up-Left, Up, Up-Right

            # Check regular one-step moves
            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc
                
                if (0 <= new_row < self.board_size and 
                    0 <= new_col < self.board_size and 
                    self.is_valid_move(row, col, new_row, new_col)):
                    return True
            
            # Check capture moves
            # Horizontal captures (3 spaces)
            for col_offset in [-3, 3]:
                new_col = col + col_offset
                if (0 <= new_col < self.board_size and 
                    self.can_capture(row, col, row, new_col)):
                    return True
            
            # Vertical captures (3 spaces)
            for row_offset in [-3, 3]:
                new_row = row + row_offset
                if (0 <= new_row < self.board_size and 
                    self.can_capture(row, col, new_row, col)):
                    return True
            
            # Diagonal captures (3 spaces)
            for row_offset in [-3, 3]:
                for col_offset in [-3, 3]:
                    new_row = row + row_offset
                    new_col = col + col_offset
                    if (0 <= new_row < self.board_size and 
                        0 <= new_col < self.board_size and 
                        self.can_capture(row, col, new_row, new_col)):
                        return True
        
        return False

    def handle_macan_movement(self, row, col):
        old_row, old_col = self.selected_piece
        
        if self.is_valid_move(old_row, old_col, row, col):
            self.move_piece(old_row, old_col, row, col)
            self.turn = "uwong"
            self.status_label.config(text="Uwong's turn")

            self.selected_piece = None
            self.redraw_board()
                
        elif self.can_capture(old_row, old_col, row, col):
            self.capture_uwong(old_row, old_col, row, col)
            self.turn = "uwong"
            self.status_label.config(text="Uwong's turn")
            
            self.selected_piece = None
            self.redraw_board()

            # Check win conditions
            if self.count_uwong() < 3:
                messagebox.showinfo("Game Over", "Macan wins!")
                self.restart_game()
            elif not self.check_macan_has_moves():
                messagebox.showinfo("Game Over", "Uwong wins! Macan has no valid moves left!")
                self.restart_game()

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
    menu = MainMenu(root)
    root.mainloop()