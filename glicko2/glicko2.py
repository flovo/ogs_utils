from collections import namedtuple

GlickoRating = namedtuple("GlickoRating", ["r", "RD", "σ"])
Glicko2Rating = namedtuple("Glicko2Rating", ["μ", "φ", "σ"])

deltaE = 10.0**-5

conversion_factor = 173.7178


def convert_Glicko_to_Glicko2(gr):
    return Glicko2Rating(μ=(gr.r - 1500)/173.7178, φ=gr.RD/173.7178, σ=gr.σ)


def convert_Glicko2_to_Glicko(gr):
    return GlickoRating(r=173.7178*gr.μ + 1500, RD=173.7178*gr.φ, σ=gr.σ)


def _g(φ):
    from numpy import sqrt, pi
    return 1 / sqrt(1 + 3 * φ**2 / pi**2)


def _E(g, μp, μo):
    from numpy import exp, minimum, maximum
    try:
        return maximum(minimum(1 / (1 + exp(-g * (μp - μo))), 1-deltaE), deltaE)
    except FloatingPointError as e:
        print('g', g)
        print('μp', μp)
        print('μo', μo)
        raise e


def _v(g, E):
    from numpy import sum
    try:
        return 1 / sum(g**2 * E * (1 - E))
    except FloatingPointError as e:
        print(g)
        print(E)
        print(e)
        raise e


def _Δ(v, g, s, E):
    from numpy import sum
    return v * sum(g * (s - E))


def _σ_new(σ, Δ, φ, v, τ, ε, εf):
    from numpy import log, abs, exp
    a = log(σ**2)

    def f(x):
        from numpy import exp
        return exp(x) * (Δ**2 - φ**2 - v - exp(x)) / (2 * (φ**2 + v + exp(x))**2) - (x - a) / τ**2
    A = a
    if Δ**2 > φ**2 + v:
        B = log(Δ**2 - φ**2 - v)
    else:
        k = 1
        while f(a - k * τ) < 0:
            k += 1
        B = a - k * τ
    from scipy.optimize import brentq
    A = brentq(f, A, B, disp=True, xtol=ε)
    # fA, fB = f(A), f(B)
    # while abs(B - A) > ε:
    #     try:
    #         C = A + (A - B) * fA / (fB - fA)
    #         fC = f(C)
    #     except FloatingPointError as e:
    #         print(e)
    #         print('A {A:10.10}        B {B:10.10}        fA {fA:10.10}          fB {fB:10.10}        div {div:10.10}'.format(A=A, B=B, fA=fA, fB=fB, div=abs(A-B)/ε))
    #         print(Δ**2 - φ**2 - v)
    #         print(φ**2 + v)
    #         print(a)
    #         raise e
    #     if fC * fB < 0:
    #         A, fA = B, fB
    #     else:
    #         fA /= 2
    #     B, fB = C, fC
    return exp(A/2)


def _φ_star(φ, σ_new):
    from numpy import sqrt
    return sqrt(φ**2 + σ_new**2)


def update(p, os, s, handicap, τ=1.2, ε=0.000001, εf=0):
#    print(p)
#    for o in os:
#        print(o)
#    print(s)
    from numpy import sqrt, array, exp
    handicap = array(handicap)
    if isinstance(p, Glicko2Rating):
        return_type = "Glicko2"
    elif isinstance(p, GlickoRating):
        μp = (p.r  * exp(handicap * 0.032) - 1500) / 173.7178
        p = convert_Glicko_to_Glicko2(p)
        os = [convert_Glicko_to_Glicko2(o) for o in os]
        return_type = "Glicko"
    if len(os) == 0:
        res = Glicko2Rating(μ=p.μ, φ=min(sqrt(p.φ**2 + p.σ**2), 350/173.7178), σ=p.σ)
        if return_type == "Glicko2":
            return res
        elif return_type == "Glicko":
            return convert_Glicko2_to_Glicko(res)
        else:
            raise SyntaxError
    s = array(s)
    μo = array([o.μ for o in os])
    φo = array([o.φ for o in os])
    s = array(s)
    g = _g(φo)
    E = _E(g=g, μp=μp, μo=μo)
    v = _v(g, E)
    Δ = _Δ(v, g, s, E)
    σ_new = _σ_new(σ=p.σ, Δ=Δ, φ=p.φ, v=v, τ=τ, ε=ε, εf=εf)
    φ_new = 1 / sqrt(1 / _φ_star(p.φ, σ_new=σ_new)**2 + 1 / v )
    μ_new = p.μ + φ_new**2 * sum( g * (s - E) )
    res = Glicko2Rating(μ=μ_new, φ=φ_new, σ=σ_new)
    if return_type == "Glicko2":
        return res
    elif return_type == "Glicko":
        res = convert_Glicko2_to_Glicko(res)
        if res.RD > 700:
            print(res.RD)
#            raise
        if res.RD <= 0:
            print(res.RD)
#            raise
        return res
    else:
        raise SyntaxError


def win_probability(rating_1, rating_2, handicap=0):
    from numpy import exp
    μp = (rating_1 * exp(handicap * 0.032) - 1500) / 173.7178
    μo = (rating_2 - 1500) / 173.7178
    return _E(0, μp, μo)


from numpy import seterr
seterr(all='raise')
