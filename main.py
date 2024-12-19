import numpy as np

# Representasi papan sebagai matriks
# 0 = kosong, 1 = macan, 2 = uwong
board = np.zeros((5, 5), dtype=int)

# Koordinat valid (bentuk papan permainan)
valid_positions = [
    (0, 0), (0, 2), (0, 4),
    (1, 1), (1, 3),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
    (3, 1), (3, 3),
    (4, 0), (4, 2), (4, 4)
]

# Menampilkan papan
def print_board():
    for i in range(5):
        row = ""
        for j in range(5):
            if (i, j) not in valid_positions:
                row += "   "  # Posisi tidak valid
            elif board[i, j] == 0:
                row += " . "  # Kosong
            elif board[i, j] == 1:
                row += " M "  # Macan
            elif board[i, j] == 2:
                row += " U "  # Uwong
        print(row)
    print("\n")

# Cek apakah langkah valid
def is_valid_move(x, y):
    return (x, y) in valid_positions and board[x, y] == 0

# Peletakan awal pion
def place_piece(player, x, y):
    if is_valid_move(x, y):
        board[x, y] = player
        return True
    return False

# Gerakan pion
def move_piece(player, x1, y1, x2, y2):
    if board[x1, y1] == player and is_valid_move(x2, y2):
        board[x1, y1] = 0
        board[x2, y2] = player
        return True
    return False

# Logika giliran
def player_turn(player):
    print_board()
    if player == 1:
        print("Giliran Macan")
    else:
        print("Giliran Uwong")

    x, y = map(int, input("Masukkan posisi awal (x y): ").split())
    if player == 1:  # Macan bergerak
        x2, y2 = map(int, input("Masukkan posisi tujuan (x y): ").split())
        if move_piece(player, x, y, x2, y2):
            return True
    else:  # Uwong meletakkan pion
        if place_piece(player, x, y):
            return True

    print("Langkah tidak valid, coba lagi.")
    return False

# Permainan utama
def main():
    uwong_count = 8
    placed_uwong = 0
    macan_count = 2
    current_player = 1  # Macan memulai permainan

    while True:
        if current_player == 1:  # Giliran macan
            if not player_turn(1):
                continue
        else:  # Giliran uwong
            if placed_uwong < uwong_count:
                if not player_turn(2):
                    continue
                placed_uwong += 1
            else:  # Uwong habis, mulai bergerak
                if not player_turn(2):
                    continue

        # Ganti giliran
        current_player = 3 - current_player  # Bergantian 1 -> 2, 2 -> 1

        # Logika akhir permainan
        # Tambahkan logika menang/kalah di sini
        print("Cek kondisi akhir permainan...\n")

if __name__ == "__main__":
    main()
