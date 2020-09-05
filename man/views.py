from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def man_home(request):
    return render(request, 'man/index.html')
