from django.contrib import messages
from django.db.models import Q, ObjectDoesNotExist, Subquery
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView

from .models import Flat, Price, AllFlatsLastPrice
from members.models import SelectedFlat


class IndexList(ListView):
    model = Flat
    template_name = 'flats/table.html'
    context_object_name = 'flats'  # вместо objects_list
    paginate_by = 50

    def get_queryset(self):
        return AllFlatsLastPrice.objects.all()


class SelectedFlatList(ListView):
    model = Flat
    template_name = 'flats/flats_selected_user.html'
    context_object_name = 'flats'  # вместо objects_list

    def get_queryset(self):
        sq = Subquery(SelectedFlat.objects.filter(flats_user=self.kwargs['user_id']).values('flat_id'))
        return AllFlatsLastPrice.objects.filter(flat_id__in=sq)


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

        total_selected = SelectedFlat.objects.filter(flat_id=self.kwargs['flatid']).count()
        chose_this_user = SelectedFlat.objects.filter(Q(flats_user=self.request.user.id) &
                                                      Q(flat_id=self.kwargs['flatid'])
                                                      ).exists()    # True если нет False
        context["total_selected"] = total_selected
        context["chose"] = chose_this_user
        return context


class ProjectListView(ListView):
    model = Flat
    template_name = 'flats/table.html'
    context_object_name = 'flats'  # вместо objects_list
    paginate_by = 50

    def get_queryset(self):
        return AllFlatsLastPrice.objects.filter(project_id=self.kwargs['project_id'])


def page_not_found(request, exception):
    return render(request, 'flats/base.html')


def add_flat_to_selected(request, flat_id):
    """
    Добавляет квартиру в список отслеживаемых пользователем
    или убирает из него, если она уже в нем.
    """
    try:
        selected_flat = SelectedFlat.objects.get(flats_user=request.user.id, flat_id=flat_id)
        selected_flat.delete()
        messages.add_message(request, messages.SUCCESS, 'Квартира убрана из отслеживаемых.')
        return HttpResponseRedirect(reverse('flat-detail', kwargs={'flatid': flat_id}))

    except ObjectDoesNotExist:
        user_selected_flats = SelectedFlat.objects.filter(flats_user=request.user)
        if len(user_selected_flats) >= 3:
            messages.add_message(request, messages.SUCCESS, 'Достигнут предел отслеживаемых квартир.')
            return HttpResponseRedirect(reverse('flat-detail', kwargs={'flatid': flat_id}))

        flat = Flat.objects.get(flat_id=request.POST.get('flat_id'))
        data_created = Price.objects.values('data_created').get(flat=flat_id)
        SelectedFlat.objects.create(
            flats_user=request.user,
            flat_id=flat,
            data_created=data_created['data_created']
        )
        messages.add_message(request, messages.SUCCESS, 'Квартира добавлена к отслеживаемым.')
        return HttpResponseRedirect(reverse('flat-detail', kwargs={'flatid': flat_id}))
