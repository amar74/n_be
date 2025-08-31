__all__ = [
    "User",
    "Organization",
    "Address",
    "Contact",
    "Account",
    "Invite",
]

# Avoid importing models at module import time to prevent circular imports.
# Importing these symbols lazily keeps `app.models` usable for type hints without side effects.
def __getattr__(name):
    if name == "User":
        from .user import User as _User
        return _User
    if name == "Organization":
        from .organization import Organization as _Organization
        return _Organization
    if name == "Address":
        from .address import Address as _Address
        return _Address
    if name == "Contact":
        from .contact import Contact as _Contact
        return _Contact
    if name == "Account":
        from .account import Account as _Account
        return _Account
    if name == "Invite":
        from .invite import Invite as _Invite
        return _Invite
    raise AttributeError(name)
