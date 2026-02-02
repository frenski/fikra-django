# Django settings for cultipass project.
# env can be local_dev, local_built, production
from .env_settings.env import env

from .env_settings.settings_common import *

if env == 'local':
	from .env_settings.settings_local import *
elif env == 'staging':
	from .env_settings.settings_staging import *
elif env == 'production':
	from .env_settings.settings_production import *
elif env == 'local_docker':
	from .env_settings.settings_local_docker import *

TEMPLATES[0]['DIRS'] = TMPL_DIRS
