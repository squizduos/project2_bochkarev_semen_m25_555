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

