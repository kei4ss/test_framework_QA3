import json
import pytest
from unittest.mock import mock_open, patch

from src.utils.file_reader import FileReader


def test_read_json_success_with_dict():
    fake_data = {"name": "Vitor", "age": 25}

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(fake_data))):
        result = FileReader.read_json("data.json")

    assert result == fake_data


def test_read_json_success_with_list():
    fake_data = [{"name": "Vitor"}, {"name": "João"}]

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=json.dumps(fake_data))):
        result = FileReader.read_json("data.json")

    assert result == fake_data


def test_read_json_file_not_found():
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError) as error:
            FileReader.read_json("missing.json")

    assert "Arquivo JSON não encontrado" in str(error.value)


def test_read_json_invalid_json():
    invalid_json = "{invalid_json"

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=invalid_json)):
        with pytest.raises(json.JSONDecodeError) as error:
            FileReader.read_json("invalid.json")

    assert "Erro ao decodificar JSON" in str(error.value)


def test_read_csv_success():
    csv_content = (
        "name,age,active,height\n"
        "Vitor,25,true,1.75\n"
        "Ana,30,false,1.65\n"
    )

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=csv_content)):
        result = FileReader.read_csv("users.csv")

    assert result == [
        {
            "name": "Vitor",
            "age": 25,
            "active": True,
            "height": 1.75,
        },
        {
            "name": "Ana",
            "age": 30,
            "active": False,
            "height": 1.65,
        },
    ]


def test_read_csv_file_not_found():
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError) as error:
            FileReader.read_csv("missing.csv")

    assert "Arquivo CSV não encontrado" in str(error.value)


def test_read_csv_empty_values_are_converted_to_none():
    csv_content = "name,age\nVitor,\n"

    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=csv_content)):
        result = FileReader.read_csv("users.csv")

    assert result == [{"name": "Vitor", "age": None}]


@pytest.mark.parametrize(
    "value, expected",
    [
        ("true", True),
        ("false", False),
        ("TRUE", True),
        ("FALSE", False),
        ("10", 10),
        ("10.5", 10.5),
        ("", None),
        (None, None),
        ("Vitor", "Vitor"),
    ],
)
def test_convert_value(value, expected):
    assert FileReader._convert_value(value) == expected


def test_list_files_in_directory_without_extension():
    fake_files = ["data.json", "users.csv", "readme.md"]

    def fake_isfile(path):
        return True

    with patch("os.path.exists", return_value=True), \
         patch("os.listdir", return_value=fake_files), \
         patch("os.path.isfile", side_effect=fake_isfile):
        result = FileReader.list_files_in_directory("data")

    assert result == fake_files


def test_list_files_in_directory_with_extension():
    fake_files = ["data.json", "users.csv", "config.json"]

    with patch("os.path.exists", return_value=True), \
         patch("os.listdir", return_value=fake_files), \
         patch("os.path.isfile", return_value=True):
        result = FileReader.list_files_in_directory("data", ".json")

    assert result == ["data.json", "config.json"]


def test_list_files_in_directory_ignores_directories():
    fake_files = ["data.json", "folder", "users.csv"]

    def fake_isfile(path):
        return not path.endswith("folder")

    with patch("os.path.exists", return_value=True), \
         patch("os.listdir", return_value=fake_files), \
         patch("os.path.isfile", side_effect=fake_isfile):
        result = FileReader.list_files_in_directory("data")

    assert result == ["data.json", "users.csv"]


def test_list_files_in_directory_not_found():
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError) as error:
            FileReader.list_files_in_directory("missing_dir")

    assert "Diretório não encontrado" in str(error.value)