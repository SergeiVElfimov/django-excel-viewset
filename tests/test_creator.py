from io import BytesIO

from xlsxwriter import Workbook

from django_excel_viewset.excel_writer import XLSXCreator
from django_excel_viewset.excel_writer.creator import XLSXTable


class TestXLSXCreator:
    """Test the XLSXCreator."""

    @classmethod
    def setup_class(cls):
        cls.file = BytesIO()
        cls._workbook = Workbook(cls.file, {"in_memory": True})
        cls._worksheet = cls._workbook.add_worksheet(name="test")
        cls._xlsx_creator = XLSXCreator(
            workbook=cls._workbook,
            worksheet=cls._worksheet,
            datetime_cell_format={},
            date_cell_format={},
            percent_cell_format={},
            format_cell_border={},
            format_header_table={},
            table_label_format={},
        )
        cls._headers = ("Head 1", "Head 2")
        cls._data = [[1, 2], [3, 4]]

    def test_add_table(self):
        """Test the add_table method."""
        self._xlsx_creator.add_table(heading=self._headers, data=self._data, table_label="Test table")
        assert len(self._xlsx_creator.blocks) == 1
        assert isinstance(self._xlsx_creator.blocks[0], XLSXTable)
