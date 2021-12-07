import re
import sys

from .settings import *

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
    'htmlemailer',
    'notifications',
    'dbstorage',
    'guardian',

    'siteapp',
    'guidedmodules',
    'discussion',
    'controls',
    'system_settings',

    'loadtesting',
]
OIDC_CONFIG = environment.get("oidc", {})

# default endpoint values for different OpenID Connect providers
OIDC_PROFILES = {
    'okta': {
        "oidc_op_jwks_endpoint": "/oauth2/v1/keys",
        "oidc_op_authorization_endpoint": "/oauth2/v1/authorize",
        "oidc_op_token_endpoint": "/oauth2/v1/token",
        "oidc_op_user_endpoint": "/oauth2/v1/userinfo",
    },
    'auth0': {
        "oidc_op_jwks_endpoint": "/.well-known/jwks.json",
        "oidc_op_authorization_endpoint": "/authorize",
        "oidc_op_token_endpoint": "/oauth/token",
        "oidc_op_user_endpoint": "/userinfo",
    }
}
# https://blog.theodo.com/2021/03/okta-sso-with-django-admin/ - example for login override
if OIDC_CONFIG:
    LOGIN_ENABLED = False
    AUTHENTICATION_BACKENDS += ['siteapp.authentication.OIDCAuthentication.OIDCAuth', ]   
    OIDC_DOMAIN = OIDC_CONFIG['domain']
    BASE_URL = environment['govready-url'].replace(':443', '')  
    # User information
    USER_CRM_ID = None
    USER_EMAIL = None
    OIDC_RP_SIGN_ALGO = "RS256"

    profile = OIDC_PROFILES[OIDC_CONFIG.get('profile', 'okta')]

    def _endpoint(name: str) -> str:
        """
        Return an absolute endpoint URL.
        Use the value in the provided config, if present.
        Otherwise, use the default value from the profile.
        """
        default_endpoint = profile.get(name, None)
        endpoint = OIDC_CONFIG.get(name, default_endpoint)
        if not endpoint:
            raise ValueError(f"Missing {name} endpoint")
        if not endpoint.startswith("/"):
            raise ValueError(f"OpenID Connect {name} endpoint {endpoint} must start with a '/'")
        return OIDC_DOMAIN + endpoint
    
    OIDC_OP_JWKS_ENDPOINT = _endpoint("oidc_op_jwks_endpoint")
    OIDC_OP_AUTHORIZATION_ENDPOINT = _endpoint("oidc_op_authorization_endpoint")
    OIDC_OP_TOKEN_ENDPOINT = _endpoint("oidc_op_token_endpoint")
    OIDC_OP_USER_ENDPOINT = _endpoint("oidc_op_user_endpoint")
   
    OIDC_RP_SCOPES = "openid email profile groups"
    OIDC_RP_CLIENT_ID = OIDC_CONFIG['client_id']
    OIDC_RP_CLIENT_SECRET = OIDC_CONFIG['client_secret']
    OIDC_VERIFY_SSL = True
    LOGIN_REDIRECT_URL = f"{BASE_URL}/"
    OIDC_REDIRECT_URL = f"{BASE_URL}/oidc/callback/"
    OIDC_AUTH_REQUEST_EXTRA_PARAMS = {"redirect_uri": OIDC_REDIRECT_URL}
    LOGOUT_REDIRECT_URL = f"{BASE_URL}/logged-out"

    INSTALLED_APPS += ['mozilla_django_oidc']
    # The mozilla_django_oidc.middleware.SessionRefresh middleware will check to see if the user’s id token has expired
    # and if so, redirect to the OIDC provider’s authentication endpoint for a silent re-auth.
    # That will redirect back to the page the user was going to.
    # The length of time it takes for an id token to expire is set in settings.OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS
    # which defaults to 15 minutes.
    MIDDLEWARE += ['siteapp.authentication.OIDCAuthentication.OIDCSessionRefresh', ]

    # Mapping functionality to support via config
    OIDC_CLAIMS_MAP = OIDC_CONFIG['claims_map']
    OIDC_ROLES_MAP = OIDC_CONFIG['roles_map']
    LOGGING['loggers'].update({
        'mozilla_django_oidc': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    })
if environment.get("trust-user-authentication-headers"):
    # When this is set, the 'username' and 'email' keys hold HTTP header
    # names which control user authentication. Standard authentication
    # is disabled. Instead, user login is handled by a proxy server running
    # in front of Q. These headers are always expected to be set and trusted
    # when this setting is enabled. Per the Django Documentation (https://docs.djangoproject.com/en/dev/howto/auth-remote-user/),
    # you must be sure that your front-end web server does not permit an
    # end-user to submit a spoofed header value for these headers *as well
    # as* other headers that normalize to the same key as seen by Django.
    # Because regular authentication is disabled, before setting this setting
    # you should ensure you'll be able to log in with the proxy using the
    # username of an admin account that is already registered.
    MIDDLEWARE.append('siteapp.middleware.ProxyHeaderUserAuthenticationMiddleware') # must be after AuthenticationMiddleware but before OrganizationSubdomainMiddleware
    AUTHENTICATION_BACKENDS.remove('django.contrib.auth.backends.ModelBackend') # disable the standard login backends
    AUTHENTICATION_BACKENDS.remove('allauth.account.auth_backends.AuthenticationBackend')
    AUTHENTICATION_BACKENDS.append('siteapp.middleware.ProxyHeaderUserAuthenticationBackend') # add backend for this method
    PROXY_HEADER_AUTHENTICATION_HEADERS = environment["trust-user-authentication-headers"]
    print("Trusting authentication headers:", PROXY_HEADER_AUTHENTICATION_HEADERS)
    LOGOUT_REDIRECT_URL = "/sso-logout"
    print("Setting LOGOUT_REDIRECT_URL to", LOGOUT_REDIRECT_URL)

