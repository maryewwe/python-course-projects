import random
from collections import deque


class Cell:
    '''
    Класс, представляющий собой игровую ячейку поля
    '''
    def __init__(self, is_mine:bool=False, is_revealed:bool=False, is_flagged:bool=False, adjacent_mines:int=0):
        self.is_mine = is_mine
        self.is_revealed = is_revealed
        self.is_flagged = is_flagged
        self.adjacent_mines = adjacent_mines

    def __repr__(self):
        '''
        Возвращает строковое представление ячейки
        '''
        if self.is_mine and self.is_revealed:
            return f'*'
        elif self.is_revealed and not self.is_mine:
            return f'{self.adjacent_mines}'
        elif not self.is_revealed and self.is_flagged:
            return f'F'
        else:
            return f'#'


def empty_gameboard(rows: int, cols: int) -> list[list[Cell]]:
    '''
    Генерирует пустое поле заданного размера.
    '''
    return [[Cell() for _ in range(cols)] for _ in range(rows)]


def generate_board(rows: int, cols: int, num_mines: int, first_click_coordinates: tuple[int, int]) -> list[list[Cell]]:
    '''
    Генерирует игровое поле с минами, гарантируя безопасность первого хода.
    Если у ячейки первого хода 0 соседей с минами, происходит рекурсивное
    открытие соседей.
    '''
    r1, c1 = first_click_coordinates
    available_mine_positions = [(row, col) for row in range(rows) for col in range(cols) if r1 != row or c1 != col]
    mine_coordinates = random.sample(available_mine_positions, num_mines)
    board = [[Cell() for _ in range(cols)] for _ in range(rows)]
    for row, col in mine_coordinates:
        board[row][col].is_mine = True
        for move_r in [-1, 0, 1]:
            for move_c in [-1, 0, 1]:
                if not (0 <= row + move_r < rows and 0 <= col + move_c < cols):
                    continue
                board[row+move_r][col+move_c].adjacent_mines += 1
    return cascade_reveal(board, rows, cols, r1, c1)


def open_cell(board: list[list[Cell]], row: int, col: int) -> list[list[Cell]]:
    '''
    Открывает указанную ячейку на игровом поле.
    '''
    board[row][col].is_revealed = True
    return board


def cascade_reveal(board: list[list[Cell]], rows: int, cols: int, row: int, col: int) -> list[list[Cell]]:
    '''
    Выполняет каскадное открытие ячеек с использованием алгоритма BFS
    '''
    if board[row][col].adjacent_mines == 0:
        queue = deque()
        queue.append((row, col))
        visited = set()
        while queue:
            x, y = queue.popleft()
            for move_r in [-1, 0, 1]:
                for move_c in [-1, 0, 1]:
                    if (move_r == 0 and move_c == 0) or not (0 <= x + move_r < rows and 0 <= y + move_c < cols):
                        continue
                    if board[x+move_r][y+move_c].is_mine or board[x+move_r][y+move_c].is_flagged:
                        continue
                    open_cell(board, x+move_r, y+move_c)
                    if board[x+move_r][y+move_c].adjacent_mines == 0 and not((x+move_r, y+move_c) in visited):
                        queue.append((x+move_r, y+move_c))
            visited.add((x, y))
        for row, col in visited:
            board[row][col].is_revealed = True
    return board


def check_win(board: list[list[Cell]], rows: int, cols: int) -> bool:
    '''
    Проверяет, выиграл ли игрок (открыл ли он все безопасные ячейки)
    '''
    safe_positions = [board[row][col] for row in range(rows) for col in range(cols) if not board[row][col].is_mine]
    if all(cell.is_revealed for cell in safe_positions):
        return True
    return False


def check_game_over(board: list[list[Cell]], row: int, col: int) -> bool:
    '''
    Проверяет, не проиграл ли игрок (не открыл ли ячейку с миной)
    '''
    if board[row][col].is_mine and board[row][col].is_revealed:
        return True
    return False