from abc import ABC, abstractmethod
from json import dumps as json_dumps
from json import loads as json_loads
from pathlib import Path
import sys

import eqa.lib.settings as eqa_settings


def handleException(e: Exception, e_desc: str, e_print=True, e_log=False):
    last_exec_info = sys.exc_info()[-1]

    if last_exec_info is None:
        line_no = "???"
    else:
        line_no = str(last_exec_info.tb_lineno)

    error_string = f"{e_desc}: Error on line: {line_no}: {str(e)}"

    if e_print:
        print(error_string)
    if e_log:
        eqa_settings.log(error_string)


class SerializedFileHandler(ABC):
    def __init__(self, filename: str | Path) -> None:
        self.filename = filename

    @abstractmethod
    def serialize(self, data):
        pass

    @abstractmethod
    def deserialize(self, data):
        pass

    def write(self, data):
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write(self.serialize(data) or "")

    def read(self) -> dict:
        with open(self.filename, "r", encoding="utf-8") as file:
            return self.deserialize(file.read()) or {}


class JSONFileHandler(SerializedFileHandler):
    def serialize(self, data):
        return json_dumps(data).encode("utf-8")

    def deserialize(self, data):
        return json_loads(data)
