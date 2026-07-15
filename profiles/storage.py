from django.conf import settings
from django.core.files.storage import FileSystemStorage


def get_private_storage():
    """Storage for files that must never be reachable by direct URL.

    Kept completely outside MEDIA_ROOT/MEDIA_URL (which nginx serves
    publicly) — files here are only ever readable through the
    login-protected `protected_media` view. `base_url=None` means calling
    `.url` on one of these files raises an error instead of silently
    returning a public link, so a future bug can't accidentally expose one.

    A callable (not a ready-made instance) is used here on purpose: Django
    stores whatever this returns as a reference in migrations, so it stays
    correct across machines with different project paths instead of baking
    in one absolute path at migration-writing time.
    """
    return FileSystemStorage(location=str(settings.PRIVATE_MEDIA_ROOT), base_url=None)
