import json
from pathlib import Path

from . import objects

RESPONSE_HEADERS = {f"header_{i}": "value" for i in range(10)}
RESPONSE_COOKIES = {f"cookie_{i}": "value" for i in range(10)}

data_path = Path(__file__).parent

FILE_100B = (data_path / "100B").resolve()
FILE_1K = (data_path / "1K").resolve()
FILE_10K = (data_path / "10K").resolve()
FILE_100K = (data_path / "100K").resolve()
FILE_500K = (data_path / "500K").resolve()
FILE_1M = (data_path / "1M").resolve()
FILE_5M = (data_path / "5M").resolve()

TEXT_100B = (data_path / "100B.txt").read_text()
TEXT_1K = (data_path / "1K.txt").read_text()
TEXT_10K = (data_path / "10K.txt").read_text()
TEXT_100K = (data_path / "100K.txt").read_text()
TEXT_500K = (data_path / "500K.txt").read_text()
TEXT_1M = (data_path / "1M.txt").read_text()
TEXT_5M = (data_path / "5M.txt").read_text()


JSON_SIMPLE = {f"key_{i}": "value" for i in range(10)}
JSON_1K = json.loads((data_path / "1K.json").read_text())
JSON_10K = json.loads((data_path / "10K.json").read_text())
JSON_100K = json.loads((data_path / "100K.json").read_text())
JSON_500K = json.loads((data_path / "500K.json").read_text())
JSON_1M = json.loads((data_path / "1M.json").read_text())
JSON_5M = json.loads((data_path / "5M.json").read_text())

PERSON_DATA_50 = json.loads((data_path / "persons_50.json").read_text())
PERSON_DATA_100 = json.loads((data_path / "persons_100.json").read_text())
PERSON_DATA_500 = json.loads((data_path / "persons_500.json").read_text())


PERSONS_PYDANTIC_50, PERSONS_DATACLASSES_50 = objects.load(PERSON_DATA_50)
PERSONS_PYDANTIC_100, PERSONS_DATACLASSES_100 = objects.load(PERSON_DATA_100)
PERSONS_PYDANTIC_500, PERSONS_DATACLASSES_500 = objects.load(PERSON_DATA_500)

MULTIPART_1K_HEADERS = json.loads((data_path / "MULTIPART_1K_HEADERS.json").read_text())
MULTIPART_1K = (data_path / "MULTIPART_1K").read_bytes()

FORM_URLENCODED_1K = (data_path / "FORM_URLENCODED_1K").read_bytes()
FORM_URLENCODED_1K_HEADERS = json.loads((data_path / "FORM_URLENCODED_1K_HEADERS.json").read_text())

FILE_UPLOAD_1K_HEADERS = json.loads((data_path / "FILE_UPLOAD_1K_HEADERS.json").read_text())
