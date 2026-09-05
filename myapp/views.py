import boto3
import uuid
import json
import logging
import secrets

import stripe
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import PersonForm, UserRegistrationForm, UserLoginForm, PlayerProfileForm, UnsubscribeForm, EventRSVPForm, SponsorInquiryForm, ReferralSourceForm, LeagueTeamCreateForm, LeagueFreeAgentForm, TournamentTeamCreateForm
from .models import Person, Pickup, Event, EventImage, AttendancePayment, EmailUnsubscribe, EventRSVP, OneOffEvent, Partner, ReferralSource, LeagueTeam, LeagueTeamPlayer, LeagueFreeAgent
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Create your views here.
from django.http import HttpResponse, JsonResponse, Http404
from textwrap import dedent
from .forms import ForgotUsernameForm
from functools import wraps


def hide_on_prod(view_func):
    """Blocks a view entirely on the prod stage — feature not ready for real users yet.
    Still fully live on dev/local. Remove this decorator when ready to launch on prod."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if settings.IS_PROD:
            raise Http404
        return view_func(request, *args, **kwargs)
    return wrapper


logger = logging.getLogger(__name__)


class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        inactive_user = User.objects.filter(email__iexact=email, is_active=False).first()
        if inactive_user:
            site = get_current_site(self.request)
            uid = urlsafe_base64_encode(force_bytes(inactive_user.pk))
            token = default_token_generator.make_token(inactive_user)
            activation_link = f"https://{site.domain}/activate/{uid}/{token}/"
            html = render_to_string('account_activation_email.html', {
                'user': inactive_user,
                'activation_link': activation_link,
            })
            email_msg = EmailMessage('Activate your Bare Bones Soccer account', html, settings.EMAIL_HOST_USER, [inactive_user.email])
            email_msg.content_subtype = 'html'
            try:
                email_msg.send()
            except Exception:
                pass
            messages.warning(self.request, "Hey! Looks like this account was never activated. We just resent your activation email — check your inbox (and spam folder) to activate before signing in.")
            return redirect('login')
        return super().form_valid(form)
stripe.api_key = settings.STRIPE_SECRET_KEY


def unsubscribe_footer(request):
    url = request.build_absolute_uri(reverse('unsubscribe'))
    return f'<p style="font-size:11px;color:#777;border-top:1px solid #eee;padding-top:10px;margin-top:16px;text-align:center;">You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="{url}" style="color:#777;">Unsubscribe</a>.</p>'

SES = boto3.client("ses", region_name="us-east-2")
FROM = "Bare Bones Soccer <no-reply@barebonessoccer.com>"
# db_client.py


def send_email_ses(to, subject, body_html, body_text=None):
    if EmailUnsubscribe.objects.filter(email__iexact=to).exists():
        logger.info(f"Skipping email to unsubscribed address: {to}")
        return
    body = {"Html": {"Data": body_html}}
    if body_text:
        body["Text"] = {"Data": body_text}
    SES.send_email(
        Source=FROM,
        Destination={"ToAddresses":[to]},
        Message={
          "Subject": {"Data": subject},
          "Body":    body
        }
    )


# Create an EventBridge client
EVENTBRIDGE = boto3.client('events', region_name='us-east-2')  

def home(request):
    events = Event.objects.all().order_by('-start_time')  # Fetch all events ordered by start time
    return render(request, "home.html", {"events": events})


def about(request):
    return render(request, 'about.html')


def sponsors_partners(request):
    partners = Partner.objects.filter(active=True)
    form = SponsorInquiryForm()
    if request.method == 'POST':
        form = SponsorInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            subject = "New Sponsor/Partner Inquiry"
            body = f"""
            <p>New sponsor/partner inquiry received:</p>
            <p><strong>Name:</strong> {form.cleaned_data['name']}</p>
            <p><strong>Business:</strong> {form.cleaned_data.get('business') or '—'}</p>
            <p><strong>Email:</strong> {form.cleaned_data['email']}</p>
            <p><strong>Message:</strong> {form.cleaned_data['message']}</p>
            """
            send_email_ses('soccerbarebones@gmail.com', subject, body)
            messages.success(request, "Thanks! We'll be in touch soon.")
            return redirect('sponsors_partners')
    return render(request, 'partners.html', {'partners': partners, 'form': form})


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

            # Send email to admin
            subject = "New Contact Form Submission"
            message = f"""
            <p>New contact form submission received:</p>
            <p><strong>Name:</strong> {form.cleaned_data['name']}</p>
            <p><strong>Email:</strong> {form.cleaned_data['email']}</p>
            <p><strong>Message:</strong> {form.cleaned_data['message']}</p>
            """
            send_email_ses('soccerbarebones@gmail.com', subject, message)

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
    # Only ever carry `next` through account creation for the league claim-confirmation
    # flow specifically — not for team registration or any other page, so a curious click
    # into the league doesn't accidentally dump a brand-new user onto "Create Your Team".
    raw_next = request.POST.get('next') or request.GET.get('next', '')
    next_url = raw_next if '/leagues/waldy-street-league/claim/' in raw_next else ''
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
            try:
                current_site = get_current_site(request)
                mail_subject = 'Activate your Bare Bones Soccer account'
                message = render_to_string('account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'next': next_url,
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.content_subtype = 'html'
                email.send()
            except Exception as e:
                print(f"ACTIVATION EMAIL FAILED TO SEND: {e}")

            return redirect('activation_sent')

        else:
            # Here form errors are attached to each field.
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserRegistrationForm()
        profile_form = PlayerProfileForm()
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form, 'next': next_url})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # 2) Publish EventBridge event (best-effort — must never block real account activation)
        try:
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
        except Exception:
            logger.exception("Failed to publish UserRegistered EventBridge event")

        # Send them a welcome email
        subject = "Welcome to Bare Bones Soccer!"
        message = f"""
                <!DOCTYPE html>
                <html>
                <body>
                <!-- Email content with direct image URL -->

                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
                <tr>
                    <td align="center" style="padding:0;">
                    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
                        <tr>
                        <td align="center" style="padding:24px;">
                            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">
                            
                            <!-- Header -->
                            <tr>
                                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold;">
                                You're officially in — welcome to Bare Bones Soccer!
                                </td>
                            </tr>
                            
                            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
                            
                            <!-- Main Content -->
                            <tr>
                                <td style="font-size:16px; line-height:24px; text-align:center;">
                                We're not just running soccer games.<br>
                                We're building a community and pushing a cultural shift in how soccer is experienced in America.
                                Bare Bones exists to make the game more social, more meaningful and more fun.<br>Pickup runs, special events, local partnerships and good people who just love the game and being around others who do.
                                </td>
                            </tr>
                    
                            
                            <tr><td style="height:24px; line-height:24px;">&nbsp;</td></tr>
                            
                            <!-- How to Get Involved -->
                            <tr>
                                <td style="font-size:18px; line-height:24px; text-align:center; font-weight:bold;">
                                How to get involved right away:
                                </td>
                            </tr>
                            
                            <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>
                            
                            <!-- Details -->
                            <tr>
                                <td style="font-size:16px; padding:0 24px; text-align:center; line-height:26px;">
                                
                                💬 Join our WhatsApp community for weekly pickup chats, event news, community chatter & more!:<br>
                                👉 <a href="https://chat.whatsapp.com/IzHQHb1UODABuoABqXotvm" target="_blank" style="color:#0066cc;">Join WhatsApp Group</a><br><br>
                                
                                Follow us on Instagram <a href="https://www.instagram.com/barebonessoccer/" target="_blank" style="color:#0066cc;">here</a> where we also post event & pickup info plus more footy content<br><br>
                                
                                Whether you're here to play hard, play casual, or just be part of something social — you're in the right place.
                                </td>
                            </tr>
                            
                            <tr><td style="height:24px; line-height:24px;">&nbsp;</td></tr>
                            
                            <!-- Closing -->
                            <tr>
                                <td style="font-size:16px; line-height:24px; text-align:center;">
                                See you soon,<br>
                                The Bare Bones Crew
                                </td>
                            </tr>
                            
                            <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>
                            
                            <tr>
                                <td style="font-size:14px; line-height:20px; text-align:center; font-style:italic; color:#666;">
                                By soccer people, For soccer people
                                </td>
                            </tr>

                            </table>
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                </table>
                {unsubscribe_footer(request)}
                </body>
                </html>
                """

        try:
            email = EmailMessage(subject, message, to=[user.email])
            email.content_subtype = "html"
            email.send()
        except Exception:
            logger.exception("Failed to send welcome email")

        login(request, user)
        next_url = request.GET.get('next', '')
        if '/leagues/waldy-street-league/claim/' in next_url:
            return redirect(next_url)
        return redirect('welcome_next_steps')
    else:
        return render(request, 'activation_invalid.html')


def activation_sent(request):
    return render(request, 'activation_sent.html')


def registration_success(request):
    """
    Display registration success message and redirect to login after 5 seconds
    """
    return render(request, 'registration_success.html')


@login_required
def welcome_next_steps(request):
    """
    Shown right after account activation — Follow IG / Join WhatsApp, plus a
    one-time "how did you find us?" survey saved to ReferralSource.
    """
    existing = ReferralSource.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ReferralSourceForm(request.POST, instance=existing)
        if form.is_valid():
            referral = form.save(commit=False)
            referral.user = request.user
            referral.save()
            return redirect('series_catalog')
    else:
        form = ReferralSourceForm(instance=existing)

    return render(request, 'welcome_next_steps.html', {'form': form})



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
                # Check for next parameter, default to series_catalog if not present
                next_url = request.GET.get('next') or request.POST.get('next', 'series_catalog')
                
                # If next is waldschanke, create checkout session directly
                if next_url == '/waldschanke/' or next_url == 'waldschanke':
                    if OneOffEvent.objects.filter(user=user, event_name='WALDSCHANKE BRUNCH BALL 2').exists():
                        return redirect('waldschanke')
                    
                    session = stripe.checkout.Session.create(
                        payment_method_types=["card"],
                        line_items=[{
                            "price_data": {
                                "currency": "usd",
                                "product_data": {"name": "Bare Bones Brunch Ball 2 - Jan 18, 2025"},
                                "unit_amount": 1500,
                            },
                            "quantity": 1,
                        }],
                        mode="payment",
                        success_url=request.build_absolute_uri(reverse('waldschanke_payment_success')) + f"?session_id={{CHECKOUT_SESSION_ID}}",
                        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
                    )
                    return redirect(session.url)
                
                return redirect(next_url)
            else:
                try:
                    inactive_user = User.objects.get(username=username, is_active=False)
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your Bare Bones Soccer account'
                    activation_message = render_to_string('account_activation_email.html', {
                        'user': inactive_user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(inactive_user.pk)),
                        'token': default_token_generator.make_token(inactive_user),
                    })
                    activation_email = EmailMessage(mail_subject, activation_message, to=[inactive_user.email])
                    activation_email.content_subtype = 'html'
                    activation_email.send()
                    messages.warning(request, "Hey! Looks like this account was never activated. We just resent your activation link — check your email (and spam folder) and click the link to get in!")
                except User.DoesNotExist:
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
    events = Event.objects.all()

    next_event = events.filter(start_time__gte=timezone.now()).order_by('start_time').first()
    if next_event:
        return render(request, 'event_detail.html', {
            'event': next_event,
            'gallery_images': next_event.images.all(),
            'event_image_url': next_event.image.url if next_event.image else None,
        })

    seen_urls = set()
    carousel_images = []
    for event in events:
        image_entries = [(event.image.url, event.title)] if event.image else []
        image_entries += [(img.image.url, '') for img in event.images.all()]
        for url, label in image_entries:
            if url not in seen_urls:
                seen_urls.add(url)
                carousel_images.append({'url': url, 'label': label})

    has_rsvpd = False
    if request.user.is_authenticated:
        has_rsvpd = OneOffEvent.objects.filter(
            user=request.user,
            event_name='world_cup_final'
        ).exists()

    rsvp_count = OneOffEvent.objects.filter(
        event_name='world_cup_final',
        status='Free RSVP'
    ).count()

    rsvp_full = rsvp_count >= 40
    spots_remaining = max(0, 40 - rsvp_count)

    return render(request, 'events.html', {
        'events': events,
        'carousel_images': carousel_images,
        'has_rsvpd': has_rsvpd,
        'rsvp_count': rsvp_count,
        'rsvp_full': rsvp_full,
        'spots_remaining': spots_remaining,
    })


@login_required
def register_wcf_rsvp(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = request.user

    if OneOffEvent.objects.filter(user=user, event_name='world_cup_final').exists():
        return JsonResponse({'error': 'Already registered'}, status=400)

    rsvp_count = OneOffEvent.objects.filter(event_name='world_cup_final', status='Free RSVP').count()
    if rsvp_count >= 40:
        return JsonResponse({'error': 'Spots full'}, status=400)

    OneOffEvent.objects.create(
        user=user,
        event_name='world_cup_final',
        event_date='2026-07-19',
        ticket_type='player',
        payment_id='FREE',
        amount=0.00,
        status='Free RSVP'
    )

    # Send confirmation email via SES
    subject = "You're In — World Cup Final Party RSVP Confirmed!"
    message = f"""
