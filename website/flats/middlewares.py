from .models import Projects


def projects(request):
    """ Добавляет информацию о проектах на главной странице """
    return {'projects': Projects.objects.values('name', 'project_id')}
