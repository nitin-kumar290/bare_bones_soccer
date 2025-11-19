import boto3
import uuid
import json
import logging

import stripe
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PersonForm, UserRegistrationForm, UserLoginForm, PlayerProfileForm, UnsubscribeForm, EventRSVPForm
from .models import Person, Pickup, Event, EventImage, AttendancePayment, EmailUnsubscribe, EventRSVP, OneOffEvent
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Create your views here.
from django.http import HttpResponse, JsonResponse
from textwrap import dedent
from .forms import ForgotUsernameForm


logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

SES = boto3.client("ses", region_name="us-east-2")
FROM = "Bare Bones Soccer <no-reply@barebonessoccer.com>"
# db_client.py


def send_email_ses(to, subject, body_html):
    SES.send_email(
        Source=FROM,
        Destination={"ToAddresses":[to]},
        Message={
          "Subject": {"Data": subject},
          "Body":    {"Html": {"Data": body_html}}
        }
    )


# Create an EventBridge client
EVENTBRIDGE = boto3.client('events', region_name='us-east-2')  

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

            # Deactivate account till it is verified
            user.is_active = False 
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Send activation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Bare Bones Soccer account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.send()
            
            return redirect('activation_sent')
            
        else:
            # Here form errors are attached to each field.
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserRegistrationForm()
        profile_form = PlayerProfileForm()
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # 2) Publish EventBridge event
        detail = {
            'userId': str(user.id),
            'email': user.email,
            'registeredAt': user.date_joined.isoformat()
        }
        EVENTBRIDGE.put_events(
            Entries=[{
                'Source': 'barebones.app',
                'DetailType': 'UserRegistered',
                'Detail': json.dumps(detail),
                'EventBusName': 'default'
            }]
        )

        # Send them a welcome email
        subject = "Welcome to Bare Bones Soccer!"
        message = f"""
        <p>Hey {user.username},</p>
        <p>You're officially in! Welcome to Bare Bones Soccer — the most social, one-of-a-kind soccer communities around. We're pumped to have you! Here's what you need to know:</p>
        <p>💥 Your first pickup session at Blue Sport Stable (Superior) is FREE!! (Just $5 every Monday after that)
        <br>
        ⚡ Fast-paced court soccer with music & good vibes — this is part of our weekly Social Series, where we partner with local businesses for unique footy experiences.
        <br>
        📍 Blue Sport Stable - 1 Superior Drive, Superior
        <br>
        ⏰ Monday nights, 6:00-8:00 PM
        <br>
        🍔 20% off food & drinks 🍻 at Stable Bar & Grill (on-site restaurant)
        </p>
        <p><a href="https://barebonessoccer.com/login/"> Sign in to reserve your spot!</a></p>
        <p>We also run free pickup every Saturday at 9:30AM at Broomfield Commons Sports Fields. For all other pickup and event updates, check our Instagram stories weekly.</p>
        <p>See you out there — on the court, the pitch, or wherever the game takes us.</p>
        <p>The Bare Bones Crew</p>
    """
        recipient_list = [user.email]  # user_form.email also works
        send_email_ses(user.email, subject, message)
        #send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

        messages.success(request, "Account created! Please sign in.")
        login(request, user)
        return redirect('registration_success')
    else:
        return render(request, 'activation_invalid.html')


