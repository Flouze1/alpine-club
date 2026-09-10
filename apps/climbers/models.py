from django.db import models

# Create your models here.
class climbers(models.Model):
    first_name=models.CharField(max_length=150)
    last_name=models.CharField(max_length=150)
    email=models.CharField(max_length=150)
    sports_category=models.CharField(max_length=10)
    schoole=models.BooleanField()
    test=models.BooleanField()
    created_at= models.DateTimeField()

class groups(models.Model):
    name=models.CharField(max_length=150)
    mountain_id=models.ForeignKey(
        'mountains.mountains',
        on_delete=models.PROTECT,
        related_name='led_groups'
    )
    max_members=models.PositiveSmallIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)





class climber_members(models.Model):
    climber_id = models.ForeignKey(
        'climbers',
        on_delete=models.PROTECT,
        related_name='led_climber'
    )

    groups_id=models.ForeignKey(
        'groups',
        on_delete=models.PROTECT,
        related_name='group_member'
    )

    role=models.BooleanField()
    joined_date=models.DateTimeField()
