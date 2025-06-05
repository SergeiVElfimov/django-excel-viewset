import io
import typing
import warnings
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO

from PIL import Image
from xlsxwriter import Workbook

from django_excel_viewset.settings import LOCAL_TIMEZONE


class HeaderAndDataNotTheSameLengthWarning(Warning):
    pass


class XLSXCreator:
    """
    A basic class for creating Excel files with tables and/or explicit cells.

    All columns start from 0.
    Example:
        wb = xlsxwriter.Workbook(f"example.xlsx")
        ws = wb.add_worksheet("single")
        xlsx_creator = XLSXCreator(workbook=wb, worksheet=ws)
        xlsx_creator.add_table(heading=header, data=list_of_lists, table_label="1")
        xlsx_creator.add_cell(text="test text",
                            cell_format={"bold": True, "text_wrap": True, "font_size": 15}, row_padding=2
                            )
        xlsx_creator.add_row(row=["test", 3], row_padding=1)
    """

    def __init__(
        self,
        workbook,
        worksheet,
        datetime_cell_format,
        date_cell_format,
        percent_cell_format,
        format_cell_border,
        format_header_table,
        table_label_format,
    ):
        self.workbook = workbook
        self.worksheet = worksheet
        self.last_row_num = 0
        self.blocks = []
        self._datetime_cell_format = datetime_cell_format
        self._date_cell_format = date_cell_format
        self._percent_cell_format = percent_cell_format
        self._format_border = format_cell_border
        self._format_header_table = format_header_table
        self._table_label_format = table_label_format

    @property
    def ws_last_row_num(self) -> int:
        """
        Getting the position of the line we are on.

        :return: number of position.
        """
        return self.last_row_num

    def update_last_row(self, row_step: int) -> None:
        """
        Update last row.

        :param row_step: step size.
        :return: number of position.
        """
        self.last_row_num += row_step

    def add_table(self, heading: typing.Iterable | None, data: list[list], table_label: str = "") -> None:
        """
        Add table.

        :param heading:
        :param data:
        :param table_label:
        :return:
        """
        self.blocks.append(
            XLSXTable(
                heading,
                data,
                table_label,
                workbook=self.workbook,
                worksheet=self.worksheet,
                datetime_cell_format=self._datetime_cell_format,
                date_cell_format=self._date_cell_format,
                percent_cell_format=self._percent_cell_format,
                format_cell_border=self._format_border,
                format_header_table=self._format_header_table,
                table_label_format=self._table_label_format,
            )
        )

    def add_cell(self, text: str, row_padding: int, cell_format: dict) -> None:
        """
        Add cell.

        :param text: Content cell.
        :param row_padding: Indent from a cell.
        :param cell_format: Format cell.
        """
        self.blocks.append(
            XLSXCell(
                text=text,
                row_padding=row_padding,
                cell_format=cell_format,
                worksheet=self.worksheet,
                workbook=self.workbook,
                datetime_cell_format=self._datetime_cell_format,
                date_cell_format=self._date_cell_format,
                percent_cell_format=self._percent_cell_format,
                format_cell_border=self._format_border,
                format_header_table=self._format_header_table,
                table_label_format=self._table_label_format,
            )
        )

    def add_row(self, row: list, row_padding: int) -> None:
        """
        Add row.

        :param row: List.
        :param row_padding: Indent from a row.
        :return:
        """
        self.blocks.append(
            XLSXRow(
                row=row,
                row_padding=row_padding,
                worksheet=self.worksheet,
                workbook=self.workbook,
                datetime_cell_format=self._datetime_cell_format,
                date_cell_format=self._date_cell_format,
                percent_cell_format=self._percent_cell_format,
                format_cell_border=self._format_border,
                format_header_table=self._format_header_table,
                table_label_format=self._table_label_format,
            )
        )

    def _format_cell_datetime(self):
        return self.workbook.add_format(self._datetime_cell_format)

    def _format_cell_date(self):
        return self.workbook.add_format(self._date_cell_format)

    def _format_cell_percent(self):
        return self.workbook.add_format(self._percent_cell_format)

    def _format_cell_border(self):
        return self.workbook.add_format(self._format_border)

    def write_row(self, row_num, row) -> None:
        """Write new row.

        :param row_num: Number row.
        :param row: Excel row.
        """
        for col_num, elem in enumerate(row):
            if isinstance(elem, datetime):
                if str(elem.tzinfo) == "UTC":
                    elem = elem.astimezone(tz=LOCAL_TIMEZONE)
                    elem = elem.replace(tzinfo=None)
                self.worksheet.write_datetime(row_num, col_num, elem, cell_format=self._format_cell_datetime())
            elif isinstance(elem, date):
                self.worksheet.write_datetime(row_num, col_num, elem, cell_format=self._format_cell_date())
            elif isinstance(elem, Decimal | int):
                self.worksheet.write_number(row_num, col_num, elem, cell_format=self._format_cell_border())
            elif isinstance(elem, str):
                self.worksheet.write(row_num, col_num, elem, self._format_cell_border())
            elif isinstance(elem, Image.Image):
                im_bytes = io.BytesIO()
                elem.save(im_bytes, format="JPEG")
                self.worksheet.insert_image(row_num, col_num, elem.info["filename"], {"image_data": im_bytes})
            else:
                if elem is None:
                    elem = ""
                self.worksheet.write(row_num, col_num, str(elem), self._format_cell_border())

    def make_excel(self, close_workbook: bool = True) -> None:
        """Create excel by blocks."""
        for block in self.blocks:
            if isinstance(block, XLSXCell):
                block.write_cell()
            elif isinstance(block, XLSXRow):
                block.row_write()
            elif isinstance(block, XLSXTable):
                block.write_table_label()
                block.write_heading()
                block.write_data()
                block.resize_cols()
                block.resize_rows_for_image()
        self.last_row_num = 0
        if close_workbook:
            self.workbook.close()


