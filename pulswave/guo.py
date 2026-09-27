from .foam import load
from .reference import GUO_LI_MM, GUO_POSTSHOCK_T


def initiation(case, t, phi):
    rows = load(case, t, ("T", "p", "U", "CO2", "Qdot"))
    wall = sorted((r for r in rows if r["y"] < 0.2e-3), key=lambda r: r["x"])
    post = [r["T"] for r in wall if 0.003 < r["x"] < 0.008]
    t_post = sum(post) / len(post)
    peak = max(wall, key=lambda r: r["Qdot"])
    rise = next((r for r in wall if r["x"] > 0.003 and r["T"] > 1.1 * t_post), None)
    return {
        "postshock_T": (t_post, GUO_POSTSHOCK_T[phi]),
        "Li_hrr_mm": (peak["x"] * 1e3, GUO_LI_MM[phi]),
        "Li_T110_mm": (rise["x"] * 1e3 if rise else float("nan"), GUO_LI_MM[phi]),
    }
