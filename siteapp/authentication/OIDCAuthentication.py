import time
from urllib.parse import urlencode
import requests

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.crypto import get_random_string
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.middleware import SessionRefresh
from mozilla_django_oidc.utils import absolutify, add_state_and_nonce_to_session
import logging
from siteapp.models import Portfolio

logger = logging.getLogger(__name__)

class OIDCAuth(OIDCAuthenticationBackend):

    def verify_claims(self, claims):
        logger.debug("OIDCAuth.verify_claims(claims = %r)", claims)
        profile = settings.OIDC_PROFILE
        verify = profile.verify(claims)
        logger.debug("OIDCAuth.verify_claims: returning %r", verify)
        return verify        

    def filter_users_by_claims(self, claims):
        logger.debug("OIDCAuth.filter_users_by_claims(claims=%r)", claims)
        profile = settings.OIDC_PROFILE
        username = claims.get(profile.get_claim_name("username"))
        if not username:
            logger.debug("OIDCAuth.filter_users_by_claims: no username %r found",
                         username)
            return self.UserModel.objects.none()
        user = self.UserModel.objects.filter(username__iexact=username)
        logger.debug("OIDCAuth.filter_users_by_claims: found user %r for username %s",
                     user, username)
        return user

    def create_user(self, claims):
        logger.debug("OIDCAuth.create_user(claims=%r)", claims)
        profile = settings.OIDC_PROFILE
        data = profile.get_user_attrs(claims)
        logger.debug("OIDCAuth.create_user with attrs = %r", data)
        user = self.UserModel.objects.create_user(**data)
        logger.debug("OIDCAuth.create_user: created user %r", user)
        portfolio_title = f"{user.first_name} {user.last_name} ({user.username})"
        portfolio_description = f"Personal portfolio for {user.first_name} {user.last_name}"
        portfolio = Portfolio.objects.create(title=portfolio_title, description=portfolio_description)
        portfolio.assign_owner_permissions(user)
        return user

    def update_user(self, user, claims):
        logger.debug("OIDCAuth.update_user(user=%r, claims=%r)", user, claims)
        profile = settings.OIDC_PROFILE
        if not profile.sync_users:
            logger.debug("OIDCAuth.update_user: user sync disabled; ignoring")
            user = self.UserModel.objects.filter(username__iexact=data["username"])
            return user

        original_values = [getattr(user, x.name) for x in user._meta.get_fields() if hasattr(user, x.name)]
        data = profile.get_user_attrs(claims)
        logger.debug("OIDCAuth.update_user with attrs = %r", data)
        user.username = data["username"]
        user.email = data["email"]
        user.name = data["name"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.is_staff = data["is_staff"]
        user.is_superuser = user.is_staff

        new_values = [getattr(user, x.name) for x in user._meta.get_fields() if hasattr(user, x.name)]
        if new_values != original_values:
            logger.debug("OIDCAuth.update_user: attributes have changed")
            user.save()
        return user


# TODO: not clear to me that OIDCSessionRefresh is actually needed
class OIDCSessionRefresh(SessionRefresh):
    def process_request(self, request):
        if not self.is_refreshable_url(request):
            logger.debug('request is not refreshable')
            return

        expiration = request.session.get('oidc_id_token_expiration', 0)
        now = time.time()
        if expiration > now:
            # The id_token is still valid, so we don't have to do anything.
            logger.debug('id token is still valid (%s > %s)', expiration, now)
            return

        logger.debug('id token has expired')
        # The id_token has expired, so we have to re-authenticate silently.
        auth_url = self.get_settings('OIDC_OP_AUTHORIZATION_ENDPOINT')
        client_id = self.get_settings('OIDC_RP_CLIENT_ID')
        state = get_random_string(self.get_settings('OIDC_STATE_SIZE', 32))

        # Build the parameters as if we were doing a real auth handoff, except
        # we also include prompt=none.
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': absolutify(
                request,
                reverse(self.get_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                          'oidc_authentication_callback'))
            ),
            'state': state,
            'scope': self.get_settings('OIDC_RP_SCOPES', 'openid email'),
            'prompt': 'none',
        }

        if self.get_settings('OIDC_USE_NONCE', True):
            nonce = get_random_string(self.get_settings('OIDC_NONCE_SIZE', 32))
            params.update({
                'nonce': nonce
            })
        params.update(self.get_settings('OIDC_AUTH_REQUEST_EXTRA_PARAMS', {}))

        add_state_and_nonce_to_session(request, state, params)

        request.session['oidc_login_next'] = request.get_full_path()

        query = urlencode(params)
        redirect_url = '{url}?{query}'.format(url=auth_url, query=query)
        if request.is_ajax():
            # Almost all XHR request handling in client-side code struggles
            # with redirects since redirecting to a page where the user
            # is supposed to do something is extremely unlikely to work
            # in an XHR request. Make a special response for these kinds
            # of requests.
            # The use of 403 Forbidden is to match the fact that this
            # middleware doesn't really want the user in if they don't
            # refresh their session.
            response = JsonResponse({'refresh_url': redirect_url}, status=403)
            response['refresh_url'] = redirect_url
            return response
        return HttpResponseRedirect(redirect_url)
