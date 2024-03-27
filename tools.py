from tabulate import tabulate

from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.padding import Padding

from SeaBattleHelper import SeaBattleHelper



# Вывод красивой таблицы с полем
def print_pretty_area(helper: SeaBattleHelper, header: str) -> None:
	# подсветка максимальных значений
	max_chances = helper.find_max()
	
	for x, y in max_chances[0]:
		helper.area[y][x] = helper.max_chance_format[0](max_chances[1])
	
	# Создание таблицы
	table = tabulate(
		helper.area,
		["#"] + helper.headers,
		tablefmt="simple",
		showindex=[i + 1 for i in range(helper.width)],
		colalign=["left"] + ["right"] * 10,
		maxcolwidths=3
	)
	
	# Замена обычных символов на цветные
	# (Если их сразу добавить цветными в таблицу, то она разъедется,
	# потому что tabulate будет считать форматирование для rich,
	# как содержимое ячейки)
	for s in helper.symbols:
		table = table.replace(helper.symbols[s][0], helper.symbols[s][1])
	
	# Подсветка максимальных значений
	max_value = helper.max_chance_format[1](max_chances[1])
	table = table.replace(helper.max_chance_format[0](max_chances[1]), max_value)
	
	panel = Padding(
		Panel(
			Align(table, align="center"),
			highlight=True,
			title=header,
			width=58
		),
		pad=(2, 0, 0, 1)
	)
	
	print(panel)
	
	# Возвращаем максимальные значения обратно (на всякий случай)
	for x, y in max_chances[0]:
		helper.area[y][x] = max_chances[1]


# Выбор из предложенных вариантов
def choice_of_variants(
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
			f"{(' [Enter = [spring_green2]' + default + '[/spring_green2]]') if show_default else ''}: ",
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
		

# Выбор в список
def list_choice(
		question: str,
		func = str,
		sep: str = " ",
		default: str | None = None,
		show_default: bool = False,
		min_value: int | None = None,
		max_value: int | None = None
	):
	while True:
		print(
			f"{question}"
			f"{(' [Enter = [spring_green2]' + default + '[/spring_green2]]') if show_default else ''}: ",
			end=""
		)
		inp = input()
		
		if not inp and default:
			inp = default
		
		lst = inp.split(sep)
		
		try:
			result = list(map(func, lst))
			
			if min_value:
				result = list(map(lambda x: max(min_value, x), result))
				
			if max_value:
				result = list(map(lambda x: min(max_value, x), result))
			
			break
		except:
			continue
			
	return result