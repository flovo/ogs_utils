

def rank(rating):
    # rating = 850 * exp(rank * 0.032)
    from numpy import log
    return log(rating / 850) / 0.032


def ogs_rank(rating):
    return min(max(rank(rating), 5), 30 + 9)


def rating(rank):
    # rating = 850 * exp(rank * 0.032)
    from numpy import exp
    return 850 * exp(rank * 0.032)


def rank_str(rating, deviation=None, decimals=1):
    from ogs_utils.rating import rank as rank_fkt
    from ogs_utils.glicko2 import GlickoRating
    if isinstance(rating, GlickoRating):
        deviation = rating.RD
        rating = rating.r
    if deviation is not None:
        tol = rank_fkt(rating + deviation) - rank_fkt(rating)
    rank = rank_fkt(rating=rating) - 30
    if rank < 0:
        if deviation is not None:
            return ('{rank:.' + str(decimals) + 'f}k ± {tol:.' + str(decimals) + 'f}').format(rank=-rank, tol=tol)
        else:
            return ('{rank:.' + str(decimals) + 'f}k').format(rank=-rank)
    else:
        if deviation is not None:
            return ('{rank:.' + str(decimals) + 'f}d ± {tol:.' + str(decimals) + 'f}').format(rank=rank+1, tol=tol)
        else:
            return ('{rank:.' + str(decimals) + 'f}d').format(rank=rank+1)


def adjust_for_handicap(player_rating, handicap):
    return rating(rank(player_rating) + handicap)