class XLSXRow(XLSXCreator):
    """Class for adding a row."""

    def __init__(
        self,
        workbook,
        worksheet,
        row: list,
        row_padding,
        datetime_cell_format,
        date_cell_format,
        percent_cell_format,
        format_cell_border,
        format_header_table,
        table_label_format,
    ):
        super().__init__(
            workbook,
            worksheet,
            datetime_cell_format,
            date_cell_format,
            percent_cell_format,
            format_cell_border,
            format_header_table,
            table_label_format,
        )
        self.row = row
        self.row_padding = row_padding

    def row_write(self):
        """Write row."""
        self.write_row(self.ws_last_row_num, self.row)
        self.update_last_row(1)
        self.update_last_row(self.row_padding)


class XLSXCell(XLSXCreator):
    """Class to add 1 cell per row in table."""

    def __init__(
        self,
        workbook,
        worksheet,
        text,
        row_padding,
        cell_format: dict,
        datetime_cell_format,
        date_cell_format,
        percent_cell_format,
        format_cell_border,
        format_header_table,
        table_label_format,
    ):
        super().__init__(
            workbook,
            worksheet,
            datetime_cell_format,
            date_cell_format,
            percent_cell_format,
            format_cell_border,
            format_header_table,
            table_label_format,
        )
        self.text = text
        self.cell_format = cell_format
        self.row_padding = row_padding

    def _format_cell(self):
        return self.workbook.add_format(self.cell_format)

    def write_cell(self):
        """Write cell and increase position last_row_num."""
        self.worksheet.write(self.ws_last_row_num, 0, self.text, self._format_cell())
        self.update_last_row(self.row_padding)


