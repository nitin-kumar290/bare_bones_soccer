from django.shortcuts import render, redirect, get_object_or_404
from .forms import PersonForm, UserRegistrationForm, UserLoginForm
from .models import Person, Pickup, Event, EventImage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.
from django.http import HttpResponse, JsonResponse

def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        form  = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for contacting us! Your message has been received.")
            return redirect('contact')
    else:
        form = PersonForm()
    return render(request, 'contact.html', {'form': form})


def pickup(request):
    return render(request, 'pickup.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are now logged in!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


def get_events(request):
    events = Pickup.objects.all()
    events_list = [{
        "title": event.title,
        "start": event.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "description": event.description,
    } for event in events]
    return JsonResponse(events_list, safe=False)


def events(request):
    events = Event.objects.all()  # Fetch all events
    return render(request, 'events.html', {'events': events})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)  # Fetch specific event
    gallery_images = event.images.all()  # Fetch associated gallery images
    return render(request, 'event_detail.html', {'event': event, 'gallery_images': gallery_images})
