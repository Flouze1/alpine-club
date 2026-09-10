from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Avg
from .models import climbs
from .serializers import AscentSerializer


class AscentViewSet(viewsets.ModelViewSet):
    queryset = climbs.objects.all()
    serializer_class = AscentSerializer

    @action(detail=False, methods=['get'], url_path='report/by-group')
    def report_by_group(self, request):
        data = climbs.objects.values('group_id__name').annotate(
            ascent_count=Count('id'),
            avg_rating=Avg('note')
        ).order_by('-ascent_count')
        return Response(data)

    @action(detail=False, methods=['get'], url_path='report/success-rate')
    def report_success_rate(self, request):
        total = climbs.objects.count()
        if total == 0:
            return Response({'success_rate': 0, 'total': 0})

        success = climbs.objects.filter(result='success').count()
        return Response({
            'success_rate': round(success / total * 100, 2),
            'total': total,
            'success': success,
            'failed': total - success
        })