# PDF Generation settings
GR_PDF_GENERATOR = environment.get("gr-pdf-generator", None)
# Validate pdf generator is supported
GR_PDF_GENERATOR_SUPPORTED = ["off", "wkhtmltopdf"]
if GR_PDF_GENERATOR not in GR_PDF_GENERATOR_SUPPORTED:
    # Log error
    print("WARNING: Specified PDF generator is not supported. Setting generator to 'off'.")
    # Set pdf generator to None
    GR_PDF_GENERATOR = "off"
else:
    print("INFO: GR_PDF_GENERATOR set to {}".format(GR_PDF_GENERATOR))

# PDF Generation settings
GR_IMG_GENERATOR = environment.get("gr-img-generator", None)
# Validate img generator is supported
GR_IMG_GENERATOR_SUPPORTED = ["off", "wkhtmltopdf"]
if GR_IMG_GENERATOR not in GR_IMG_GENERATOR_SUPPORTED:
    # Log error
    print("WARNING: Specified IMG generator is not supported. Setting generator to 'off'.")
    # Set img generator to None
    GR_IMG_GENERATOR = "off"
else:
    print("INFO: GR_IMG_GENERATOR set to {}".format(GR_IMG_GENERATOR))

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'siteapp.middleware.ContentSecurityPolicyMiddleware',
    'guidedmodules.middleware.InstrumentQuestionPageLoadTimes',
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'siteapp.middleware.QTemplateContextProcessor',
]

AUTHENTICATION_BACKENDS += ['siteapp.models.DirectLoginBackend']

INTERNAL_IPS = ['127.0.0.1'] # for django_debug_toolbar

TESTING_MODE = 'test' in sys.argv # Are we running tests with test mode and debugging?
if TESTING_MODE or ENABLE_TOOLBAR == False:
    DISABLE_DJANGO_DEBUG_TOOLBAR = True
    # Prevent caching when we are testing
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

def DEBUG_TOOLBAR_SHOW_TOOLBAR_CALLBACK(r):
    # return True # Force debug toolbar to be true regardless of INTERNAL_IPS settings
    import debug_toolbar.middleware
    return debug_toolbar.middleware.show_toolbar(r) and not DISABLE_DJANGO_DEBUG_TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': DEBUG_TOOLBAR_SHOW_TOOLBAR_CALLBACK,
}

LOGIN_REDIRECT_URL = "/projects"

if (GOVREADY_URL.hostname and GOVREADY_URL.hostname != ""):
    EMAIL_DOMAIN = environment.get("email", {}).get("domain", GOVREADY_URL.hostname)
elif "host" in environment:
    EMAIL_DOMAIN = environment.get("email", {}).get("domain", environment["host"].split(":")[0])
else:
    EMAIL_DOMAIN = environment.get("email", {}).get("domain", environment["host"].split(":")[0])
    print("WARNING: host not properly defined to set EMAIL_DOMAIN")

SERVER_EMAIL = ("GovReady Q <q@%s>" % EMAIL_DOMAIN)
DEFAULT_FROM_EMAIL = SERVER_EMAIL
NOTIFICATION_FROM_EMAIL_PATTERN = "%s via GovReady Q <q@" + EMAIL_DOMAIN + ">"
NOTIFICATION_REPLY_TO_EMAIL_PATTERN = "%s <q+notification+%d+%s@" + EMAIL_DOMAIN + ">"
NOTIFICATION_REPLY_TO_EMAIL_REGEX = r"q\+notification\+(\d+)\+([a-f\d\-]+)@" + re.escape(EMAIL_DOMAIN) + ""
DEFAULT_FILE_STORAGE = 'dbstorage.storage.DatabaseStorage'
NOTIFICATIONS_USE_JSONFIELD = True # allows us to store extra data on Notification instances

GOVREADY_CMS_API_AUTH = environment.get('govready_cms_api_auth')
MAILGUN_API_KEY = environment.get('mailgun_api_key', '') # for the incoming mail route

VALIDATE_EMAIL_DELIVERABILITY = True

# Get the version of this software from the VERSION file which has up to two lines.
# The first line is a version string for display. The second line is the git commit
# hash that the build was based on. If the second line isn't present, we use git to
# get the hash of current HEAD, plus a marker if there are local modifications.
with open("VERSION") as f:
    APP_VERSION_STRING = f.readline().strip()
    APP_VERSION_COMMIT = f.readline().strip()
if not APP_VERSION_COMMIT and os.path.exists(".git"):
    import subprocess  # nosec
    APP_VERSION_COMMIT = subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"]).strip().decode("ascii")
    if subprocess.run(["/usr/bin/git", "diff-index", "--quiet", "HEAD", "--"]):
        # see https://stackoverflow.com/questions/3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes
        APP_VERSION_COMMIT += "-dirty"
