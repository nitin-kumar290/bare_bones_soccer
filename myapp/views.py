import boto3
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PersonForm, UserRegistrationForm, UserLoginForm
from .models import Person, Pickup, Event, EventImage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import JsonResponse


# Create your views here.
from django.http import HttpResponse, JsonResponse

def home(request):
    events = Event.objects.all().order_by('-start_time')  # Fetch all events ordered by start time
    return render(request, "home.html", {"events": events})


def about(request):
    return render(request, 'about.html')


# def contact(request):
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             save_contact_form(
#                 form.cleaned_data['name'],
#                 form.cleaned_data['email'],
#                 form.cleaned_data['message']
#             )
#             messages.success(request, "Thank you for contacting us! Your message has been saved.")
#             return redirect('contact')
#     else:
#         form = ContactForm()

#     return render(request, 'contact.html', {'form': form})

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

def pickup_temp(request):
    return render(request, 'pickup-temp.html')


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
        "end": event.end_time.strftime("%Y-%m-%dT%H:%M:%S") if event.end_time else None,
        "description": event.description,
    } for event in events]
    return JsonResponse(events_list, safe=False)


def events(request):
    events = Event.objects.all()  # Fetch all events
    return render(request, 'events.html', {'events': events})

def privacypolicy(request):
    return render(request, 'privacy-policy.html')

def datadeletion(request):
    return render(request, 'data-deletion.html')


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)  # Fetch specific event
    gallery_images = event.images.all()  # Fetch associated gallery images
    return render(request, 'event_detail.html', {'event': event, 'gallery_images': gallery_images})


def get_presigned_url(request):
    """Generate a pre-signed S3 upload URL."""
    s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)

    file_name = request.GET.get("filename", f"{uuid.uuid4()}.jpg")
    file_type = request.GET.get("filetype", "image/jpeg")
    object_key = f"events/{file_name}"

    response = s3_client.generate_presigned_post(
        settings.AWS_STORAGE_BUCKET_NAME,
        object_key,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            ["starts-with", "$Content-Type", "image/"]
        ],
        ExpiresIn=3600
    )

    return JsonResponse({
        "url": response["url"],
        "fields": response["fields"],
        "object_key": object_key
    })