import datetime
import json
import requests
import hashlib
import hmac
import urllib
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Optional, Tuple
from math import ceil
from pprint import pprint
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.conf import settings
from django.db.models import F
from django.core import serializers
from django.utils import formats
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from nodes.models import UserProfile, Node
from .models import Newsletter, Subscribed, SubscriptionOffering, PaymentTransactionLog
from .forms import *
from nodes.views import _get_node_engine_choices
# from django.contrib.auth.forms import UserCreationForm
from humanfriendly import format_timespan
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@receiver(pre_save, sender=User)
def set_new_user_inactive(sender, instance, **kwargs):
    if instance._state.adding is True:
        instance.is_active = False

def signup_user(request):
    """
    Handle user registration using UserCreationForm
    """
    message = ''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the user and log them in
            user = form
            user.is_active = False
            user.save()
            form = None
            message = _('Registration successful! You will be notified once we have activated your account!')
    else:
        # For GET requests, create a blank form
        form = SignUpForm()

    # Render the registration template
    return render(request, 'clients/signup.html', {'form': form, 'message':message})


def dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    # Initializing the main variables
    prof = None
    nodes = None
    ads = None
    subscriptions = None
    perk_embed_allowed = False
    profile_form = None

    show_embedded = request.GET.get('show_embedded', False)
    if show_embedded == 'on':
        show_embedded = True

    # Setting the profile object
    my_profiles = UserProfile.objects.filter(user=request.user)
    if len(my_profiles) > 0:
        prof = my_profiles[0]
        # If profile exists we get the other objects
        # Setting the nodes object
        if show_embedded:
            nodes = Node.objects.filter(owner=prof).order_by('-modified_at')
        else:
            nodes = Node.objects.filter(owner=prof, embedded_in=None).order_by('-modified_at')

        for node in nodes:
            if node.engine in settings.GAME_URLS['play']:
                node.ifr_url = settings.GAME_URLS['play'][node.engine] + node.xml_file
            else:
                node.ifr_url = '%s/piece/?autoplay=true&file=%s' % (settings.SITE_URL, node.xml_file)

        subscriptions = Subscribed.objects.filter(user=prof,
            end_period__gt=datetime.datetime.today())
        perk_embed_allowed, error_perk = _validate_user_subscription_perks(
            request.user, 'embed', True)

        if request.method == 'POST':
            profile_form = ProfileForm(request.POST, request.FILES)
            if profile_form.is_valid():
                prof.name = profile_form.cleaned_data.get("name")
                prof.country = profile_form.cleaned_data.get("country")
                prof.city = profile_form.cleaned_data.get("city")
                picture = profile_form.cleaned_data.get("picture")

                # Do not delete avatar if a new one is not selected
                if picture:
                    prof.picture = picture

                try:
                    prof.save()
                    return HttpResponseRedirect(reverse('clients_dashboard'))
                except:
                    pass

        else:
            profile_form = ProfileForm(instance=prof)

    return render(request, 'clients/dashboard.html',
        {'media_url': settings.MEDIA_URL,
        'profile': prof,
        'nodes': nodes,
        'profile_form':profile_form,
        'ads': ads,
        # 'balance': balance
        'subscriptions': subscriptions,
        'show_embedded': show_embedded,
        'perk_embed_allowed':perk_embed_allowed,
        })


def _get_user_subscription(user):
    prof = None
    if not user.is_authenticated:
        return None, 'ERROR: User not logged in'
    my_profiles = UserProfile.objects.filter(user=user)
    if len(my_profiles) == 0:
        return None, "ERROR: Profile with this ID doesn't exist"
    else:
        prof = my_profiles[0]
        subscriptions = Subscribed.objects.filter(user=prof,
            end_period__gt=datetime.datetime.today())
        if len(subscriptions) == 0:
            return None, "ERROR: The user doesn't have an active plan"
        else:
            return subscriptions[0], ''


def _validate_user_subscription_perks(user, perk, thresh):
    subscr, _err = _get_user_subscription(user)
    if not subscr:
        return False, _err
    else:
        perks = subscr.offering.perks
        perks_track = subscr.perks_tracker
        if perk not in perks:
            return False, "ERROR: This feature is not available with this type of plan"
        else:
            if perk not in perks_track:
                return False, "ERROR: This feature is not available in your plan"
            else:
                if perks_track[perk] < thresh:
                    return False, "ERROR: No credits left"
                else:
                    return True, "User has access to the perk"


