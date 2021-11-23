import os
import re
import time


def _connect_to_db_cook_book(path):
    """
    Фуцнкция эмулирует подключение к БД, а именно проверяет существует ли файл по заданному в path пути.
    В случае неудачного подключения, а именно не найдя заданный файл в пераметре path функция возращает False,
     как признак того, что подключение установить не удалось, перед этим проводя 5 попыток его обнаружить.

    Для эмуляции работы функции можно передать ей путь до файла, а сам файл переименовать, затем, в момент попыток
    совершить повторное изменение имени файда на исходное.
    """
    attempt = 1
    while not os.path.exists(path):
        while attempt < 6:
            print(f'Попытка подключеня к БД {attempt}', end='')
            for i in range(5):
                print(".", end='')
                time.sleep(1)
            print()
            attempt += 1
            if attempt == 6:
                print('Не удалось подключиться к БД, операция не выполнена.')
                return False
            else:
                break
    return True


def get_cook_book(path):
    """
    В качетсве параметра функция принимает путь до файла, используя функцию _connect_to_db_cook_book происходит проверка,
    что файл доступен. В случае доступности файла сожержимое парсится и записывается в словарь result, который возвращает
    функуия.

    В случае недоступности файла, выводится сообщение и возвращается None.
    """
    # if path.find('\\') != -1:
    #     file_name = path.split('\\')
    # elif path.find('/') != -1:
    #     file_name = path.split('/')

    if not _connect_to_db_cook_book(path):
        print(f'База данных не найдена, файл {os.path.basename(path)} отсутствует в дериктории {os.getcwd()}')
        return None
    with open(path, 'rt', encoding='utf-8') as file:
        result = {}
        for dish in file:
            dish_name = dish.strip()
            count_of_ingredients = int(file.readline().strip())
            temp_data = []
            for item in range(count_of_ingredients):
                ingredient_name, quantity, measure = file.readline().split('|')
                temp_data.append({'ingredient_name': ingredient_name.strip(), 'quantity': quantity.strip(),
                                  'measure': measure.strip()})
            result[dish_name] = temp_data
            file.readline()
    return result


def get_cook_book_text(cook_book, print_cook_book_text=False):
    """
    Функция возращает содержание локальной копии книги поваренка в том виде как оно хранится в БД, либо же выводит содер
    жание локальной копии книги поваренка на экран, в зависимости от параметра  print_cook_book_text.
    :param cook_book: локальная копия книги поваренка
    :param print_cook_book_text: false возвращает содержание локальной копии, true отображает в терминале содержангие
    локальной копии книги поваренка
    """
    cook_book_text = ''
    for dish in cook_book:

        if not print_cook_book_text:
            cook_book_text += f'{dish}\n{len(cook_book[dish])}\n'
        else:
            print(f"{dish}:")

        for ingredient in cook_book[dish]:
            ingredient_text = f"{ingredient['ingredient_name']} | {ingredient['quantity']} | {ingredient['measure']}"

            if not print_cook_book_text:
                cook_book_text += ingredient_text + "\n"
            else:
                print(ingredient_text)

        if not print_cook_book_text:
            cook_book_text += "\n"
        else:
            print()

    if not print_cook_book_text:
        return cook_book_text


def _get_dishes_to_list(cook_book):
    """
    Функция позволяет сформировать список блюд, ингредиенты которых требуется купить в магазине, запрашивая пользователя,
    что он хочет приготовить из книги поваренка.
    """
    dish_list = []
    dish_list_for_buy = []

    for dish in cook_book:
        dish_list.append(dish)
    while True:
        for dish in dish_list:
            print(f"[{dish_list.index(dish)}] {dish}")
        print(f"[{len(dish_list)}] Закончить выбор блюд\n")

        choose = input('Укажите № блюда для добавления его ингридиентов в список покупок: ')

        if choose.isdigit():
            choose = int(choose)
            if choose == len(dish_list):
                break
            elif dish_list[choose] not in dish_list_for_buy:
                dish_list_for_buy.append(dish_list[choose])
            else:
                print(f"Вы уже добавили блюдо '{dish_list[choose]}' в список для покупки его ингридиентов\n")
        else:
            print('Введенные данные не являются номером блюда, введите цифру')
    return dish_list_for_buy


def _get_user_input(exp, message, arg=''):
    """
    Без комментариев
    """
    while not re.match(exp, arg):
        arg = input(message)
    return arg


def _save_shop_list_for_dishes(ingredients_list):
    """
    Позволяет сохранить список ингрединетов для прокупки в отдельный файл
    """
    path = os.path.join(os.getcwd(), 'ingredients_list.txt')
    string = 'Список ингредиентов для покупки:\n'

    for key, value in ingredients_list.items():
        string += f'{key} - {value[0]} {value[1]}\n'
    with open(path, 'wt', encoding='utf-8') as file:
        file.write(string)
    return path