def activation_sent(request):
    return render(request, 'activation_sent.html')


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
    paid_weeks = AttendancePayment.objects.filter(user=request.user).values_list('game_date', flat=True)
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
    dates = data.get('dates', [])
    user      = request.user
    
    # 1) Have they ever paid before?
    has_paid = AttendancePayment.objects.filter(user=user).exists()

    # 2) If not, give the first date free
    if not has_paid and dates:
        free_date     = dates[0]
        charge_dates  = dates[1:]
    else:
        free_date     = None
        charge_dates  = dates
    free_flag = '1' if free_date else '0'

    formatted_dates = []
    for date_str in dates:
        try:
            # Parse the date string (assuming YYYY-MM-DD format)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Format it nicely (e.g., "Monday, May 15, 2023")
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
            formatted_dates.append(formatted_date)
        except ValueError:
            # If date parsing fails, use the original string
            formatted_dates.append(date_str)

    # 3) If there’s something to charge, make a Stripe session
    if charge_dates:
        line_items = [{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Paid Session: {datetime.strptime(d, '%Y-%m-%d').date().strftime('%A, %B %d, %Y')}"},
                "unit_amount": 500,       # $5.00
            },
            "quantity": 1,
        } for d in charge_dates]
        # Account for the free date
        if free_date:
            line_items.insert(0, {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Free Session: {datetime.strptime(free_date, '%Y-%m-%d').date().strftime('%A, %B %d, %Y')}"},
                    "unit_amount": 0,       # $0.00
                },
                "quantity": 1,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=(
              request.build_absolute_uri('/payment-success/') +
              f"?session_id={{CHECKOUT_SESSION_ID}}&free={free_flag}&dates={','.join(dates)}"
            ),
            cancel_url=request.build_absolute_uri('/payment-cancel/'),
        )
        return JsonResponse({"id": session.id})

    # 4) Otherwise, it’s all free — record zero‑dollar payments
    for d in dates:
        AttendancePayment.objects.create(
            user       = user,
            game_date  = d,
            payment_id = "FREE",
            amount     = 0.00,
            status     = "Free"
        )
    # And tell the front‑end “free checkout”
    return JsonResponse({"id": None, "free": True, "dates": dates})


