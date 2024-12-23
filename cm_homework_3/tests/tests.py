import unittest
import re
from main import *

class TestParseValue(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(parse_value("42"), 42)
        self.assertEqual(parse_value("-7"), -7)

    def test_float(self):
        self.assertEqual(parse_value("3.14"), 3.14)
        self.assertEqual(parse_value("-0.001"), -0.001)

    def test_array(self):
        self.assertEqual(parse_value("<<1, 2, 3>>"), [1, 2, 3])
        self.assertEqual(parse_value("<<1.1, 2.2, 3.3>>"), [1.1, 2.2, 3.3])

    def test_dict(self):
        self.assertEqual(parse_value(
"""{a = 1
    b = 2}"""), {'a': 1, 'b': 2})
        self.assertEqual(parse_value(
"""{x = 3.14
    y = 2.71}"""), {'x': 3.14, 'y': 2.71})

    def test_expression(self):
        self.assertEqual(parse_value("^[+ 1 1]"), 2) 

    def test_invalid_value(self):
        with self.assertRaises(ValueError):
            parse_value("неизвестная_константа")
        with self.assertRaises(ValueError):
            parse_value("неизвестное значение")

    def test_evaluate_expression(self):
        self.assertEqual(evaluate_expression("+ 1 2 3"), 6)
        self.assertEqual(evaluate_expression("- 5 2 1"), 2)
        self.assertEqual(evaluate_expression("* 2 3 4"), 24)
        self.assertEqual(evaluate_expression("/ 8 2 2"), 2)
        self.assertEqual(evaluate_expression("abs -5"), 5)
        with self.assertRaises(ValueError):
            evaluate_expression("/ 5 0")
        with self.assertRaises(ValueError):
            evaluate_expression("unknown 1 2")

    def test_split_array(self):
        self.assertEqual(split_array("1, 2, 3"), ["1", "2", "3"])
        self.assertEqual(split_array("1, <<2, 3>>, 4"), ["1", "<<2, 3>>", "4"])
        self.assertEqual(split_array(""), [])
    
    def test_split_dict(self):
        self.assertEqual(split_dict("key1 = value1\nkey2 = value2"), ['key1 = value1', 'key2 = value2'])
        self.assertEqual(split_dict("key1 = value1"), ["key1 = value1"])
        self.assertEqual(split_dict(""), [])
    
    def test_extract_comment(self):
        self.assertEqual(extract_comment("строка \\ комментарий"), ["строка ", " комментарий"])
        self.assertEqual(extract_comment("строка без комментария"), ("строка без комментария", None))
    
    def test_parse_custom_config(self):
        with open('test_config.txt', 'w', encoding='utf-8') as f:
            f.write("var x 10;\n")
            f.write("var y 20;\n")
            f.write("\\ комментарий\n")
            f.write("var z ^[+ x y];\n")
        
        global constants, config_data
        constants = {}
        config_data = []
        
        result = parse_custom_config('test_config.txt')
        self.assertIsNotNone(result)
        self.assertIn(('x', 10, None), result)
        self.assertIn(('y', 20, None), result)
        self.assertIn((None, None, ' комментарий'), result)
        self.assertIn(('z', 30, None), result)

    def test_format_value(self):
        self.assertEqual(format_value("test"), '"test"')
        self.assertEqual(format_value(10), '10')
        self.assertEqual(format_value(10.5), '10.5')
        self.assertEqual(format_value(["a", "b", 1]), '["a", "b", 1]')
        self.assertEqual(format_value({"key": 1, "number": 42}), '{key = 1, number = 42}')

    def test_generate_toml(self):
        config_data = [
            ("x", 10, "Значение x"),
            ("y", 20.5, None),
            (None, None, "Комментарий"),
            ("z", ["a", "b", "c"], "Список"),
        ]
        
        expected_output = (
            'x = 10  #Значение x\n'
            'y = 20.5\n'
            '#Комментарий\n'
            'z = ["a", "b", "c"]  #Список'
        )
        
        self.assertEqual(generate_toml(config_data), expected_output)

if __name__ == '__main__':
    unittest.main()