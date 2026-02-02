# STATICFILES_DIRS = (
	# "/srv/www/vizlaipedia/vizlaipedia-django/vizlaipedia/static/",
# )

MEDIA_ROOT = '/fikra/fikra-django/fikra/media'
STATIC_ROOT = '/fikra/fikra-django/fikra/static'

TMPL_DIRS =  ['/fikra/fikra-django/templates']

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vizlaipedia',
        'USER': 'vizlaipedia',
        'PASSWORD': 'N0d3$MEETN0d3$',
        'HOST': '',
        'PORT': '',
    }
}

SITE_URL = 'https://fikra.games'

GRAPHICS_BATCH_UPLOAD_SOURCE_DIR = "/zzz/vizlai-batchgraphics/"
RESOURCES_DIR = "/fikra/fikra-django/fikra/media/content/"

CONTENT_PATH = "/fikra/fikra-django/fikra/media/content/"


GAME_URLS = {
    'play': {
        'game_matching': 'https://games.vizipedia.ai/play/memory-cards/demo/index.html',
        'game_mapconv': 'https://games.vizipedia.ai/play/conversations-map/game.html',
        'game_fillblank': 'https://games.vizipedia.ai/play/fill-in-the-blank/demo/index.html',
        'game_pointnclick': 'https://games.vizipedia.ai/play/point-and-click/',
		'game_multchoice': 'https://games.vizipedia.ai/play/multiple-choice/',
        'game_occupation': 'https://games.vizipedia.ai/play/occupation/',
        'game_endlessrunner': 'https://games.vizipedia.ai/play/endless-runner/',
        'game_fallingcategoriser': 'https://games.vizipedia.ai/play/falling-categoriser/',
    },
    'create': {
        'game_matching': 'https://games.vizipedia.ai/create/memory-cards/',
        'game_mapconv': 'https://games.vizipedia.ai/create/conversations-map/',
        'game_fillblank': 'https://games.vizipedia.ai/create/fill-in-the-blank/',
        'game_pointnclick': 'https://games.vizipedia.ai/create/point-and-click/',
		'game_multchoice': 'https://games.vizipedia.ai/create/multiple-choice/',
        'game_occupation': 'https://games.vizipedia.ai/create/occupation/',
        'game_endlessrunner': 'https://games.vizipedia.ai/create/endless-runner/',
        'game_fallingcategoriser': 'https://games.vizipedia.ai/create/falling-categoriser/',
    },
    'playroot': {
        'game_matching': 'https://games.vizipedia.ai/play/memory-cards/',
        'game_mapconv': 'https://games.vizipedia.ai/play/conversations-map/',
        'game_fillblank': 'https://games.vizipedia.ai/play/fill-in-the-blank/',
        'game_pointnclick': 'https://games.vizipedia.ai/play/point-and-click/',
		'game_multchoice': 'https://games.vizipedia.ai/play/multiple-choice/',
        'game_occupation': 'https://games.vizipedia.ai/play/occupation/',
        'game_endlessrunner': 'https://games.vizipedia.ai/play/endless-runner/',
        'game_fallingcategoriser': 'https://games.vizipedia.ai/play/falling-categoriser/',
    },
}

GAME_PATHS_SPEC = {
    'create': {
        'game_matching': 'vizipedia-memory-cards-game',
        'game_mapconv': 'vizipedia-conversation-game',
        'game_fillblank': 'vizipedia-fill-in-the-blank-game',
        'game_pointnclick': 'vizipedia-point-and-click-game',
		'game_multchoice': 'vizipedia-multiple-choice-game',
        'game_occupation': 'vizipedia-occupation-game',
        'game_endlessrunner': 'vizipedia-endless-runner-game',
        'game_fallingcategoriser': 'vizipedia-falling-categoriser-game',
    },
    'app': {
        'game_matching': 'memory-cards',
        'game_mapconv': 'conversations-map',
        'game_fillblank': 'fill-in-the-blank',
        'game_pointnclick': 'point-and-click',
        'game_multchoice': 'multiple-choice',
        'game_occupation': 'occupation',
        'game_endlessrunner': 'endless-runner',
        'game_fallingcategoriser': 'falling-categoriser',
    },
}

GAME_PATH_DEF = '/vizipedia-games/data/create/'

GAME_APP_ROOT = '/vizipedia-games/app/'

GAME_WEB_PLAY_ROOT = '/vizipedia-games/web/play/'

GAME_EXPORT_PATH = '/vizipedia-games/data/exports/'
