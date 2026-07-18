"""Wraps django-ckeditor's upload/browse endpoints with a staff check.

By default `ckeditor_uploader.urls` only requires the user to be logged
in — since every registered patient is a logged-in user on this site,
that would let any patient POST directly to /ckeditor/upload/ and store
arbitrary files, even though the CKEditor widget itself only ever appears
on the staff-only blog post form. This file re-declares the same two
URLs wrapped in `staff_member_required`, and is included instead of
`ckeditor_uploader.urls` in config/urls.py.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from ckeditor_uploader import views as ckeditor_views

urlpatterns = [
    path('upload/', staff_member_required(ckeditor_views.upload), name='ckeditor_upload'),
    path('browse/', staff_member_required(ckeditor_views.browse), name='ckeditor_browse'),
]
