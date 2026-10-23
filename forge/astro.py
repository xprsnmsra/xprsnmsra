"""Astronomy for the telemetry strip: solar elevation (NOAA algorithm) and moon phase."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
LUCKNOW = (26.8467, 80.9462)  # lat, lon (deg)
SYNODIC = 29.530588853


def julian_day(dt: datetime) -> float:
    dt = dt.astimezone(timezone.utc)
    y, m = dt.year, dt.month
    d = dt.day + (dt.hour + (dt.minute + dt.second / 60.0) / 60.0) / 24.0
    if m <= 2:
        y, m = y - 1, m + 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5


def sun_elevation(dt: datetime, lat: float, lon: float) -> float:
    """Solar elevation above the horizon in degrees (no refraction)."""
    jd = julian_day(dt)
    jc = (jd - 2451545.0) / 36525.0
    l0 = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360.0
    m = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    ecc = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)
    mr = math.radians(m)
    c = (math.sin(mr) * (1.914602 - jc * (0.004817 + 0.000014 * jc))
         + math.sin(2 * mr) * (0.019993 - 0.000101 * jc) + math.sin(3 * mr) * 0.000289)
    true_long = l0 + c
    omega = 125.04 - 1934.136 * jc
    app_long = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    obliq = (23.0 + (26.0 + (21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))) / 60.0) / 60.0
             + 0.00256 * math.cos(math.radians(omega)))
    decl = math.asin(math.sin(math.radians(obliq)) * math.sin(math.radians(app_long)))
    y = math.tan(math.radians(obliq) / 2.0) ** 2
    l0r = math.radians(l0)
    eq_time = 4.0 * math.degrees(
        y * math.sin(2 * l0r) - 2 * ecc * math.sin(mr) + 4 * ecc * y * math.sin(mr) * math.cos(2 * l0r)
        - 0.5 * y * y * math.sin(4 * l0r) - 1.25 * ecc * ecc * math.sin(2 * mr))
    u = dt.astimezone(timezone.utc)
    minutes = u.hour * 60 + u.minute + u.second / 60.0
    tst = (minutes + eq_time + 4.0 * lon) % 1440.0
    ha = math.radians(tst / 4.0 - 180.0)
    latr = math.radians(lat)
    return math.degrees(math.asin(
        math.sin(latr) * math.sin(decl) + math.cos(latr) * math.cos(decl) * math.cos(ha)))


def moon_age(dt: datetime) -> float:
    """Phase in [0,1): 0 = new, 0.5 = full. Epoch: new moon 2000-01-06 18:14 UTC."""
    return ((julian_day(dt) - 2451550.26) / SYNODIC) % 1.0


def moon_illumination(age: float) -> float:
    return (1.0 - math.cos(2.0 * math.pi * age)) / 2.0


def moon_name(age: float) -> str:
    names = ["New", "Waxing crescent", "First quarter", "Waxing gibbous",
             "Full", "Waning gibbous", "Last quarter", "Waning crescent"]
    return names[int(age * 8 + 0.5) % 8]


def day_curve(dt: datetime, lat: float, lon: float, step_min: int = 10) -> list[tuple[float, float]]:
    """(hour_of_day_IST, elevation°) samples across the IST calendar day of `dt`."""
    local = dt.astimezone(IST)
    start = local.replace(hour=0, minute=0, second=0, microsecond=0)
    return [(m / 60.0, sun_elevation(start + timedelta(minutes=m), lat, lon))
            for m in range(0, 24 * 60 + 1, step_min)]


def sun_times(curve: list[tuple[float, float]]) -> tuple[float | None, float | None]:
    """Sunrise / sunset (IST hours) by linear interpolation of zero crossings."""
    rise = sset = None
    for (h0, e0), (h1, e1) in zip(curve, curve[1:]):
        if e0 < 0 <= e1 and rise is None:
            rise = h0 + (h1 - h0) * (-e0) / (e1 - e0)
        if e0 >= 0 > e1:
            sset = h0 + (h1 - h0) * e0 / (e0 - e1)
    return rise, sset


def hm(h: float | None) -> str:
    if h is None:
        return "--:--"
    mm = int(round(h * 60)) % 1440
    return f"{mm // 60:02d}:{mm % 60:02d}"
