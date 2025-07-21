from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(
                reverse_lazy("login")
            )  # ✅ must be inside the form.is_valid() block
    else:
        form = UserCreationForm()

    return render(request, "account/register.html", {"form": form})
