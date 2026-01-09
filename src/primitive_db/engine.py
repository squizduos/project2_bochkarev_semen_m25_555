import shlex

import prompt

from src.primitive_db.core import create_table, drop_table, list_tables
from src.primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = 'db_meta.json'


def print_help():
    print("***Процесс работы с таблицей***")
    print("Функции:")
    msg = (
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print(msg)
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def run():
    print("***База данных***")
    print("\nФункции:")
    msg = (
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print(msg)
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

    while True:
        user_input = prompt.string(">>>Введите команду: ").strip()

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректное значение. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            if len(args) < 3:
                print("Некорректное значение. Попробуйте снова.")
                continue

            table_name = args[1]
            columns = args[2:]

            metadata = load_metadata(METADATA_FILE)
            old_metadata = metadata.copy()
            metadata = create_table(metadata, table_name, columns)

            if metadata != old_metadata:
                save_metadata(METADATA_FILE, metadata)
        elif command == "list_tables":
            metadata = load_metadata(METADATA_FILE)
            tables = list_tables(metadata)

            if tables:
                for table in tables:
                    print(f"- {table}")
            else:
                pass
        elif command == "drop_table":
            if len(args) < 2:
                print("Некорректное значение. Попробуйте снова.")
                continue

            table_name = args[1]
            metadata = load_metadata(METADATA_FILE)
            old_metadata = metadata.copy()
            metadata = drop_table(metadata, table_name)

            if metadata != old_metadata:
                save_metadata(METADATA_FILE, metadata)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
