"""
Требования к разряду для восхождения на горы разной сложности.
"""

MOUNTAIN_REQUIREMENTS = {
    '1А': ['3', '2', '1', 'КМС', 'МС'],
    '1Б': ['2', '1', 'КМС', 'МС'],
    '2А': ['1', 'КМС', 'МС'],
    '2Б': ['КМС', 'МС'],
    '3А': ['МС'],
    '3Б': ['МС'],
}


def can_climb(climber, mountain):
    """Может ли альпинист идти на эту гору?"""
    allowed_ranks = MOUNTAIN_REQUIREMENTS.get(mountain.difficulty, [])
    return climber.sports_category in allowed_ranks