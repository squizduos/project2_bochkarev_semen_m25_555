VALID_TYPES = {'int', 'str', 'bool'}


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

