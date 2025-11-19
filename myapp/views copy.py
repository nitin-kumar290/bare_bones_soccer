import boto3
import uuid
import json
import logging

import stripe
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PersonForm, UserRegistrationForm, UserLoginForm, PlayerProfileForm
from .models import Person, Pickup, Event, EventImage, AttendancePayment
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse, JsonResponse

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

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

def series(request):
    return render(request, 'series.html')

def pickup_temp(request):
    return render(request, 'pickup-temp.html')

# DELETE LATER
# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])  # Hash the password
#             user.save()
#             messages.success(request, "Your account has been created successfully!")
#             return redirect('login')
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'register.html', {'form': form})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = PlayerProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Send them a welcome email
            subject = "Welcome to Bare Bones Soccer!"
            message = (
                f"Hi {user.username},\n\n"
                "Thank you for creating an account with Bare Bones Soccer Collective!\n\n"
                "We look forward to seeing you at our games and events. Log in to reserve your spot at any of our Social Series games. We'll see you at Blue Sport Stable in Superior every Monday night 5:30 - 8:00 PM with music, food/drink discount and more!\n\n"
                "Cheers,\n"
                "Bare Bones Soccer"
            )
            recipient_list = [user.email]  # user_form.email also works
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

            messages.success(request, "Account created! Please sign in.")
            return redirect('registration_success')
        else:
            # Here form errors are attached to each field.
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserRegistrationForm()
        profile_form = PlayerProfileForm()
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})


def registration_success(request):
    """
    Display registration success message and redirect to login after 5 seconds
    """
    return render(request, 'registration_success.html')



def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            # Convert username input to lowercase.
            username = form.cleaned_data['username'].lower()
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are now logged in!")
                return redirect('series_catalog')
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

# def sports_stable_register(request):
#     if request.method == 'POST':
#         form = SportsStableForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "You have successfully registered for the Sport Stable Series!")
#             return redirect('series')  # or wherever you want to redirect
#     else:
#         form = SportsStableForm()

#     return render(request, 'sports_stable_register.html', {'form': form})


@login_required
def schedule(request):
    today = datetime.today().date()
    schedule = [(today + timedelta(weeks=i)) for i in range(6)]

    # Check which weeks the user already paid
    paid_weeks = AttendancePayment.objects.filter(user=request.user, status="Paid").values_list('game_date', flat=True)
    paid_weeks_json = json.dumps([d.strftime("%Y-%m-%d") for d in paid_weeks])

    return render(request, 'schedule.html', {
        'schedule': schedule,
        #'paid_weeks': paid_weeks,
        'paid_weeks_list': paid_weeks_json
    })

@login_required
def series_catalog(request):
    return render(request, 'series_catalog.html')



# 

@login_required
def create_multi_checkout_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    data = json.loads(request.body)
    lumpsum = data.get('lumpsum', False)
    dates = data.get('dates', [])
    user      = request.user
    
    # If lumpsum == true => single line item for $70
    if lumpsum:
        line_items = [{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Bare Bones: All Monday Games"},
                "unit_amount": 5000, # $50 in cents
            },
            "quantity": 1,
        }]
        # Optionally record something in your DB about paying for "all games"
    else:
        # Otherwise, charge per date (e.g. $10 each or $5 each, up to you)
        # We'll assume $10 each for example:
        line_items = []
        for d in dates:
            line_items.append({
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Bare Bones Game: {d}"},
                    "unit_amount": 500, 
                },
                "quantity": 1,
            })
        # Optionally record these chosen dates in your DB as "Pending"

    # Create the Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        # success_url=request.build_absolute_uri('/payment-success/'), 
        success_url=(
            request.build_absolute_uri('/payment-success/') +
            f"?session_id={{CHECKOUT_SESSION_ID}}&dates={','.join(dates)}"
            ),
        cancel_url=request.build_absolute_uri('/payment-cancel/'),
    )
    logging.info(f"dates: {dates}")
    
    return JsonResponse({"id": session.id})