<!DOCTYPE html>
<html>
<body>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
  <tr>
    <td align="center" style="padding:0;">
      <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
        <tr>
          <td align="center" style="padding:24px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

              <!-- Header -->
              <tr>
                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold;">
                  ⚽🏆 WORLD CUP FINAL PARTY — RSVP CONFIRMED!
                </td>
              </tr>

              <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

              <!-- Hook -->
              <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                  You're all set, {user.first_name or user.username}! Your player spot for the 7/19 World Cup Final Party is confirmed!
                </td>
              </tr>

              <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

              <!-- Details -->
              <tr>
                <td style="font-size:16px; line-height:28px;">
                  📍 <b>Waldschänke Ciders — 4100 Jason St, Denver, CO</b><br><br>
                  💰 Pickup is donation based - donate below 👇<br>
                  📺 Watch party is <b>free and open to all</b> — no ticket needed<br><br>
                  <i>*Proper shoes required to play — flats or grippy sneakers*</i>
                </td>
              </tr>

              <tr><td style="height:24px; line-height:24px;">&nbsp;</td></tr>

              <!-- Donate section -->
              <tr>
                <td style="text-align:center; background:#f8f8f8; border-radius:10px; padding:20px 16px;">
                  <p style="font-size:18px; font-weight:bold; margin:0 0 4px 0; letter-spacing:1px;">Support the Community — Donate What You Want</p>
                  <p style="font-size:13px; color:#777; margin:0 0 18px 0;"></p>

                  <!-- Venmo -->
                  <p style="font-size:15px; font-weight:bold; color:#3D95CE; margin:0 0 8px 0; letter-spacing:1px;">VENMO</p>
                  <img src="https://bare-bones-soccer.s3.amazonaws.com/images/bbs_venmo.jpeg" alt="Venmo QR Code" width="220" height="220" style="display:block; margin:0 auto 8px; border-radius:8px;">
                  <p style="font-size:15px; font-weight:bold; color:#3D95CE; margin:0 0 20px 0;">@barebonessoccer</p>

                  <!-- Divider -->
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td style="height:1px; background:#ddd; font-size:0; line-height:0;">&nbsp;</td></tr></table>

                  <!-- Zelle -->
                  <p style="font-size:15px; font-weight:bold; color:#9b59f5; margin:16px 0 4px 0; letter-spacing:1px;">ZELLE</p>
                  <p style="font-size:14px; color:#444; margin:0;">soccerbarebones@gmail.com</p>
                </td>
              </tr>

              <tr><td style="height:24px; line-height:24px;">&nbsp;</td></tr>

              <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                  See you at Waldschänke Ciders!<br>
                  The Bare Bones Crew
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""
    # send_email_ses(user.email, subject, message)
    email = EmailMessage(subject, message, to=[user.email])
    email.content_subtype = "html"
    email.send()

    return JsonResponse({'success': True})



def privacypolicy(request):
    return render(request, 'privacy-policy.html')

def datadeletion(request):
    return render(request, 'data-deletion.html')


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


def leagues_hub(request):
    return render(request, 'leagues_hub.html')


def waldy_street_league(request):
    return render(request, 'waldy_street_league.html')


