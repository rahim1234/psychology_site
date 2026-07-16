from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import PHQ9Result, GAD7Result
from .forms import PHQ9TestForm, GAD7TestForm
from .scoring import (
    calculate_phq9_score, calculate_gad7_score,
    get_phq9_severity_label, get_gad7_severity_label,
    PHQ9_INTERPRETATION, GAD7_INTERPRETATION,
    interpret_mcmi4_results, get_mcmi4_interpretation_guide,
    calculate_mcmi4_scale_scores, MCMI4_WARNING,
)


class PHQ9TestView(LoginRequiredMixin, View):
    def get(self, request):
        form = PHQ9TestForm()
        return render(request, 'assessments/phq9_test.html', {'form': form})

    def post(self, request):
        form = PHQ9TestForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            score, severity = calculate_phq9_score(answers)
            result = PHQ9Result.objects.create(
                user=request.user,
                score=score,
                severity=severity,
                answers=answers,
            )
            return redirect('phq9_result_detail', pk=result.pk)
        return render(request, 'assessments/phq9_test.html', {'form': form})


class GAD7TestView(LoginRequiredMixin, View):
    def get(self, request):
        form = GAD7TestForm()
        return render(request, 'assessments/gad7_test.html', {'form': form})

    def post(self, request):
        form = GAD7TestForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            score, severity = calculate_gad7_score(answers)
            result = GAD7Result.objects.create(
                user=request.user,
                score=score,
                severity=severity,
                answers=answers,
            )
            return redirect('gad7_result_detail', pk=result.pk)
        return render(request, 'assessments/gad7_test.html', {'form': form})


class PHQ9ResultDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        result = get_object_or_404(PHQ9Result, pk=pk, user=request.user)
        severity_label = get_phq9_severity_label(result.severity)
        interpretation = PHQ9_INTERPRETATION.get(result.severity, '')
        return render(request, 'assessments/result_detail.html', {
            'result': result,
            'test_type': 'PHQ-9',
            'test_name': 'آزمون افسردگی',
            'severity_label': severity_label,
            'interpretation': interpretation,
        })


class GAD7ResultDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        result = get_object_or_404(GAD7Result, pk=pk, user=request.user)
        severity_label = get_gad7_severity_label(result.severity)
        interpretation = GAD7_INTERPRETATION.get(result.severity, '')
        return render(request, 'assessments/result_detail.html', {
            'result': result,
            'test_type': 'GAD-7',
            'test_name': 'آزمون اضطراب',
            'severity_label': severity_label,
            'interpretation': interpretation,
        })


class TestHistoryView(LoginRequiredMixin, ListView):
    template_name = 'assessments/history.html'
    context_object_name = 'results'

    def get_queryset(self):
        from .models import BDIResult, BAIResult, MCMI4Result

        phq9 = list(PHQ9Result.objects.filter(user=self.request.user).values('pk', 'score', 'severity', 'created_at'))
        gad7 = list(GAD7Result.objects.filter(user=self.request.user).values('pk', 'score', 'severity', 'created_at'))
        bdi = list(BDIResult.objects.filter(user=self.request.user).values('pk', 'score', 'severity', 'created_at'))
        bai = list(BAIResult.objects.filter(user=self.request.user).values('pk', 'score', 'severity', 'created_at'))
        mcmi4 = list(MCMI4Result.objects.filter(user=self.request.user).values('pk', 'score', 'created_at'))

        for r in phq9:
            r['type'] = 'PHQ-9'
            r['type_name'] = 'افسردگی (PHQ-9)'
            r['severity_label'] = get_phq9_severity_label(r['severity'])
        for r in gad7:
            r['type'] = 'GAD-7'
            r['type_name'] = 'اضطراب (GAD-7)'
            r['severity_label'] = get_gad7_severity_label(r['severity'])
        for r in bdi:
            r['type'] = 'BDI-II'
            r['type_name'] = 'افسردگی Beck'
            r['severity_label'] = get_bdi_severity_label(r['severity'])
        for r in bai:
            r['type'] = 'BAI'
            r['type_name'] = 'اضطراب Beck'
            r['severity_label'] = get_bai_severity_label(r['severity'])
        for r in mcmi4:
            r['type'] = 'MCMI-4'
            r['type_name'] = 'شخصیت میلون'
            r['severity'] = 'N/A'
            r['severity_label'] = 'نیاز به تفسیر متخصص'

        all_results = phq9 + gad7 + bdi + bai + mcmi4
        all_results.sort(key=lambda x: x['created_at'], reverse=True)
        return all_results

