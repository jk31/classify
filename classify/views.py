from django.shortcuts import redirect


def not_found(request):
    return redirect("app:home")