@login_required
def waldy_league_register(request):
    from .context_processors import WALDY_LEAGUE_TEAM_CAP
    if LeagueTeam.paid_count('Waldy Street League') >= WALDY_LEAGUE_TEAM_CAP:
        return render(request, 'waldy_league_register.html', {'league_full': True})

    existing_agent = LeagueFreeAgent.objects.filter(player=request.user, league_name='Waldy Street League').first()

    if request.method == 'POST':
        registration_type = request.POST.get('registration_type', 'individual')

        if registration_type == 'free_agent':
            if existing_agent:
                if existing_agent.status != 'Pending':
                    messages.info(request, "You're already in the free agent pool.")
                    return redirect(request.build_absolute_uri(reverse('waldy_street_league')))
                session = create_free_agent_stripe_session(request, existing_agent)
                return redirect(session.url)
            fa_form = LeagueFreeAgentForm(request.POST)
            if fa_form.is_valid():
                agent = fa_form.save(commit=False)
                agent.player = request.user
                agent.league_name = 'Waldy Street League'
                agent.save()
                session = create_free_agent_stripe_session(request, agent)
                return redirect(session.url)
            return render(request, 'waldy_league_register.html', {
                'form': LeagueTeamCreateForm(), 'fa_form': fa_form,
                'existing_agent': existing_agent, 'selected_type': 'free_agent',
            })

        post_data = request.POST.copy()
        post_data['payment_mode'] = registration_type
        form = LeagueTeamCreateForm(post_data)
        if form.is_valid():
            payment_mode = form.cleaned_data['payment_mode']
            roster_size = form.cleaned_data.get('prepaid_roster_size')
            teammates = []

            if payment_mode == 'team_prepay':
                if not roster_size:
                    messages.error(request, "Select a roster size.")
                    return render(request, 'waldy_league_register.html', {
                        'form': form, 'fa_form': LeagueFreeAgentForm(initial={'email': request.user.email}),
                        'existing_agent': existing_agent, 'selected_type': registration_type,
                    })
                for i in range(1, int(roster_size)):
                    fn = request.POST.get(f'teammate_first_name_{i}', '').strip()
                    ln = request.POST.get(f'teammate_last_name_{i}', '').strip()
                    em = request.POST.get(f'teammate_email_{i}', '').strip()
                    if not (fn and ln and em):
                        messages.error(request, "Enter a first name, last name, and email for every teammate on your roster — each of them will get an email to confirm their spot with their own Bare Bones account.")
                        return render(request, 'waldy_league_register.html', {
                            'form': form, 'fa_form': LeagueFreeAgentForm(initial={'email': request.user.email}),
                            'existing_agent': existing_agent, 'selected_type': registration_type,
                        })
                    teammates.append((fn, ln, em))

            team = form.save(commit=False)
            team.captain = request.user
            team.league_name = 'Waldy Street League'
            if payment_mode == 'team_prepay' and roster_size:
                team.prepaid_amount = int(roster_size) * 40
            team.save()

            LeagueTeamPlayer.objects.get_or_create(
                team=team, player=request.user,
                defaults={
                    'is_captain': True,
                    'first_name': form.cleaned_data['captain_first_name'],
                    'last_name': form.cleaned_data['captain_last_name'],
                    'email': request.user.email,
                    'amount': 40 if payment_mode == 'team_prepay' else 50,
                }
            )

            for fn, ln, em in teammates:
                LeagueTeamPlayer.objects.create(
                    team=team, first_name=fn, last_name=ln, email=em,
                    claim_code=secrets.token_hex(4).upper(), amount=40,
                )

            session = create_league_team_stripe_session(request, team)
            return redirect(session.url)

        return render(request, 'waldy_league_register.html', {
            'form': form, 'fa_form': LeagueFreeAgentForm(initial={'email': request.user.email}),
            'existing_agent': existing_agent, 'selected_type': registration_type,
        })
    else:
        form = LeagueTeamCreateForm()
        fa_form = LeagueFreeAgentForm(initial={'email': request.user.email})

    return render(request, 'waldy_league_register.html', {'form': form, 'fa_form': fa_form, 'existing_agent': existing_agent})


def waldy_league_free_agent(request):
    return redirect(request.build_absolute_uri(reverse('waldy_league_register')))


def create_free_agent_stripe_session(request, agent):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"{agent.first_name} {agent.last_name} — Free Agent Spot, Waldy Street League"},
                "unit_amount": 5000,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri(reverse('free_agent_checkout_success', args=[agent.id])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )


@login_required
def free_agent_checkout_success(request, agent_id):
    agent = get_object_or_404(LeagueFreeAgent, id=agent_id, player=request.user)
    session_id = request.GET.get("session_id")
    if session_id and agent.status == 'Pending':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            agent.status = 'Paid'
            agent.payment_id = session_id
            agent.save()
            send_free_agent_signup_confirmation_email(request, agent)
    return render(request, 'waldy_league_free_agent_success.html', {'agent': agent})


