from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import StudentRegisterForm


def register(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = StudentRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')
