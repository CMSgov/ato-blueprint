#
# Define a class to encapsulate some provider specific state and behavior
#
# May eventually move this into OIDCAuthenticate.py

from itertools import groupby
from typing import List
import logging


logger = logging.getLogger(__name__)
class OIDCProfile:

    defaults = {}

    def __init__(self, config: dict):
        """
        `config` should be the value of the `oidc` attribute from
        the application config in environment.json.
        """
        self.config = config
        self.domain = config["domain"]
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.claims_map = config["claims_map"]
        self.roles_map = config["roles_map"]
        self.scopes = "openid email profile"
        # WARNING: next three lines are "hacks" that may be
        # ok to use in a test environment, but probably don't
        # want this near production
        self.admins = config.get("admins", [])
        self.users = config.get("users", [])
        self.sync_users = config.get("sync_users", True)

    def get_endpoint(self, name: str) -> str:
        default_endpoint = self.defaults.get(name, None)
        endpoint = self.config.get(name, default_endpoint)
        if not endpoint:
            raise ValueError(f"OpenID Connect missing {name} endpoint")
        if not endpoint.startswith("/"):
            raise ValueError(
                f"OpenID Connect {name} endpoint {endpoint} must start with a '/'"
            )
        return self.domain + endpoint

    def get_claim_name(self, name: str) -> str:
        return self.claims_map.get(name)

    def get_role_name(self, name: str) -> str:
        return self.roles_map.get(name)

    def get_groups_from_claims(self, claims: dict) -> List[str]:
        return claims.get(self.get_claim_name("groups"), [])

    def get_user_attrs(self, claims: dict) -> dict:
        "Returns an dictionary of values to create/update a Blueprint User"
        username = claims[self.get_claim_name("username")]
        groups = self.get_groups_from_claims(claims)

        attrs = {
            "email": claims[self.get_claim_name("email")],
            "name": claims[self.get_claim_name("full_name")],
            "first_name": claims[self.get_claim_name("first_name")],
            "last_name": claims[self.get_claim_name("last_name")],
            "username": username,
            "is_staff": self.is_admin(username, groups),
        }
        return attrs

    def is_user(self, username, groups):
        user = False
        if username in self.users:
            user = True
        else:
            user_role = self.get_role_name("user")
            if user_role and user_role in groups:
                user = True
        logger.debug("OIDCProfile.is_user(username=%r, groups=%r) => %r",
                     username, groups, user)
        return user
        
    def is_admin(self, username, groups):
        admin = False
        if username in self.admins:
            admin = True
        else:
            admin_role = self.get_role_name("admin")
            if admin_role and admin_role in groups:
                admin = True

        logger.debug("OIDCProfile.is_admin(username=%r, groups=%r) => %r",
                     username, groups, admin)
        return admin

    def verify(self, claims) -> bool:
        username = claims[self.get_claim_name("username")]
        groups = claims.get(self.get_claim_name("groups"), [])
        return self.is_user(username, groups) or self.is_admin(username, groups)


# utilities for dealing with job code claims

# TODO: just put this together very quickly, could probably be
# improved

def _labeler(cns: List[bool]) -> List[int]:
    """
    Generator that takes a list of boolean values that correspond to
    a list of DN parts where "true"
    values indicate a change in item, and
    produces a corresponding list of labels (integers)
    """
    label = 0
    for n in cns:
        if n:
            label += 1
        yield label


def parse_jobcode_claim(s: str) -> List[str]:
    """
    Given a jobcode claim, return a list of jobcodes (FQDNS).
    The tricky bit is that a jobcode claim could have more than
    one job code, and the job codes are separated by commas.
    Unfortunately, there are embedded commas in the FQDNs, so
    this is not that easy to parse.  The idea here is to break up
    the claim list by splitting on commas, and then put it back together
    using the "cn=xxx" pieces as clues to where DNs start.

    This has NOT BEEN TESTED with real data from the IDM
    because we haven't been able to get more than one job code
    back in a claim, but this should agree with what the IDM
    folks have told us.
    """

    # split the list of jobcodes (as FQDNs) into parts, and then
    # find all the "cn=" parts
    parts = s.split(',')
    cns = [part.startswith('cn=') for part in parts]

    # label and group the parts
    groups = groupby(zip(parts, _labeler(cns)),
                     key=lambda labeled_part: labeled_part[1])

    # put the parts back together by group
    return [
        ','.join(map(lambda part: part[0], parts))
        for parts in [list(items) for _, items in groups]
    ]

class OKTAOIDCProfile(OIDCProfile):

    defaults = {
        "oidc_op_jwks_endpoint": "/v1/keys",
        "oidc_op_authorization_endpoint": "/v1/authorize",
        "oidc_op_token_endpoint": "/v1/token",
        "oidc_op_user_endpoint": "/v1/userinfo",
    }

    # override get_groups_from_claims to properly parse
    # job codes ... this is relatively untested!

    def get_groups_from_claims(self, claims: dict) -> List[str]:
        unparsed = claims.get(self.get_claim_name("groups"), "")
        groups = parse_jobcode_claim(unparsed)
        logger.debug("OKTAOIDCProfile.get_group_from_claims(claims=%r) => %r",
                     claims, groups)
        return groups
class AUTH0OIDCProfile(OIDCProfile):

    defaults = {
        "oidc_op_jwks_endpoint": "/.well-known/jwks.json",
        "oidc_op_authorization_endpoint": "/authorize",
        "oidc_op_token_endpoint": "/oauth/token",
        "oidc_op_user_endpoint": "/userinfo",
    }


def get_profile(config: dict) -> OIDCProfile:
    "Given an OIDC config, return an OIDCProfile"
    profile_name = config.get("profile")
    if profile_name == "auth0":
        return AUTH0OIDCProfile(config)
    else:
        return OKTAOIDCProfile(config)
