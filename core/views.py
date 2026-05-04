from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, ListView
from .models import Master, QuizResult, Booking

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_masters'] = Master.objects.all()[:4]
        context['step'] = self.request.session.get('quiz_step', 1)
        return context

    def post(self, request):
        if request.POST.get('back'):
            request.session['quiz_step'] = max(1, request.session.get('quiz_step', 1) - 1)
            return redirect('/#quiz')
        step = int(request.POST.get('step', 1))
        
        if step == 1:
            request.session['hair_type'] = request.POST.get('hair_type')
            request.session['quiz_step'] = 2
        elif step == 2:
            request.session['face_shape'] = request.POST.get('face_shape')
            request.session['quiz_step'] = 3
        elif step == 3:
            request.session['lifestyle'] = request.POST.get('lifestyle')
            request.session['quiz_step'] = 4
        elif step == 4:
            request.session['priority'] = request.POST.get('priority')
            # Save Result
            if request.user.is_authenticated:
                QuizResult.objects.create(
                    user=request.user,
                    hair_type=request.session.get('hair_type'),
                    face_shape=request.session.get('face_shape'),
                    lifestyle=request.session.get('lifestyle'),
                    priority=request.session.get('priority')
                )
            request.session['quiz_step'] = 1 
            return redirect('master_list')

        return redirect('/#quiz')

class MasterListView(ListView):
    model = Master
    template_name = 'core/master_list.html'
    context_object_name = 'masters'
