import unittest
import os
import tarfile
import xml.etree.ElementTree as ET
from emulator import Emulator, load_config
import coverage

# Инициализируем coverage
cov = coverage.Coverage()
cov.start()

class TestEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем временный tar файл с тестовыми данными
        cls.vfs_path = "test_vfs.tar"
        with tarfile.open(cls.vfs_path, 'w') as tar:
            # Создаем тестовые файлы
            with open("test_file.txt", "w") as f:
                f.write("This is a test file.")
            tar.add("test_file.txt")
            os.remove("test_file.txt")

        # Загружаем конфигурацию для тестирования
        cls.config = {
            'username': 'test_user',
            'hostname': 'test_host',
            'vfs_path': cls.vfs_path,
            'log_path': 'test_log.xml'
        }
        cls.emulator = Emulator(cls.config)

    @classmethod
    def tearDownClass(cls):
        # Удаляем временные файлы после тестов
        if os.path.exists(cls.vfs_path):
            os.remove(cls.vfs_path)
        if os.path.exists(cls.config['log_path']):
            os.remove(cls.config['log_path'])

    def test_whoami(self):
        # Проверяем, что команда whoami возвращает правильное имя пользователя
        self.assertEqual(self.emulator.username, 'test_user')

    def test_ls(self):
        # Проверяем, что команда ls отображает файлы в текущем каталоге
        try:
            self.emulator.list_directory()
        except Exception as e:
            self.fail(f"Команда ls вызвала ошибку: {e}")

    def test_cd(self):
        # Проверяем, что команда cd не вызывает ошибок
        try:
            self.emulator.change_directory("test_directory")
        except Exception as e:
            self.fail(f"Команда cd вызвала ошибку: {e}")

    def test_rm(self):
        # Проверяем, что команда rm удаляет файл
        try:
            self.emulator.remove_file("test_file.txt")
            self.assertFalse(os.path.exists("test_file.txt"))
        except Exception as e:
            self.fail(f"Команда rm вызвала ошибку: {e}")

    def test_exit(self):
        # Проверяем, что команда exit завершает работу эмулятора
        self.emulator.exit_emulator()
        self.assertFalse(self.emulator.is_running)

    def test_load_config(self):
        # Проверяем, что функция load_config работает корректно
        config = load_config('config.toml')
        self.assertIsNotNone(config)
        self.assertIn('username', config)
        self.assertIn('hostname', config)
        self.assertIn('vfs_path', config)
        self.assertIn('log_path', config)

    def test_log_action(self):
        # Проверяем, что метод log_action записывает действие в лог-файл
        self.emulator.log_action("test_action")
        self.assertTrue(os.path.exists(self.config['log_path']))
        tree = ET.parse(self.config['log_path'])
        root = tree.getroot()
        self.assertEqual(root.find("action").text, "test_action")

if __name__ == "__main__":
    try:
        unittest.main(verbosity=2)
    finally:
        cov.stop()
        cov.save()
        print("Coverage report:")
        cov.report()
