from django.views.generic import ListView, DetailView

from flats.models import Flats


class IndexList(ListView):
    model = Flats
    template_name = 'flats/table_cls.html'
    context_object_name = 'flats'  # вместо objects_list
    paginate_by = 50

    # queryset = Flats.objects.filter(rooms=1).select_related('project').prefetch_related('prices')[:20]

    # Переопределяем запрос в базу данных
    def get_queryset(self):
        return Flats.objects.select_related('project').prefetch_related('prices') \
                   .order_by('-prices__data_created', 'prices__price')


class FlatDetailView(DetailView):
    model = Flats
    template_name = 'flats/flat_detail.html'
    context_object_name = 'flat'
    # slug_url_kwarg = 'flatslug'
    pk_url_kwarg = 'flatid'

    def get_queryset(self):
        return Flats.objects.filter(pk=self.kwargs['flatid']).select_related('project').prefetch_related('prices')
