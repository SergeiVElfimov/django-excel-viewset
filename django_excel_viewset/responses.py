import typing

from django.http import HttpResponse
from django.utils.http import urlquote

from .excel_writer import SimpleExcelFileCreator


class XLSXResponse(HttpResponse):
    """Django response, which accepts the data required to build the xlsx file.

    During initialization and returns the generated excel file.
    """

    __content_type = "application/vnd.ms-excel"
    __extension = "xlsx"
    excel_creator = SimpleExcelFileCreator

    def __init__(
        self,
        excel_header: typing.Iterable | None,
        excel_data: list[list],
        datetime_cell_format: dict[str, typing.Any],
        date_cell_format: dict[str, typing.Any],
        percent_cell_format: dict[str, typing.Any],
        format_cell_border: dict[str, typing.Any],
        format_header_table: dict[str, typing.Any],
        table_label_format: dict[str, typing.Any],
        worksheet_label: str = "report",
        table_label: str = "report",
        filename: str = "report",
        *args,
        **kwargs,
    ):
        excel_creator = self.excel_creator(
            header=excel_header,
            data=excel_data,
            worksheet_label=worksheet_label,
            table_label=table_label,
            datetime_cell_format=datetime_cell_format,
            date_cell_format=date_cell_format,
            percent_cell_format=percent_cell_format,
            format_cell_border=format_cell_border,
            format_header_table=format_header_table,
            table_label_format=table_label_format,
        )
        super().__init__(excel_creator.get_excel_for_response(), *args, **kwargs, content_type=self.__content_type)

        self["Content-Disposition"] = f"attachment; filename={urlquote(self._add_file_extension(filename))}"

    def _add_file_extension(self, filename: str) -> str:
        """Extension to the file name if it does not exist.

        :param filename: Filename.
        :return: filename with extension.
        """
        dotted_ext = "." + self.__extension
        if not filename.endswith(dotted_ext):
            filename = filename + dotted_ext
        return filename
