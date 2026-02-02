# To remove this when a new psycopg2 is fixed
USE_TZ = False

STATICFILES_DIRS = (
	"/Users/yanefrenski/projects/vizlai/Dev/vizlaipedia/dev/fikra-django/fikra/static/",
)

TMPL_DIRS =  ['/Users/yanefrenski/projects/vizlai/Dev/vizlaipedia/dev/fikra-django/fikra/templates']

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

SITE_URL = 'http://127.0.0.1:8000'

GRAPHICS_BATCH_UPLOAD_SOURCE_DIR = "/Users/yanefrenski/projects/vizlai/Content/GraphicsBatch/"
RESOURCES_DIR = "/Users/yanefrenski/projects/vizlai/Dev/vizlaipedia/dev/vizlaipedia-django/vizlaipedia/vizlaipedia/media/content/"

CONTENT_PATH = '/Users/yanefrenski/projects/vizlai/Dev/vizlaipedia/dev/vizlaipedia-django/vizlaipedia/vizlaipedia/media/content/'

GAME_URLS = {
    'play': {
		'game_matching': 'http://localhost/vizipedia/games/matching/demo/',
        'game_mapconv': 'https://games.vizipedia.ai/play/conversations-map/game.html',
        'game_fillblank': 'https://games.vizipedia.ai/play/fill-in-the-blank/demo/index.html',
        'game_pointnclick': 'http://localhost/vizipedia/games/vizipedia-point-and-click-game/',
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
        'game_matching': 'vizipedia-memory-cards-game',
        'game_mapconv': 'vizipedia-conversation-game',
        'game_fillblank': 'vizipedia-fill-in-the-blank-game',
        'game_pointnclick': 'vizipedia-point-and-click-game',
		'game_multchoice': 'vizipedia-multiple-choice-game',
        'game_occupation': 'vizipedia-occupation-game',
        'game_endlessrunner': 'endless-runner',
        'game_fallingcategoriser': 'falling-categoriser',
    },
}

GAME_PATH_DEF = '/Library/WebServer/Documents/vizipedia/games/'

GAME_APP_ROOT = '/Library/WebServer/Documents/vizipedia/games/'

GAME_WEB_PLAY_ROOT = '/Library/WebServer/Documents/vizipedia/games/'

GAME_EXPORT_PATH = '/Library/WebServer/Documents/vizipedia/games/exports/'

# Added by Yane to prevent issues on http (not https) logins
SESSION_COOKIE_DOMAIN = None
