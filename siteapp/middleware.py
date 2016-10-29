from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse

from urllib.parse import urlsplit, urlencode

from .models import Organization

allowed_paths = None

class OrganizationSubdomainMiddleware:
    def process_request(self, request):
        global allowed_paths

        # Use a different set of routes depending on whether the request
        # is for q.govready.com, the special landing domain, or an
        # organization subdomain.

        # Get the hostname in the UA's original HTTP request. It may be
        # a HOST:PORT --- just take the HOST portion.
        request_host = request.get_host().split(":")[0]

        # When debugging, the Django runserver server uses this host.
        # But we can't do subdomains on that hostname. As a convenience,
        # redirect to "localhost".
        if settings.DEBUG and request_host == "127.0.0.1":
            return HttpResponseRedirect("http://localhost:" + request.get_port() + request.path)

        # What is our main landing domain?
        s = urlsplit(settings.SITE_ROOT_URL)
        main_landing_domain = s[1].split(":")[0]

        # Is this a request for our main landing domain?
        if request_host == main_landing_domain:
            # This is one of our recognized main domain names. We serve
            # a special set of URLs for our main domain landing pages.
            request.urlconf = 'siteapp.urls_landing'
            return None # continue with normal request processing

        # Is this a request for an organization subdomain?
        if request_host.endswith('.' + settings.ORGANIZATION_PARENT_DOMAIN):
            subdomain = request_host[:-len(settings.ORGANIZATION_PARENT_DOMAIN)-1]

            # Does this subdomain correspond with a known organization?
            org = Organization.objects.filter(subdomain=subdomain).first()
            if org:
                # Only authenticated users can see inside organizational subdomains.
                # We don't want to reveal any information about the organization.
                # Except:
                # * the log in and sign up pages must be accessible anonymously.
                # * the invitation acceptance URL must be accessible while logged in
                #   but not yet a member of the organization
                if request.path.startswith("/invitation/accept/"):
                    # Allow this through.
                    request.organization = org
                    return None

                elif request.user.is_authenticated() and org.can_read(request.user):
                    # Ok, this request is good.

                    # Set the Organiation on the request object.
                    request.organization = org

                    # Pre-load the user's settings task if the user is logged in,
                    # so that we have global access to it.
                    request.user.localize_to_org(request.organization)

                    # Continue with normal request processing.
                    return None

        # The HTTP host did not match a domain we can serve or that the user is authenticated
        # to see.

        # Log the user out if they don't have permission to see this subdomain.
        # Otherwise the login page redirects to the home page, and then we
        # get back here and redirect to the login page, infinitely.
        if request.user.is_authenticated():
            from django.contrib.auth import logout
            from django.contrib import messages
            logout(request)
            messages.add_message(request, messages.ERROR, 'You are not a member of this organization.')

        # The user isn't authenticated to see inside the organization subdomain, but
        # we have to allow them to log in, sign up, and reset their password (both
        # submitting the form and then hitting the email confirmation link). Build
        # a white list of allowed URL patterns by reversing the known URL names
        # from allauth/account/urls.py. Because account_reset_password_from_key has
        # URL parameters, turn the reverse'd URLs into regular expressions to match
        # against.
        if allowed_paths == None:
            import re
            allowed_paths = [reverse("account_login"), reverse("account_signup"),
                reverse("account_reset_password"), reverse("account_reset_password_done"), reverse("account_reset_password_from_key", kwargs={"uidb36":"aaaaaaaa", "key":"aaaaaaaa"}), reverse("account_reset_password_from_key_done")]
            allowed_paths = re.compile("|".join(("^" + re.escape(path).replace("aaaaaaaa", ".+") + "$") for path in allowed_paths))

        if allowed_paths.match(request.path):
            # Don't leak any organization information. But do render the login/signup
            # pages and allow the routes for the form POSTs from there.
            return None

        # The user is not authenticated on this domain, is logged out, and is requesting
        # a path besides login/signup. Redirect to the login route.
        return HttpResponseRedirect(reverse("account_login") + "?" + urlencode({ "next": request.path }))
