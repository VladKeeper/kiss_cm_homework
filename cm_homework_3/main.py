import argparse
import re

config_data = []
constants = {}

def parse_value(value):
        #целые числа
        if re.match(r"^-?\d+$", value):
            return int(value)
        # числа с плавающей точкой
        elif re.match(r"^-?\d*\.\d+$", value):
            return float(value)
        #имя переменной
        elif re.match(r"[_a-z]+", value):
            reference_key = value
            if reference_key in constants:
                return constants[reference_key]
            else:
                raise ValueError(f"Неизвестная константа: {reference_key}")
        #массив
        elif value.startswith('<<') and value.endswith('>>'):
            return [parse_value(v.strip()) for v in split_array(value[2:-2])]
        #словарь
        elif value.startswith("{") and value.endswith("}"):
            return {k.strip(): parse_value(v.strip()) for item in split_dict(value[1:-1]) for k, v in [item.split('=', 1)]}
        #выражение
        elif value.startswith("^"):
            return evaluate_expression(value[1:].strip('[]'))
        else:
            raise ValueError(f"Неверное значение: {value}")

def evaluate_expression(expression):
        tokens = expression.split()
        operator = tokens[0]
        if operator == "+":
            return sum(parse_value(v) for v in tokens[1:])
        elif operator == "-":
            return parse_value(tokens[1]) - sum(parse_value(v) for v in tokens[2:])
        elif operator == "*":
            result = parse_value(tokens[1])
            for v in tokens[2:]:
                result *= parse_value(v)
            return result
        elif operator == "/":
            numerator = parse_value(tokens[1])
            for v in tokens[2:]:
                denominator = parse_value(v)
                if denominator == 0:
                    raise ValueError("Деление на ноль!")
                numerator /= denominator
            return int(numerator) if numerator.is_integer() else numerator
        elif operator == "abs":
            return abs(parse_value(tokens[1]))
        else:
            raise ValueError(f"Неизвестная операция: {operator}")
        
def split_array(array_string):
        result = []
        buffer = ""
        depth = 0
        for char in array_string:
            if char == '<':
                depth += 1
            elif char == '>':
                depth -= 1
            if char == ',' and depth == 0:
                result.append(buffer.strip())
                buffer = ""
            else:
                buffer += char
        if buffer.strip():
            result.append(buffer.strip())
        return result


def split_dict(dict_string):
    items = []
    buffer = ""
    depth = 0
    for char in dict_string:
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        if char == '\n' and depth == 0:
            if buffer.strip():
                items.append(buffer.strip())
                buffer = ""
        else:
            buffer += char
    if buffer.strip():
        items.append(buffer.strip())
    return items


def extract_comment(line):
    if '\\' in line:
        return line.split('\\', 1)
    return line, None

def parse_custom_config(input_file):
    try:
        with open(input_file, 'r', encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("\\"):
                    config_data.append((None, None, line[1:]))
                    continue
                line, comment = extract_comment(line)
                line = line.strip()
                comment = comment.strip() if comment else None

                if line.startswith("var") and "{" in line:
                    buffer = line
                    while not buffer.endswith("};"):
                        line = next(f).strip()
                        buffer += "\n" + line
                    line = buffer

                if line.startswith("var"):
                    match = re.match(r"var\s+([_a-z]+)\s+(.+);", line, flags=re.DOTALL)
                    if match:
                        key, value = match.groups()
                        try:
                            parsed_value = parse_value(value.strip())
                            constants[key] = parsed_value
                            config_data.append((key, parsed_value, comment))
                        except ValueError as e:
                            print(f"Ошибка синтаксиса в строке {line_number}: {e}")
                            return None
                    else:
                        print(f"Ошибка синтаксиса в строке {line_number}.")
                        return None
                elif line:
                    print(f"Ошибка синтаксиса в строке {line_number}.")
                    return None
    except Exception as e:
        print(f"Ошибка при чтении файла '{input_file}': {e}")
        return None
    
    return config_data

def format_value(value):
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, list):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    elif isinstance(value, dict):
        return "{" + ", ".join(f"{k} = {format_value(v)}" for k, v in value.items()) + "}"
    else:
        return str(value)


def generate_toml(config_data):
    lines = []
    for key, value, comment in config_data:
        if key and value:
            line = f"{key} = {format_value(value)}"
            if comment:
                line += f"  #{comment}"
        elif comment:
            line = f"#{comment}"
        lines.append(line)

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Преобразование учебного конфигурационного языка в TOML.")
    parser.add_argument("input_file", help="Путь к входному файлу")
    parser.add_argument("output_file", help="Путь к выходному файлу")
    args = parser.parse_args()

    config_data = parse_custom_config(args.input_file)

    if config_data is None:
        print('Преобразование не удалось')
        return

    toml_output = generate_toml(config_data)

    with open(args.output_file, 'w', encoding="utf-8") as f:
        f.write(toml_output)
        
    print("Преобразование завершено успешно!")

if __name__ == "__main__":
    main()