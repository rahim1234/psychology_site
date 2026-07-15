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
        phq9 = list(PHQ9Result.objects.filter(user=self.request.user).values('pk', 'score', 'severity', 'created_at'))
        gad7 = list(GAD7Result.objects.filter(user=self.request.user).values('pk', 'score', 'severity', 'created_at'))
        for r in phq9:
            r['type'] = 'PHQ-9'
            r['type_name'] = 'افسردگی'
            r['severity_label'] = get_phq9_severity_label(r['severity'])
        for r in gad7:
            r['type'] = 'GAD-7'
            r['type_name'] = 'اضطراب'
            r['severity_label'] = get_gad7_severity_label(r['severity'])
        all_results = phq9 + gad7
        all_results.sort(key=lambda x: x['created_at'], reverse=True)
        return all_results
