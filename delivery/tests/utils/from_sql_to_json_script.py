import ast
import importlib.util
import json
import os
import re


def get_function_names(file_path):
    """Получает имена всех функций из файла"""

    with open(f'{file_path}', "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    return [
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def load_module_from_path(file_path):
    """Загружает модуль из .py файла по пути"""
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def process_sql_value(val_str: str):
    """
    Обрабатывает одно значение из SQL-запроса, приводя его к нужному типу.
    Версия 5: Различает массивы объектов и массивы простых значений.
    """
    original_val = val_str.strip()

    # 1. Проверяем на нестроковые литералы SQL
    if original_val.lower() == 'null':
        return None
    if original_val.lower() == 'true':
        return True
    if original_val.lower() == 'false':
        return False

    # 2. Проверяем, является ли значение строкой в кавычках
    if original_val.startswith("'") and original_val.endswith("'"):
        content_str = original_val[1:-1].replace("''", "'")
        content_stripped = content_str.strip()

        # Пытаемся распарсить как JSON-объект
        if content_stripped.startswith('{') and content_stripped.endswith('}'):
            try:
                return json.loads(content_stripped)
            except json.JSONDecodeError:
                pass  # Если не JSON, продолжаем как обычная строка

        # ----- УЛУЧШЕННАЯ ЛОГИКА ДЛЯ МАССИВОВ -----
        if content_stripped.startswith('[') and content_stripped.endswith(']'):
            try:
                arr = json.loads(content_stripped)
                if not isinstance(arr, list): return content_stripped  # На случай, если это не список

                # Если массив пуст или содержит объекты (словари), возвращаем как нативный список
                if not arr or isinstance(arr[0], dict):
                    return arr
                # Иначе это массив простых значений, форматируем в строку "{...}"
                else:
                    return f"{{{','.join(map(str, arr))}}}"
            except (json.JSONDecodeError, IndexError):
                pass  # Если не JSON, продолжаем как обычная строка

        # Если это не JSON, то это обычная строка
        return content_str

    # 3. Если кавычек не было, значит это число
    try:
        return int(original_val)
    except (ValueError, TypeError):
        try:
            return float(original_val)
        except (ValueError, TypeError):
            return original_val


def split_sql_values(values_str: str):
    """
    Надежно разделяет значения из секции VALUES.
    Версия 3: Улучшенный парсер, который корректно обрабатывает '' и экранированные кавычки.
    """
    values = []
    current_val = ""
    in_quotes = False
    i = 0
    n = len(values_str)
    while i < n:
        char = values_str[i]

        if not in_quotes:
            if char == "'":
                in_quotes = True
            elif char == ',':
                values.append(current_val.strip())
                current_val = ""
                i += 1
                continue
            current_val += char
        else:  # in_quotes is True
            if char == "'":
                if i + 1 < n and values_str[i + 1] == "'":
                    current_val += "''"
                    i += 1
                else:
                    in_quotes = False
            current_val += char
        i += 1

    values.append(current_val.strip())
    return values


def parse_and_save_inserts(sql_text, output_dir=None):
    """
    Парсит SQL INSERT-запросы, корректно обрабатывая типы данных, и сохраняет в JSON.
    """
    statements = [stmt.strip() for stmt in sql_text.strip().split(';') if stmt.strip()]
    inserts_by_table = {}

    for stmt in statements:
        if not stmt.lower().startswith("insert into"):
            continue

        insert_regex = re.compile(
            r"insert into\s+(?P<full_table_name>[\w`\"\[\].]+)\s*"
            r"\((?P<columns>[^)]+)\)\s*"
            r"values\s*\("
            r"(?P<values>.*)"
            r"\s*\)",
            re.IGNORECASE | re.DOTALL
        )
        match = insert_regex.search(stmt)
        if not match:
            print(f"Пропущено: не удалось разобрать -> {stmt[:100]}...")
            continue

        table_name = match.group("full_table_name").split('.')[-1].strip('`"[]')

        columns_str = match.group("columns").replace('\n', '')
        columns = [col.strip().strip('`"[]') for col in columns_str.split(",")]

        values_str = match.group("values").replace('\n', ' ').strip()
        raw_values = split_sql_values(values_str)
        processed_values = [process_sql_value(v) for v in raw_values]

        if len(columns) != len(processed_values):
            print(
                f"⚠️ Несовпадение колонок ({len(columns)}) и значений ({len(processed_values)}) в запросе к таблице '{table_name}'.")
            continue

        row = dict(zip(columns, processed_values))
        inserts_by_table.setdefault(table_name, []).append(row)

    if output_dir is None:
        output_dir = os.getcwd()

    os.makedirs(output_dir, exist_ok=True)

    for table, rows in inserts_by_table.items():
        output_path = os.path.join(output_dir, f"{table}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=4, ensure_ascii=False)
        print(f"💾 Сохранено: {output_path}")


file_path = "conftest.py"  # Замените на путь к вашему файлу

function_names = get_function_names(file_path)
module = load_module_from_path(file_path)

if function_names:
    print("Исполняем функции:")
    for func_name in function_names:
        if "insert_script" in func_name:
            func = getattr(module, func_name, None)
            result = func()

            parse_and_save_inserts(result, 'fixtures')
