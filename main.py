from itertools import compress
from tabulate import tabulate
from rich import print
import os


class SeaBattleHelper:
	def __init__(self,
	             ships_count: [int] = [4, 3, 2, 1],
	             ships_cells: [int] = [1, 2, 3, 4]):
		
		self.width = 10
		self.height = 10
		
		self.area = [["0" for i in range(self.width)] for j in range(self.height)]
		
		self.ships_count = ships_count
		self.ships_cells = ships_cells
		self.ships_alive = list(map(bool, ships_count))
		self.ships_destroyed = [0, 0, 0, 0]
		
		self._damaged_ships = []
		self._checked_hit_cells = set()
		
		self.biggest_ship = lambda: max(compress(self.ships_cells, self.ships_alive))
		
		self.headers = list("АБВГДЕЖЗИК")
		
		# 0 - просто символ (добавляется перед созданием таблицы)
		# 1 - отформатированный символ (на него заменяется [0] ПОСЛЕ создания таблицы)
		self.symbols = {
			"miss": ("O", "[bright_black]О[/bright_black]"),
			"hit": ("X", "[gold1]X[/gold1]")
		}
		self.max_chance_format = (
			lambda x: "@" * len(str(x)),
			lambda x: f"[red]{x}[/red]"
		)
	
	
	# Очистка поля
	def clear_area(self, save_symbols: bool = True) -> None:
		for y in range(self.height):
			for x in range(self.width):
				char = self.area[y][x]
				self.area[y][x] = "0" if char.isdigit() or not save_symbols else char
	
	
	# Поиск клетки с наивысшей вероятностью нахождения в ней корабля
	def find_max(self) -> ([(int, int)], str):  # ([max_cells*], max_value)
		max_cells = []
		max_value = 0
		
		for y in range(self.height):
			for x in range(self.width):
				char = self.area[y][x]
				
				if not char.isdigit(): continue
				
				if int(char) > max_value:
					max_cells = [(x, y)]
					max_value = int(char)
				elif int(char) == max_value:
					max_cells.append((x, y))
		
		return max_cells, str(max_value)
	
	
	# Заполнение таблицы вероятностей, относительно попаданий
	def update_hits(self) -> None:
		self._checked_hit_cells = set()
		
		for y in range(self.height):
			for x in range(self.width):
				if self.area[y][x] != self.symbols["hit"][0]:
					continue
				
				hit_cells = []
				if not (x, y) in self._checked_hit_cells:
					hit_cells.append((x, y))
					self._checked_hit_cells.add((x, y))
				else:
					continue
				
				is_one_hit = True
				direction = (0, 0)
				
				for cell in self._get_around_cells(x, y, True):
					if self.area[cell[1]][cell[0]] == self.symbols["hit"][0]:
						is_one_hit = False
						direction = (cell[0] - x, cell[1] - y)
				
				if is_one_hit:
					for cell in self._get_cross_cells(x, y):
						add_value = self.biggest_ship() - self._distance(cell, (x, y))
						self.area[cell[1]][cell[0]] = str(int(self.area[cell[1]][cell[0]]) + add_value * 6)
				else:
					new_cell = (
						hit_cells[0][0] + direction[0],
						hit_cells[0][1] + direction[1]
					)
					
					while True:
						if not (0 <= new_cell[0] < self.width and 0 <= new_cell[1] < self.height):
							break
						
						if self.area[new_cell[1]][new_cell[0]] != self.symbols["hit"][0]:
							break
							
						if not new_cell in self._checked_hit_cells:
							hit_cells.append(new_cell)
							self._checked_hit_cells.add(new_cell)
						
						new_cell = (
							new_cell[0] + direction[0],
							new_cell[1] + direction[1]
						)
					
					direction_1 = (
						hit_cells[1][0] - hit_cells[0][0],
						hit_cells[1][1] - hit_cells[0][1]
					)
					
					for cell in self._get_line_cells(*hit_cells[0], direction_1, True):
						if not self.area[cell[1]][cell[0]].isdigit():
							continue
						
						add_value = self.biggest_ship() - self._distance(cell, hit_cells[0])
						self.area[cell[1]][cell[0]] = str(int(self.area[cell[1]][cell[0]]) + add_value * 6)
					
					direction_2 = (
						hit_cells[-2][0] - hit_cells[-1][0],
						hit_cells[-2][1] - hit_cells[-1][1]
					)
					
					for cell in self._get_line_cells(*hit_cells[-1], direction_2, True):
						if not self.area[cell[1]][cell[0]].isdigit():
							continue
						
						add_value = self.biggest_ship() - self._distance(cell, hit_cells[-1])
						self.area[cell[1]][cell[0]] = str(int(self.area[cell[1]][cell[0]]) + add_value * 6)
				
				if not hit_cells in self._damaged_ships:
					self._damaged_ships.append(hit_cells)
	
	
	# Заполнение таблицы вероятностей
	def fill_area(self) -> None:
		self.update_hits()
		# return None
		
		# Заполняем поле относительно кораблей
		for ship in compress(self.ships_cells, self.ships_alive):
			# Проверяем горизонтальные позиции
			for y in range(self.height):
				for x in range(self.width):
					
					cells = [(x + i, y) for i in range(ship)]
					
					valid = True
					
					for cell in cells:
						if cell[0] >= self.width or self.area[cell[1]][cell[0]] == self.symbols["miss"][0]:
							valid = False
							break
					
					if not valid: continue
					
					for cell in cells:
						if self.area[cell[1]][cell[0]] != self.symbols["hit"][0]:
							self.area[cell[1]][cell[0]] = str(int(self.area[cell[1]][cell[0]]) + 1)
			
			if ship == 1: continue
			
			# Проверяем вертикальные позиции
			for y in range(self.height):
				for x in range(self.width):
					cells = [(x, y + i) for i in range(ship)]
					
					valid = True
					
					for cell in cells:
						if cell[1] >= self.height or self.area[cell[1]][cell[0]] == self.symbols["miss"][0]:
							valid = False
							break
					
					if not valid: continue
					
					for cell in cells:
						if self.area[cell[1]][cell[0]] != self.symbols["hit"][0]:
							self.area[cell[1]][cell[0]] = str(int(self.area[cell[1]][cell[0]]) + 1)
	
	
	# Получаем ячейки вокруг одной клетки
	def _get_around_cells(self, x: int, y: int, include_symbols: bool = False) -> [(int, int)]:
		cells = []
		add_coords = [-1, 0, 1]
		
		for add_y in add_coords:
			for add_x in add_coords:
				new_x = x + add_x
				new_y = y + add_y
				
				if x == new_x and y == new_y:
					continue
				
				if 0 <= new_x < self.width and 0 <= new_y < self.height and (
						self.area[new_y][new_x].isdigit() or include_symbols):
					cells.append((new_x, new_y))
		
		return cells
	
	
	# Получаем ячейки в форме креста вокруг одной клетки
	def _get_cross_cells(self, x: int, y: int) -> [(int, int)]:
		funcs = (
			lambda a, b, n: (a, b + n),
			lambda a, b, n: (a - n, b),
			lambda a, b, n: (a + n, b),
			lambda a, b, n: (a, b - n),
		)
		cells = []
		
		for i, func in enumerate(funcs):
			for j in range(1, self.biggest_ship()):
				new_x, new_y = func(x, y, j)
				
				if 0 <= new_x < self.width and 0 <= new_y < self.width and self.area[new_y][new_x].isdigit():
					cells.append((new_x, new_y))
				else:
					break
		
		return cells
	
	
	# Получаем ячейки по одной линии от клетки
	def _get_line_cells(self, x: int, y: int, direction: (int, int), pass_hits: bool = False):
		cells = []
		
		for i in range(1, self.biggest_ship()):
			new_x = x + direction[0] * i
			new_y = y + direction[1] * i
			
			if not (0 <= new_x < self.width and 0 <= new_y < self.width):
				continue
			
			if self.area[new_y][new_x].isdigit() or (pass_hits and self.area[new_y][new_x] == self.symbols["hit"][0]):
				cells.append((new_x, new_y))
			else:
				break
		
		return cells
	
	
	# Расстояние между двумя клетками
	def _distance(self, a: (int, int), b: (int, int)) -> float:
		return int(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)
	
	
	# Конвертация "программных" координат клетки в "человеческие"
	def humanize_cell(self, x: int, y: int) -> str:
		return self.headers[x] + str(y + 1)
	
	
	# Конвертация "человеческих" координат клетки в "программные"
	def cell_to_coords(self, s: str) -> (int, int):
		x = self.headers.index(s[0])
		y = int(s[1:]) - 1
		
		return x, y
	
	
	# Промах
	def miss(self, x: int, y: int) -> None:
		self.area[y][x] = self.symbols["miss"][0]
	
	
	# Попадание
	def hit(self, x: int, y: int, killed: bool) -> None:
		self.area[y][x] = self.symbols["hit"][0]
		
		if not killed:
			return
		
		is_one_hit = True
		direction = (0, 0)
		
		for cell in self._get_around_cells(x, y, True):
			if self.area[cell[1]][cell[0]] == self.symbols["hit"][0]:
				is_one_hit = False
				direction = (cell[0] - x, cell[1] - y)
		
		new_cell = (x, y)
		ship_cells = [new_cell]
		
		if not is_one_hit:
			while True:
				if not (0 <= new_cell[0] < self.width and 0 <= new_cell[1] < self.height):
					break
				
				if self.area[new_cell[1]][new_cell[0]] != self.symbols["hit"][0]:
					break
					
				if not new_cell in ship_cells:
					ship_cells.append(new_cell)
				
				new_cell = (
					new_cell[0] + direction[0],
					new_cell[1] + direction[1]
				)
		
		for cell in ship_cells:
			for ar_cell in self._get_around_cells(*cell):
				self.miss(*ar_cell)
		
		self.ships_count[len(ship_cells) - 1] -= 1
		if self.ships_count[len(ship_cells) - 1] <= 0:
			self.ships_alive[len(ship_cells) - 1] = False
	
	
	# Вывод красивой таблицы с полем
	def print_pretty_area(self) -> None:
		# подсветка максимальных значений
		max_chances = self.find_max()
		
		for x, y in max_chances[0]:
			self.area[y][x] = self.max_chance_format[0](max_chances[1])
		
		# Создание таблицы
		table = tabulate(
			self.area,
			["#"] + self.headers,
			tablefmt="simple",
			showindex=[i + 1 for i in range(self.width)],
			colalign=["center"] + ["right"] * 10,
			maxcolwidths=3
		)
		
		# Замена обычных символов на цветные
		# (Если их сразу добавить цветными в таблицу, то она разъедется,
		# потому что tabulate будет считать форматирование для rich,
		# как содержимое ячейки)
		for s in self.symbols:
			table = table.replace(self.symbols[s][0], self.symbols[s][1])
		
		# Подсветка максимальных значений
		max_value = self.max_chance_format[1](max_chances[1])
		table = table.replace(self.max_chance_format[0](max_chances[1]), max_value)
		
		print(table)
		
		# Возвращаем максимальные значения обратно (на всякий случай)
		for x, y in max_chances[0]:
			self.area[y][x] = max_chances[1]


