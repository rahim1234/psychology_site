from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from .forms import SiteContentForm
from .models import SiteContent


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """فقط سوپریوزر (ادمین اصلی) اجازه دسترسی دارد؛ بقیه به صفحه ورود هدایت یا 403 می‌شوند."""

    def test_func(self):
        return self.request.user.is_superuser


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_content'] = SiteContent.get_solo()
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_content'] = SiteContent.get_solo()
        return context


class ContactView(TemplateView):
    template_name = 'core/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_content'] = SiteContent.get_solo()
        return context


class ManageContentView(SuperuserRequiredMixin, UpdateView):
    """یک صفحه‌ی ساده برای ویرایش تمام متن‌های قابل‌ویرایش سایت (صفحه اصلی، درباره ما، تماس
    با ما، فوتر)، بدون نیاز به پنل ادمین."""

    model = SiteContent
    form_class = SiteContentForm
    template_name = 'core/manage_content.html'
    success_url = reverse_lazy('manage_content')

    # گروه‌بندی فیلد‌ها برای نمایش مرتب در قالب کارت‌های مجزا
    FIELD_GROUPS = [
        ('\u0627\u0637\u0644\u0627\u0639\u0627\u062a \u06a9\u0644\u06cc \u0633\u0627\u06cc\u062a', ['site_owner_name', 'site_tagline']),
        ('\u0635\u0641\u062d\u0647 \u0627\u0635\u0644\u06cc — \u062a\u0635\u0648\u06cc\u0631 \u0627\u0628\u062a\u062f\u0627\u06cc\u06cc (\u0647\u06cc\u0631\u0648)', [
            'home_hero_eyebrow', 'home_hero_title', 'home_hero_lead',
            'hero_photo_1', 'hero_photo_2', 'hero_photo_3', 'hero_photo_4',
        ]),
        ('\u0635\u0641\u062d\u0647 \u0627\u0635\u0644\u06cc — \u062f\u0648 \u0645\u0633\u06cc\u0631 \u0634\u0631\u0648\u0639', [
            'start_card1_eyebrow', 'start_card1_title', 'start_card1_desc',
            'start_card2_eyebrow', 'start_card2_title', 'start_card2_desc',
        ]),
        ('\u0635\u0641\u062d\u0647 \u0627\u0635\u0644\u06cc — \u0628\u062e\u0634 \u0622\u0632\u0645\u0648\u0646\u200c\u0647\u0627', [
            'tests_section_eyebrow', 'tests_section_title', 'tests_section_desc',
            'test1_desc', 'test2_desc', 'test3_desc', 'test4_desc', 'test5_desc', 'test6_desc',
        ]),
        ('\u0635\u0641\u062d\u0647 \u0627\u0635\u0644\u06cc — \u062c\u0645\u0644\u0647\u200c\u06cc \u0646\u0642\u0644\u200c\u0642\u0648\u0644', ['manifesto_quote']),
        ('\u0635\u0641\u062d\u0647 \u0627\u0635\u0644\u06cc — \u062f\u0631\u0628\u0627\u0631\u0647\u200c\u06cc \u0645\u0646 (\u0648\u0633\u0637 \u0635\u0641\u062d\u0647)', [
            'about_me_eyebrow', 'about_me_title', 'about_me_text', 'about_me_photo',
        ]),
        ('\u0635\u0641\u062d\u0647 \u0627\u0635\u0644\u06cc — \u0631\u0648\u0646\u062f \u06a9\u0627\u0631', [
            'process_section_eyebrow', 'process_section_title',
            'process_step1_title', 'process_step1_desc',
            'process_step2_title', 'process_step2_desc',
            'process_step3_title', 'process_step3_desc',
        ]),
        ('\u0635\u0641\u062d\u0647 \u0627\u0635\u0644\u06cc — \u062f\u0639\u0648\u062a \u0628\u0647 \u0627\u0642\u062f\u0627\u0645 \u067e\u0627\u06cc\u0627\u0646\u06cc', ['cta_title', 'cta_text']),
        ('\u062f\u0631\u0628\u0627\u0631\u0647\u200c\u06cc \u0645\u0627', ['about_intro', 'about_mission']),
        ('درباره‌ی ما — ابزارها و هشدار مهم', [
            'about_tool1_title', 'about_tool1_desc', 'about_tool2_title', 'about_tool2_desc',
            'about_tools_note', 'about_warning_title', 'about_warning_text',
        ]),
        ('\u062a\u0645\u0627\u0633 \u0628\u0627 \u0645\u0627', [
            'contact_email', 'contact_phone', 'contact_address', 'contact_hours',
            'contact_message', 'emergency_phone', 'emergency_text',
        ]),
        ('\u0641\u0648\u062a\u0631 — \u0645\u0639\u0631\u0641\u06cc \u0648 \u0634\u0628\u06a9\u0647\u200c\u0647\u0627\u06cc \u0627\u062c\u062a\u0645\u0627\u0639\u06cc', [
            'footer_brand_title', 'footer_brand_text',
            'social_instagram_url', 'social_telegram_url', 'social_whatsapp_url', 'social_twitter_url',
        ]),
        ('\u0641\u0648\u062a\u0631 — \u062e\u062f\u0645\u0627\u062a \u0648 \u06a9\u067e\u06cc\u200c\u0631\u0627\u06cc\u062a', ['footer_services', 'footer_copyright']),
        ('فوتر — تماس با ما', ['contact_email', 'contact_phone', 'contact_address']),
    ]

    def get_object(self, queryset=None):
        return SiteContent.get_solo()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        context['grouped_fields'] = [
            (title, [form[name] for name in names if name in form.fields])
            for title, names in self.FIELD_GROUPS
        ]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '\u0645\u062c\u062a\u0648\u0627\u06cc \u0633\u0627\u06cc\u062a \u0628\u0627 \u0645\u0648\u0641\u0642\u06cc\u062a \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f.')
        return response


def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500(request):
    return render(request, 'core/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'core/403.html', status=403)

def custom_400(request, exception):
    return render(request, 'core/400.html', status=400)    