def _get_user_subscription_perks(user):
    subscr, _err = _get_user_subscription(user)
    if subscr:
        return subscr.perks_tracker
    else:
        return {}


def _validate_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def newsletter(request):

    output = {
        'success': False,
        'message':  ''
    }

    if request.method != 'POST':
        output['message'] = 'Wrong POST method'

    email = request.POST.get('email', None)
    subscription_type = request.POST.get('subscription_type', None)

    if email is None or subscription_type is None:
        output['message'] = 'Subscription type and/or email is missing'
    else:
        if not _validate_email(email):
            output['message'] = 'Wrong email format'
        else:
            type_list = [tp[0] for tp in Newsletter._meta.get_field('type').choices]
            if subscription_type not in type_list:
                output['message'] = 'Wrong subscription type'
            else:
                subscr = Newsletter.objects.filter(email=email,
                                                    type=subscription_type)
                if len(subscr) > 0:
                    output['message'] = 'You are already subscribed!'
                else:
                    subscr_n = Newsletter.objects.create(
                        email = email,
                        type = subscription_type
                    )
                    subscr_n.save()
                    output['success'] = True
                    output['message'] = 'Thanks for subscribing'

    return JsonResponse(output, content_type='application/json')


def get_logged_user_data(request):
    output = {
        'success': False,
        'message':  '',
        'name': None,
        'avatar': None
    }
    prof = None
    user = request.user
    if not user.is_authenticated:
        output['message'] = 'ERROR: User not logged in'
        return JsonResponse(output, content_type='application/json')
    my_profiles = UserProfile.objects.filter(user=user)
    if len(my_profiles) == 0:
        output['message'] = "ERROR: Profile with this ID doesn't exist"
        return JsonResponse(output, content_type='application/json')
    else:
        prof = my_profiles[0]
        output['message'] = "Success"
        output['success'] = True
        output['name'] = prof.name
        output['avatar'] = prof.picture.url
    return JsonResponse(output, content_type='application/json')



def dashboard_node(request, node_id):

    node = get_object_or_404(Node, pk=node_id)

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')

    # Initializing the main variables
    prof = None
    access_allowed = False
    stat_totalplayed = 0
    stat_completed = 0
    stat_timespent = 0
    stat_challengsuc = 0
    stat_rating = 0
    stat_feedback = 0

    def process_data (db_extract):
        data = []
        for item in db_extract:
            data.append({
                'date': item['day'].strftime('%Y-%m-%d'),
                'score': item['score']
            })

        # Fill in missing days with 0 views
        data_dict = {item['date']: item['score'] for item in data}
        daily_data_visit = []

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_data_visit.append({
                'date': date_str,
                'score': data_dict.get(date_str, 0)
            })
            current_date += datetime.timedelta(days=1)

        return daily_data_visit

    # Setting the profile object
    my_profiles = UserProfile.objects.filter(user=request.user)
    if len(my_profiles) > 0:
        prof = my_profiles[0]
        if node.owner == prof:
            access_allowed = True

            start_date = request.GET.get('start_date', None)
            end_date = request.GET.get('end_date', None)

            time_stat_label = None

            try:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            except:
                pass

            try:
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            except:
                pass

            if not start_date and not end_date:
                time_stat_label = _('Last 30 Days')

            # getting the usage daily data
            if not end_date:
                end_date = datetime.datetime.now().date()

            if not start_date:
                init_days = int(request.GET.get('days', 30))
                start_date = end_date - datetime.timedelta(days=init_days)

            if not time_stat_label:
                time_stat_label = "%s - %s" % (str(start_date), str(end_date))

            print (end_date)
            print (start_date)

            print (time_stat_label)


            # create main log lists with the corresponding queries
            logs_list = NodeUseLog.objects.filter (
                node=node,
                created_at__gte=start_date,
                created_at__lte=end_date
            )
            logs_list_compl = NodeUseLog.objects.filter (
                node=node,
                completed=True,
                created_at__gte=start_date,
                created_at__lte=end_date
            )

            daily_views = (
                logs_list
                .annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(score=Count('id'))
                .order_by('day')
            )

            # Aggregate completions per day
            daily_completions = (
                logs_list_compl
                .annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(score=Count('id'))
                .order_by('day')
            )

            daily_timespent = (
                logs_list
                .annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(score=Avg('usage_time'))
                .order_by('day')
            )

            daily_data_visit = process_data (daily_views)
            daily_data_complete = process_data (daily_completions)
            daily_data_time = process_data (daily_timespent)

            stat_totalplayed = logs_list.count()
            stat_completed = logs_list_compl.count()
            stat_timespent = logs_list.aggregate(Avg('usage_time'))
            if not stat_timespent['usage_time__avg']:
                stat_timespent['usage_time__avg'] = 0

            print (stat_timespent)

            for log in logs_list:
                log.usage_time_h = format_timespan(round(log.usage_time))


            # stat_totalplayed = NodeUseLog.objects.filter(node=node).count()
        engine_choices = _get_node_engine_choices()

    return render(request, 'clients/dashboard-node.html',
        {'media_url': settings.MEDIA_URL,
        'profile': prof,
        'node': node,
        'access_allowed': access_allowed,
        'engine_choices': engine_choices,
        'logs_list': logs_list,
        'stat_totalplayed': stat_totalplayed,
        'stat_completed': stat_completed,
        'stat_timespent': format_timespan(round(stat_timespent['usage_time__avg'])),
        'time_stat_label': time_stat_label,
        'stat_challengsuc': stat_challengsuc,
        'stat_rating': stat_rating,
        'stat_feedback': stat_feedback,
        'daily_data_visit':daily_data_visit,
        'daily_data_complete':daily_data_complete,
        'daily_data_time':daily_data_time
        })

