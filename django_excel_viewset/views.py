from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView


class ExcelMixin(GenericAPIView):
    """
    View export queryset to excel.

    serializer_class must be run from ExcelSerializerMixin.
    """

    @action(detail=False, pagination_class=None)
    def excel(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return serializer.excel_response
