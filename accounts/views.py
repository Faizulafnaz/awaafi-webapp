from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model, get_backends
from django.contrib import messages
from .forms import CustomUserCreationForm, EmailAuthenticationForm

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        print(form)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
        else:
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                if not user.has_usable_password():
                    messages.error(request, 'This account was created using Google. Please use "Continue with Google" to sign in.')
                else:
                    messages.error(request, 'Incorrect password. Please try again.')
            except User.DoesNotExist:
                    messages.error(request, 'No account found with this email address.')

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully!")
            return redirect('/')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html')