from .models import BDIResult, BAIResult, MCMI4Result
from .forms import BDITestForm, BAITestForm, MCMI4TestForm
from .scoring import (
    calculate_bdi_score, calculate_bai_score, calculate_mcmi4_score,
    get_bdi_severity_label, get_bai_severity_label,
    BDI_INTERPRETATION, BAI_INTERPRETATION,
)


class BDITestView(LoginRequiredMixin, View):
    def get(self, request):
        form = BDITestForm()
        return render(request, 'assessments/bdi_test.html', {'form': form})

    def post(self, request):
        form = BDITestForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            score, severity = calculate_bdi_score(answers)
            result = BDIResult.objects.create(
                user=request.user,
                score=score,
                severity=severity,
                answers=answers,
            )
            return redirect('bdi_result_detail', pk=result.pk)
        return render(request, 'assessments/bdi_test.html', {'form': form})


class BAIResultDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        result = get_object_or_404(BAIResult, pk=pk, user=request.user)
        severity_label = get_bai_severity_label(result.severity)
        interpretation = BAI_INTERPRETATION.get(result.severity, '')
        return render(request, 'assessments/result_detail.html', {
            'result': result,
            'test_type': 'BAI',
            'test_name': 'آزمون اضطراب Beck',
            'severity_label': severity_label,
            'interpretation': interpretation,
        })


class BAITestView(LoginRequiredMixin, View):
    def get(self, request):
        form = BAITestForm()
        return render(request, 'assessments/bai_test.html', {'form': form})

    def post(self, request):
        form = BAITestForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            score, severity = calculate_bai_score(answers)
            result = BAIResult.objects.create(
                user=request.user,
                score=score,
                severity=severity,
                answers=answers,
            )
            return redirect('bai_result_detail', pk=result.pk)
        return render(request, 'assessments/bai_test.html', {'form': form})


class BDIResultDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        result = get_object_or_404(BDIResult, pk=pk, user=request.user)
        severity_label = get_bdi_severity_label(result.severity)
        interpretation = BDI_INTERPRETATION.get(result.severity, '')
        return render(request, 'assessments/result_detail.html', {
            'result': result,
            'test_type': 'BDI-II',
            'test_name': 'آزمون افسردگی Beck',
            'severity_label': severity_label,
            'interpretation': interpretation,
        })


class MCMI4TestView(LoginRequiredMixin, View):
    def get(self, request):
        form = MCMI4TestForm()
        return render(request, 'assessments/mcmi4_test.html', {
            'form': form,
            'warning': MCMI4_WARNING,
        })

    def post(self, request):
        form = MCMI4TestForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data
            
            # محاسبه نمرات مقیاس‌ها
            scale_scores = calculate_mcmi4_scale_scores(answers)
            
            # محاسبه نمره کل (برای سازگاری با مدل قدیمی)
            total_score = scale_scores.get('total', 0)
            
            # ذخیره نتیجه
            try:
                # تلاش برای ذخیره با ساختار جدید (raw_scores)
                result = MCMI4Result.objects.create(
                    user=request.user,
                    answers=answers,
                    raw_scores=scale_scores,
                    score=total_score,  # برای سازگاری backward
                )
            except TypeError:
                # اگر مدل raw_scores ندارد، فقط با score ذخیره کن
                result = MCMI4Result.objects.create(
                    user=request.user,
                    answers=answers,
                    score=total_score,
                )
            
            return redirect('mcmi4_result_detail', pk=result.pk)
        return render(request, 'assessments/mcmi4_test.html', {'form': form})



class MCMI4ResultDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        result = get_object_or_404(MCMI4Result, pk=pk, user=request.user)
        
        # دریافت یا محاسبه raw_scores
        # اگر فیلد وجود داشت از آن استفاده کن، وگرنه از answers محاسبه کن
        if hasattr(result, 'raw_scores') and result.raw_scores:
            raw_scores = result.raw_scores
        else:
            # برای رکوردهای قدیمی که raw_scores ندارند
            raw_scores = calculate_mcmi4_scale_scores(result.answers)
        
        # محاسبه تفسیر بالینی
        interpretation = interpret_mcmi4_results(raw_scores)
        
        return render(request, 'assessments/mcmi4_result.html', {
            'result': result,
            'raw_scores': raw_scores,
            'interpretation_data': interpretation,
            'interpretation_guide': get_mcmi4_interpretation_guide(),
        })