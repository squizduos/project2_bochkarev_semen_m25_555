VALID_TYPES = {'int', 'str', 'bool'}


def parse_where_clause(where_str):
    if not where_str or '=' not in where_str:
        return None
    
    parts = where_str.split('=', 1)
    if len(parts) != 2:
        return None
    
    column = parts[0].strip()
    value_str = parts[1].strip()
    
    if value_str.startswith('"') and value_str.endswith('"'):
        value = value_str[1:-1]
    elif value_str.startswith("'") and value_str.endswith("'"):
        value = value_str[1:-1]
    else:
        if value_str.lower() == 'true':
            value = True
        elif value_str.lower() == 'false':
            value = False
        else:
            try:
                value = int(value_str)
            except ValueError:
                value = value_str
    
    return {column: value}


def parse_set_clause(set_str):
    result = {}
    assignments = set_str.split(',')
    
    for assignment in assignments:
        if '=' not in assignment:
            continue
        
        parts = assignment.split('=', 1)
        if len(parts) != 2:
            continue
        
        column = parts[0].strip()
        value_str = parts[1].strip()
        
        if value_str.startswith('"') and value_str.endswith('"'):
            value = value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            value = value_str[1:-1]
        else:
            if value_str.lower() == 'true':
                value = True
            elif value_str.lower() == 'false':
                value = False
            else:
                try:
                    value = int(value_str)
                except ValueError:
                    value = value_str
        
        result[column] = value
    
    return result


def convert_value_type(value, target_type):
    if target_type == 'int':
        return int(value)
    elif target_type == 'str':
        return str(value)
    elif target_type == 'bool':
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)
    return value


def validate_record(record, metadata, table_name):
    columns = metadata[table_name]
    
    for col_name, col_type in columns:
        if col_name not in record:
            return False, f"Отсутствует столбец: {col_name}"
        
        value = record[col_name]
        expected_type = col_type
        
        if expected_type == 'int' and not isinstance(value, int):
            return False, f"Неверный тип для столбца {col_name}: ожидается int"
        elif expected_type == 'str' and not isinstance(value, str):
            return False, f"Неверный тип для столбца {col_name}: ожидается str"
        elif expected_type == 'bool' and not isinstance(value, bool):
            return False, f"Неверный тип для столбца {col_name}: ожидается bool"
    
    return True, None


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    validated_columns = []
    validated_columns.append(('ID', 'int'))

    for col_def in columns:
        if ':' not in col_def:
            print(f'Некорректное значение: {col_def}. Попробуйте снова.')
            return metadata

        col_name, col_type = col_def.rsplit(':', 1)
        col_type = col_type.strip().lower()

        if col_type not in VALID_TYPES:
            print(f'Некорректное значение: {col_def}. Попробуйте снова.')
            return metadata

        validated_columns.append((col_name.strip(), col_type))

    metadata[table_name] = validated_columns

    col_str = ', '.join([f'{name}:{type_}' for name, type_ in validated_columns])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {col_str}')

    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')

    return metadata


def list_tables(metadata):
    if not metadata:
        return []

    return list(metadata.keys())


def insert(metadata, table_name, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    
    columns = metadata[table_name]
    expected_count = len(columns) - 1
    
    if len(values) != expected_count:
        msg = (
            f'Ошибка: Количество значений ({len(values)}) '
            f'не соответствует количеству столбцов ({expected_count}).'
        )
        print(msg)
        return None
    
    record = {}
    record['ID'] = 0
    
    for i, (col_name, col_type) in enumerate(columns[1:], 0):
        value_str = values[i].strip()
        
        if value_str.startswith('"') and value_str.endswith('"'):
            value = value_str[1:-1]
        elif value_str.startswith("'") and value_str.endswith("'"):
            value = value_str[1:-1]
        else:
            try:
                value = convert_value_type(value_str, col_type)
            except (ValueError, TypeError):
                msg = (
                    f'Ошибка: Не удалось преобразовать значение "{value_str}" '
                    f'в тип {col_type} для столбца {col_name}.'
                )
                print(msg)
                return None
        
        record[col_name] = value
    
    return record


def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data
    
    filtered = []
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                match = False
                break
        if match:
            filtered.append(record)
    
    return filtered


def update(table_data, metadata, table_name, set_clause, where_clause):
    if table_name not in metadata:
        return table_data, 0, []
    
    columns = metadata[table_name]
    column_dict = {col[0]: col[1] for col in columns}
    
    for key in set_clause.keys():
        if key not in column_dict:
            print(f'Ошибка: Столбец "{key}" не существует в таблице "{table_name}".')
            return table_data, 0, []
        value = set_clause[key]
        expected_type = column_dict[key]
        if expected_type == 'int' and not isinstance(value, int):
            print(f'Ошибка: Неверный тип для столбца {key}: ожидается int.')
            return table_data, 0, []
        elif expected_type == 'str' and not isinstance(value, str):
            print(f'Ошибка: Неверный тип для столбца {key}: ожидается str.')
            return table_data, 0, []
        elif expected_type == 'bool' and not isinstance(value, bool):
            print(f'Ошибка: Неверный тип для столбца {key}: ожидается bool.')
            return table_data, 0, []
    
    updated_count = 0
    updated_ids = []
    
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                match = False
                break
        
        if match:
            for key, value in set_clause.items():
                if key in record:
                    record[key] = value
            updated_count += 1
            updated_ids.append(record.get('ID', 'unknown'))
    
    return table_data, updated_count, updated_ids


def delete(table_data, where_clause):
    deleted_count = 0
    deleted_ids = []
    filtered = []
    
    for record in table_data:
        match = True
        for key, value in where_clause.items():
            if key not in record or record[key] != value:
                match = False
                break
        
        if match:
            deleted_count += 1
            deleted_ids.append(record.get('ID', 'unknown'))
        else:
            filtered.append(record)
    
    return filtered, deleted_count, deleted_ids


def info(metadata, table_name, table_data):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    
    columns = metadata[table_name]
    col_str = ', '.join([f'{name}:{type_}' for name, type_ in columns])
    
    print(f'Таблица: {table_name}')
    print(f'Столбцы: {col_str}')
    print(f'Количество записей: {len(table_data)}')

