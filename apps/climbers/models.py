from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class climbers(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='climber'
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    sports_category = models.CharField(max_length=10, default='новичок')
    schoole = models.BooleanField(default=False)
    test = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_attestation_date = models.DateField(null=True, blank=True, verbose_name="Последняя аттестация")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class groups(models.Model):
    name = models.CharField(max_length=150)
    mountain_id = models.ForeignKey(
        'mountains.mountains',
        on_delete=models.PROTECT,
        related_name='groups'
    )
    max_members = models.PositiveSmallIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class climber_members(models.Model):
    climber_id = models.ForeignKey(
        climbers,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    groups_id = models.ForeignKey(
        groups,
        on_delete=models.CASCADE,
        related_name='members'
    )
    role = models.BooleanField(default=False)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['climber_id', 'groups_id']

    def __str__(self):
        return f"{self.climber_id} в {self.groups_id}"

class Attestation(models.Model):
    """Заявка на аттестацию с результатами"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('passed', 'Пройдена'),
        ('failed', 'Не пройдена'),
    ]

    climber = models.ForeignKey(
        climbers,
        on_delete=models.CASCADE,
        related_name='attestations'
    )
    target_rank = models.CharField(max_length=10, verbose_name="Целевой разряд")
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата сдачи")

    pullups = models.IntegerField(null=True, blank=True)
    rope_climbing = models.IntegerField(null=True, blank=True)
    pushups = models.IntegerField(null=True, blank=True)
    squats = models.IntegerField(null=True, blank=True)
    back_bends = models.IntegerField(null=True, blank=True)
    cross_10km = models.IntegerField(null=True, blank=True, verbose_name="Кросс 10 км (сек)")
    shuttle_run = models.IntegerField(null=True, blank=True, verbose_name="Челночный бег (сек)")
    hang = models.IntegerField(null=True, blank=True, verbose_name="Вис (сек)")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    awarded_rank = models.CharField(max_length=10, null=True, blank=True, verbose_name="Присвоенный разряд")

    class Meta:
        verbose_name = "Аттестация"
        verbose_name_plural = "Аттестации"
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.climber} → {self.target_rank}"

# ===== Автоматическое создание Climber при создании User =====
@receiver(post_save, sender=User)
def create_climber_for_user(sender, instance, created, **kwargs):
    if created:
        climbers.objects.create(
            user=instance,
            first_name=instance.first_name or instance.username,
            last_name=instance.last_name or "Участник",
            email=instance.email or f"{instance.username}@alpine.local",
            sports_category='новичок',
            schoole=False,
            test=False,
        )