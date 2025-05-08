from django.shortcuts import render

def app_run(request):
    return render(request, "app.html")