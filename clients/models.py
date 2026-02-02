import uuid
import os
from shutil import copyfile
from xml.dom.minidom import parse, parseString
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.text import slugify
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from tinymce.models import HTMLField


PAYMENT_PROVIDERS = [
    ('tap', 'Tap'),
]

def _get_file_path(instance, filename, dir):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(dir, filename)

def _get_file_path_adpositionthmb(instance, filename):
    return _get_file_path(instance, filename, 'adpositionthmbs/')

def _get_file_path_adcampaignpic(instance, filename):
    return _get_file_path(instance, filename, 'adcampaignpics/')


class SubscriptionOffering(models.Model):

    name = models.CharField(max_length=400,
    	                    verbose_name=_('Offering name'),
    	                    blank=False)
    access_requirement = models.CharField(max_length=100,
        	                verbose_name=_('Access requirement'),
        	                blank=True,
                            null=False,
                            default=None)
    access_requirement_description = HTMLField(
                            verbose_name=_('Access requirement description'),
                            blank=True)
    price = models.FloatField(default=0)
    perks = JSONField(blank=True, default=dict)

    def __str__(self):
        return self.name


class Subscribed(models.Model):

    user = models.OneToOneField('nodes.UserProfile', blank=False, null=False,
                            on_delete=models.CASCADE)
    offering = models.ForeignKey(SubscriptionOffering, on_delete=models.CASCADE,
                            null=False, blank=False)
    perks_tracker = JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    start_period = models.DateTimeField(blank=False, null=False)
    end_period = models.DateTimeField(blank=False, null=False)
    payment_data = JSONField(blank=True, default=dict)

    def __str__(self):
        return self.user.name + " -> " + self.offering.name

    def save(self, *args, **kwargs):
        if not self.perks_tracker:
            self.perks_tracker = self.offering.perks
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _("Subscribed profiles")


class Newsletter(models.Model):

    TYPE_CHOICES = (
    	('waitlist_game_wizzard_beta', _('Waitlist for game wizzard beta')),
    	('waitlist_video_wizzard_beta', _('Waitlist for video wizzard beta')),
    )

    email = models.CharField(max_length=100,
	                         verbose_name=_('Email address'),
	                         blank=False)
    type = models.CharField(max_length=40, choices=TYPE_CHOICES,
                            verbose_name=_('Subscription Type'),
                            blank=False)

    def __str__(self):
        return self.email + " -> " + self.type


class NodeUseLog(models.Model):
    user = models.ForeignKey('nodes.UserProfile', blank=True, null=True,
                                on_delete=models.CASCADE)

    node = models.ForeignKey('nodes.Node', on_delete=models.CASCADE,
                                null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    usage_time = models.FloatField(default=0)

    completed = models.BooleanField(default=False, blank=False, null=False)
    tracking_data = JSONField(blank=True, default=dict)

    def __str__(self):
        username = 'Anonymous'
        if self.user is not None:
            username = self.user.name
        return username + " -> " + self.node.title


class PaymentTransactionLog(models.Model):
    user = models.ForeignKey('nodes.UserProfile', blank=False, null=False,
                            on_delete=models.CASCADE)
    offering = models.ForeignKey(SubscriptionOffering, on_delete=models.CASCADE,
                            null=False, blank=False)
    provider = models.CharField(max_length=40, choices=PAYMENT_PROVIDERS,
	                            verbose_name=_('What is the payment provider'),
                                default="tap")
    headers = models.TextField(default="")
    body = models.TextField(default="")
    result = models.CharField(default="", max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + " -> " + self.offering.name