@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")
    dates_str = request.GET.get("dates", "")
    
    if not session_id or not dates_str:
        messages.error(request, "Invalid payment session.")
        return redirect('home')
    
    # Convert to list
    dates = [d.strip() for d in dates_str.split(',') if d.strip()]
    
    # 1) Retrieve the session from Stripe to ensure payment is successful
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            # 2) Create AttendancePayment records for each date
            for game_date in dates:
                AttendancePayment.objects.create(
                    user=request.user,
                    game_date=game_date,
                    payment_id=session_id,
                    amount=5.00, # or from session.amount_total
                    status='Paid'
                )
            
            # 3) (Optional) email confirmation
            subject = "Bare Bones Soccer Payment Confirmation"
            message = (
                f"Hi {request.user.username},\n\n"
                f"Thank you for your payment. You've successfully paid for:\n"
                + ", ".join(dates) +
                "\n\nIf you can no longer attend a game and need a refund, please send an email to soccerbarebones@gmail.com 2 HOURS BEFORE THE SCHEDULED GAME.\n\n"
                "\nWe look forward to seeing you on the pitch!\n\n"
                "Cheers,\nBare Bones Soccer"
            )
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False
            )
            
            # 4) Show success page
            messages.success(request, "Payment successful!")
            return render(
                request,
                'payment_success.html',
                {"dates": dates, "session_id": session_id}
            )
        else:
            messages.error(request, "Payment was not completed.")
            return redirect('home')
    except stripe.error.StripeError as e:
        messages.error(request, f"Error verifying payment: {e}")
        return redirect('home')



# @login_required
# def payment_success(request):
#     # date = request.GET.get("date")
#     # session_id = request.GET.get("session_id")
#     session_id = request.GET.get("session_id")
#     dates = request.GET.get("dates", "").split(',')  # Get and split the dates
#     logging.info(f"dates: {dates}")


#     # payment = AttendancePayment.objects.filter(payment_id=session_id).update(status='Paid')
#     if session_id:
#         for date in dates:
#             AttendancePayment.objects.create(
#             user=request.user,
#             game_date=date,
#             payment_id=session_id,
#             amount=7.00,
#             status='Paid'
#         )

#         # send notification email
#         # Grab the user’s email (all payments share the same user)
#     user = payment.first().user  
#     user_email = user.email

#     # Optionally, build a message with details about which dates they paid for.
#     # Or if lumpsum, we can craft a lumpsum message. If single date, we can mention that date.
#     paid_dates = [p.game_date for p in payment]
#     date_list_str = ", ".join(str(d) for d in paid_dates)

#     subject = "Bare Bones Soccer Payment Confirmation"
#     message = (
#         f"Hi {user.username},\n\n"
#         f"Thank you for your payment. You've successfully paid for the following date(s): {date_list_str}.\n"
#         "We look forward to seeing you on the pitch!\n\n"
#         "Cheers,\n"
#         "Bare Bones Soccer"
#     )
#     send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email], fail_silently=False)

#     return render(request, 'payment_success.html', {"date": dates})

@login_required
def payment_cancel(request):
    date = request.GET.get("date")
    session_id = request.GET.get("session_id")
    status = request.GET.get("status", "failed")  # 'failed' or 'canceled'

    payment = AttendancePayment.objects.filter(payment_id=session_id).first()
    # if payment:
    #     payment.status = 'Failed' if status == 'failed' else 'Canceled'
    #     payment.save()

        # Optional: send notification email or log the event
        

    template_name = 'payment_cancel.html'
    message = ("Your payment was not successful. Please try again or contact support if the problem persists."
              if status == 'failed' else 
              "Your payment has been canceled. You can try again whenever you're ready.")

    return render(request, template_name, {
        "date": date,
        "message": message
    })


#@login_required
# def create_checkout_session(request, date_str):
#     date = datetime.strptime(date_str, "%Y-%m-%d").date()

#     session = stripe.checkout.Session.create(
#         payment_method_types=["card"],
#         line_items=[{
#             "price_data": {
#                 "currency": "usd",
#                 "product_data": {
#                     "name": f"Bare Bones Game: {date}",
#                 },
#                 "unit_amount": 1000,
#             },
#             "quantity": 1,
#         }],
#         mode="payment",
#         success_url=request.build_absolute_uri('/payment-success/') + f"?date={date_str}&session_id={{CHECKOUT_SESSION_ID}}",
#         cancel_url=request.build_absolute_uri('/payment-cancel/'),
#     )

#     AttendancePayment.objects.create(
#         user=request.user,
#         game_date=date,
#         payment_id=session.id,
#         amount=10.00,
#         status='Pending'
#     )

#     return redirect(session.url, code=303)

