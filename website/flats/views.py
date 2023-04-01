from django.views.generic import ListView, DetailView

from flats.models import Flats, Prices, AllFlatsLastPrice


class IndexList(ListView):
    model = Flats
    template_name = 'flats/table_cls.html'
    context_object_name = 'flats'  # вместо objects_list
    paginate_by = 50

    def get_queryset(self):
        return AllFlatsLastPrice.objects.all()


class FlatDetailView(DetailView):
    model = Flats
    template_name = 'flats/flat_detail.html'
    context_object_name = 'flats'
    # slug_url_kwarg = 'flatslug'
    pk_url_kwarg = 'flatid'

    def get_queryset(self):
        return Flats.objects.values(
            'address', 'rooms', 'area', 'floor', 'finishing', 'settlement_date', 'url_suffix',
            'project__name', 'project__url'
        ).filter(pk=self.kwargs['flatid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prices'] = Prices.objects.values(
            'flat', 'data_created',
            'price', 'booking_status',
            'benefit_name', 'benefit_description'
        ).filter(flat=self.kwargs['flatid']).order_by('-data_created')
        return context


class ProjectListView(ListView):
    model = Flats
    template_name = 'flats/table_cls.html'
    context_object_name = 'flats'  # вместо objects_list
    paginate_by = 50

    def get_queryset(self):
        return AllFlatsLastPrice.objects.filter(project_id=self.kwargs['project_id'])
