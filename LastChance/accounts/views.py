from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm  # your forms
from django.contrib.auth.decorators import login_required

# ----------------------------
# Signup view
# ----------------------------
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.get_full_name()}! Your account has been created.')

            # Redirect based on role
            if user.is_staff:
                return redirect('staff-dashboard')
            else:
                return redirect('customer-dashboard')
        else:
            messages.error(request, 'There was an error creating your account. Please check the details.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


# ----------------------------
# Signin / Login view
# ----------------------------
def signin_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')

                # Redirect based on role
                if user.is_staff:
                    return redirect('staff-dashboard')
                else:
                    return redirect('customer-dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/signin.html', {'form': form})


# ----------------------------
# Signout / Logout view
# ----------------------------
def signout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('signin')  # redirect to login page

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')  # create this template