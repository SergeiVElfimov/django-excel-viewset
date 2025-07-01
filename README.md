# Django Excel ViewSet

[![build-status-image]][build-status]
[![codeql-image]][codeql]
[![pypi-version]][pypi]
[![pypi-downloads]][pypi]

Small improvement in the functionality of [drf](https://github.com/encode/django-rest-framework) for exporting data into excel file.

## Examples

```python
# models.py
from django.db.models import Model


class Contact(Model):
    first_name = models.CharField( max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'contact'
        verbose_name_plural = 'contacts'

# serializers.py
from rest_framework.serializers import ModelSerializer
from django_excel_viewset.serializers import ExcelSerializerMixin
from .models import Contact


class ContactExcelSerializer(ExcelSerializerMixin, ModelSerializer):
    # Settings excel table
    excel_filename = "contacts"
    excel_sheetname = "contacts"
    excel_table_label = "Contacts"
    datetime_cell_format = {"num_format": "dd.mm.yyyy h:mm;@", "border": 1, "border_color": "#000000"}
    date_cell_format = {"num_format": "dd.mm.yyyy", "border": 1, "border_color": "#000000"}
    percent_cell_format = {"num_format": "0.00"%"", "border": 1, "border_color": "#000000"}
    format_cell_border = {"border": 1, "border_color": "#000000", "text_wrap": True}
    format_header_table = {"bold": True, "align": "center", "border": 1, "border_color": "#000000", "text_wrap": True}
    table_label_format = {"italic": True, "font_size": 14}

    class Meta:
        model = Contact
        fields = (
            "id",
            "last_name",
            "first_name",
            "middle_name",
            "phone",
            "email",
        )
        extra_kwargs = {
            "last_name": {"help_text": "Last name"},
            "first_name": {"help_text": "First name"},
            "middle_name": {"help_text": "Middle name"},
            "phone": {"help_text": "Phone number"},
            "email": {"help_text": "Email"},
        }
# views.py
from django_excel_viewset.views import ExcelMixin
from rest_framework.viewsets import GenericViewSet
from .serializers import ContactExcelSerializer
from .models import Contact

class ContactViewSet(ExcelMixin, GenericViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactExcelSerializer

```

## Environment variables

DJANGO_EXCEL_VIEWSET_LOCAL_TIMEZONE - setting time zone (default value "Europe/Moscow").

## Required
- python >=3.11, <4.0
- django >=4.2, <6.0
- djangorestframework >=3.11
- pillow >=9.2
- xlsxwriter >=1.3.6
- pytz >=2020.1
- environs >=9.3.1

## Installation
```pip install django-excel-viewset```

## Contributing

Before contributing please read our [contributing guidelines](CONTRIBUTING.md).

[build-status-image]: https://github.com/SergeiVElfimov/django-excel-viewset/actions/workflows/python-package.yml/badge.svg
[build-status]: https://github.com/SergeiVElfimov/django-excel-viewset/actions/workflows/python-package.yml
[pypi-version]: https://img.shields.io/pypi/v/django-excel-viewset.svg
[pypi-downloads]: https://img.shields.io/pypi/dm/django-excel-viewset?color=%232E73B2&logo=python&logoColor=%23F9D25F
[pypi]: https://pypi.org/project/django-excel-viewset/
[codeql-image]: https://github.com/SergeiVElfimov/django-excel-viewset/actions/workflows/codeql.yml/badge.svg
[codeql]: https://github.com/SergeiVElfimov/django-excel-viewset/actions/workflows/codeql.yml
