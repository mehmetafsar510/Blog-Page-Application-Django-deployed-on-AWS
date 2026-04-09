from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm, ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email
            try:
                send_mail(
                    subject,
                    f"From: {name} ({email})\n\n{message}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],  # Send to admin email
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent!")
                return redirect("contact")
            except Exception as e:
                messages.error(request, f"Error sending message: {str(e)}")
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, "users/contact.html", context)


def register(request):
    form = RegistrationForm(request.POST or None)
    if request.user.is_authenticated:
        messages.warning(request, "You already have an account!")
        return redirect("blog:list")
    if form.is_valid():
        form.save()
        name = form.cleaned_data["username"]
        messages.success(request, f"Acoount created for {name}")
        return redirect("login")

    context = {
        "form": form,
    }

    return render(request, "users/register.html", context)


def profile(request):
    # obj = User.objects.get(id=id)
    u_form = UserUpdateForm(request.POST or None, instance=request.user)
    p_form = ProfileUpdateForm(
        request.POST or None, request.FILES or None, instance=request.user.profile)

    if u_form.is_valid() and p_form.is_valid():
        u_form.save()
        p_form.save()
        messages.success(request, "Your profile has been updated!!")
        return redirect(request.path)

    context = {
        "u_form": u_form,
        "p_form": p_form
    }

    return render(request, "users/profile.html", context)


@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    profile = user_to_follow.profile
    
    if request.user not in profile.followers.all():
        profile.followers.add(request.user)
        messages.success(request, f"You are now following {user_to_follow.username}")
    else:
        messages.info(request, f"You are already following {user_to_follow.username}")
    
    return redirect(request.META.get('HTTP_REFERER', 'blog:list'))


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    profile = user_to_unfollow.profile
    
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        messages.success(request, f"You are no longer following {user_to_unfollow.username}")
    
    return redirect(request.META.get('HTTP_REFERER', 'blog:list'))
