import functools
import time

import prompt


def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            msg = (
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
            print(msg)
            if func.__name__ in ('update', 'delete'):
                return args[0] if args else [], 0, []
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            if func.__name__ in ('update', 'delete'):
                return args[0] if args else [], 0, []
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            if func.__name__ in ('update', 'delete'):
                return args[0] if args else [], 0, []
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            if func.__name__ in ('update', 'delete'):
                return args[0] if args else [], 0, []
            return None
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if response != 'y':
                print("Операция отменена.")
                if func.__name__ == 'delete':
                    return args[0] if args else [], 0, []
                return args[0] if args else None
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    cache = {}
    
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
    
    def clear_cache():
        cache.clear()
    
    cache_result.clear = clear_cache
    return cache_result

