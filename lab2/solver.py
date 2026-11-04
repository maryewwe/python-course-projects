from minesweeper_engine import *


class Solver:
    '''
    Решатель для игры сапер с детерминированными и вероятностными методами.
    Решатель выводит детерминированные правила: базовые и CSP, использует правило
    подмножеств для вывода новых фактов и производит вероятностный анализ с помощью
    бэктрекинга.
    '''

    def solve_step(self, board: list[list[Cell]]) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        '''
        Метод для базового решения.
        Пока не перестанет находить новые решения, итеративно применяет правила:

        1. Если число в открытой ячейке равно количеству неоткрытых соседей,
        то все эти соседи - мины.

        2. Если число в открытой ячейке равно количеству флагов среди соседей,
        все остальные неоткрытые соседи безопасны.
        '''
        rows, cols = len(board), len(board[0])
        safe_cells = set()
        cells_to_flag = set()
        changed = True
        limit = rows * cols
        while changed and limit > 0:
            changed = False
            limit -= 1
            for row in range(rows):
                for col in range(cols):
                    cell = board[row][col]
                    if cell.adjacent_mines == 0 or not cell.is_revealed:
                        continue
                    neighbours, flags = self.hidden_neighbours(row, col, board)
                    if cell.adjacent_mines == flags:
                        for neighbour in neighbours:
                            if neighbour not in safe_cells:
                                safe_cells.add(neighbour)
                                changed = True
                    if cell.adjacent_mines - flags == len(neighbours):
                        for neighbour in neighbours:
                            cells_to_flag.add(neighbour)
                        changed = True
        return safe_cells, cells_to_flag


    def hidden_neighbours(self, row: int, col: int, board: list[list[Cell]]) -> tuple[list[tuple[int, int]], int]:
        '''
        Метод для нахождения всех неоткрытых соседей данной ячейки и количества флагов
        возле нее.
        Возвращает кортеж с координатами всех закрытых соседей, на которых не установлен
        флаг, и количеством флагов возле ячейки.
        '''
        neighbours = []
        flags = 0
        rows = len(board)
        cols = len(board[0])
        for r_c in [-1, 0, 1]:
            for c_c in [-1, 0, 1]:
                neigh_r, neigh_c = row + r_c, col + c_c
                if not(0 <= neigh_r < rows and 0 <= neigh_c < cols) or (r_c == 0 and c_c == 0):
                    continue
                cell = board[neigh_r][neigh_c]
                if cell.is_flagged:
                    flags += 1
                elif not cell.is_revealed:
                    neighbours.append((neigh_r, neigh_c))
        return neighbours, flags


    def _generate_constraints(self, board: list[list[Cell]]) -> list[tuple[frozenset[tuple[int, int]], int]]:
        '''
        Генерирует CSP ограничения на основе открытых ячеек с числами.
        Для каждой открытой ячейки создает кортеж из множества закрытых соседей
        и количества мин среди них.
        '''
        constraints = []
        rows, cols = len(board), len(board[0])
        for row in range(rows):
            for col in range(cols):
                cell = board[row][col]
                if not cell.is_revealed or cell.adjacent_mines == 0:
                    continue
                hidden, flags = self.hidden_neighbours(row, col, board)
                if not hidden:
                    continue
                mines_remained = cell.adjacent_mines - flags
                if mines_remained < 0:
                    mines_remained = 0
                constraints.append((frozenset(hidden), mines_remained))
        return constraints


    def _apply_subset_rule(self, constraints: list[tuple[frozenset[tuple[int, int]], int]]) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        '''
        Применяет правило подмножеств для вывода новых фактов на основе CSP ограничений.
        Правило:

        Если set1 - подмножество set2, среди set1 n мин, среди set2 k мин, то
        среди set2 - set1 k - n мин.
        '''
        safe_cells = set()
        mine_cells = set()
        for _ in range(20):
            new_safe_cells = set()
            new_mine_cells = set()
            new_constrains = []
            for i in range(len(constraints)):
                set1, value1 = constraints[i]
                for j in range(i+1, len(constraints)):
                    set2, value2 = constraints[j]
                    if set1.issubset(set2) and set1 != set2:
                        d = set2 - set1
                        new_value = value2 - value1
                    elif set2.issubset(set1) and set1 != set2:
                        d = set1 - set2
                        new_value = value1 - value2
                    else:
                        continue
                    if new_value < 0 or new_value > len(d):
                        continue
                    if d:
                        new_constrains.append((frozenset(d), new_value))
            if new_constrains:
                constraints.extend(new_constrains)
            for cells, count in constraints:
                if count == 0:
                    new_safe_cells.update(cells)
                elif count == len(cells):
                    new_mine_cells.update(cells)
            if not(new_safe_cells - safe_cells or new_mine_cells - mine_cells):
                break
            safe_cells |= new_safe_cells
            mine_cells |= new_mine_cells
            simplified = []
            for cells, count in constraints:
                remained = set(cells) - safe_cells - mine_cells
                new_value = count - len(set(cells) & mine_cells)
                if remained:
                    simplified.append((frozenset(remained), new_value))
            constraints = simplified
        return safe_cells, mine_cells


    def make_probabilistic_move(self, board: list[list[Cell]]) -> tuple[int, int]:
        '''
        Выбирает ячейку для открытия на основе вероятностного анализа.
        Использует backtracking для нахождения всех возможных расстановок мин
        в независимых группах и вычисляет вероятности для каждой ячейки.
        Возвращает ячейку, имеющую наименьшую вероятность быть миной.

        Если ограничений нет, возвращает первую попавшуюся закрытую ячейку.
        '''
        constraints = self._generate_constraints(board)
        if not constraints:
            for r in range(len(board)):
                for c in range(len(board[0])):
                    cell = board[r][c]
                    if not cell.is_revealed and not cell.is_flagged:
                        return (r, c)
        groups = self.independent_groups(constraints)
        probabilities = {}
        for group in groups:
            group_constraints = []
            for vars_set, count in constraints:
                if any(cell in group for cell in vars_set):
                    group_constraints.append((vars_set & group, count))
            variables = list(group)
            all_solutions = []
            current_prob_vals = {}

            self.backtrack(variables, group_constraints, 0, current_prob_vals, all_solutions)

            if not all_solutions:
                continue
            mine_counts = {}
            for sol in all_solutions:
                for cell, val in sol.items():
                    if val == 1:
                        mine_counts[cell] = mine_counts.get(cell, 0) + 1

            for cell in group:
                mine_count = mine_counts.get(cell, 0)
                probabilities[cell] = mine_count / len(all_solutions)
        if not probabilities:
            for r in range(len(board)):
                for c in range(len(board[0])):
                    cell = board[r][c]
                    if not cell.is_revealed and not cell.is_flagged:
                        return (r, c)

        safest = min(probabilities.items(), key=lambda x: x[1])[0]
        return safest


    def backtrack(self, coordinates: list[tuple[int, int]], constraints: list[tuple[frozenset[tuple[int, int]], int]], ind: int, prob_board: dict[tuple[int, int], int], solutions: list[dict[tuple[int, int], int]]) -> None:
        '''
        Рекурсивный алгоритм backtracking для нахождения всех возможных решений.
        '''
        if ind == len(coordinates):
            if self.check_constraints(prob_board, constraints):
                solutions.append(dict(prob_board))
            return
        var = coordinates[ind]
        for prob_value in [0, 1]:
            prob_board[var] = prob_value
            if self.check_constraints(prob_board, constraints):
                self.backtrack(coordinates, constraints, ind+1, prob_board, solutions)
            del prob_board[var]


    def check_constraints(self, prob_board: dict, constraints: list[tuple[frozenset[tuple[int, int]], int]]):
        '''
        Проверяет, является ли текущее присваивание ячейке значения выполнимым.
        '''
        for vars_set, count in constraints:
            total = 0
            unknown = 0
            for cell in vars_set:
                if cell in prob_board:
                    total += prob_board[cell]
                else:
                    unknown += 1
            if total > count:
                return False
            if total + unknown < count:
                return False
        return True


    def independent_groups(self, constraints: list[tuple[frozenset[tuple[int, int]], int]]) -> list[set[tuple[int, int]]]:
        '''
        Разбивает переменные на независимые группы с помощью Union-Find
        по следующему принципу: две переменные принадлежат одной группе,
        если они связаны через общие ограничения.
        '''
        parent = {}
        cells = set()
        for vs, _ in constraints:
            cells |= vs
        for cell in cells:
            parent[cell] = cell

        for vs, _ in constraints:
            v_list = list(vs)
            for i in range(1, len(v_list)):
                self.union(parent, v_list[0], v_list[i])

        groups_map = {}
        for cell in cells:
            root = self.find(parent, cell)
            if root not in groups_map:
                groups_map[root] = set()
            groups_map[root].add(cell)

        return list(groups_map.values())


    def find(self, parent: dict, x: tuple[int, int]) -> tuple[int, int]:
        '''
        Находит элемент-родитель для данного элемента в Union-Find структуре.
        '''
        root = x
        while parent[root] != root:
            root = parent[root]
        while x != root:
            parent[x], x = root, parent[x]
        return root


    def union(self, parent: dict, a: tuple[int, int], b: tuple[int, int]) -> None:
        '''
        Объединяет два множества в структуре Union-Find.
        '''
        root_a, root_b = self.find(parent, a), self.find(parent, b)
        if root_a != root_b:
            parent[root_b] = root_a
        return None