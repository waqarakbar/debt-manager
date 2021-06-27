from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from .forms import DebtorCreationForm, DebtorUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test

def user_login(request):

    if request.method == "POST":
        #print('login the user here')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')

            if user.is_superuser:
                return redirect('home')
            else:
                return redirect('my-transaction')

        else:
            messages.error(request, 'Incorrect username/password')
            return redirect('user-login')

    return render(request, 'users/login.html')


@login_required
def profile(request):

    if request.method == "POST":
        form = DebtorUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile update successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DebtorUpdateForm(instance=request.user)

    context = {
        'form': form
    }

    return render(request, 'users/profile.html', context)


@login_required
def user_password_change(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Profile update successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form
    }

    return render(request, 'users/password_change.html', context)


def user_logout(request):
    logout(request)
    return redirect('user-login')


# check if a given user is super_user
def _super_user_test(user):
    return user.is_superuser


@login_required
@user_passes_test(_super_user_test, login_url='my-transactions/')
def user_register(request):

    if request.method == "POST":
        form = DebtorCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.groups.add(1)
            messages.success(request, 'Mew member save successfully')
            return redirect('home')
    else:
        form = DebtorCreationForm()

    context = {
        'form': form
    }

    return render(request, 'users/user_register.html', context)