if __name__ == "__main__":
	def choice(
			question: str,
			variants: [str],
			default: str | None = None,
			show_variants: bool = False,
			show_default: bool = False,
			upper_input: bool = False,
			lower_input: bool = False
	):
		while True:
			print(
				f"{question}"
				f"{(' (' + ' / '.join(variants) + ')') if show_variants else ''}"
				f"{(' [enter = [spring_green2]' + default + '[/spring_green2]]') if show_default else ''}: ",
				end=""
			)
			inp = input()
			
			if not inp and default:
				return default
			
			if upper_input:
				inp = inp.upper()
			if lower_input:
				inp = inp.lower()
			
			if inp in variants:
				return inp
	
	
	helper = SeaBattleHelper()
	
	human_cells = []
	for i in helper.headers:
		for j in range(helper.height):
			human_cells.append(i + str(j + 1))
	
	while True:
		os.system("cls")
		print('Программа-помощник для игры [spring_green2]"Морской Бой"[/spring_green2], '
		      'анализирующая поле противника для предугадывания самых выгодных ходов.\n\n')
		
		helper.clear_area()
		helper.fill_area()
		
		print("Таблица вероятностей:\n")
		helper.print_pretty_area()
		
		print("\nОсталось кораблей:")
		for i in range(3, -1, -1):
			alive = helper.ships_alive[i]
			print(
				f"[{'gold1' if alive else 'red'}]X {'X ' * i}[/{'gold1' if alive else 'red'}]: "
				f"{'[red]' if not alive else ''}"
				f"{helper.ships_count[i]}"
			)
		
		print("\nЖелательно стреляй в одну из следующих клеток:\n  ", end="")
		max_cells = helper.find_max()[0]
		inp_def = helper.humanize_cell(*max_cells[0])
		for cell in max_cells:
			print(f"[spring_green2]{helper.humanize_cell(*cell)}", end=" ")
		
		print("\n\n")
		target_cell = choice(
			"Клетка для выстрела",
			human_cells,
			default=inp_def,
			show_default=True,
			upper_input=True
		)
		coords = helper.cell_to_coords(target_cell)
		
		damage = choice(
			"Попал? ([spring_green2]Да[/spring_green2] / [spring_green2]Нет[/spring_green2])",
			["д", "да", "1", "н", "нет", "0"],
			default="нет",
			show_default=True,
			lower_input=True
		) in "да1"
		
		if damage:
			if sum(helper.ships_count) != helper.ships_count[0]: # Проверка на то, что остались только 1-палубные корабли
				kill = choice(
					"Убил? ([spring_green2]Да[/spring_green2] / [spring_green2]Нет[/spring_green2])",
					["д", "да", "1", "н", "нет", "0"],
					default="нет",
					show_default=True,
					lower_input=True
				) in "да1"
				helper.hit(*coords, kill)
			else:
				helper.hit(*coords, True)
		else:
			helper.miss(*coords)
		
		if not any(helper.ships_alive):
			break
	
	print('\n\n[italic spring_green2]Поздравляю![/italic spring_green2] Ты победил своего противника в "Морской Бой"!')
	input()