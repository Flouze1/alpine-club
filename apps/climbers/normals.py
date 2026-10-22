"""
Нормативы для разрядов.
Хранятся в коде — это бизнес-правила, а не данные.
"""

NORMALS = {
    'МС': {
        'pullups': 25, 'rope_climbing': 8, 'pushups': 60,
        'squats': 30, 'back_bends': 15,
        'cross_10km': 2400, 'shuttle_run': 25, 'hang': 120,
    },
    'КМС': {
        'pullups': 20, 'rope_climbing': 7, 'pushups': 50,
        'squats': 25, 'back_bends': 13,
        'cross_10km': 2700, 'shuttle_run': 27, 'hang': 90,
    },
    '1': {
        'pullups': 15, 'rope_climbing': 6, 'pushups': 40,
        'squats': 20, 'back_bends': 11,
        'cross_10km': 3000, 'shuttle_run': 29, 'hang': 60,
    },
    '2': {
        'pullups': 12, 'rope_climbing': 5, 'pushups': 30,
        'squats': 15, 'back_bends': 9,
        'cross_10km': 3300, 'shuttle_run': 31, 'hang': 45,
    },
    '3': {
        'pullups': 8, 'rope_climbing': 4, 'pushups': 20,
        'squats': 10, 'back_bends': 7,
        'cross_10km': 3600, 'shuttle_run': 33, 'hang': 30,
    },
}

RANKS_ORDER = ['МС', 'КМС', '1', '2', '3']


def check_normal(results, normal):
    """Проверяет, что все показатели соответствуют нормативу."""
    checks = []
    for key in ['pullups', 'rope_climbing', 'pushups', 'squats', 'back_bends', 'hang']:
        if results.get(key) is not None:
            checks.append(results[key] >= normal[key])
    for key in ['cross_10km', 'shuttle_run']:
        if results.get(key) is not None:
            checks.append(results[key] <= normal[key])
    return all(checks) if checks else False


def calculate_rank(results):
    """Определяет разряд на основе результатов."""
    for rank in RANKS_ORDER:
        if check_normal(results, NORMALS[rank]):
            return rank
    return None