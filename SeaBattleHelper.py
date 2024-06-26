from itertools import compress


class SeaBattleHelper:
	def __init__(
			self,
			ships_count: [int] = [4, 3, 2, 1],
			ships_cells: [int] = [1, 2, 3, 4]
	) -> None:
		
		self.width = 10
		self.height = 10
		
		self.area = [["0" for _ in range(self.width)] for __ in range(self.height)]
		
		self.ships_count = ships_count
		self.ships_cells = ships_cells
		self.ships_alive = list(map(bool, ships_count))
		self.ships_destroyed = [0, 0, 0, 0]
		
		self._damaged_ships = []
		self._checked_hit_cells = set()
		
		self.get_biggest_ship = lambda: max(compress(self.ships_cells, self.ships_alive))
		self.get_lowest_ship = lambda: min(compress(self.ships_cells, self.ships_alive))
		self.get_alive_ships_cells = lambda: compress(self.ships_cells, self.ships_alive)
		
		self.headers = list("АБВГДЕЖЗИК")
		
		# [0] - просто символ (добавляется перед созданием таблицы)
		# [1] - отформатированный символ (на него заменяется [0] ПОСЛЕ создания таблицы)
		self.symbols = {
			"miss": ("O", "[bright_black]О[/bright_black]"),
			"hit": ("X", "[light_goldenrod1]X[/light_goldenrod1]")
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
	def find_max(self) -> ([(int, int)], str):  # ([*max_cells], max_value)
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
		def update_cells(start_cell: (int, int), line_direction: (int, int)):
			if sum(line_direction):
				cells = self._get_line_cells(*start_cell, line_direction, True)
			
				if not self._is_valid_cells(cells):
					return
			else:
				cells = self._get_cross_cells(*start_cell)
			
			for cell in cells:
				if not self.area[cell[1]][cell[0]].isdigit():
					continue
				
				add_value = self.get_biggest_ship() - self._distance(cell, hit_cells[0])
				self.area[cell[1]][cell[0]] = str(int(self.area[cell[1]][cell[0]]) + add_value * 10)
		
		
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
				
				hit_cells = self.get_ship_cells(hit_cells[0])
				
				if len(hit_cells) == 1:
					update_cells((x, y), (0, 0))
				else:
					
					direction_1 = (
						hit_cells[1][0] - hit_cells[0][0],
						hit_cells[1][1] - hit_cells[0][1]
					)
					
					direction_2 = (
						hit_cells[-2][0] - hit_cells[-1][0],
						hit_cells[-2][1] - hit_cells[-1][1]
					)
					
					update_cells(hit_cells[0], direction_1)
					update_cells(hit_cells[-1], direction_2)
				
				if not hit_cells in self._damaged_ships:
					self._damaged_ships.append(hit_cells)
	
	
	# Получаем все клетки корабля
	def get_ship_cells(self, start_cell: (int, int)) -> [(int, int)]:
		self._checked_hit_cells = set()
		
		cells = [start_cell]
		
		is_one_hit = True
		direction = (0, 0)
		
		for cell in self._get_around_cells(*start_cell, True):
			if self.area[cell[1]][cell[0]] == self.symbols["hit"][0]:
				is_one_hit = False
				direction = (cell[0] - start_cell[0], cell[1] - start_cell[1])
		
		if not is_one_hit:
			new_cell = (
				cells[0][0] + direction[0],
				cells[0][1] + direction[1]
			)
			
			while True:
				if not (0 <= new_cell[0] < self.width and 0 <= new_cell[1] < self.height) or \
						self.area[new_cell[1]][new_cell[0]] != self.symbols["hit"][0]:
					break
				
				if not new_cell in self._checked_hit_cells:
					cells.append(new_cell)
					self._checked_hit_cells.add(new_cell)
				
				new_cell = (
					new_cell[0] + direction[0],
					new_cell[1] + direction[1]
				)
		
		return cells
	
	
	# Проверка на то, что в данных ячейках может находиться корабль
	# (Передавать ТОЛЬКО ЛИНИЮ клеток)
	def _is_valid_cells(self, cells: (int, int)) -> bool:
		valid = True
		
		for cell in cells:
			if cell[0] >= self.width or cell[1] >= self.height or \
					self.area[cell[1]][cell[0]] == self.symbols["miss"][0]:
				valid = False
				break
		
		return valid
		
		
	# Заполнение таблицы вероятностей
	def fill_area(self) -> None:
		def update_by_ship(start_cell: (int, int), direction: (int, int)) -> None:
			cells = [
				(
					start_cell[0] + i * direction[0],
					start_cell[1] + i * direction[1]
				)
				for i in range(ship)
			]
			
			if not self._is_valid_cells(cells):
				return
			
			for cell in cells:
				if self.area[cell[1]][cell[0]] != self.symbols["hit"][0]:
					self.area[cell[1]][cell[0]] = str(int(self.area[cell[1]][cell[0]]) + 1)
		
		# Заполняем поле относительно попаданий
		self.update_hits()
		
		# return None
		
		# Заполняем поле, расставляя корабли
		for ship in compress(self.ships_cells, self.ships_alive):
			for y in range(self.height):
				for x in range(self.width):
					# Горизонтальные позиции
					update_by_ship((x, y), (1, 0))
					
					if ship == 1: continue
					
					# Вертикальные позиции
					update_by_ship((x, y), (0, 1))
	
	
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
		directions = (
			(0, 1),
			(1, 0),
			(0, -1),
			(-1, 0)
		)
		
		cells = []
		
		for direction in directions:
			line = self._get_line_cells(x, y, direction, pass_miss=False)
			
			cells += line
		
		return cells
	
	
	# Получаем ячейки по одной линии от клетки
	def _get_line_cells(self,
	                    x: int, y: int,
	                    direction: (int, int),
	                    pass_hits: bool = False,
	                    pass_miss: bool = False) -> [(int, int)]:
		cells = []
		
		for i in range(1, self.get_biggest_ship()):
			new_x = x + direction[0] * i
			new_y = y + direction[1] * i
			
			if not (0 <= new_x < self.width and 0 <= new_y < self.width):
				continue
			
			if self.area[new_y][new_x].isdigit() or \
					(pass_hits and self.area[new_y][new_x] == self.symbols["hit"][0]) or \
					(pass_miss and self.area[new_y][new_x] == self.symbols["miss"][0]):
				cells.append((new_x, new_y))
			else:
				break
		
		if len(cells) < self.get_lowest_ship() - 1:
			return []
		
		return cells
	
	
	# Расстояние между двумя клетками
	def _distance(self, a: (int, int), b: (int, int)) -> int:
		return int(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)
	
	
	# Конвертация "программных" координат клетки в "человеческие"
	def humanize_cell(self, cell: (int, int)) -> str:
		return self.headers[cell[0]] + str(cell[1] + 1)
	
	
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
		
		ship_cells = self.get_ship_cells((x, y))
		
		for cell in ship_cells:
			for ar_cell in self._get_around_cells(*cell):
				self.miss(*ar_cell)
		
		self.ships_count[len(ship_cells) - 1] -= 1
		if self.ships_count[len(ship_cells) - 1] <= 0:
			self.ships_alive[len(ship_cells) - 1] = False
