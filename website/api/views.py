from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import BadSignature
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Subquery

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from flats.models import Project, Flat, Price, AllFlatsLastPrice
from members.models import SelectedFlat
from members.utilities import signer, send_activation_notification
from .serializers import (
    ProjectSerializer, AllFlatsLastPriceSerializer,
    UserReadSerializer, UserUpdateSerializer, UserCreateSerializer
)


# ================ Квартиры, ЖК ================

class ProjectList(generics.ListAPIView):
    """ Возвращает информацию по всем доступным ЖК. """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class AllFlatsLastPriceList(generics.ListAPIView):
    """
    Возвращает информацию по всем квартирам.
    С фильтром "project-id" только по квартирам указанного ЖК.
    """
    serializer_class = AllFlatsLastPriceSerializer
    pagination_class = LimitOffsetPagination
    pagination_class.max_limit = settings.REST_FRAMEWORK_PAGINATION_MAX_SIZE

    def get_queryset(self):
        project_id = self.request.query_params.get('project-id')
        if project_id:
            return AllFlatsLastPrice.objects.filter(project_id=project_id)
        return AllFlatsLastPrice.objects.all()


# ================ Пользователи ================

class UserAPIView(APIView):
    """
    Класс для работы с пользователем.
    Авторизованный пользователь может получить информацию о себе и изменить ее.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = get_user_model().objects.get(id=request.user.id)
        serializer = UserReadSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = get_user_model().objects.get(id=request.user.id)
        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['put'])
@permission_classes((permissions.AllowAny,))
def create_user(request):
    """
    Создает нового пользователя.
    """
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['get'])
@permission_classes((permissions.IsAuthenticated,))
def send_email_for_activate_user(request):
    """
    Отправляет email для подтверждения email пользователя
    и активации пользователя.
    """
    send_activation_notification(request.user)
    return Response({'info': f'Email was sent to {request.user.email}.'}, status=status.HTTP_200_OK)


@api_view(http_method_names=['get'])
@permission_classes((permissions.AllowAny,))
def user_email_activate(request, sign):
    """
    Функция для подтверждения email пользователя.
    Принимает сообщение о подтверждении адреса электронной почты
    и если все верно и подпись не скомпрометирована, активирует email пользователя.
    """
    try:
        username = signer.unsign(sign)
        user = get_user_model().objects.get(username=username)
    except BadSignature:
        return Response({'error': 'Signature does not match.'}, status=status.HTTP_400_BAD_REQUEST)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return Response({'error': 'User is not found.'}, status=status.HTTP_400_BAD_REQUEST)

    if user.is_email_activated:
        return Response({'info': 'Email has already been activated.'}, status=status.HTTP_200_OK)
    else:
        user.is_email_activated = True
        user.save()
    return Response({'info': 'Email is activated successfully.'}, status=status.HTTP_200_OK)


# ================ Квартиры пользователя для отслеживания ================

class UserSelectedFlatsAPIView(APIView):
    """
    Класс для работы со списком отслеживаемых пользователем квартир.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Возвращает информацию по всем отслеживаемым пользователем квартирам.
        """
        subquery = Subquery(SelectedFlat.objects.filter(flats_user=request.user.id).values('flat_id'))
        user_flats = AllFlatsLastPrice.objects.filter(flat_id__in=subquery)
        serializer = AllFlatsLastPriceSerializer(instance=user_flats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Добавляем квартиру к отслеживаемым пользователем.
        """
        # Проверяем количество уже отслеживаемых квартир
        user_selected_flats = SelectedFlat.objects.filter(flats_user=request.user).values('flat_id')
        if len(user_selected_flats) >= 3:
            return Response({'info': 'Reached the limit of tracked flats (3 pieces).'},
                            status=status.HTTP_403_FORBIDDEN)

        # добавляем квартиру, если она найдена и не присутствует в отслеживаемых
        # для текущего пользователя
        try:
            flat = Flat.objects.get(flat_id=request.data.get('flat_id'))
            if flat.flat_id not in [selected_flat['flat_id'] for selected_flat in user_selected_flats]:
                data_created = Price.objects.values('data_created').filter(flat=request.POST.get('flat_id')).first()
                SelectedFlat.objects.create(
                    flats_user=request.user,
                    flat_id=flat,
                    data_created=data_created['data_created']
                )
                return Response({'info': 'The flat is added to the trackable.'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'info': 'The flat has already been added to the tracked.'},
                                status=status.HTTP_200_OK)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return Response({'info': 'The flat was not found.'},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Удаляет квартиру из отслеживаемых пользователем.
        """
        selected_flat = SelectedFlat.objects.filter(
            flats_user=request.user.id, flat_id=request.data.get('flat_id')
        ).first()
        if selected_flat:
            selected_flat.delete()
            return Response({'info': 'The flat is removed from tracked.'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'info': 'The flat was not found.'},
                            status=status.HTTP_400_BAD_REQUEST)
