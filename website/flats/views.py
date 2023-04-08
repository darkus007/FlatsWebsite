from django.shortcuts import render
from django.views.generic import ListView, DetailView

from flats.models import Flat, Price, AllFlatsLastPrice


class IndexList(ListView):
    model = Flat
    template_name = 'flats/table_cls.html'
    context_object_name = 'flats'  # вместо objects_list
    paginate_by = 50

    def get_queryset(self):
        return AllFlatsLastPrice.objects.all()


class FlatDetailView(DetailView):
    model = Flat
    template_name = 'flats/flat_detail.html'
    context_object_name = 'flats'
    # slug_url_kwarg = 'flatslug'
    pk_url_kwarg = 'flatid'

    def get_queryset(self):
        return Flat.objects.values(
            'address', 'rooms', 'area', 'floor', 'finishing', 'settlement_date', 'url_suffix',
            'project__name', 'project__url'
        ).filter(pk=self.kwargs['flatid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prices'] = Price.objects.values(
            'flat', 'data_created',
            'price', 'booking_status',
            'benefit_name', 'benefit_description'
        ).filter(flat=self.kwargs['flatid']).order_by('-data_created')
        return context


class ProjectListView(ListView):
    model = Flat
    template_name = 'flats/table_cls.html'
    context_object_name = 'flats'  # вместо objects_list
    paginate_by = 50

    def get_queryset(self):
        return AllFlatsLastPrice.objects.filter(project_id=self.kwargs['project_id'])


def page_not_found(request, exception):
    return render(request, 'flats/base.html')
