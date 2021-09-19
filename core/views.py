from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Subscriber
from .forms import SubscriberForm
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def random_number():
    return "%0.12d" % random.randint(0, 999999999999)


@csrf_exempt
def new(request):
    if request.method == "POST":
        sub = Subscriber(email=request.POST["email"], conf_num=random_number())
        sub.save()
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=sub.email,
            subject='International Holiday Newsletter Sign-Up Confirmation',
            html_content='Thank you for signing up to receive international public holiday notifications! \
                Please complete the sign-up process by \
                <a href="{}?email={}&conf_num={}"> visiting this link to \
                confirm registration</a>.'.format(request.build_absolute_uri("/confirm/"),
                                                    sub.email,
                                                    sub.conf_num))
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return render(request, "index.html", {"email": sub.email, "action": "added", "form": SubscriberForm()})
    else:
        return render(request, "index.html", {"form": SubscriberForm()})


def confirm(request):
    sub = Subscriber.objects.get(email=request.GET["email"])
    if sub.conf_num == request.GET["conf_num"]:
        sub.confirmed = True
        sub.save()
        return render(request, "index.html", {"email": sub.email, "action": "confirmed"})
    else:
        return render(request, "index.html", {"email": sub.email, "action": "denied"})


def delete(request):
    sub = Subscriber.objects.get(email=request.GET["email"])
    if sub.conf_num == request.GET["conf_num"]:
        sub.delete()
        return render(request, "index.html", {"email": sub.email, "action": "unsubscribed"})
    else:
        return render(request, "index.html", {"email": sub.email, "action": "denied"})