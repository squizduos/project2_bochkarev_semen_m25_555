import re
import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db.constants import METADATA_FILE
from src.primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from src.primitive_db.decorators import create_cacher
from src.primitive_db.parser import parse_set_clause, parse_where_clause
from src.primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)
cache_result = create_cacher()


def print_help():
    print("***Операции с данными***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print(
        "<command> select from <имя_таблицы> - прочитать все записи."
    )
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def display_table(table_data, metadata, table_name):
    if not table_data:
        return
    
    columns = metadata[table_name]
    table = PrettyTable()
    
    field_names = [col[0] for col in columns]
    table.field_names = field_names
    
    for record in table_data:
        row = []
        for col_name, _ in columns:
            value = record.get(col_name, '')
            if isinstance(value, bool):
                value = 'True' if value else 'False'
            row.append(value)
        table.add_row(row)
    
    print(table)


def parse_insert_command(user_input):
    pattern = r'insert\s+into\s+(\w+)\s+values\s+\((.*)\)'
    match = re.search(pattern, user_input, re.IGNORECASE)
    if not match:
        return None, None
    
    table_name = match.group(1)
    values_str = match.group(2).strip()
    
    try:
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(values_str):
            char = values_str[i]
            
            if char in ('"', "'") and (i == 0 or values_str[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_value += char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                    current_value += char
                else:
                    current_value += char
            elif char == ',' and not in_quotes:
                if current_value.strip():
                    values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        if current_value.strip():
            values.append(current_value.strip())
        
        return table_name, values
    except Exception:
        return None, None


def parse_select_command(user_input):
    pattern = r'select\s+from\s+(\w+)(?:\s+where\s+(.+))?'
    match = re.search(pattern, user_input, re.IGNORECASE)
    if not match:
        return None, None
    
    table_name = match.group(1)
    where_clause_str = match.group(2) if match.group(2) else None
    
    where_clause = None
    if where_clause_str:
        where_clause = parse_where_clause(where_clause_str.strip())
    
    return table_name, where_clause


def parse_update_command(user_input):
    pattern = r'update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)'
    match = re.search(pattern, user_input, re.IGNORECASE)
    if not match:
        return None, None, None
    
    table_name = match.group(1)
    set_clause_str = match.group(2)
    where_clause_str = match.group(3)
    
    set_clause = parse_set_clause(set_clause_str.strip())
    where_clause = parse_where_clause(where_clause_str.strip())
    
    return table_name, set_clause, where_clause


def parse_delete_command(user_input):
    pattern = r'delete\s+from\s+(\w+)\s+where\s+(.+)'
    match = re.search(pattern, user_input, re.IGNORECASE)
    if not match:
        return None, None
    
    table_name = match.group(1)
    where_clause_str = match.group(2)
    
    where_clause = parse_where_clause(where_clause_str.strip())
    
    return table_name, where_clause


def run():
    print("***Операции с данными***")
    print("\nФункции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print(
        "<command> select from <имя_таблицы> - прочитать все записи."
    )
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

    while True:
        user_input = prompt.string(">>> Введите команду: ").strip()

        if not user_input:
            continue

        if user_input.lower().startswith('insert into'):
            table_name, values = parse_insert_command(user_input)
            if table_name is None or values is None:
                print("Некорректное значение. Попробуйте снова.")
                continue
            
            metadata = load_metadata(METADATA_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            record = insert(metadata, table_name, values)
            if record is None:
                continue
            
            table_data = load_table_data(table_name)
            
            if table_data:
                max_id = max(r.get('ID', 0) for r in table_data)
                record['ID'] = max_id + 1
            else:
                record['ID'] = 1
            
            table_data.append(record)
            save_table_data(table_name, table_data)
            cache_result.clear()
            msg = (
                f'Запись с ID={record["ID"]} '
                f'успешно добавлена в таблицу "{table_name}".'
            )
            print(msg)
        
        elif user_input.lower().startswith('select from'):
            table_name, where_clause = parse_select_command(user_input)
            if table_name is None:
                print("Некорректное значение. Попробуйте снова.")
                continue
            
            metadata = load_metadata(METADATA_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = load_table_data(table_name)
            cache_key = (table_name, str(where_clause) if where_clause else None)
            filtered_data = cache_result(
                cache_key,
                lambda: select(table_data, where_clause)
            )
            display_table(filtered_data, metadata, table_name)
        
        elif user_input.lower().startswith('update'):
            table_name, set_clause, where_clause = parse_update_command(user_input)
            if table_name is None or set_clause is None or where_clause is None:
                print("Некорректное значение. Попробуйте снова.")
                continue
            
            metadata = load_metadata(METADATA_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = load_table_data(table_name)
            table_data, updated_count, updated_ids = update(
                table_data, metadata, table_name, set_clause, where_clause
            )
            
            if updated_count > 0:
                save_table_data(table_name, table_data)
                cache_result.clear()
                for record_id in updated_ids:
                    msg = (
                        f'Запись с ID={record_id} в таблице "{table_name}" '
                        f'успешно обновлена.'
                    )
                    print(msg)
            else:
                print(f'Записи не найдены для обновления в таблице "{table_name}".')
        
        elif user_input.lower().startswith('delete from'):
            table_name, where_clause = parse_delete_command(user_input)
            if table_name is None or where_clause is None:
                print("Некорректное значение. Попробуйте снова.")
                continue
            
            metadata = load_metadata(METADATA_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = load_table_data(table_name)
            table_data, deleted_count, deleted_ids = delete(table_data, where_clause)
            
            if deleted_count > 0:
                save_table_data(table_name, table_data)
                cache_result.clear()
                for record_id in deleted_ids:
                    msg = (
                        f'Запись с ID={record_id} '
                        f'успешно удалена из таблицы "{table_name}".'
                    )
                    print(msg)
            else:
                print(f'Записи не найдены для удаления в таблице "{table_name}".')
        
        elif user_input.lower().startswith('info'):
            try:
                args = shlex.split(user_input)
                if len(args) < 2:
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                
                table_name = args[1]
                metadata = load_metadata(METADATA_FILE)
                table_data = load_table_data(table_name)
                info(metadata, table_name, table_data)
            except ValueError:
                print("Некорректное значение. Попробуйте снова.")
                continue
        
        elif user_input.lower() == 'exit':
            break
        
        elif user_input.lower() == 'help':
            print_help()
        
        elif user_input.lower().startswith('create_table'):
            try:
                args = shlex.split(user_input)
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
            except ValueError:
                print("Некорректное значение. Попробуйте снова.")
                continue
        
        elif user_input.lower() == 'list_tables':
            metadata = load_metadata(METADATA_FILE)
            tables = list_tables(metadata)

            if tables:
                for table in tables:
                    print(f"- {table}")
        
        elif user_input.lower().startswith('drop_table'):
            try:
                args = shlex.split(user_input)
                if len(args) < 2:
                    print("Некорректное значение. Попробуйте снова.")
                    continue

                table_name = args[1]
                metadata = load_metadata(METADATA_FILE)
                old_metadata = metadata.copy()
                metadata = drop_table(metadata, table_name)

                if metadata != old_metadata:
                    save_metadata(METADATA_FILE, metadata)
            except ValueError:
                print("Некорректное значение. Попробуйте снова.")
                continue
        
        else:
            print("Функции нет. Попробуйте снова.")