@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")
    dates_str = request.GET.get("dates", "")
    free_game = request.GET.get('free') == '1'
    dates     = [d for d in dates_str.split(',') if d]
    logging.info(f"session_id: {session_id}, dates_str: {dates_str}, dates: {dates}")
    
    
    # Convert to list
    dates = [d.strip() for d in dates_str.split(',') if d.strip()]
    formatted_dates = []
    for date_str in dates:
        try:
            # Parse the date string (assuming YYYY-MM-DD format)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Format it nicely (e.g., "Monday, May 15, 2023")
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
            formatted_dates.append(formatted_date)
        except ValueError:
            # If date parsing fails, use the original string
            formatted_dates.append(date_str)
    
    # 1) Retrieve the session from Stripe to ensure payment is successful
    try:
        if session_id:
            logging.info(f"Checking session_id if statement : {session_id}")
            if not AttendancePayment.objects.filter(payment_id=session_id).exists():
                logging.info(f"passed AttendancePayment if statement : {session_id}")
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == "paid":
                    if free_game:
                        AttendancePayment.objects.create(
                            user=request.user,
                            game_date=dates[0],
                            payment_id=session.id,
                            amount=0.00,
                            status='Free'
                        )
                        for game_date in dates[1:]:
                            AttendancePayment.objects.create(
                                user=request.user,
                                game_date=game_date,
                                payment_id=session_id,
                                amount=5.00, # or from session.amount_total
                                status='Paid'
                            )
                    else:
                        # 2) Create AttendancePayment records for each date
                        for game_date in dates:
                            AttendancePayment.objects.create(
                                user=request.user,
                                game_date=game_date,
                                payment_id=session_id,
                                amount=5.00, # or from session.amount_total
                                status='Paid'
                            )
                    
                    # 3) email confirmation

                    # Join the formatted dates with line breaks and bullet points
                    date_list_str = "".join([f"<li style='margin-bottom: 8px;'>• {date}</li>" for date in formatted_dates])
                    subject = "You're in for Monday ⚽"
                    message = f"""
                    <p>Hey {request.user.username},</p>
                    <p>Thank you for your payment. You're officially signed up for the following dates:</p>
                    <ul style='list-style-type: none; padding-left: 10px;'>
                    {date_list_str}
                    </ul>
                    <p>🕠 6:00 PM - 8:00 PM
                    <br>
                    📍 Blue Sport Stable - 1 Superior Drive, Superior
                    <br>
                    🍔 Grab 20% off food & drinks at Stable Bar & Grill
                    </p>
                    <p><em>*Continuous games, come and go as you please. Teams are formed as players arrive.</em> Bring proper footwear, water and good vibes.</p>
                    <p>See you on the courts!</p>
                    <p>The Bare Bones Crew</p>
                    """
                    send_email_ses(request.user.email, subject, message)
                    # send_mail(
                    #     subject,
                    #     message,
                    #     settings.EMAIL_HOST_USER,
                    #     [request.user.email],
                    #     fail_silently=False
                    # )
                    
                    # 4) Show success page
                    messages.success(request, "Payment successful!")
                    return render(
                        request,
                        'payment_success.html',
                        {"dates": formatted_dates, "session_id": session_id}
                    )
                else:
                    messages.error(request, "Payment was not completed.")
                    return redirect('home')
            else:
                messages.error(request, "This page should not be refreshed")
                return redirect('home')
        else:
            
            date_list_str = "".join([f"<li style='margin-bottom: 8px;'>• {date}</li>" for date in formatted_dates])
            subject = "You're in for Monday ⚽"
            message = f"""
            <p>Hey {request.user.username},</p>
            <p>Congrats! You're signed up for your free session! We'll see you on the following date:</p>
            <ul style='list-style-type: none; padding-left: 10px;'>
            {date_list_str}
            </ul>
            <p>🕠 6:00 PM - 8:00 PM
            <br>
            📍 Blue Sport Stable - 1 Superior Drive, Superior
            <br>
            🍔 Grab 20% off food & drinks at Stable Bar & Grill
            </p>
            <p><em>*Continuous games, come and go as you please. Teams are formed as players arrive.</em> Bring proper footwear, water and good vibes.</p>
            <p>See you on the courts!</p>
            <p>The Bare Bones Crew</p>
            """
            # # subject = "Bare Bones Soccer Payment Confirmation"
            # # message = (
            # #     f"Hi {request.user.username},\n\n"
            # #     f"Thank you. You've successfully signed up for the following session dates:\n"
            # #     + ", ".join(dates) +
            # #     "\nWe look forward to seeing you on the pitch!\n\n"
            # #     "Cheers,\nBare Bones Soccer"
            # # )
            send_email_ses(request.user.email, subject, message)

            # send_mail(
            #     subject,
            #     message,
            #     settings.EMAIL_HOST_USER,
            #     [request.user.email],
            #     fail_silently=False
            # )
            
            # 4) Show success page
            messages.success(request, "Sign Up successful!")
            return render(
                request,
                'payment_success.html',
                {"dates": formatted_dates, "session_id": session_id}
            )
    except stripe.error.StripeError as e:
        messages.error(request, f"Error verifying payment: {e}")
        return redirect('home')


# views.py

