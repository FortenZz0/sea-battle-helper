from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.padding import Padding
from rich.console import Console

import os

from SeaBattleHelper import SeaBattleHelper

import tools



if __name__ == "__main__":
	console = Console()
	console.set_window_title("Sea Battle Helper -- by FortenZz")

	print(" По умолчанию программа настроена на:")
	print("  - 1 4-палубный корабль")
	print("  - 2 3-палубных корабля")
	print("  - 3 2-палубных корабля")
	print("  - 4 1-палубных корабля\n")
	
	enter_ships = tools.choice_of_variants(
		" Изменить эти данные? ([spring_green2]Да[/spring_green2] / [spring_green2]Нет[/spring_green2])",
		["д", "да", "1", "н", "нет", "0"],
		default="Нет",
		show_default=True,
		lower_input=True
	) in "да1"
	
	
	if enter_ships:
		# Выбор типов кораблей на поле
		ships_cells = tools.list_choice(
			"\n\n Введите допустимые размеры кораблей (в клетках, от 1 до 10)",
			default="1 2 3 4",
			show_default=True,
			func=int,
			min_value=1,
			max_value=10
		)
		
		print("\n Введите количество каждого типа кораблей на поле (от 0 до 10):")
		
		# Выбор количества этих кораблей
		ships_count = [0 for _ in range(len(ships_cells))]
		vars = [str(i) for i in range(11)]
		
		for i, ship in enumerate(ships_cells):
			ships_count[i] = int(tools.choice_of_variants(
				str(ship),
				vars,
			))
	
		helper = SeaBattleHelper(ships_count=ships_count, ships_cells=ships_cells)
	else:
		helper = SeaBattleHelper()
		
		
	
	human_cells = []
	for i in helper.headers:
		for j in range(helper.height):
			human_cells.append(i + str(j + 1))
			
	header_panel = Panel(
		'Программа-помощник для игры [spring_green2]"Морской Бой"[/spring_green2], '
		'анализирующая поле противника для предугадывания самых выгодных ходов.',
		highlight=True,
		title="[light_goldenrod1]Sea Battle Helper[/light_goldenrod1]",
		width=60
	)
	
	while True:
		os.system("mode con cols=61 lines=38")
		console.clear()
		
		# Очистка и заполнение таблицы
		helper.clear_area()
		helper.fill_area()
		
		# Вывод хедера
		print(header_panel)
		
		# Вывод таблицы
		tools.print_pretty_area(helper, "[light_goldenrod1]Таблица вероятностей[/light_goldenrod1]")
		
		
		max_cells = helper.find_max()[0] # Клетки с наибольшей вероятностью
		human_max_cells = list(map(helper.humanize_cell, max_cells)) # Те же клетки, но в "человеческом" виде
		inp_default = human_max_cells[0] # Значение по умолчанию для запроса целевой клетки
		
		
		# Вывод клеток с наибольшей вероятностью
		print(Padding(
			Panel(
				Align(
					"[spring_green2]" + " ".join(human_max_cells) + "[/spring_green2]",
					align="center"
				),
				title="[light_goldenrod1]Наибольшая вероятность[/light_goldenrod1]",
				highlight=True,
				width=58
			),
			pad=(1, 0, 1, 1)
		))
		
		
		# Вывод оставшегося количества кораблей
		ships = [" Осталось кораблей:"]
		for i in range(len(helper.ships_alive)-1, -1, -1):
			alive = helper.ships_alive[i]
			ships.append(
				f" [{'light_goldenrod1' if alive else 'red'}]"  # Открывающий тег с цветом
				f"{' '.join(['X' for _ in range(helper.ships_cells[i])])}"  # Визуализация корабля
				f"[/{'light_goldenrod1' if alive else 'red'}]: "  # Закрывающий тег с цветом и ":"
				f"{'[red]' if not alive else ''}"  # открывающий тег с цветом мёртвого корабля
				f"{helper.ships_count[i]}"  # количество кораблей
				f"{'[/red]' if not alive else ''}"  # закрывающий тег с цветом мёртвого корабля и ":"
			)
		print("\n".join(ships) + "\n\n")
		
		
		# Запрос целевой клетки
		target_cell = tools.choice_of_variants(
			" Клетка для выстрела",
			human_cells,
			default=inp_default,
			show_default=True,
			upper_input=True
		)
		coords = helper.cell_to_coords(target_cell) # Координаты целевой клетки
		
		
		# Попал ли игрок
		damage = tools.choice_of_variants(
			" Попал? ([spring_green2]Да[/spring_green2] / [spring_green2]Нет[/spring_green2])",
			["д", "да", "1", "н", "нет", "0"],
			default="нет",
			show_default=True,
			lower_input=True
		) in "да1"
		
		
		if damage: # Попадание
			# Был ли убит вражеский корабль этим попаданием
			kill = tools.choice_of_variants(
				" Убил? ([spring_green2]Да[/spring_green2] / [spring_green2]Нет[/spring_green2])",
				["д", "да", "1", "н", "нет", "0"],
				default="нет",
				show_default=True,
				lower_input=True
			) in "да1"
			
			helper.hit(*coords, kill)
		else: # Промах
			helper.miss(*coords)
		
		
		# Победа (нет живых кораблей соперника)
		if not any(helper.ships_alive):
			print('\n\n[italic spring_green2]Поздравляю![/italic spring_green2]'
			      'Ты победил своего противника в "Морской Бой"!')
			input()
			
	
	