def get_shop_list_by_dishes(cook_book, dishes=None, person_count=None):
    """
    Функция принимает в качестве параметров
    :param cook_book: книгу поваренка
    :param dishes: список блюд из книги, можети быть None, тогда функция запросит пользовательский ввод
    :param person_count: количество персон, можети быть None, тогда функция запросит пользовательский ввод

    Для каждого блюда из :param dishes: функция смотрит ингредиенты и умножает количество показатель измерения каждого
    ингредиента на количество персон.
    :return:
    """
    if dishes is None:
        dishes = _get_dishes_to_list(cook_book)

    if person_count is None:
        person_count = int(_get_user_input(r'^\d+$', 'Введите количество гостей: '))

    if len(dishes) != 0:
        ingredients_list = {}
        for dish in dishes:
            ingredients_dish_in_cook_book = cook_book.get(dish)
            if ingredients_dish_in_cook_book is not None:
                for item in ingredients_dish_in_cook_book:
                    if item['ingredient_name'] in ingredients_list:
                        ingredients_list[item['ingredient_name']] = \
                            [ingredients_list.get(item['ingredient_name'])[0] + int(item['quantity']) * person_count,
                             item['measure']]
                    else:
                        ingredients_list[item['ingredient_name']] = \
                            [int(item['quantity']) * person_count, item['measure']]
            else:
                print(f'Блюда {dish} не существует в поваренной книге, для этого блюда не возможно рассчиать'
                      'необходимое количество ингредиентов.')
        if _get_user_input(r'^[yn]$', 'Сохранить список продуктов в файл? (y/n)') == 'y':
            path = _save_shop_list_for_dishes(ingredients_list)
            print(f'Список ингридиентов к покупке сохранен в {path}')
        else:
            print(ingredients_list)
        return ingredients_list
    print('Список блюд для покупки ингредиентов пуст. Невозможно сформировать список покупок')
    return None


def _update_db_cook_book(cook_book, path):
    """
    Функция обновляет БД из её локальной версии.
    """
    if _connect_to_db_cook_book(path):
        with open(path, 'wt', encoding='utf-8') as file:
            file.write(get_cook_book_text(cook_book))
            print('База рецептов успешно обновлена!')
            return True
    else:
        return False


def add_dish_to_cook_book(cook_book, path):
    """Функция позволяет добавить в локальную копию книги поваренка новый рецепт, а затем выгрузить ее в БД"""
    while True:
        dish_name = input('Введите название блюда: ')
        if dish_name not in cook_book:
            count_of_ingredients = _get_user_input(r'^\d+$', 'Введите количество ингредитентов: ')
            break
        else:
            print('Блюдо уже существует в поваренной книге')

    ingredient_list = []
    for ingredient in range(int(count_of_ingredients)):
        ingredient_name = input(f'Введите название игредиента №{ingredient + 1}: ')
        measure = input(f'Введите еденицу измерения для {ingredient_name}: ')
        quantity = _get_user_input(r'^\d+$', f'Введите количество {measure} для приготовления блюда в расчете на одну '
                                             f'персону: ')
        ingredient_list.append({'ingredient_name': ingredient_name, 'quantity': quantity, 'measure': measure})

    cook_book[dish_name] = ingredient_list

    if not _update_db_cook_book(cook_book, path):
        cook_book.pop(dish_name)


def remove_dish_in_cook_book(cook_book, path):
    """Функция позволяет удалить из локальной копии книги поваренка выбранный рецепт, а затем выгрузить ее в БД"""
    dish_list = ''
    for index, dish, in enumerate(cook_book):
        dish_list += f"{index + 1}) {dish}\n "
    print(f'В поваренную книгу добавлены следующие блюда:\n {dish_list}')
    while True:
        dish_name = input('Введите название блюда которе хотите удалить: ')
        if dish_name in cook_book:
            ingredient_list = cook_book.pop(dish_name)
            if not _update_db_cook_book(cook_book, path):
                cook_book[dish_name] = ingredient_list
            break
        else:
            print('Блюдо с указаным названием отсутствует в списке')


def main():
    path = os.path.join(os.getcwd(), 'cook_book.txt')
    cook_book = get_cook_book(path)
    if cook_book is not None:
        menu_list = """
                [1] Показать блюда из поваренной книни
                [2] Рассчитать ингредиенты для готовки блюд по количеству персон
                [3] Добавить блюдо в поваренную книгу
                [4] Удалить блюдо из поваренной книги
                [5] Выход"""
        while True:
            choose = input(f"Выберите действие: {menu_list}\nВаш выбор: ")
            if choose == '1':
                get_cook_book_text(cook_book, True)
                input('Нажмите любую кнопку')
            if choose == '2':
                get_shop_list_by_dishes(cook_book)
                input('Нажмите любую кнопку')
            if choose == '3':
                add_dish_to_cook_book(cook_book, path)
                input('Нажмите любую кнопку')
            if choose == '4':
                remove_dish_in_cook_book(cook_book, path)
                input('Нажмите любую кнопку')
            if choose == '5':
                break


if __name__ == '__main__':
    main()
