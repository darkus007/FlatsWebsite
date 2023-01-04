from django.views.generic import ListView

from flats.models import Flats


class IndexList(ListView):
    model = Flats
    template_name = 'flats/table_cls.html'
    context_object_name = 'flats'  # вместо objects_list
    # paginate_by = 50
    # queryset = Flats.objects.filter(rooms=1).select_related('project').prefetch_related('prices')[:20]

    queryset = Flats.objects.values('pk', 'project__name', 'project__url',
                                    'rooms', 'prices__price',
                                    'area', 'floor', 'settlement_date',
                                    'url_suffix', 'address')[:20]

    # Переопределяем запрос в базу данных
    # def get_queryset(self):
    # q = Product_r.objects.all().annotate(uuid=F('fk_product__uuid')).values('uuid')
    # .annotate(total=Count('id')).order_by('total')

    # res = Flats.objects.filter(rooms=1).select_related('project')[:20]
    # res = Flats.objects.filter(rooms=1).select_related('project').prefetch_related('prices__price')[:10]

    # res = Flats.objects.values('pk', 'project__name', 'project__url',
    #                            'rooms', 'prices__price', 'prices__flat_id',
    #                            'area', 'floor', 'settlement_date',
    #                            'url_suffix', 'address').annotate()
    # res = Flats.objects.annotate(uuid=F('prices__data_created')) \
    #           .values('uuid', 'pk', 'project__name', 'project__url',
    #                   'rooms', 'prices__price', 'prices__flat_id',
    #                   'area', 'floor', 'settlement_date', 'url_suffix', 'address') \
    #           .annotate(total=Count('prices__flat_id'))[:20]

    # return res