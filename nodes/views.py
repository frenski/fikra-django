from django.shortcuts import render, render_to_response, get_object_or_404
from django.conf import settings
from .models import UserProfile, Node, NodeCategory, Tag, Channel, SubChannel, FeaturedNode, LockCondition, LockUnlocked
from django.db.models import Q, F, Count
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from datetime import timedelta, datetime
from clients.models import NodeUseLog
import os
from crawlerdetect import CrawlerDetect

def _get_logged_profile (request):
    profile_id = -1
    profile = None
    log_msg = ''
    if not request.user.is_authenticated:
        log_msg = "User not logged in!"
    else:
        profiles = UserProfile.objects.filter(user=request.user)
        if len(profiles) > 0:
            profile_id = profiles[0].pk
            profile = profiles[0]
        else:
            log_msg = "There is no profile associated with this user!"
    return profile, profile_id, log_msg

def index(request):

    return render(request, 'nodes/index.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def student(request):

    return render(request, 'nodes/student.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def business(request):

    return render(request, 'nodes/business.html',
        {
            'media_url': settings.MEDIA_URL,
        })

def individual(request):

    return render(request, 'nodes/individual.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def about(request):

    return render(request, 'nodes/about.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def privacy_policy(request):

    return render(request, 'nodes/privacy_policy.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def terms_and_conditions(request):

    return render(request, 'terms_and_conditions/about.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def support(request):

    return render(request, 'nodes/support.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def contact_us(request):

    return render(request, 'nodes/contact_us.html',
        {
            'media_url': settings.MEDIA_URL,
        })


def _get_node_engine_choices():
    engine_choices = {}
    for ec in Node._meta.get_field('engine').choices:
        engine_choices[ec[0]] = ec[1]
    return engine_choices


def _render_nodes_pages(request, sort, landing_page=False):

    template='nodes/library.html'
    page_template='nodes/node_list_page.html'

    # Requesting the categories
    categories = NodeCategory.objects.all()
    tags = Tag.objects.annotate(
        num_nodes=Count('nodes')).order_by('-num_nodes')[0:settings.HOME_MAX_TAGS]
    channels = Channel.objects.all().order_by('-views')[:settings.HOME_MAX_CHANNELS]


    print (categories)
    # Setting up the filters
    q = Q()

    filt_category = []
    filt_interactivity = []
    filt_keywords = []
    filt_type = [t[0] for t in Node.NODE_INT_TYPES]

    if not request.is_ajax() and request.method != 'POST':
        if 'filt_type' in request.session:
            del request.session['filt_type']

    if 'filt_category' in request.session:
        if request.session['filt_category']:
            filt_category = request.session['filt_category']

    if 'filt_type' in request.session:
        if request.session['filt_type']:
            filt_type = request.session['filt_type']

    if 'filt_keywords' in request.session:
        if request.session['filt_keywords']:
            filt_keywords = request.session['filt_keywords']

    if request.method == 'POST':
        if ('int_type' in request.POST):
            filt_type = request.POST.getlist('int_type')
            request.session['filt_type'] = filt_type
        if ('category' in request.POST):
            p_cat = request.POST['category']
            if "-1" in p_cat:
                filt_category = []
            else:
                filt_category = [ int(x) for x in p_cat ]
            request.session['filt_category'] = filt_category
        if ('keyword' in request.POST):
            p_key = request.POST['keyword']
            # print (p_key)
            if p_key.replace(" ", "") == "":
                filt_keywords = []
            else:
                filt_keywords = [ str(x) for x in p_key.split(" ") ]
            request.session['filt_keywords'] = filt_keywords


    q.add(Q(access=0), Q.AND)

    if len(filt_category) > 0:
        q.add(Q(categories__in=filt_category), Q.AND)

    if len(filt_type) > 0 and len(filt_type) < len(Node.NODE_INT_TYPES):
        qt = Q()
        eng_games = [ e[0] for e in Node.ENGINE_GAMES ]
        eng_basic = [ e[0] for e in Node.ENGINE_BASIC ]
        if 'game' in filt_type:
            qt.add(Q(engine__in=eng_games), Q.OR)
        if 'intpiece' in filt_type and 'video' in filt_type:
            qt.add(Q(engine__in=eng_basic), Q.AND)
        elif 'intpiece' in filt_type and 'video' not in filt_type:
            qtt = Q()
            qtt.add(Q(engine__in=eng_basic), Q.AND)
            qtt.add(Q(interactivity__gte=2), Q.AND)
            qt.add(qtt, Q.OR)
        elif 'video' in filt_type and 'intpiece' not in filt_type:
            qtt = Q()
            qtt.add(Q(engine__in=eng_basic), Q.AND)
            qtt.add(Q(interactivity__lt=2), Q.AND)
            qt.add(qtt, Q.OR)
        q.add(qt, Q.AND)

    if len(filt_keywords) > 0:
        for key in filt_keywords:
            q.add(Q(title__contains=key), Q.AND)

    # Setting up the ordering
    order = '-id'
    if sort == 'most_views':
        order = ('-views')
    if sort == 'most_likes':
        order = ('-likes')

    # Requesting the nodes
    nodes = Node.objects.all().filter(q).order_by(order);

    featured_node = None

    if request.is_ajax():
        template = page_template

    if landing_page:
        fnode = FeaturedNode.objects.all().order_by('-pk')
        if len(fnode) > 0:
            if fnode[0].node and fnode[0].node.thumbnail_video:
                featured_node = fnode[0]

    engine_choices = _get_node_engine_choices()
    max_day_new = datetime.now() - timedelta(days=7)

    return render(request, template,
        {'nodes':nodes,
        'engine_choices':engine_choices,
        'max_day_new':max_day_new,
        # 'nodes_count':nodes_count,
        'page_template': page_template,
        'categories':categories,
        'interactivities': Node.INTERACTIVITY_CHOICES,
        'int_type_filts': filt_type,
        'int_type_filts_all': Node.NODE_INT_TYPES,
        'tags': tags,
        'channels': channels,
        'filt_category':filt_category,
        'filt_interactivity':filt_interactivity,
        'sort': sort,
        'media_url':settings.MEDIA_URL,
        'filt_keywords':filt_keywords,
        'landing_page':landing_page,
        'featured_node':featured_node
        })


def nodes_list(request, sort="recent"):
    # setting the page id
    # page_id = int(page_id)
    # if page_id < 0:
    #     page_id = 1

    return _render_nodes_pages(request, sort)


def nodes_detail(request, slug=None, slug_channel=None):
    node = get_object_or_404(Node, slug=slug)
    channel = None
    if slug_channel:
        channels = Channel.objects.filter(slug=slug_channel)
        if len(channels) > 0:
            channel = channels[0]
    Node.objects.filter(pk=node.pk).update(views=F('views') + 1)
    tags = node.tags.all()
    languages = []
    language_selected = get_language().split('-')[0] # TODO: Add from default
    if request.method == 'POST':
        language_selected = request.POST['node-language']
    extra_params = {}
    if node.xml_file:
        if node.engine == 'explot':
            file_dir = node.xml_file[0:node.xml_file.rindex('/')+1]
        else:
            file_dir = node.xml_file + '/locale/'
            full_furl = node.xml_file
            if full_furl[0] == '#':
                full_furl = full_furl[1:]
                params_list = full_furl.split('&')
                for param in params_list:
                    param_t = param.split('=')
                    if len(param_t) > 1:
                        extra_params[param_t[0]] = param_t[1]
        locale_dir = settings.MEDIA_ROOT + "/content/" + file_dir + "xmllocale/"
        if os.path.exists (locale_dir):
            languages = [ dr for dr in os.listdir(locale_dir) if os.path.isdir(os.path.join(locale_dir, dr)) ]
            # languages = os.listdir(locale_dir)
    ifr_url = ''
    node_type = 'video'
    template_url = 'nodes/node-detail-video.html'
    if node.interactivity > 1:
        node_type = 'intpiece'
    if node.engine in settings.GAME_URLS['play']:
        ifr_url = settings.GAME_URLS['play'][node.engine] + node.xml_file + '&lang=' + request.LANGUAGE_CODE
        node_type = 'game'
        template_url = 'nodes/node-detail-game.html'
    elif node.engine == 'html_page':
        node_type = 'html_page'
        template_url = 'nodes/node-detail-html_page.html'

    return render(request, template_url,
        {'node':node,
        'tags':tags,
        'media_url':settings.MEDIA_URL,
        'ifr_url': ifr_url,
        'langlist': languages,
        'language_selected': language_selected,
        'node_type': node_type,
        'channel': channel
        })


def node_play(request, node_id=None):
    branding = True
    if 'branding' in request.GET:
        br = request.GET['branding']
        if br == '0' or br == 'false':
            branding = False
    node = get_object_or_404(Node, pk=node_id)
    if node.engine in settings.GAME_URLS['play']:
        ifr_url = settings.GAME_URLS['play'][node.engine] + node.xml_file + '&lang=' + request.LANGUAGE_CODE
    # recording usage
    prof, _, _ = _get_logged_profile(request)
    print (request.META['HTTP_USER_AGENT'])
    use_log_new_id = 'null'
    crawler_detect = CrawlerDetect(user_agent=request.META['HTTP_USER_AGENT'])
    if not crawler_detect.isCrawler():
        print ("not a Crawler")
        use_log_new = NodeUseLog.objects.create(user=prof, node=node, completed=False)
        use_log_new.save()
        use_log_new_id = use_log_new.pk
    return render(request, 'nodes/node-play.html',
        {
            'node':node,
            'ifr_url': ifr_url,
            'branding': branding,
            'site_url':settings.SITE_URL,
            'use_log_new_id': use_log_new_id
        })


def _clear_nodes_filter_session(request):
    if 'filt_category' in request.session:
        request.session['filt_category'] = None

    if 'filt_interactivity' in request.session:
        request.session['filt_interactivity'] = None


def library(request):
    _clear_nodes_filter_session(request)
    # return HttpResponse(settings.LOCALE_PATHS)
    return _render_nodes_pages(request, "recent", True)


def channel_detail(request, slug=None):
    channel = get_object_or_404(Channel, slug=slug)
    Channel.objects.filter(pk=channel.pk).update(views=F('views') + 1)
    nodes = channel.nodes.all().exclude(access = '2')
    subchannels = channel.subchannel_set.filter(parent_channels=None)
    naccess_request = {}
    naccess_granted = {}
    nodes_locked = nodes.filter(access='3')
    profile, profile_id, prof_err_msg = _get_logged_profile(request)
    for nl in nodes_locked:
        lock_conditions = nl.lockcondition_set.all()
        naccess_request[nl.pk] = []
        naccess_granted[nl.pk] = False
        naccess_user_granted = None

        for lc in lock_conditions:
            user_record = lc.lockunlocked_set.filter(user=profile)

            if len(user_record) == 0:
                naccess_user_granted = False
            else:
                if naccess_user_granted is None:
                    naccess_user_granted = True
        if naccess_user_granted is True:
            naccess_granted[nl.pk] = True

    contributors = channel.contributors.all()
    tags = channel.tags.all()
    engine_choices = _get_node_engine_choices()
    # nodes = [val for val in Store.attribute_answers.all() if val in wishList.attribute_answers]
    return render(request, 'nodes/channel-detail.html',
        {'channel':channel,
         'subchannels':subchannels,
         'nodes':nodes,
         'naccess_request': naccess_request,
         'naccess_granted': naccess_granted,
         'profile': profile,
         'profile_id':profile_id,
         'engine_choices':engine_choices,
         'contributors':contributors,
         'tags':tags,
         'media_url':settings.MEDIA_URL,
         })

def subchannel_detail(request, slug_channel=None, slug_subchannel=None):
    channel = get_object_or_404(Channel, slug=slug_channel)
    subchannel = get_object_or_404(SubChannel, slug=slug_subchannel)
    nodes = subchannel.nodes.all().exclude(access = '2')
    child_subchannels = subchannel.subchannels.all()
    parent_channels = subchannel.parent_channels.all()
    naccess_request = {}
    naccess_granted = {}
    engine_choices = _get_node_engine_choices()
    profile, profile_id, prof_err_msg = _get_logged_profile(request)
    return render(request, 'nodes/channel-sub-detail.html',
        {'channel':channel,
         'subchannel':subchannel,
         'subchannels':child_subchannels,
         'nodes':nodes,
         'naccess_request': naccess_request,
         'naccess_granted': naccess_granted,
         'profile': profile,
         'profile_id':profile_id,
         'engine_choices':engine_choices,
         # 'contributors':contributors,
         # 'tags':tags,
         'media_url':settings.MEDIA_URL,
         })

def channels_list(request, page_id=1):
    channels = Channel.objects.all()
    channels_paginated = Paginator(channels, settings.NODE_ITEMS_PER_PAGE)

    try:
        channels = channels_paginated.page(page_id)
    except PageNotAnInteger:
        return HttpResponseRedirect('/channels/1')
    except EmptyPage:
        return HttpResponseRedirect(
                '/channels/'+str(nodes_paginated.num_pages))

    channels_count = \
        _('%(s)s to %(e)s of total %(t)s)') \
        % {'s':channels.start_index(),
            'e': channels.end_index(),
            't': channels.count,}
    return render(request, 'nodes/channels-list.html',
        {'channels':channels,
         'channels_count': channels_count,
         'media_url':settings.MEDIA_URL,
         })
