from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MaxFileSizeValidator:
    """Rejects uploaded files larger than `max_mb` megabytes.

    Class-based (not a closure) so it can be safely referenced from a
    model field's `validators=[...]` and serialized into migrations.
    """

    def __init__(self, max_mb):
        self.max_mb = max_mb

    def __call__(self, value):
        limit_bytes = self.max_mb * 1024 * 1024
        if value.size > limit_bytes:
            raise ValidationError(f'حجم فایل نباید بیشتر از {self.max_mb} مگابایت باشد.')

    def __eq__(self, other):
        return isinstance(other, MaxFileSizeValidator) and self.max_mb == other.max_mb
