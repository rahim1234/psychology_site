"""Monkey-patch Django's template context for Python 3.14 compatibility.

Python 3.14 changed copy(super()) behavior — super() objects are no longer
copyable in the standard way. This breaks BaseContext.__copy__ in
django.template.context. This patch fixes it.
"""
from copy import copy as _copy
import django.template.context as _ctx


def _fixed_base_context_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    return duplicate


def _fixed_context_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    duplicate.autoescape = self.autoescape
    duplicate.use_l10n = self.use_l10n
    duplicate.use_tz = self.use_tz
    duplicate.template_name = self.template_name
    duplicate.render_context = _copy(self.render_context)
    duplicate.template = self.template
    return duplicate


def _fixed_render_context_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    return duplicate


_ctx.BaseContext.__copy__ = _fixed_base_context_copy
_ctx.Context.__copy__ = _fixed_context_copy
_ctx.RenderContext.__copy__ = _fixed_render_context_copy
