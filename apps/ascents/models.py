from django.db import models

# Create your models here.
class climbs(models.Model):
    group_id=models.ForeignKey(
            'climbers.groups',
            on_delete=models.PROTECT,
            related_name='group_ascents'
        )
    start_event=models.DateTimeField()
    end_event=models.DateTimeField()


    RESULT_CHOICES = [
        ('not_started', 'Не начат'),
        ('success', 'Успешно'),
        ('failed', 'Неудача'),
    ]
    result = models.CharField(max_length=15, choices=RESULT_CHOICES, default='not_started')

    
    comment=models.CharField(max_length=200)
    note=models.FloatField(null=True, blank=True)
    