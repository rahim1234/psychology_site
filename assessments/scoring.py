"""PHQ-9 and GAD-7 scoring logic with severity levels and Persian interpretations."""

# PHQ-9 Scoring (9 questions, 0-3 each, total 0-27)
PHQ9_QUESTIONS = [
    'در دو هفته اخیر، چقدر به کارهای روزمره علاقه یا لذت داشته‌اید؟',
    'در دو هفته اخیر، چقدر احساس ناراحتی، افسردگی یا ناامیدی کرده‌اید؟',
    'در دو هفته اخیر، چقدر مشکل در به خواب رفتن، در خواب ماندن یا زیاد خوابیدن داشته‌اید؟',
    'در دو هفته اخیر، چقدر احساس خستگی یا کمبود انرژی کرده‌اید؟',
    'در دو هفته اخیر، چقدر اشتهای شما کم یا زیاد شده است؟',
    'در دو هفته اخیر، چقدر احساس بدی نسبت به خودتان داشته‌اید؟',
    'در دو هفته اخیر، چقدر مشکل در تمرکز روی کارها داشته‌اید؟',
    'در دو هفته اخیر، چقدر در حرکت کردن یا صحبت کردن کند شده‌اید؟',
    'در دو هفته اخیر، چقدر فکر آسیب رساندن به خودتان یا مرگ از ذهنتان گذشته است؟',
]

PHQ9_ANSWERS = [
    ('0', 'اصلاً'),
    ('1', 'چند روزی'),
    ('2', 'بیش از نصف روزها'),
    ('3', 'تقریباً هر روز'),
]

PHQ9_SEVERITY = {
    'Normal': {'range': (0, 4), 'label': 'طبیعی'},
    'Mild': {'range': (5, 9), 'label': 'خفیف'},
    'Moderate': {'range': (10, 14), 'label': 'متوسط'},
    'Moderately Severe': {'range': (15, 19), 'label': 'نسبتاً شدید'},
    'Severe': {'range': (20, 27), 'label': 'شدید'},
}

PHQ9_INTERPRETATION = {
    'Normal': 'شما علائم افسردگی قابل توجهی ندارید.',
    'Mild': 'شما علائم خفیفی از افسردگی دارید. اگر این علائم ادامه یافت، با یک متخصص مشورت کنید.',
    'Moderate': 'شما علائم متوسطی از افسردگی دارید. توصیه می‌شود با یک متخصص بهداشت روان صحبت کنید.',
    'Moderately Severe': 'شما علائم نسبتاً شدیدی از افسردگی دارید. لطفاً هرچه سریع‌تر با یک متخصص مشورت کنید.',
    'Severe': 'شما علائم شدیدی از افسردگی دارید. لطفاً فوراً با یک متخصص بهداشت روان تماس بگیرید.',
}

# GAD-7 Scoring (7 questions, 0-3 each, total 0-21)
GAD7_QUESTIONS = [
    'در دو هفته اخیر، چقدر احساس عصبی بودن، نگرانی یا در تنگنا بودن داشته‌اید؟',
    'در دو هفته اخیر، چقدر نتوانسته‌اید نگرانی را کنترل یا متوقف کنید؟',
    'در دو هفته اخیر، چقدر نگرانی‌های مختلف زیادی داشته‌اید؟',
    'در دو هفته اخیر، چقدر مشکل در آرام شدن داشته‌اید؟',
    'در دو هفته اخیر، چقدر آشفته بوده‌اید و نتوانسته‌اید آرام باشید؟',
    'در دو هفته اخیر، چقدر نسبت به چیزی که باعث نگرانی شما می‌شود بی‌صبر یا تحریک‌پذیر بوده‌اید؟',
    'در دو هفته اخیر، چقدر ترسیده‌اید که ممکن است اتفاق وحشتناکی بیفتد؟',
]

GAD7_ANSWERS = [
    ('0', 'اصلاً'),
    ('1', 'چند روزی'),
    ('2', 'بیش از نصف روزها'),
    ('3', 'تقریباً هر روز'),
]

GAD7_SEVERITY = {
    'Normal': {'range': (0, 4), 'label': 'طبیعی'},
    'Mild': {'range': (5, 9), 'label': 'خفیف'},
    'Moderate': {'range': (10, 14), 'label': 'متوسط'},
    'Severe': {'range': (15, 21), 'label': 'شدید'},
}

GAD7_INTERPRETATION = {
    'Normal': 'شما علائم قابل توجهی از اضطراب ندارید.',
    'Mild': 'شما علائم خفیفی از اضطراب دارید.',
    'Moderate': 'شما علائم متوسطی از اضطراب دارید. مشورت با متخصص توصیه می‌شود.',
    'Severe': 'شما علائم شدیدی از اضطراب دارید. لطفاً فوراً با یک متخصص صحبت کنید.',
}


def calculate_phq9_score(answers: dict) -> tuple[int, str]:
    """Calculate PHQ-9 score and return (score, severity_key)."""
    score = sum(int(answers.get(f'q{i}', 0)) for i in range(1, 10))
    for severity, info in PHQ9_SEVERITY.items():
        low, high = info['range']
        if low <= score <= high:
            return score, severity
    return score, 'Severe'


def calculate_gad7_score(answers: dict) -> tuple[int, str]:
    """Calculate GAD-7 score and return (score, severity_key)."""
    score = sum(int(answers.get(f'q{i}', 0)) for i in range(1, 8))
    for severity, info in GAD7_SEVERITY.items():
        low, high = info['range']
        if low <= score <= high:
            return score, severity
    return score, 'Severe'


def get_phq9_severity_label(severity_key: str) -> str:
    return PHQ9_SEVERITY.get(severity_key, {}).get('label', severity_key)


def get_gad7_severity_label(severity_key: str) -> str:
    return GAD7_SEVERITY.get(severity_key, {}).get('label', severity_key)
