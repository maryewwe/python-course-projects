from minesweeper_engine import *


def parse_command():
    '''
    Парсит команды пользователя из консольного ввода. Работает в цикле до получения
    корректного ввода.
    '''
    open_command = ['o', 'open']
    flag_command = ['f', 'flag']
    while True:
        try:
            command_parts = input('Введите команду o или open для открытия ячейки'
                                  ' либо f или flag для установки флага ').split()
            if len(command_parts) != 3:
                print('\nНеверный формат. Пожалуйста, попробуйте еще раз.')
                continue
            command, row, col = command_parts
            if command not in open_command + flag_command:
                print('\nНеизвестная команда. Используйте o/open/f/flag.')
                continue
            if not (row.isdigit() and col.isdigit()):
                print('\nКоординаты должны быть целыми числами. Попробуйте еще раз.')
            return command, int(row), int(col)
        except ValueError:
            print('\nОшибка ввода. Попробуйте снова.')



def print_board(board: list[list[Cell]], rows: int, cols: int):
    '''
    Выводит текущее состояние игрового поля в консоль.
    '''
    print('  ' + ' '.join(str(i) for i in range(cols)))
    for row in range(rows):
        print(row, ' '.join(str(board[row][col]) for col in range(cols)))
    return None


def main():
    '''
    Основная функция игры с консольным интерфейсом. Производит основной игровой цикл
    и проверку условий победы/поражения
    '''
    rows, cols, mines = [int(i) for i in input('Введите ряды, колонки и количество мин ').split()]
    if rows <= 0 or cols <= 0 or mines <= 0:
        return "Параметры должны быть положительными числами"
    if mines >= rows*cols:
        return "Слишком много мин для данного поля"
    board1 = empty_gameboard(rows, cols)
    print_board(board1, rows, cols)
    command, r1, c1 = input('Введите o или open и координаты клетки, чтобы сделать первый ход ').split(' ')
    r1, c1 = int(r1), int(c1)
    board = generate_board(rows, cols, mines, (r1, c1))
    board[r1][c1].is_revealed = True
    while True:
        print_board(board, rows, cols)
        if check_win(board, rows, cols):
            print('Поздравляем! Вы выиграли!')
        command, row, col = parse_command()
        if command in ['o', 'open']:
            board = open_cell(board, row, col)
            if board[row][col].adjacent_mines == 0:
                board = cascade_reveal(board, rows, cols, row, col)
            if check_game_over(board, row, col):
                print_board(board, rows, cols)
                print('Вы проиграли!')
                break
        elif command in ['f', 'flag']:
            board[row][col].is_flagged = (board[row][col].is_flagged + 1) % 2


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
            print("\nИгра прервана. До свидания!")
