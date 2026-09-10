from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import mountains
from .serializers import MountainSerializer


class MountainViewSet(viewsets.ModelViewSet):
    queryset = mountains.objects.all()
    serializer_class = MountainSerializer

    def destroy(self, request, *args, **kwargs):
        mountain = self.get_object()
        from apps.climbers.models import groups

        if groups.objects.filter(mountain_id=mountain).exists():
            return Response(
                {"error": "Нельзя удалить гору"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)