def username_reset(request):
    if request.method == 'POST':
        form = ForgotUsernameForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Try to find an active user with that email
            qs = User.objects.filter(email__iexact=email, is_active=True)
            if qs.exists():
                user = qs.first()
                # Send the email
                subject = "Your Bare Bones Soccer username"
                message = (
                    f"Hi there,\n\n"
                    f"We received a request to remind you of your username for Bare Bones Soccer.\n\n"
                    f"Your username is: {user.username}\n\n"
                    f"If you didn’t request this, you can safely ignore this email.\n\n"
                    f"Thanks,\nThe Bare Bones Crew"
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return redirect('username_reset_done')
            else:
                # Don’t leak whether the email exists—show generic message
                messages.success(
                    request,
                    "If an account with that email exists, an email has been sent with your username."
                )
                return redirect('username_reset_done')
    else:
        form = ForgotUsernameForm()

    return render(request, 'username_reset.html', {'form': form})

def username_reset_done(request):
    return render(request, 'username_reset_done.html')



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

def unsubscribe(request):
    if request.method == 'POST':
        form = UnsubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            reason = form.cleaned_data['reason']
            other_reason = form.cleaned_data['other_reason'] if reason == 'other' else None
            
            # Add to unsubscribe list
            EmailUnsubscribe.objects.get_or_create(
                email=email,
                defaults={
                    'reason': reason,
                    'other_reason': other_reason
                }
            )
            
            return redirect('unsubscribe_success')
    else:
        email = request.GET.get('email', '')
        form = UnsubscribeForm(initial={'email': email})
    
    return render(request, 'unsubscribe.html', {'form': form})


def unsubscribe_success(request):
    return render(request, 'unsubscribe_success.html')


def event_rsvp(request):
    if request.method == 'POST':
        form = EventRSVPForm(request.POST)
        if form.is_valid():
            rsvp = form.save(commit=False)
            rsvp.event_name = "BARE BONES SOCCER WAREHOUSE PARTY"
            rsvp.event_date = "2025-11-20"  # Update this date as needed
            try:
                rsvp.save()
                #messages.success(request, "RSVP successful! See you there!")
                return redirect('rsvp_success')
            except:
                messages.error(request, "You've already RSVP'd for this event.")
            return redirect('events')
    return redirect('events')


def rsvp_success(request):
    return render(request, 'rsvp_success.html')


@login_required
def waldschanke(request):
    event_date = datetime(2025, 12, 7).date()
    has_registered = OneOffEvent.objects.filter(
        user=request.user, 
        event_name='WALDSCHANKE BRUNCH BALL'
    ).exists()
    
    return render(request, 'waldschanke.html', {
        'event_date': event_date,
        'has_registered': has_registered
    })


@login_required
def create_waldschanke_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY 
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    user = request.user
    
    # Check if already registered
    if OneOffEvent.objects.filter(user=user, event_name='WALDSCHANKE BRUNCH BALL').exists():
        return JsonResponse({'error': 'Already registered'}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Waldschänke Brunch Ball - Dec 7, 2025"},
                "unit_amount": 100,  # $15.00
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri('/waldschanke-payment-success/') + f"?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri('/payment-cancel/'),
    )

    return JsonResponse({"id": session.id})


@login_required
def waldschanke_payment_success(request):
    session_id = request.GET.get("session_id")
    
    try:
        if session_id and not OneOffEvent.objects.filter(payment_id=session_id).exists():
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                OneOffEvent.objects.create(
                    user=request.user,
                    event_name='WALDSCHANKE BRUNCH BALL',
                    event_date='2025-12-07',
                    payment_id=session_id,
                    amount=15.00,
                    status='Paid'
                )
                
                # Send confirmation email
                subject = "You're registered for Waldschänke Brunch Ball!"
                message = f"""
                <p>Hey {request.user.username},</p>
                <p>You're all set for Waldschänke Brunch Ball!</p>
                <p><strong>Sunday, December 7, 2025</strong><br>
                Wäldschanke Ciders - 4100 Jason St, Denver<br>
                10:30 AM - 1:30 PM</p>
                <p>Get ready for unlimited pickup games, player prize packages & raffle entry!</p>
                <p>See you there!</p>
                <p>The Bare Bones Crew</p>
                """
                send_email_ses(request.user.email, subject, message)
                
                messages.success(request, "Registration successful!")
                return render(request, 'waldschanke_payment_success.html')
            else:
                messages.error(request, "Payment was not completed.")
                return redirect('waldschanke')
        else:
            messages.error(request, "Invalid session or already processed.")
            return redirect('waldschanke')
    except stripe.error.StripeError as e:
        messages.error(request, f"Error verifying payment: {e}")
        return redirect('waldschanke')




def promo_video(request):
    return render(request, 'promo_video.html')



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

