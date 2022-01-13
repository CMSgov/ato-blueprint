#
# Define a class to encapsulate some provider specific state and behavior
#
# May eventually move this into OIDCAuthenticate.py


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

    def get_user_attrs(self, claims: dict) -> dict:
        "Returns an dictionary of values to create/update a Blueprint User"
        username = claims[self.get_claim_name("username")]
        groups = claims.get(self.get_claim_name("groups"), [])
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
        if username in self.users:
            return True
        elif self.get_role_name("user") in groups:
            return True
        else:
            return False

    def is_admin(self, username, groups):
        if username in self.admins:
            return True
        elif self.get_role_name("admin") in groups:
            return True
        else:
            return False

    def verify(self, claims) -> bool:
        username = claims[self.get_claim_name("username")]
        groups = claims.get(self.get_claim_name("groups"), [])
        return self.is_user(username, groups) or self.is_admin(username, groups)


class OKTAOIDCProfile(OIDCProfile):

    defaults = {
        "oidc_op_jwks_endpoint": "/v1/keys",
        "oidc_op_authorization_endpoint": "/v1/authorize",
        "oidc_op_token_endpoint": "/v1/token",
        "oidc_op_user_endpoint": "/v1/userinfo",
    }


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
