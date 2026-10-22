from datetime import date, timedelta
from django.utils import timezone
from .models import Attestation
from .normals import calculate_rank


def can_attest(climber):
    """Может ли альпинист пройти аттестацию?"""
    if climber.last_attestation_date is None:
        return True
    one_year_ago = date.today() - timedelta(days=365)
    return climber.last_attestation_date <= one_year_ago


def is_attestation_overdue(climber):
    """Просрочена ли аттестация?"""
    if climber.last_attestation_date is None:
        return True
    one_year_ago = date.today() - timedelta(days=365)
    return climber.last_attestation_date < one_year_ago


def process_attestation(attestation):
    """Обрабатывает аттестацию и сохраняет результат."""
    results = {
        'pullups': attestation.pullups,
        'rope_climbing': attestation.rope_climbing,
        'pushups': attestation.pushups,
        'squats': attestation.squats,
        'back_bends': attestation.back_bends,
        'cross_10km': attestation.cross_10km,
        'shuttle_run': attestation.shuttle_run,
        'hang': attestation.hang,
    }

    rank = calculate_rank(results)

    if rank:
        attestation.status = 'passed'
        attestation.awarded_rank = rank

        climber = attestation.climber
        climber.sports_category = rank
        climber.last_attestation_date = timezone.now().date()
        climber.save()
    else:
        attestation.status = 'failed'

    attestation.completed_at = timezone.now()
    attestation.save()
    return rank