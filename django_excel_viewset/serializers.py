import typing

from rest_framework.serializers import LIST_SERIALIZER_KWARGS, Field, ListSerializer

from .responses import XLSXResponse

ListSerializerType = typing.TypeVar("ListSerializerType", bound=ListSerializer)


class ExcelSerializerMixin(typing.Generic[ListSerializerType]):
    """Mixin that allows you to transfer data to an Excel file.

    The column names are taken from the help_text parameters passed to the field constructor.
    """

    excel_response_class: type[XLSXResponse] = XLSXResponse
    data: list[dict]
    child: type[Field]

    # default settings excel file
    excel_filename: str = "report"
    excel_sheetname: str = "Sheet 1"
    excel_table_label: str | None = None
    datetime_cell_format = {"num_format": "dd.mm.yyyy h:mm;@", "border": 1, "border_color": "#000000"}
    date_cell_format = {"num_format": "dd.mm.yyyy", "border": 1, "border_color": "#000000"}
    percent_cell_format = {"num_format": '0.00"%"', "border": 1, "border_color": "#000000"}
    format_cell_border = {"border": 1, "border_color": "#000000", "text_wrap": True}
    format_header_table = {"bold": True, "align": "center", "border": 1, "border_color": "#000000", "text_wrap": True}
    table_label_format = {"italic": True, "font_size": 14}

    @classmethod
    def many_init(cls, *args, **kwargs):
        """Overload to generate a ListSerializer with the ability to export to Excel."""
        allow_empty = kwargs.pop("allow_empty", None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            "child": child_serializer,
        }
        if allow_empty is not None:
            list_kwargs["allow_empty"] = allow_empty
        list_kwargs.update({key: value for key, value in kwargs.items() if key in LIST_SERIALIZER_KWARGS})
        meta = getattr(cls, "Meta", None)
        list_serializer_class = getattr(meta, "list_serializer_class", ListSerializer)
        transfer_arguments = [
            "excel_response_class",
            "excel_filename",
            "excel_sheetname",
            "excel_table_label",
        ]
        updated_list_serializer_class = type(
            cls.__name__ + "ListSerializer",
            (ExcelSerializerMixin, list_serializer_class),
            {atr: getattr(cls, atr) for atr in transfer_arguments},
        )
        return updated_list_serializer_class(*args, **list_kwargs)

    def get_excel_filename(self):
        return self.excel_filename

    def get_excel_sheetname(self):
        return self.excel_sheetname

    def get_excel_table_label(self):
        return self.excel_table_label

    @property
    def excel_header(self) -> tuple[str | typing.Any, ...]:
        """Column names based on help_text in field instances."""
        return tuple([fi.help_text or "" for fi in self.child.fields.values()])

    @property
    def excel_rows(self) -> list[list[typing.Any]]:
        """Converting a queryset to a list of lists."""
        rows = []
        json_result = self.data
        for dct in json_result:
            rows.append(list(dct.values()))
        return rows

    @property
    def excel_response(self):
        return self.excel_response_class(
            excel_header=self.excel_header,
            excel_data=self.excel_rows,
            worksheet_label=self.get_excel_sheetname(),
            filename=self.get_excel_filename(),
            table_label=self.get_excel_table_label(),
            datetime_cell_format=self.datetime_cell_format,
            date_cell_format=self.date_cell_format,
            percent_cell_format=self.percent_cell_format,
            format_cell_border=self.format_cell_border,
            format_header_table=self.format_header_table,
            table_label_format=self.table_label_format,
        )
