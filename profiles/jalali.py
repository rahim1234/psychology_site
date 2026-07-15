"""Pure-Python Gregorian <-> Jalali (Shamsi/Persian) calendar conversion.

Implements the well-known public-domain conversion algorithm (originally by
Roozbeh Pournader and Mohammad Toossi), reproduced independently and verified
against several well-known reference dates (Iranian revolution date,
1979-02-11 -> 1357-11-22; Nowruz 1403 -> 2024-03-20; Nowruz 1404 -> 2025-03-21).

No third-party package is required, so this has no pip/internet dependency.
"""

JALALI_MONTHS = [
    (1, 'فروردین'), (2, 'اردیبهشت'), (3, 'خرداد'), (4, 'تیر'),
    (5, 'مرداد'), (6, 'شهریور'), (7, 'مهر'), (8, 'آبان'),
    (9, 'آذر'), (10, 'دی'), (11, 'بهمن'), (12, 'اسفند'),
]
JALALI_MONTH_NAMES = dict(JALALI_MONTHS)

_G_D_M = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


def gregorian_to_jalali(gy, gm, gd):
    """(year, month, day) in Gregorian -> (year, month, day) in Jalali."""
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = (
        (365 * gy)
        + ((gy2 + 3) // 4)
        - ((gy2 + 99) // 100)
        + ((gy2 + 399) // 400)
        - 80
        + gd
        + _G_D_M[gm - 1]
    )
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + (days % 31)
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def jalali_to_gregorian(jy, jm, jd):
    """(year, month, day) in Jalali -> (year, month, day) in Gregorian."""
    if jy > 979:
        gy = 1600
        jy -= 979
    else:
        gy = 621
    if jm < 7:
        days = (jm - 1) * 31
    else:
        days = ((jm - 7) * 30) + 186
    days += (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + 78 + jd
    gy += 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    is_leap = (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)
    g_d_m = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335] if is_leap \
        else [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gm = 12
    for i in range(11, -1, -1):
        if gd > g_d_m[i]:
            gm = i + 1
            gd -= g_d_m[i]
            break
    return gy, gm, gd


def date_to_jalali_str(d):
    """Format a datetime.date/datetime as 'DD ماه YYYY' in Jalali. Empty string if d is None."""
    if not d:
        return ''
    jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
    return f'{jd} {JALALI_MONTH_NAMES[jm]} {jy}'
