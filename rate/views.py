import csv  # noqa
import xlsxwriter  # noqa

from django.http import HttpResponse  # noqa
from django.views.generic import ListView, View, TemplateView  # noqa

from rate.models import Rate  # noqa
from rate.selectors import get_latest_rates
from rate.utils import display  # noqa
from rate import model_choices as mch  # noqa


class RateList(ListView):
    queryset = Rate.objects.all()
    template_name = 'rate-list.html'


class LatestRatesView(TemplateView):
    template_name = 'latest-rates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = get_latest_rates()
        return context


class RateDownloadCSV(View):
    HEADERS = [
        'id',
        'created',
        'source',
        'amount',
        'type',
    ]
    queryset = Rate.objects.all().iterator()

    def get(self, request):

        response = self.get_response()

        writer = csv.writer(response)
        writer.writerow(self.__class__.HEADERS)

        for rate in self.queryset:
            values = []
            for attr in self.__class__.HEADERS:
                values.append(display(rate, attr))

            writer.writerow(values)

        return response

    def get_response(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        return response


class RateDownloadXLSX(View):
    HEADERS = (
        'id',
        'created',
        'source',
        'amount',
        'type',
    )

    queryset = Rate.objects.all()

    def get(self, request):
        response = self.get_response

        book = xlsxwriter.Workbook(response, {'in_memory': True})
        sheet = book.add_worksheet()

        for i, column in enumerate(self.__class__.HEADERS):
            sheet.write(0, i, column)

        for i, rate in enumerate(self.queryset, start=1):
            values = []
            for attr in self.__class__.HEADERS:
                values.append(display(rate, attr))

        book.close()

        return response

    @property
    def get_response(self):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = "attachment; filename=rates.xlsx"
        return response
