from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from tinymce.models import HTMLField
import uuid
import os

def _get_file_path(instance, filename, dir):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(dir, filename)

def _get_file_path_profpic(instance, filename):
    return _get_file_path(instance, filename, 'profilepics/')

def _get_file_path_profcover(instance, filename):
    return _get_file_path(instance, filename, 'profcovers/')

def _get_file_path_nodethmb(instance, filename):
    return _get_file_path(instance, filename, 'nodethmb/')

def _get_file_path_channelcover(instance, filename):
    return _get_file_path(instance, filename, 'channelcovers/')

def _get_file_path_channelthmbs(instance, filename):
    return _get_file_path(instance, filename, 'channelthmbs/')

DISTRIBUTION_GROUP = [
    ('global', 'Global Group'),
    ('dawraty', 'Dawraty Group'),
]

class UserProfile(models.Model):
    PROFESSION_CHOICES = (
		('educator', _('educator')),
		('journalist', _('journalist')),
		('designer', _('designer')),
		('animator', _('animator')),
		('marketer', _('marketer/advertiser')),
		('student', _('student')),
		('influencer', _('influencer')),
		('programmer', _('programmer')),
		('other', _('other')),
	)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=400, verbose_name=_('Display name'))
    profession = models.CharField(max_length=40, choices=PROFESSION_CHOICES,
	                            verbose_name=_('What does best describe you?'))
    distribution_group = models.CharField(max_length=40, choices=DISTRIBUTION_GROUP,
	                            verbose_name=_('What is your distribution group'),
                                default="global")
    picture = models.ImageField(verbose_name=_('Avatar'), blank=True,
	                            upload_to=_get_file_path_profpic)
    cover_picture = models.ImageField(verbose_name=_('Cover picture'), blank=True,
	                                   upload_to=_get_file_path_profcover)
    more_info = models.TextField(verbose_name=_('More info'), blank=True)
    country = models.CharField(max_length=200,
	                            verbose_name=_('Country'),
	                            blank=True)
    city = models.CharField(max_length=200, verbose_name=_('City'), blank=True)
    region = models.CharField(max_length=200,
	                            verbose_name=_('Region/State'),
	                            blank=True)
    address = models.CharField(max_length=400,
	                            verbose_name=_('Address'),
	                            blank=True)
    phone = models.CharField(max_length=20,
	                        verbose_name=_('Phone number'),
	                        blank=True)
    website = models.CharField(max_length=400,
	                            verbose_name=_('Website'),
	                            blank=True)
    contact_email = models.CharField(max_length=100,
	                                verbose_name=_('Contact email'),
	                                blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    word = models.CharField(max_length=250)
    slug = models.CharField(max_length=250, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word

    def _get_unique_slug(self):
        slug = slugify(self.word)
        unique_slug = slug
        num = 1
        while Tag.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class NodeCategory(models.Model):
    title = models.CharField(max_length=400, verbose_name=_('Title'))
    slug = models.SlugField(max_length=400, unique=True, blank=True)
    description = models.TextField(verbose_name=_('Description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Node categories"

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while NodeCategory.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class Node(models.Model):

    INTERACTIVITY_CHOICES = (
		(0, _('No interactivity')),
		(1, _('Low interactivity')),
		(2, _('Medium interactivity')),
		(3, _('High interactivity')),
	)

    TIMELINE_CHOICES = (
    	(0, _('Blocked')),
    	(1, _('Limited to screen times')),
    	(2, _('Full')),
    )

    ACCESS_CHOICES = (
    	(0, _('Public')),
    	(1, _('Unlisted')),
    	(2, _('Private')),
        (3, _('Locked')),
    )

    ENGINE_GAMES = (
    	('game_matching', _('Matching game')),
    	('game_mapconv', _('Conversation game')),
        ('game_fillblank', _('Fill in the blanks')),
        ('game_pointnclick', _('Point&click adventure game')),
        ('game_multchoice', _('Multiple choice')),
        ('game_occupation', _('Area conquest game')),
        ('game_endlessrunner', _('Endless runner')),
        ('game_fallingcategoriser', _('Falling categoriser')),
    )

    ENGINE_BASIC = (
		('explot', _('Interactive video')),
        ('html_page', _('Info page'))
	)

    ENGINE_CHOICES = ENGINE_BASIC + ENGINE_GAMES

    NODE_INT_TYPES = (
		('game', 'game'),
		('intpiece', 'intpiece'),
		('video', 'video'),
	)

    owner = models.ForeignKey(UserProfile, blank=False, null=False,
                            on_delete=models.CASCADE)
    title = models.CharField(max_length=400, verbose_name=_('Title'))
    title_lang = models.TextField(verbose_name=_('Title in other languages'), blank=True, default="")
    slug = models.SlugField(max_length=400, unique=True, blank=True)
    tags = models.ManyToManyField(Tag,related_name='nodes')
    categories = models.ManyToManyField(NodeCategory,
                                        related_name='nodes',
                                        verbose_name=_('Categories'))
    description = HTMLField(verbose_name=_('Description'), blank=True)
    description_lang = models.TextField(verbose_name=_('Description in other languages'), blank=True, default="")
    xml_file = models.CharField(max_length=400, verbose_name=_('XML file path'))
    xml_data = models.TextField(verbose_name=_('XML data'), blank=True)
    json_data = JSONField(blank=True, default=list)
    thumbnail1 = models.ImageField(verbose_name=_('Thumbnail 1'),
                                    blank=True,
                                    upload_to=_get_file_path_nodethmb)
    thumbnail2 = models.ImageField(verbose_name=_('Thumbnail 2'),
                                    blank=True,
                                    upload_to=_get_file_path_nodethmb)
    thumbnail3 = models.ImageField(verbose_name=_('Thumbnail 3'),
                                    blank=True,
                                    upload_to=_get_file_path_nodethmb)
    thumbnail4 = models.ImageField(verbose_name=_('Thumbnail 4'),
                                    blank=True,
                                    upload_to=_get_file_path_nodethmb)
    thumbnail_video = models.FileField(verbose_name=_('Thumbnail video'),
        upload_to=_get_file_path_nodethmb, null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mov','avi','mp4','webm','mkv'])])
    likes = models.IntegerField(verbose_name=_('Likes'), default=0)
    views = models.IntegerField(verbose_name=_('Views'), default=0)
    shares = models.IntegerField(verbose_name=_('Shares'), default=0)
    interactivity = models.IntegerField(verbose_name=_('Interactivity level'),
                                        default=0, choices=INTERACTIVITY_CHOICES)
    timeline_level = models.IntegerField(verbose_name=_('Timeline level'),
                                        default=1, choices=TIMELINE_CHOICES)
    access = models.IntegerField(verbose_name=_('Access'),
                                 default=0, choices=ACCESS_CHOICES)
    tags = models.ManyToManyField(Tag,related_name='nodes',
                                verbose_name=_('Tags'))
    aspect_ratio = models.FloatField(verbose_name=_('Aspect ration'),
                                        default=1.77777)
    engine = models.CharField(max_length=40, verbose_name=_('Engine'),
                                 default='explot', choices=ENGINE_CHOICES)
    explot_version = models.FloatField(verbose_name=_('Explot version'),
                                        default=1.0)
    embedded_in = models.ManyToManyField('self',
                                        symmetrical=False,
                                        blank=True,
                                        related_name='embedded_in_nodes',
                                        verbose_name=_('Embedded in Nodes'))
    text_content = HTMLField(verbose_name=_('Text content (used mainly for HTML pages)'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Node.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class Channel(models.Model):

    LOGO_CUSTOM_CHOICES = (
		(0, _('No logo')),
		(1, _('Channel + Vizipedia logo')),
		(2, _('Only channel logo')),
	)

    owner = models.ForeignKey(UserProfile, blank=False, null=False,
                            on_delete=models.CASCADE)
    contributors = models.ManyToManyField(UserProfile,related_name='channels', blank=True)
    title = models.CharField(max_length=400)
    subtitle = models.CharField(max_length=800, blank=True)
    slug = models.CharField(max_length=400, unique=True, blank=True)
    tags = models.ManyToManyField(Tag,related_name='channels')
    description = HTMLField(verbose_name=_('Description'), blank=True)
    cover_picture = models.ImageField(verbose_name=_('Cover Picture'), blank=True,
	                            upload_to=_get_file_path_channelcover)
    thumbnail = models.ImageField(verbose_name=_('Thumbnail'), blank=True,
	                            upload_to=_get_file_path_channelthmbs)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    nodes = models.ManyToManyField(Node, related_name='channels', blank=True)
    views = models.IntegerField(verbose_name=_('Views'), default=0)
    customization_colors = JSONField(blank=True, default=dict)
    customization_fonts = JSONField(blank=True, default=dict)
    customization_logo = models.IntegerField(verbose_name=_('Logo customization level'),
                                        default=0, choices=LOGO_CUSTOM_CHOICES)
    customization_footer = HTMLField(blank=True, default="")

    def __str__(self):
        return self.title

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug + '-' + self.owner.name
        num = 1
        while Channel.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class SubChannel(models.Model):
    title = models.CharField(max_length=400)
    slug = models.CharField(max_length=450)
    channel = models.ForeignKey(Channel, blank=False, null=False,
                            on_delete=models.CASCADE)
    description = HTMLField(verbose_name=_('Description'), blank=True)
    thumbnail = models.ImageField(verbose_name=_('Thumbnail'), blank=True,
	                            upload_to=_get_file_path_channelthmbs)
    subchannels = models.ManyToManyField('self',
                                        symmetrical=False,
                                        blank=True,
                                        related_name='parent_channels',
                                        verbose_name=_('Child/subchannel'))
    nodes = models.ManyToManyField(Node, related_name='subchannels', blank=True)

    def __str__(self):
        return self.title



class FeaturedNode(models.Model):
    title = models.CharField(max_length=400, default="Node of the week", verbose_name=_('Display name'))
    node = models.ForeignKey(Node, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class LockCondition(models.Model):
    node = models.ForeignKey(Node, blank=False, null=False,
                            on_delete=models.CASCADE)
    condition = models.TextField(verbose_name=_('Condition'), blank=True)
    unlock_code = models.CharField(max_length=400, verbose_name=_('Unlock code'), blank=True)

    def __str__(self):
        return self.node.title + ': ' + self.condition


class LockUnlocked(models.Model):
    lock = models.ForeignKey(LockCondition, blank=False, null=False,
                            on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, blank=False, null=False,
                            on_delete=models.CASCADE)

    def __str__(self):
        return self.lock.node.title + ' <=> ' + self.user.name