def send_free_agent_signup_confirmation_email(request, agent):
    subject = "You're in the Free Agent Pool — Waldy Street League"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ YOU'RE IN THE POOL
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; padding:0 24px; line-height:24px; text-align:center;">
                    {agent.first_name}, your $50 is paid and you're on the Waldy Street League free agent list. We'll place you on a team with an open spot and email you as soon as it happens &mdash; nothing else for you to do.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>September 9th</b> &mdash; full league schedule will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [agent.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send free agent signup confirmation email")


def send_free_agent_placement_email(request, agent):
    team = agent.placed_team
    subject = f"You've Been Placed on {team.team_name} — Waldy Street League"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ YOU'VE GOT A TEAM
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; padding:0 24px; line-height:24px; text-align:center;">
                    {agent.first_name}, you've been placed on <b>{team.team_name}</b> in the Waldy Street League. Your $50 is already paid &mdash; you're all set, nothing else to do.
                    </td>
                </tr>

                <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:15px; padding:0 24px; line-height:22px; text-align:center;">
                    Introduce yourself to your new team in the <a href="https://chat.whatsapp.com/Gi75d6cjGbgBcaqgf9KqmI?s=cl&p=i&mlu=0&ilr=0" style="color:#00b8e8; font-weight:bold;">Waldy Street League WhatsApp chat &rarr;</a>
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>September 9th</b> &mdash; full league schedule will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [agent.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send free agent placement email")


def send_free_agent_added_to_roster_email(request, agent):
    team = agent.placed_team
    roster_count = team.players.filter(status='Paid').count()
    subject = f"New Player Added to {team.team_name} — Waldy Street League"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ NEW PLAYER ON YOUR ROSTER
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; padding:0 24px; line-height:24px; text-align:center;">
                    A free agent has been placed on <b>{team.team_name}</b> to fill an open roster spot &mdash; already paid, nothing owed.
                    </td>
                </tr>

                <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>

                <tr>
                    <td style="padding:0 24px; text-align:center;">
                    <table role="presentation" align="center" cellspacing="0" cellpadding="0" style="border:1.5px solid #00b8e8; border-radius:10px; background:#f5fbfd;">
                        <tr>
                            <td style="padding:14px 20px; text-align:center; font-size:15px; line-height:22px;">
                            <b>{agent.first_name} {agent.last_name}</b><br>{agent.email}
                            </td>
                        </tr>
                    </table>
                    </td>
                </tr>

                <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    🧢 <b>Roster:</b> {roster_count}/8 paid &mdash; add them to your team chat so they're looped in before opening night.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [team.captain.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send captain new-player notification email")


def create_league_team_stripe_session(request, team):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if team.payment_mode == 'team_prepay':
        amount_cents = int(team.prepaid_amount * 100)
        name = f"{team.team_name} — Team Prepay ({team.prepaid_roster_size} players)"
    else:
        amount_cents = 5000
        name = f"{team.team_name} — Individual Spot"

    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": name},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri(reverse('league_checkout_success', args=[team.id])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )


@login_required
def league_checkout_success(request, team_id):
    team = get_object_or_404(LeagueTeam, id=team_id, captain=request.user)
    session_id = request.GET.get("session_id")
    if session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            if team.payment_mode == 'team_prepay':
                if team.prepaid_status != 'Paid':
                    team.prepaid_status = 'Paid'
                    team.prepaid_payment_id = session_id
                    team.save()
                    team.players.update(status='Paid', payment_id=session_id)
                    send_league_captain_confirmation_email(request, team)
                    for teammate in team.players.filter(player__isnull=True):
                        send_league_claim_email(request, teammate)
            else:
                was_already_paid = LeagueTeamPlayer.objects.filter(team=team, player=request.user, status='Paid').exists()
                LeagueTeamPlayer.objects.filter(team=team, player=request.user).update(status='Paid', payment_id=session_id)
                if not was_already_paid:
                    send_league_captain_confirmation_email(request, team)
    return render(request, 'waldy_league_checkout_success.html', {'team': team})


def send_league_captain_confirmation_email(request, team):
    invite_link = request.build_absolute_uri(reverse('waldy_league_join', args=[team.invite_code]))

    if team.payment_mode == 'team_prepay':
        subject = f"Team Payment Confirmed — {team.team_name} is Locked In for Waldy Street League"
        teammates = team.players.filter(is_captain=False)
        names = "<br>".join(f"{p.first_name} {p.last_name}" for p in teammates)
        roster_html = ""
        if names:
            roster_html = f"""
            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
            <tr>
                <td style="font-size:15px; padding:0 24px; text-align:center; line-height:24px;">
                <b>Your Roster:</b><br>{names}
                </td>
            </tr>
            <tr><td style="height:14px; line-height:14px;">&nbsp;</td></tr>
            <tr>
                <td style="font-size:13px; padding:0 24px; text-align:center; line-height:20px; color:#555;">
                Each teammate above will get their own email to confirm their spot with a Bare Bones account &mdash; everyone needs one for game-day roster verification.
                </td>
            </tr>
            """
        body_details = f"""
            <tr>
                <td style="font-size:16px; padding:24px; text-align:center; line-height:26px;">
                💰 <b>${team.prepaid_amount} paid</b> for {team.prepaid_roster_size} players<br>
                🧢 <b>Team:</b> {team.team_name}
                </td>
            </tr>
            {roster_html}
        """
    else:
        subject = f"You're In! {team.team_name} — Waldy Street League Confirmed"
        body_details = f"""
            <tr>
                <td style="font-size:16px; padding:24px 24px 8px; text-align:center; line-height:26px;">
                💰 <b>$50 paid</b> — your spot is locked in<br>
                🧢 <b>Team:</b> {team.team_name}
                </td>
            </tr>
            <tr><td style="height:12px; line-height:12px;">&nbsp;</td></tr>
            <tr>
                <td style="padding:0 24px 8px; text-align:center;">
                <table role="presentation" align="center" cellspacing="0" cellpadding="0" style="border:1.5px solid #00b8e8; border-radius:10px; background:#f5fbfd;">
                    <tr>
                        <td style="padding:16px 20px; text-align:center; font-size:14px; line-height:22px;">
                        <b>Share this with your teammates:</b><br>
                        You need 5&ndash;8 players total (including at least 1 female player) &mdash; each person pays their own $50 spot. Send them the link BELOW!<br><br>
                        <span style="font-family:monospace; font-size:13px; color:#08070b; background:#fff; border:1px solid #ddd; border-radius:6px; padding:8px 12px; display:inline-block; margin-top:4px; word-break:break-all;">{invite_link}</span>
                        <br><br>
                        <b>Copy &amp; paste to your teammates so they can sign up!</b>
                        </td>
                    </tr>
                </table>
                </td>
            </tr>
        """

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ WALDY STREET LEAGUE CONFIRMATION
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                        You're all set! Details below.
                    </td>
                </tr>

                {body_details}

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>September 9th</b> &mdash; full league schedule will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [request.user.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send league captain confirmation email")


def send_league_claim_email(request, teammate):
    claim_link = request.build_absolute_uri(reverse('waldy_league_claim', args=[teammate.claim_code]))
    team = teammate.team
    subject = f"Confirm Your Spot on {team.team_name} — Waldy Street League"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ YOU'RE ON THE ROSTER
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; padding:0 24px; line-height:24px; text-align:center;">
                    {teammate.first_name}, your captain already paid your $40 for <b>{team.team_name}</b> in the Waldy Street League. One last step &mdash; confirm your spot with a Bare Bones account so we can verify you on game day.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="padding:0 24px; text-align:center;">
                    <a href="{claim_link}" style="color:#fdf5ed; background:linear-gradient(135deg, #00b8e8 0%, #290a44 100%); padding:12px 28px; border-radius:50px; text-decoration:none; font-weight:bold; display:inline-block;">Confirm My Spot</a>
                    </td>
                </tr>

                <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:13px; padding:0 24px; line-height:20px; text-align:center; color:#555;">
                    Log in or create a free account. New account? Activate it via email first, then click this link again &mdash; logging in alone won't confirm your spot.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>September 9th</b> &mdash; full league schedule will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [teammate.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send league claim email")


@login_required
def waldy_league_join(request, invite_code):
    team = get_object_or_404(LeagueTeam, invite_code=invite_code)
    roster_count = team.players.filter(status='Paid').count()
    already_joined = team.players.filter(player=request.user, status='Paid').exists()
    is_full = roster_count >= 8
    return render(request, 'waldy_league_join.html', {
        'team': team, 'roster_count': roster_count, 'already_joined': already_joined, 'is_full': is_full
    })


@login_required
def create_league_join_checkout_session(request, invite_code):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    team = get_object_or_404(LeagueTeam, invite_code=invite_code)
    if team.players.filter(status='Paid').count() >= 8:
        return JsonResponse({'error': "This team's roster is already full — no more spots available."}, status=400)

    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        body = {}
    first_name = body.get('first_name', '').strip()
    last_name = body.get('last_name', '').strip()
    if not (first_name and last_name):
        return JsonResponse({'error': 'First and last name are required'}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Join {team.team_name} — Waldy Street League"},
                "unit_amount": 5000,
            },
            "quantity": 1,
        }],
        mode="payment",
        metadata={"first_name": first_name, "last_name": last_name},
        success_url=request.build_absolute_uri(reverse('league_join_success', args=[invite_code])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )
    return JsonResponse({"id": session.id})


@login_required
def league_join_success(request, invite_code):
    team = get_object_or_404(LeagueTeam, invite_code=invite_code)
    session_id = request.GET.get("session_id")
    if session_id and not LeagueTeamPlayer.objects.filter(team=team, player=request.user, status='Paid').exists():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            LeagueTeamPlayer.objects.update_or_create(
                team=team, player=request.user,
                defaults={
                    'status': 'Paid', 'payment_id': session_id, 'amount': 50,
                    'first_name': session.metadata.get('first_name', ''),
                    'last_name': session.metadata.get('last_name', ''),
                    'email': request.user.email,
                }
            )
            send_league_player_join_confirmation_email(request, team)
    return render(request, 'waldy_league_join_success.html', {'team': team})


def send_league_player_join_confirmation_email(request, team):
    roster_count = team.players.filter(status='Paid').count()
    subject = f"You're In! You Joined {team.team_name} — Waldy Street League"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ WALDY STREET LEAGUE CONFIRMATION
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                        You're on the roster! Details below.
                    </td>
                </tr>

                <tr>
                    <td style="font-size:16px; padding:24px; text-align:center; line-height:26px;">
                    💰 <b>$50 paid</b> — your spot is locked in<br>
                    🧢 <b>Team:</b> {team.team_name}<br>
                    👥 <b>Roster:</b> {roster_count}/8 paid
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>September 9th</b> &mdash; full league schedule will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [request.user.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send league player join confirmation email")


def send_league_week_reminder_email(player_row):
    """
    Sends the 1-week-until-kickoff reminder to a single confirmed, paid, account-linked
    LeagueTeamPlayer. Only ever call this for rows that pass the strict audience filter
    in the `send_league_reminders` management command (status='Paid' AND player is not
    None) — this function itself does not re-check eligibility, so the caller is what
    guarantees unconfirmed/unpaid people never receive it.
    """
    team = player_row.team
    user = player_row.player
    subject = "1 Week Until Kickoff — Waldy Street League"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ 1 WEEK UNTIL KICKOFF
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; padding:0 24px; line-height:24px; text-align:center;">
                    {player_row.first_name}, the Waldy Street League kicks off in one week &mdash; <b>Wednesday, September 9th</b> at Waldschänke's parking lot, 6:30&ndash;8:30 PM.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; padding:24px; text-align:center; line-height:26px;">
                    🧢 <b>Team:</b> {team.team_name}<br>
                    👟 Flats or indoor soccer shoes only &mdash; no cleats or turf shoes<br>
                    👕 Bring a light/dark shirt for color scrimmages &mdash; Bare Bones pinnies provided
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 Full league schedule will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [user.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send league week reminder email")


@login_required
def waldy_league_claim(request, claim_code):
    slot = get_object_or_404(LeagueTeamPlayer, claim_code=claim_code)
    already_claimed_by_other = slot.player is not None and slot.player != request.user
    account_conflict = LeagueTeamPlayer.objects.filter(team=slot.team, player=request.user).exclude(id=slot.id).exists()

    if request.method == 'POST' and slot.player is None and not account_conflict:
        slot.player = request.user
        slot.claimed_at = timezone.now()
        slot.save()
        messages.success(request, "You're confirmed on the roster!")
        return redirect(request.build_absolute_uri(reverse('waldy_league_claim', args=[claim_code])))

    return render(request, 'waldy_league_claim.html', {
        'slot': slot, 'team': slot.team,
        'already_claimed_by_other': already_claimed_by_other,
        'account_conflict': account_conflict,
    })


# ============================================================
# BACKYARD 3V3 TOURNAMENT — team registration (individual pay-in
# and team prepay), mirrors the Waldy Street League flow above
# but reuses the same LeagueTeam/LeagueTeamPlayer models, scoped
# by league_name='Backyard 3v3 Tournament'. $20/player flat, no
# price discount for prepay, roster 3-6, no free agent option.
# ============================================================
TOURNAMENT_LEAGUE_NAME = 'Backyard 3v3 Tournament'
TOURNAMENT_PRICE = 20
TOURNAMENT_ROSTER_CAP = 6


@login_required
def backyard_tournament_register(request):
    if request.method == 'POST':
        registration_type = request.POST.get('registration_type', 'individual')
        post_data = request.POST.copy()
        post_data['payment_mode'] = registration_type
        form = TournamentTeamCreateForm(post_data)
        if form.is_valid():
            payment_mode = form.cleaned_data['payment_mode']
            roster_size = form.cleaned_data.get('prepaid_roster_size')
            teammates = []

            if payment_mode == 'team_prepay':
                if not roster_size:
                    messages.error(request, "Select a roster size.")
                    return render(request, 'backyard_tournament_register.html', {
                        'form': form, 'selected_type': registration_type,
                    })
                for i in range(1, int(roster_size)):
                    fn = request.POST.get(f'teammate_first_name_{i}', '').strip()
                    ln = request.POST.get(f'teammate_last_name_{i}', '').strip()
                    em = request.POST.get(f'teammate_email_{i}', '').strip()
                    if not (fn and ln and em):
                        messages.error(request, "Enter a first name, last name, and email for every teammate on your roster — each of them will get an email to confirm their spot with their own Bare Bones account.")
                        return render(request, 'backyard_tournament_register.html', {
                            'form': form, 'selected_type': registration_type,
                        })
                    teammates.append((fn, ln, em))

            team = form.save(commit=False)
            team.captain = request.user
            team.league_name = TOURNAMENT_LEAGUE_NAME
            if payment_mode == 'team_prepay' and roster_size:
                team.prepaid_amount = int(roster_size) * TOURNAMENT_PRICE
            team.save()

            LeagueTeamPlayer.objects.get_or_create(
                team=team, player=request.user,
                defaults={
                    'is_captain': True,
                    'first_name': form.cleaned_data['captain_first_name'],
                    'last_name': form.cleaned_data['captain_last_name'],
                    'email': request.user.email,
                    'amount': TOURNAMENT_PRICE,
                }
            )

            for fn, ln, em in teammates:
                LeagueTeamPlayer.objects.create(
                    team=team, first_name=fn, last_name=ln, email=em,
                    claim_code=secrets.token_hex(4).upper(), amount=TOURNAMENT_PRICE,
                )

            session = create_tournament_team_stripe_session(request, team)
            return redirect(session.url)

        return render(request, 'backyard_tournament_register.html', {
            'form': form, 'selected_type': registration_type,
        })
    else:
        form = TournamentTeamCreateForm()

    return render(request, 'backyard_tournament_register.html', {'form': form})


def create_tournament_team_stripe_session(request, team):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if team.payment_mode == 'team_prepay':
        amount_cents = int(team.prepaid_amount * 100)
        name = f"{team.team_name} — Team Prepay ({team.prepaid_roster_size} players)"
    else:
        amount_cents = TOURNAMENT_PRICE * 100
        name = f"{team.team_name} — Individual Spot"

    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": name},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri(reverse('tournament_checkout_success', args=[team.id])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )


@login_required
def tournament_checkout_success(request, team_id):
    team = get_object_or_404(LeagueTeam, id=team_id, captain=request.user)
    session_id = request.GET.get("session_id")
    if session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            if team.payment_mode == 'team_prepay':
                if team.prepaid_status != 'Paid':
                    team.prepaid_status = 'Paid'
                    team.prepaid_payment_id = session_id
                    team.save()
                    team.players.update(status='Paid', payment_id=session_id)
                    send_tournament_captain_confirmation_email(request, team)
                    for teammate in team.players.filter(player__isnull=True):
                        send_tournament_claim_email(request, teammate)
            else:
                was_already_paid = LeagueTeamPlayer.objects.filter(team=team, player=request.user, status='Paid').exists()
                LeagueTeamPlayer.objects.filter(team=team, player=request.user).update(status='Paid', payment_id=session_id)
                if not was_already_paid:
                    send_tournament_captain_confirmation_email(request, team)
    return render(request, 'backyard_tournament_checkout_success.html', {'team': team})


def send_tournament_captain_confirmation_email(request, team):
    invite_link = request.build_absolute_uri(reverse('tournament_join', args=[team.invite_code]))

    if team.payment_mode == 'team_prepay':
        subject = f"Team Payment Confirmed — {team.team_name} is Locked In for the Backyard 3v3 Tournament"
        teammates = team.players.filter(is_captain=False)
        names = "<br>".join(f"{p.first_name} {p.last_name}" for p in teammates)
        roster_html = ""
        if names:
            roster_html = f"""
            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
            <tr>
                <td style="font-size:15px; padding:0 24px; text-align:center; line-height:24px;">
                <b>Your Roster:</b><br>{names}
                </td>
            </tr>
            <tr><td style="height:14px; line-height:14px;">&nbsp;</td></tr>
            <tr>
                <td style="font-size:13px; padding:0 24px; text-align:center; line-height:20px; color:#555;">
                Each teammate above will get their own email to confirm their spot with a Bare Bones account &mdash; everyone needs one for game-day roster verification.
                </td>
            </tr>
            """
        body_details = f"""
            <tr>
                <td style="font-size:16px; padding:24px; text-align:center; line-height:26px;">
                💰 <b>${team.prepaid_amount} paid</b> for {team.prepaid_roster_size} players<br>
                🧢 <b>Team:</b> {team.team_name}
                </td>
            </tr>
            {roster_html}
        """
    else:
        subject = f"You're In! {team.team_name} — Backyard 3v3 Tournament Confirmed"
        body_details = f"""
            <tr>
                <td style="font-size:16px; padding:24px 24px 8px; text-align:center; line-height:26px;">
                💰 <b>${TOURNAMENT_PRICE} paid</b> — your spot is locked in<br>
                🧢 <b>Team:</b> {team.team_name}
                </td>
            </tr>
            <tr><td style="height:12px; line-height:12px;">&nbsp;</td></tr>
            <tr>
                <td style="padding:0 24px 8px; text-align:center;">
                <table role="presentation" align="center" cellspacing="0" cellpadding="0" style="border:1.5px solid #00b8e8; border-radius:10px; background:#f5fbfd;">
                    <tr>
                        <td style="padding:16px 20px; text-align:center; font-size:14px; line-height:22px;">
                        <b>Share this with your teammates:</b><br>
                        You need 3&ndash;6 players total, coed &mdash; each person pays their own ${TOURNAMENT_PRICE} spot. Send them the link BELOW!<br><br>
                        <span style="font-family:monospace; font-size:13px; color:#08070b; background:#fff; border:1px solid #ddd; border-radius:6px; padding:8px 12px; display:inline-block; margin-top:4px; word-break:break-all;">{invite_link}</span>
                        <br><br>
                        <b>Copy &amp; paste to your teammates so they can sign up!</b>
                        </td>
                    </tr>
                </table>
                </td>
            </tr>
        """

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ BACKYARD 3V3 TOURNAMENT CONFIRMATION
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                        You're all set! Details below.
                    </td>
                </tr>

                {body_details}

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>October 2nd</b> at Insight Soccer Training &mdash; start time and bracket will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [request.user.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send tournament captain confirmation email")


def send_tournament_claim_email(request, teammate):
    claim_link = request.build_absolute_uri(reverse('tournament_claim', args=[teammate.claim_code]))
    team = teammate.team
    subject = f"Confirm Your Spot on {team.team_name} — Backyard 3v3 Tournament"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ YOU'RE ON THE ROSTER
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; padding:0 24px; line-height:24px; text-align:center;">
                    {teammate.first_name}, your captain already paid your ${TOURNAMENT_PRICE} for <b>{team.team_name}</b> in the Backyard 3v3 Tournament. One last step &mdash; confirm your spot with a Bare Bones account so we can verify you on game day.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="padding:0 24px; text-align:center;">
                    <a href="{claim_link}" style="color:#fdf5ed; background:linear-gradient(135deg, #00b8e8 0%, #290a44 100%); padding:12px 28px; border-radius:50px; text-decoration:none; font-weight:bold; display:inline-block;">Confirm My Spot</a>
                    </td>
                </tr>

                <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:13px; padding:0 24px; line-height:20px; text-align:center; color:#555;">
                    Log in or create a free account. New account? Activate it via email first, then click this link again &mdash; logging in alone won't confirm your spot.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>October 2nd</b> at Insight Soccer Training &mdash; start time and bracket will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [teammate.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send tournament claim email")


@login_required
def tournament_join(request, invite_code):
    team = get_object_or_404(LeagueTeam, invite_code=invite_code, league_name=TOURNAMENT_LEAGUE_NAME)
    roster_count = team.players.filter(status='Paid').count()
    already_joined = team.players.filter(player=request.user, status='Paid').exists()
    is_full = roster_count >= TOURNAMENT_ROSTER_CAP
    return render(request, 'backyard_tournament_join.html', {
        'team': team, 'roster_count': roster_count, 'already_joined': already_joined, 'is_full': is_full
    })


@login_required
def create_tournament_join_checkout_session(request, invite_code):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    team = get_object_or_404(LeagueTeam, invite_code=invite_code, league_name=TOURNAMENT_LEAGUE_NAME)
    if team.players.filter(status='Paid').count() >= TOURNAMENT_ROSTER_CAP:
        return JsonResponse({'error': "This team's roster is already full — no more spots available."}, status=400)

    try:
        body = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        body = {}
    first_name = body.get('first_name', '').strip()
    last_name = body.get('last_name', '').strip()
    if not (first_name and last_name):
        return JsonResponse({'error': 'First and last name are required'}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Join {team.team_name} — Backyard 3v3 Tournament"},
                "unit_amount": TOURNAMENT_PRICE * 100,
            },
            "quantity": 1,
        }],
        mode="payment",
        metadata={"first_name": first_name, "last_name": last_name},
        success_url=request.build_absolute_uri(reverse('tournament_join_success', args=[invite_code])) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )
    return JsonResponse({"id": session.id})


@login_required
def tournament_join_success(request, invite_code):
    team = get_object_or_404(LeagueTeam, invite_code=invite_code, league_name=TOURNAMENT_LEAGUE_NAME)
    session_id = request.GET.get("session_id")
    if session_id and not LeagueTeamPlayer.objects.filter(team=team, player=request.user, status='Paid').exists():
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            LeagueTeamPlayer.objects.update_or_create(
                team=team, player=request.user,
                defaults={
                    'status': 'Paid', 'payment_id': session_id, 'amount': TOURNAMENT_PRICE,
                    'first_name': session.metadata.get('first_name', ''),
                    'last_name': session.metadata.get('last_name', ''),
                    'email': request.user.email,
                }
            )
            send_tournament_player_join_confirmation_email(request, team)
    return render(request, 'backyard_tournament_join_success.html', {'team': team})


def send_tournament_player_join_confirmation_email(request, team):
    roster_count = team.players.filter(status='Paid').count()
    subject = f"You're In! You Joined {team.team_name} — Backyard 3v3 Tournament"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
    <tr>
        <td align="center" style="padding:0;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
            <tr>
            <td align="center" style="padding:24px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

                <tr>
                    <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                    ⚽ BACKYARD 3V3 TOURNAMENT CONFIRMATION
                    </td>
                </tr>

                <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                        You're on the roster! Details below.
                    </td>
                </tr>

                <tr>
                    <td style="font-size:16px; padding:24px; text-align:center; line-height:26px;">
                    💰 <b>${TOURNAMENT_PRICE} paid</b> — your spot is locked in<br>
                    🧢 <b>Team:</b> {team.team_name}<br>
                    👥 <b>Roster:</b> {roster_count}/{TOURNAMENT_ROSTER_CAP} paid
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                    📅 See you <b>October 2nd</b> at Insight Soccer Training &mdash; start time and bracket will be posted soon.
                    </td>
                </tr>

                <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

                <tr>
                    <td style="font-size:16px; line-height:24px; text-align:center;">
                    See you on the pitch!
                    <br>
                    The Bare Bones Crew
                    </td>
                </tr>

                </table>
            </td>
            </tr>
        </table>
        </td>
    </tr>
    </table>

    </body>
    </html>
    """
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [request.user.email])
    email.content_subtype = "html"
    try:
        email.send()
    except Exception:
        logger.exception("Failed to send tournament player join confirmation email")


@login_required
def tournament_claim(request, claim_code):
    slot = get_object_or_404(LeagueTeamPlayer, claim_code=claim_code, team__league_name=TOURNAMENT_LEAGUE_NAME)
    already_claimed_by_other = slot.player is not None and slot.player != request.user
    account_conflict = LeagueTeamPlayer.objects.filter(team=slot.team, player=request.user).exclude(id=slot.id).exists()

    if request.method == 'POST' and slot.player is None and not account_conflict:
        slot.player = request.user
        slot.claimed_at = timezone.now()
        slot.save()
        messages.success(request, "You're confirmed on the roster!")
        return redirect(request.build_absolute_uri(reverse('tournament_claim', args=[claim_code])))

    return render(request, 'backyard_tournament_claim.html', {
        'slot': slot, 'team': slot.team,
        'already_claimed_by_other': already_claimed_by_other,
        'account_conflict': account_conflict,
    })


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
              request.build_absolute_uri(reverse('payment_success')) +
              f"?session_id={{CHECKOUT_SESSION_ID}}&free={free_flag}&dates={','.join(dates)}"
            ),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
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
                    <p>🕠 6:15 PM - 8:15 PM
                    <br>
                    📍 Blue Sport Stable - 1 Superior Drive, Superior
                    <br>
                    🍔 Grab 20% off food & drinks at Stable Bar & Grill
                    </p>
                    <p><em>*Continuous games, come and go as you please. Teams are formed as players arrive.</em> Bring proper footwear, water and good vibes.</p>
                    <p>See you on the courts!</p>
                    <p>The Bare Bones Crew</p>
                    """
                    # send_email_ses(request.user.email, subject, message)

                    email = EmailMessage(subject, message, to=[request.user.email])
                    email.content_subtype = "html"
                    email.send()
                    
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
            <p>🕠 6:15 PM - 8:15 PM
            <br>
            📍 Blue Sport Stable - 1 Superior Drive, Superior
            <br>
            🍔 Grab 20% off food & drinks at Stable Bar & Grill
            </p>
            <p><em>*Continuous games, come and go as you please. Teams are formed as players arrive.</em> Bring proper footwear, water and good vibes.</p>
            <p>See you on the courts!</p>
            <p>The Bare Bones Crew</p>
            """
            
            email = EmailMessage(subject, message, to=[request.user.email])
            email.content_subtype = "html"
            email.send()

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
            rsvp.event_name = "WALDSCHANKE BRUNCH BALL 3"
            rsvp.event_date = "2026-03-01"  # Update this date as needed
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
    event_date = datetime(2026, 4, 12).date()
    has_registered = OneOffEvent.objects.filter(
        user=request.user, 
        event_name='WALDSCHANKE BRUNCH BALL 5'
    ).exists()
    
    # Count paid players (excluding free spectators)
    paid_players_count = OneOffEvent.objects.filter(
        event_name='WALDSCHANKE BRUNCH BALL 5',
        status='Paid'
    ).count()
    
    player_cap_reached = paid_players_count >= 32
    
    return render(request, 'waldschanke.html', {
        'event_date': event_date,
        'has_registered': has_registered,
        'player_cap_reached': player_cap_reached,
        'paid_players_count': paid_players_count
    })


@login_required
def brighton(request):
    event_date = datetime(2026, 2, 13).date()
    has_registered = OneOffEvent.objects.filter(
        user=request.user, 
        event_name='brighton'
    ).exists()
    
    # Count paid players (excluding free spectators)
    paid_players_count = OneOffEvent.objects.filter(
        event_name='brighton',
        status='Paid'
    ).count()
    
    player_cap_reached = paid_players_count >= 70
    
    return render(request, 'brighton.html', {
        'event_date': event_date,
        'has_registered': has_registered,
        'player_cap_reached': player_cap_reached,
        'paid_players_count': paid_players_count
    })

@login_required
def create_brighton_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY 
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    user = request.user
    
    # Check if already registered
    if OneOffEvent.objects.filter(user=user, event_name='brighton').exists():
        return JsonResponse({'error': 'Already registered'}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "The Brighton Warehouse Party - Feb 13, 2026"},
                "unit_amount": 1000,  # $10.00
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri('/brighton-payment-success/') + f"?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri('/payment-cancel/'),
    )

    return JsonResponse({"id": session.id})


@login_required
def brighton_payment_success(request):
    session_id = request.GET.get("session_id")
    
    try:
        if session_id and not OneOffEvent.objects.filter(payment_id=session_id).exists():
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                OneOffEvent.objects.create(
                    user=request.user,
                    event_name='brighton',
                    event_date='2026-03-15',
                    payment_id=session_id,
                    amount=10.00,
                    status='Paid'
                )
                
                subject = "You're registered for the Warehouse Soccer Party!"
                html_message = f"""
                <!DOCTYPE html>
                <html>
                <body>
                <!-- Email content with direct image URL -->

                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
                <tr>
                    <td align="center" style="padding:0;">
                    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
                        <tr>
                        <td align="center" style="padding:24px;">
                            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">
                            
                            <!-- Header -->
                            <tr>
                                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold;">
                                🏟️⚽ 2/13 WAREHOUSE PARTY CONFIRMATION!
                                </td>
                            </tr>
                            
                            <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>
                            
                            <!-- Hook -->
                            <tr>
                                <td style="font-size:16px; line-height:24px; text-align:center;">
                                    You're ready to play! Your spot for The Brighton Warehouse Party is confirmed 🙌                </td>
                            </tr>        
                            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
                            
                            <!-- Details bullets -->
                            <tr>
                                <td style="font-size:16px;padding:24px; text-align: center; line-height:26px;">
                                    📅 <b>Friday, Feb 13th, 2026</b><br>
                                    ⏰ <b>6:30PM - 9:30PM</b><br>
                                    📍 <a href="https://maps.google.com/?q=3403+Brighton+Blvd,+Denver,+Colorado" target="_blank" style="font-family: 'Oswald', sans-serif;">The Brighton - 3403 Brighton Blvd, Denver, Colorado</a><br>
                                
                                🍔 Food + Drinks | 🎶 Music & More<br>
                                <i>*Remember proper shoes! Flats/indoor soccer shoes*</i><br><br>
                                
                                
                                </td>
                            </tr>
                            
                            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
                            
                            <tr>
                                <td style="font-size:16px; line-height:24px; text-align:center;">
                                See you on the court!
                                <br>
                                The Bare Bones Crew
                                </td>
                            </tr>
                            
                            </table>
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                </table>

                </body>
                </html>          
                """
                email = EmailMessage(
                    subject,
                    html_message,
                    settings.EMAIL_HOST_USER,
                    [request.user.email]
                )
                email.content_subtype = "html"
                email.send()
                
                messages.success(request, "Registration successful!")
                return render(request, 'brighton_payment_success.html')
            else:
                messages.error(request, "Payment was not completed.")
                return redirect('brighton')
        else:
            messages.error(request, "Invalid session or already processed.")
            return redirect('brighton')
    except stripe.error.StripeError as e:
        messages.error(request, f"Error verifying payment: {e}")
        return redirect('brighton')

@login_required
def register_brighton_spectator(request):
    if request.method == 'POST':
        user = request.user
        
        if OneOffEvent.objects.filter(user=user, event_name='brighton').exists():
            return JsonResponse({'error': 'Already registered'}, status=400)
        
        OneOffEvent.objects.create(
            user=user,
            event_name='brighton',
            event_date='2026-02-13',
            payment_id='FREE_SPECTATOR',
            amount=0.00,
            status='Free Spectator'
        )
        
        subject = "You're Going! See ya at The Brighton Warehouse Party!"
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <body>
        <p>You signed up to come watch & enjoy festivities!</p>
        <p>📅 <b>Friday, Feb 13th, 2026</b><br>
        ⏰ <b>6:30PM - 9:30PM</b><br>
        📍 <b>Event Location</b></p>
        <p>See you there!<br>The Bare Bones Crew</p>
        </body>
        </html>
        """
        email = EmailMessage(
                    subject,
                    html_message,
                    settings.EMAIL_HOST_USER,
                    [request.user.email]
                )
        email.content_subtype = "html"
        email.send()
        
        return JsonResponse({'success': True, 'redirect': '/spectator-registration-success/'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def register_free_spectator(request):
    if request.method == 'POST':
        user = request.user
        
        # Check if already registered
        if OneOffEvent.objects.filter(user=user, event_name='WALDSCHANKE BRUNCH BALL 5').exists():
            return JsonResponse({'error': 'Already registered'}, status=400)
        
        OneOffEvent.objects.create(
            user=user,
            event_name='WALDSCHANKE BRUNCH BALL 5',
            event_date='2026-04-12',
            payment_id='FREE_SPECTATOR',
            amount=0.00,
            status='Free Spectator'
        )
        
        # Send confirmation email
        subject = "You're registered as a spectator for Bare Bones Brunch Ball!"
        message = f"""
        <!DOCTYPE html>
<html>
<body>
<!-- Email content with direct image URL -->

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
  <tr>
    <td align="center" style="padding:0;">
      <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
        <tr>
          <td align="center" style="padding:24px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">
              
              <!-- Header -->
              <tr>
                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold;">
                  🏟️⚽ 5/17 EVENT CONFIRMATION!
                </td>
              </tr>
              
              <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>
              
              <!-- Hook -->
              <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                    
                    You're all set! Your spot for Bare Bones Brunch Ball at Waldschänke is confirmed 🙌  </td>
              </tr>        
              <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
              
              <!-- Details bullets -->
              <tr>
                <td style="font-size:16px; line-height:26px;">
                    📅 <b> May 17th, 2026</b><br>
                    ⏰ <b>10:30AM - 1:30PM</b><br>
                    📍 <b>Waldschänke Ciders & Coffee — Sunnyside, Denver</b><br>
                
                  🍔 Food + Drinks | 🎶 Music<br>
                  <i>*Remember proper shoes! Flats/grippy sneakers *</i><br><br>
                  
                  
                </td>
              </tr>
              
              <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
              
              <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                  See you on the court!
                <br>
                The Bare Bones Crew
                </td>
              </tr>
              
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>

</body>
</html>          
        """
        email = EmailMessage(subject, message, to=[user.email])
        email.content_subtype = "html"
        email.send()

        
        return JsonResponse({'success': True, 'redirect': '/spectator-registration-success/'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)




@login_required
@login_required
def create_waldschanke_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY 
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    data = json.loads(request.body)
    ticket_type = data.get('ticket_type', 'player')
    user = request.user
    
    # Check if already registered
    if OneOffEvent.objects.filter(user=user, event_name='WALDSCHANKE BRUNCH BALL 5').exists():
        return JsonResponse({'error': 'Already registered'}, status=400)

    # Set price based on ticket type
    prices = {
        'player': 1000,  # $10
        'player_plus': 1500,  # $15
    }

    names = {
        'player': 'Player Ticket - Bare Bones Brunch Ball 5',
        'player_plus': 'Player + Drink Ticket - Bare Bones Brunch Ball 5',
    }
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": names[ticket_type]},
                "unit_amount": prices[ticket_type],  # $15.00
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri('/waldschanke-payment-success/') + f"?session_id={{CHECKOUT_SESSION_ID}}&ticket_type={ticket_type}",
        cancel_url=request.build_absolute_uri('/payment-cancel/'),
    )

    return JsonResponse({"id": session.id})


@login_required
def waldschanke_payment_success(request):
    session_id = request.GET.get("session_id")
    ticket_type = request.GET.get("ticket_type", "player")
    
    try:
        if session_id and not OneOffEvent.objects.filter(payment_id=session_id).exists():
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                OneOffEvent.objects.create(
                    user=request.user,
                    event_name='WALDSCHANKE BRUNCH BALL 5',
                    event_date='2026-05-17',
                    ticket_type=ticket_type,
                    payment_id=session_id,
                    amount=session.amount_total / 100,
                    status='Paid'
                )
                
                # Send confirmation email
                subject = "You're registered for Bare Bones Brunch Ball!"
                message = f"""
                <!DOCTYPE html>
<html>
<body>
<!-- Email content with direct image URL -->

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
  <tr>
    <td align="center" style="padding:0;">
      <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
        <tr>
          <td align="center" style="padding:24px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">
              
              <!-- Header -->
              <tr>
                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold;">
                  🏟️⚽ 5/17 EVENT CONFIRMATION!
                </td>
              </tr>
              
              <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>
              
              <!-- Hook -->
              <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                    You're all set! Your spot for Bare Bones Brunch Ball at Wäldschanke is confirmed 🙌                </td>
              </tr>        
              <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
              
              <!-- Details bullets -->
              <tr>
                <td style="font-size:16px; line-height:26px;">
                    📅 <b>Sunday, May 17th, 2026</b><br>
                    ⏰ <b>10:30AM - 1:30PM</b><br>
                    📍 <b>Waldschänke Ciders & Coffee — Sunnyside, Denver</b><br>
                
                  🍔 Food + Drinks | 🎶 Music<br>
                  <i>*Remember proper shoes! Flats/grippy sneakers *</i><br><br>
                  
                  
                </td>
              </tr>
              
              <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
              
              <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                  See you on the court!
                <br>
                The Bare Bones Crew
                </td>
              </tr>
              
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>

</body>
</html>          
                """
                # send_email_ses(request.user.email, subject, message)
                email = EmailMessage(subject, message, to=[request.user.email])
                email.content_subtype = "html"
                email.send()

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


def spectator_registration_success(request):
    return render(request, 'spectator_registration_success.html')


def waldschanke_redirect(request):
    return redirect('world_cup_block_party')


def world_cup_block_party(request):
    return redirect('events')


@login_required
def create_wcbp_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    data = json.loads(request.body)
    session_num = data.get('session_num', '1')
    user = request.user
    if session_num == 'both':
        if OneOffEvent.objects.filter(user=user, event_name__in=['WCBP_S1_2026', 'WCBP_S2_2026', 'WCBP_BOTH_2026']).exists():
            return JsonResponse({'error': 'Already registered for a session'}, status=400)
        label = 'Both Sessions (10AM–12:30PM & 1:30PM–4:00PM)'
        unit_amount = 2000
    else:
        event_name = f'WCBP_S{session_num}_2026'
        if OneOffEvent.objects.filter(user=user, event_name=event_name).exists():
            return JsonResponse({'error': 'Already registered'}, status=400)
        label = 'Session 1 (10AM–12:30PM)' if session_num == '1' else 'Session 2 (1:30PM–4:00PM)'
        unit_amount = 1500
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f'World Cup Block Party — {label}'},
                'unit_amount': unit_amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/wcbp-payment-success/') + f'?session_id={{CHECKOUT_SESSION_ID}}&session_num={session_num}',
        cancel_url=request.build_absolute_uri('/world-cup-block-party/'),
    )
    return JsonResponse({'id': session.id})


@login_required
def wcbp_payment_success(request):
    session_id = request.GET.get('session_id')
    session_num = request.GET.get('session_num', '1')
    try:
        if session_id and not OneOffEvent.objects.filter(payment_id=session_id).exists():
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                if session_num == 'both':
                    OneOffEvent.objects.create(user=request.user, event_name='WCBP_BOTH_2026', event_date='2026-06-13', payment_id=session_id, amount=20.00, status='Paid')
                    session_label = 'Both Sessions: 10:00AM–12:30PM & 1:30PM–4:00PM'
                else:
                    OneOffEvent.objects.create(
                        user=request.user,
                        event_name=f'WCBP_S{session_num}_2026',
                        event_date='2026-06-13',
                        payment_id=session_id,
                        amount=15.00,
                        status='Paid'
                    )
                    session_label = '10:00AM – 12:30PM' if session_num == '1' else '1:30PM – 4:00PM'
                try:
                    first_name = request.user.playerprofile.full_name.split()[0]
                except Exception:
                    first_name = request.user.username
                subject = "You're registered — World Cup Block Party, June 13"
                message_html = f"""
                <!DOCTYPE html>
                <html>
                <body style="margin:0; padding:0; background:#0d1928;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0d1928; margin:0; padding:0;">
                <tr><td align="center" style="padding:40px 16px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:560px; margin:0 auto; background:linear-gradient(160deg,#0d1540 0%,#1a2060 50%,#0d1928 100%); border-radius:16px; border:1px solid rgba(255,255,255,0.1);">
                <tr><td align="center" style="padding:40px 32px;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="font-family:Arial, Helvetica, sans-serif; color:#fff;">
                <tr><td style="font-size:13px; line-height:20px; text-align:center; letter-spacing:3px; text-transform:uppercase; color:#FFD700; font-weight:bold; padding-bottom:12px;">
                Bare Bones Soccer
                </td></tr>
                <tr><td style="font-size:24px; line-height:30px; text-align:center; font-weight:bold; color:#fff; padding-bottom:6px;">
                World Cup Block Party — June 13
                </td></tr>
                <tr><td style="height:16px;">&nbsp;</td></tr>
                <tr><td style="font-size:16px; line-height:24px; text-align:center; color:rgba(255,255,255,0.85);">
                Hey {first_name}, you're confirmed!
                </td></tr>
                <tr><td style="height:24px;">&nbsp;</td></tr>
                <tr><td style="background:rgba(255,255,255,0.06); border-radius:10px; border:1px solid rgba(255,255,255,0.1); padding:20px 24px; font-size:15px; line-height:28px; color:rgba(255,255,255,0.85);">
                <b style="color:#fff;">Date:</b> Saturday, June 13th, 2026<br>
                <b style="color:#FFD700;">Session:</b> {session_label}<br>
                <b style="color:#fff;">Location:</b> Waldschänke Ciders — 4100 Jason St, Denver, CO
                </td></tr>
                <tr><td style="height:24px;">&nbsp;</td></tr>
                <tr><td style="font-size:15px; line-height:26px; text-align:center; color:rgba(255,255,255,0.7);">
                Nonstop pickup games, World Cup watch party, food and drinks. ⚽<br><br>
                Bring flat footwear and good vibes. 🎉
                </td></tr>
                <tr><td style="height:32px;">&nbsp;</td></tr>
                <tr><td style="font-size:15px; line-height:24px; text-align:center; color:#fff;">
                See you on the pitch!<br>The Bare Bones Crew
                </td></tr>
                <tr><td style="height:20px;">&nbsp;</td></tr>
                <tr><td style="font-size:13px; line-height:20px; text-align:center; font-style:italic; color:rgba(255,255,255,0.4);">
                By soccer people, for soccer people
                </td></tr>
                </table>
                </td></tr>
                </table>
                </td></tr>
                </table>
                </body>
                </html>
                """
                message_text = f"""World Cup Block Party — June 13

Hey {first_name}, you're confirmed!

Date: Saturday, June 13th, 2026
Session: {session_label}
Location: Waldschänke Ciders — 4100 Jason St, Denver, CO

Nonstop pickup games, World Cup watch party, food and drinks.
Bring flat footwear and good vibes.

See you on the pitch!
The Bare Bones Crew

By soccer people, for soccer people
"""
                try:
                    email = EmailMessage(subject, message_html, to=[request.user.email])
                    email.content_subtype = "html"
                    email.send()
                except Exception as e:
                    logger.error(f"WCBP confirmation email failed for {request.user.email}: {e}")
                messages.success(request, 'Registration successful!')
                return render(request, 'wcbp_payment_success.html', {'session_label': session_label})
            else:
                messages.error(request, 'Payment was not completed.')
                return redirect('world_cup_block_party')
        else:
            messages.error(request, 'Invalid session or already processed.')
            return redirect('world_cup_block_party')
    except stripe.error.StripeError as e:
        messages.error(request, f'Error verifying payment: {e}')
        return redirect('world_cup_block_party')


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

