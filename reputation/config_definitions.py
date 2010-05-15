try:
    import json
except:
    import simplejson as json

from django_wizard.wizard import config_index as configs
from django_wizard.wizard import fixtures_index as fixtures
from django_wizard.models import ConfigOption, ConfigFixture

_CURRENT_APP = 'django_reputation'

REPUTATION_ENABLED = ConfigOption(app = _CURRENT_APP,
                                    name = 'REPUTATION_ENABLED',
                                    help_text = """If True, activates reputation controls and reputation gains/losses.""",
                                    default = json.dumps(True),
                                    available_options = json.dumps([True, False]),
                                    required = True,
                                    )

MAX_REPUTATION_GAIN_PER_DAY = ConfigOption(app = _CURRENT_APP,
                           name = 'MAX_REPUTATION_GAIN_PER_DAY',
                           help_text = """Max amount of reputation that an user can gain in a day.""",
                           default = json.dumps(250),
                           available_options = json.dumps(''),
                           required = True,
                           )

MAX_REPUTATION_LOSS_PER_DAY = ConfigOption(app = _CURRENT_APP,
                                   name = 'MAX_REPUTATION_LOSS_PER_DAY',
                                   help_text = """Max amount of reputation that an user can lose in a day.""",
                                   default = json.dumps(250),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

BASE_REPUTATION = ConfigOption(app = _CURRENT_APP,
                                   name = 'BASE_REPUTATION',
                                   help_text = """Amount of reputation that each new user starts with.""",
                                   default = json.dumps(5000),
                                   available_options = json.dumps(''),
                                   required = True,
                                   )

REPUTATION_REQUIRED_TEMPLATE = ConfigOption(app = _CURRENT_APP,
                                            name = 'REPUTATION_REQUIRED_TEMPLATE',
                                            help_text = """Template to render when user fails a reputation check.""",
                                            default = json.dumps("django_reputation/reputation_required.html"),
                                            available_options = json.dumps(''),
                                            required = True,
                                            )

configs.register(REPUTATION_ENABLED)
configs.register(MAX_REPUTATION_GAIN_PER_DAY)
configs.register(MAX_REPUTATION_LOSS_PER_DAY)
configs.register(BASE_REPUTATION)
configs.register(REPUTATION_REQUIRED_TEMPLATE)

ReputationContentFixture = ConfigFixture(help_text = 'Configure models that when modified can change a users reputation.  Example: Vote.',
                                         app_label = _CURRENT_APP,
                                         module_name = 'reputationcontent')

ReputationActionFixture = ConfigFixture(help_text = 'Configure user actions that can effect another users reputation such as voting or flagging content.',
                                         app_label = _CURRENT_APP,
                                         module_name = 'reputationaction')

PermissionFixture = ConfigFixture(help_text = 'Configure the levels of permission which grant access to the site.',
                                             app_label = _CURRENT_APP,
                                             module_name = 'permission')

fixtures.register(ReputationContentFixture)
fixtures.register(ReputationActionFixture)
fixtures.register(PermissionFixture)