class XLSXTable(XLSXCreator):
    """Class for adding a table to excel."""

    column_width_limit = 60

    def __init__(
        self,
        heading,
        data,
        table_label,
        workbook,
        worksheet,
        datetime_cell_format,
        date_cell_format,
        percent_cell_format,
        format_cell_border,
        format_header_table,
        table_label_format,
    ):
        super().__init__(
            workbook,
            worksheet,
            datetime_cell_format,
            date_cell_format,
            percent_cell_format,
            format_cell_border,
            format_header_table,
            table_label_format,
        )
        self.workbook = workbook
        self.table_label = table_label
        self.heading = heading
        self.data = data
        for row in self.data:
            if len(self.heading) != len(row):
                warnings.warn(
                    f"The number of elements in the header is not equal to the number in the row {row}",
                    HeaderAndDataNotTheSameLengthWarning,
                    stacklevel=2,
                )

    def _format_header_bold_center(self):
        return self.workbook.add_format(self._format_header_table)

    def _format_table_label(self):
        return self.workbook.add_format(self._table_label_format)

    def write_table_label(self):
        if self.table_label:
            self.worksheet.merge_range(
                self.ws_last_row_num,
                0,
                self.ws_last_row_num,
                len(self.heading) - 1,
                self.table_label,
                self._format_table_label(),
            )
            self.update_last_row(2)

    def write_heading(self):
        for col_num, header_name in enumerate(self.heading):
            self.worksheet.write(self.ws_last_row_num, col_num, header_name, self._format_header_bold_center())
        self.update_last_row(1)

    def write_data(self):
        for row_num, row in enumerate(self.data, start=self.ws_last_row_num):
            self.write_row(row_num, row)
            self.update_last_row(1)
        self.update_last_row(1)

    def __count_elem_len(self, elem):
        if isinstance(elem, Image.Image):
            width, _ = elem.size
            return int(width / 7)
        return len(str(elem))

    def resize_cols(self):
        """Resize columns."""
        try:
            first_row = self.data[0]
        except IndexError:
            return

        rows_length = [len(row) for row in self.data]
        rows_length.append(len(first_row))
        max_index = max(rows_length)
        cols_list: list[list] = []
        for _ in range(max_index):
            cols_list.append([])

        for row in self.data:
            for i, elem in enumerate(row):
                cols_list[i].append(elem)

        for i, combined_list in enumerate(cols_list):
            combined_list.append(self.heading[i])
            max_length_elem = max(combined_list, key=self.__count_elem_len)
            col_max_length = len(str(max_length_elem))
            # ресайз колонок с учетом картинок
            len_indent = 2
            if isinstance(max_length_elem, Image.Image):
                width, _ = max_length_elem.size
                col_max_length = int(width / 7)
                len_indent = 0
            if col_max_length > self.column_width_limit:
                col_max_length = self.column_width_limit
            self.worksheet.set_column(i, i, col_max_length + len_indent)

    def resize_rows_for_image(self):
        """Resize rows when there are images."""
        for i, row in enumerate(self.data):
            list_height = []
            for elem in row:
                if isinstance(elem, Image.Image):
                    _, height = elem.size
                    list_height.append(height)
                if list_height:
                    self.worksheet.set_row(i + 1, int(max(list_height) * 0.75))


class SimpleExcelFileCreator:
    """Takes a title (iterable, but optional) and data as a list of lists.

    The get_excel_for_response() method returns an excel that can be sent to Response.
    """

    def __init__(
        self,
        header: typing.Iterable | None,
        data: list[list],
        datetime_cell_format: dict[str, typing.Any],
        date_cell_format: dict[str, typing.Any],
        percent_cell_format: dict[str, typing.Any],
        format_cell_border: dict[str, typing.Any],
        format_header_table: dict[str, typing.Any],
        table_label_format: dict[str, typing.Any],
        worksheet_label: str = "Report",
        table_label: str = "",
    ):
        self.file = BytesIO()
        self._workbook = Workbook(self.file, {"in_memory": True})
        self._worksheet = self._workbook.add_worksheet(name=worksheet_label)
        xlsx_create = XLSXCreator(
            workbook=self._workbook,
            worksheet=self._worksheet,
            datetime_cell_format=datetime_cell_format,
            date_cell_format=date_cell_format,
            percent_cell_format=percent_cell_format,
            format_cell_border=format_cell_border,
            format_header_table=format_header_table,
            table_label_format=table_label_format,
        )
        xlsx_create.add_table(heading=header, data=data.copy(), table_label=table_label)
        self._xlsx_creator = xlsx_create

    def get_excel_for_response(self):
        self._xlsx_creator.make_excel()
        return self.file.getvalue()
