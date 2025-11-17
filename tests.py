import unittest
import os
from app import create_app, db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"

class CLITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_translate_compile(self):
        result = self.runner.invoke(args=["translate", "compile"])
        self.assertEqual(result.exit_code, 0)
