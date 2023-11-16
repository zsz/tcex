import csv
import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Any


class DataWriter(ABC):
    """
    Abstract interface for writing data.
    """

    @abstractmethod
    def write(self, data: list[list[..., Any]]):
        """
        Abstract method that writes the given data.
        :param data: the data to write consts of lists of anything
        :return: None
        """
        ...


class CSVFileDataWriter(DataWriter):
    """
    CSV data write implementation
    """

    T = TypeVar("T", str, int)

    def __init__(self, filename: str, write_headers: bool = False):
        """
        Constructs the writer with the given file name.
        :param filename: the name of the file to write
        :param write_headers: flag indicating whether the first list should be considered
        as headers and so written that way
        """
        self.filename = filename
        self.write_headers = write_headers

    def write(self, data: list[list[..., T]]):
        try:
            with open(self.filename, "w", newline='') as f:
                if self.write_headers:
                    dict_writer = csv.DictWriter(f, data.pop(0))
                    dict_writer.writeheader()
                    csv_writer = dict_writer.writer
                else:
                    csv_writer = csv.writer(f)
                csv_writer.writerows(data)
        except csv.Error as csv_error:
            logging.error("Unable to perform CSV exporting: %s", csv_error.__str__())
            raise csv_error
