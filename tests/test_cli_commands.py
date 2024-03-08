"""
CLI Command Extensions for Flask
"""
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
# pylint: disable=unused-import
from wsgi import app  # noqa: F401
from service.common.cli_commands import db_create  # noqa: E402


class TestFlaskCLI(TestCase):
    """TestFlaskCLI"""

    def setUp(self):
        self.runner = CliRunner()

    @patch('service.common.cli_commands.db')
    def test_db_create(self, db_mock):
        """test_db_create"""
        db_mock.return_value = MagicMock()
        with patch.dict(os.environ, {"FLASK_APP": "wsgi:app"}, clear=True):
            result = self.runner.invoke(db_create)
            self.assertEqual(result.exit_code, 0)
