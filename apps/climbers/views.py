from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import climbers, groups, climber_members
from .serializers import ClimberSerializer, GroupSerializer, GroupMemberSerializer


class ClimberViewSet(viewsets.ModelViewSet):
    queryset = climbers.objects.all()
    serializer_class = ClimberSerializer

    def destroy(self, request, *args, **kwargs):
        climber = self.get_object()
        if groups.objects.filter(leader_id=climber).exists():
            return Response(
                {'error': 'Нельзя удалить альпиниста, который является руководителем группы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = groups.objects.all()
    serializer_class = GroupSerializer

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        from apps.climbers.models import groups
        if groups.objects.filter(group_id=group).exists():
            return Response(
                {'error': 'Нельзя удалить группу'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class GroupMemberViewSet(viewsets.ModelViewSet):
    queryset = climber_members.objects.all()
    serializer_class = GroupMemberSerializer


    def perform_create(self, serializer):
        climber = serializer.validated_data.get('climber_id')
        role = serializer.validated_data.get('role')

        if not(role and climber.schoole and climber.test):
            raise ValidationError(
                'Только альпинист, прошедший школу и тест, может быть руководителем'
            )
        serializer.save()