def _currency_precision(currency: str) -> int:
    cur = (currency or "").upper()
    if cur in settings.CURRENCY_3DP:
        return 3
    return 2

def _format_amount(amount: Any, currency: str) -> str:
    prec = _currency_precision(currency)
    d = Decimal(str(amount))
    quant = Decimal("1").scaleb(-prec)  # 10^-prec
    d = d.quantize(quant, rounding=ROUND_HALF_UP)
    return f"{d:.{prec}f}"

def _calculate_tap_hashstring(data, secret_key):
    """
    Calculates the hashstring based on Tap.company documentation logic.
    Formula: sha256(id + amount + currency + gateway_reference + payment_reference + secret_key)
    """
    try:
        # Extract fields
        chg_id = data.get('id', '')

        currency = data.get('currency', '')

        # Amount formatting is crucial.
        # Tap expects the amount to be rounded/formatted (e.g., "10.000").
        # We verify the format matches the string sent in the JSON exactly.
        # Ref: https://developers.tap.company/docs/webhook
        amount = _format_amount(data.get("amount"), currency)

        status = data.get('status', '')

        # Access nested reference objects safely
        reference = data.get('reference', {})
        transaction = data.get('transaction', {})

        gateway_ref = reference.get('gateway', '')
        payment_ref = reference.get('payment', '')
        created = transaction.get('created', '')

        print (chg_id, amount, gateway_ref, payment_ref, status, created)

        # Concatenate string
        # Note: If any value is None/Empty, Tap usually expects it to be skipped or empty string.
        # We stick to the provided documentation order.
        # raw_string = f"{chg_id}{amount}{currency}{gateway_ref}{payment_ref}{secret_key}"

        raw_string = (
            f"x_id{chg_id}"
            f"x_amount{amount}"
            f"x_currency{currency}"
            f"x_gateway_reference{gateway_ref}"
            f"x_payment_reference{payment_ref}"
            f"x_status{status}"
            f"x_created{created}"
        )

        print(raw_string)

        # Calculate SHA256 hash
        # hash_object = hashlib.sha256(raw_string.encode('utf-8'))
        # return hash_object.hexdigest()
        digest = hmac.new(
            key=secret_key.encode("utf-8"),
            msg=raw_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return digest
    except Exception as e:
        print(f"Error calculating hash: {e}")
        return None


def plans(request):
    # if not request.user.is_authenticated:
    #     return HttpResponseRedirect('/login/')
    # my_profiles = UserProfile.objects.filter(user=request.user)
    # if len(my_profiles) > 0:
    #     prof = my_profiles[0]
    # else:
    #     return HttpResponseRedirect('/')

    return render(request, 'clients/plans.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def tap_payment(request, subscription_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    my_profiles = UserProfile.objects.filter(user=request.user)
    if len(my_profiles) > 0:
        prof = my_profiles[0]
    else:
        return HttpResponseRedirect('/')

    subscr = get_object_or_404(SubscriptionOffering, pk=subscription_id)

    url = settings.TAP_PAYMENT_URL
    secret_key = settings.TAP_PAYMENT_SECRET_KEY
    # post_url = request.build_absolute_uri(reverse('tap_payment_post', args=(subscription_id, prof.pk)))
    # redirect_url = request.build_absolute_uri(reverse('clients_dashboard'))
    post_url = urllib.parse.urljoin(settings.SITE_URL, reverse('tap_payment_post', args=(subscription_id, prof.pk)))
    redirect_url = urllib.parse.urljoin(settings.SITE_URL, reverse('clients_dashboard'))
    merchant_id = settings.TAP_PAYMENT_MERCHAND_ID

    headers = {
        "accept": "application/json",
        "lang_code": "en",
        "content-type": "application/json",
        "Authorization": "Bearer " + secret_key
    }

    payload = {
        "amount": subscr.price,
        "currency": "EUR",
        "customer_initiated": True,
        "threeDSecure": True,
        "save_card": True,
        "description": subscr.name,
        "receipt": {
            "email": False,
            "sms": False
        },
        "customer": {
            "first_name": request.user.first_name,
            "middle_name": "",
            "last_name": request.user.last_name,
            "email": request.user.email,
            "phone": {
                "country_code": 965,
                "number": 51234567
            }
        },
        "merchant": { "id": merchant_id },
        "source": { "id": "src_all" },
        "post": { "url": post_url },
        "redirect": { "url": redirect_url }
    }

    response = requests.post(url, json=payload, headers=headers)
    redirect = json.loads(response.text)
    pprint(redirect)
    print(redirect['transaction']['url'])

    return HttpResponseRedirect(redirect['transaction']['url'])


def tap_payment_recurring(request, subscribed_id):

    subscr = get_object_or_404(Subscribed, pk=subscribed_id)
    if 'provider' not in subscr.payment_data:
        err_msg = "Payment data missing"
        print (err_msg)
        return HttpResponseNotFound(err_msg)

    if subscr.payment_data['provider'] != 'tap':
        err_msg = "Wrong provider"
        print (err_msg)
        return HttpResponseNotFound("Wrong provider")

    url = settings.TAP_PAYMENT_URL
    secret_key = settings.TAP_PAYMENT_SECRET_KEY
    post_url = urllib.parse.urljoin(settings.SITE_URL, reverse('tap_payment_post', args=(subscr.offering.pk, subscr.user.pk)))
    redirect_url = urllib.parse.urljoin(settings.SITE_URL, reverse('clients_dashboard'))
    merchant_id = settings.TAP_PAYMENT_MERCHAND_ID

    headers = {
        "accept": "application/json",
        "lang_code": "en",
        "content-type": "application/json",
        "Authorization": "Bearer " + secret_key
    }

    #... fetch token for a saved card
    url_token = "https://api.tap.company/v2/tokens/"
    payload_token = {
        "saved_card": {
            "card_id": subscr.payment_data['card_id'],
            "customer_id": subscr.payment_data['customer_id']
        },
        "client_ip": "127.0.0.1"
    }

    response_token = requests.post(url_token, json=payload_token, headers=headers)

    print(response_token.text)

    tok = json.loads(response_token.text)
    print(tok['id'])

    headers = {
        "accept": "application/json",
        "lang_code": "en",
        "content-type": "application/json",
        "Authorization": "Bearer " + secret_key
    }

    payload = {
        "amount": subscr.offering.price,
        "currency": "EUR",
        "customer_initiated": True,
        "threeDSecure": True,
        "save_card": True,
        "description": subscr.offering.name,
        "receipt": {
            "email": False,
            "sms": False
        },
        "customer": {
            "first_name": subscr.user.user.first_name,
            "middle_name": "",
            "last_name": subscr.user.user.last_name,
            "email": subscr.user.user.email,
            "phone": {
                "country_code": 965,
                "number": 51234567
            }
        },
        "merchant": { "id": merchant_id },
        "source": { "id": tok['id'] },
        "post": { "url": post_url },
        "redirect": { "url": redirect_url }
    }

    response = requests.post(url, json=payload, headers=headers)
    redirect = json.loads(response.text)
    # pprint(redirect)
    # print(redirect['transaction']['url'])

    # return HttpResponseRedirect(redirect['transaction']['url'])
    return JsonResponse({"status": "success"}, status=200)

@csrf_exempt
@require_POST
def tap_payment_post(request, subscription_id, profile_id):

    print ( f"PROCESSING PAYMENT RESPONSE: {subscription_id} - {profile_id}")

    my_profiles = UserProfile.objects.filter(pk=profile_id)
    if len(my_profiles) > 0:
        prof = my_profiles[0]
    else:
        return JsonResponse({"status": "success", "error":"Profile doesn't exist"}, status=200)

    offerings = SubscriptionOffering.objects.filter(pk=subscription_id)
    if len(offerings) > 0:
        offering = offerings[0]
    else:
        return JsonResponse({"status": "success", "error":"Profile doesn't exist"}, status=200)

    transactionLog = PaymentTransactionLog.objects.create(
        user = prof,
        offering = offering,
        provider = 'tap'
    )

    try:
        raw_body = request.body.decode('utf-8')
        headers = dict(request.META)
        received_hash = headers.get('Hashstring') or headers.get('hashstring') or headers.get('HTTP_HASHSTRING')
        pprint (headers)
        transactionLog.headers = headers
        transactionLog.body = raw_body
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        transactionLog.result = "Invalid JSON"
        transactionLog.save()
        return HttpResponseBadRequest("Invalid JSON")

    calculated_hash = _calculate_tap_hashstring(payload, settings.TAP_PAYMENT_SECRET_KEY)
    is_valid = (received_hash == calculated_hash)

    if not is_valid:
        error_msg = f"Hash mismatch. Received: {received_hash}, Calculated: {calculated_hash}"
        print (error_msg)
        transactionLog.result = error_msg
        transactionLog.save()
        return JsonResponse({'error': 'Invalid hash signature'}, status=400)

    try:
        charge_id = payload.get('id')
        status = payload.get('status')
        amount = payload.get('amount')
        currency = payload.get('currency')

        customer_data = payload.get('customer', {})
        customer_id = customer_data.get('id')

        source_data = payload.get('source', {})
        card_id = None

        if 'card' in payload:
            # If card object is at root (saved card management webhooks)
            card_id = payload['card'].get('id')
        elif 'card' in source_data:
            # If card details are nested in source
            card_id = source_data['card'].get('id')
        else:
            # Fallback to source ID if it represents a card/token
            card_id = source_data.get('id')

        subscriptions = Subscribed.objects.filter(user=prof)

        pay_data = {
            'method': 'tap',
            'customer_id':customer_id,
            'card_id': card_id,
        }

        add_new = True
        if len(subscriptions) > 0:
            subs = subscriptions[0]
            if subs.offering.pk == offering.pk:
                subs.end_period=timezone.now()+relativedelta(months=1)
                subs.perks_tracker=offering.perks
                subs.payment_data = pay_data
                subs.save()
                add_new = False
            else:
                subs.delete()

        if add_new:
            new_subs = Subscribed.objects.create(
                user=prof,
                offering=offering,
                start_period=timezone.now(),
                end_period=timezone.now()+relativedelta(months=1),
                perks_tracker=offering.perks,
                payment_data=pay_data
            )
            new_subs.save()

        transactionLog.result = "success"
        transactionLog.save()
        return JsonResponse({"status": "success"}, status=200)

    except Exception as e:
        error_msg = "Error processing Tap webhook: " + str(e)
        transactionLog.result = error_msg
        transactionLog.save()
        print(error_msg)
        return JsonResponse({'error': 'Internal server error'}, status=500)
    # return JsonResponse(data, content_type='application/json')
