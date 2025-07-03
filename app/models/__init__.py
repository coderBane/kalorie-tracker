from .base import Entity, AuditableEntity, SoftDeleteEntity # noqa: I001

# solve: sqlalchemy.exc.InvalidRequestError: # noqa: E501
# When initializing mapper Mapper[AppUser(app_user)], expression 'User' failed to locate a name ('User'). # noqa: E501
# If this is a class name, consider adding this relationship() to the <class 'app.models.user.AppUser'> class after both dependent classes have been defined. # noqa: E501
import app.models.auth # noqa: F401
import app.models.user # noqa: F401


__all__ = ['Entity', 'AuditableEntity', 'SoftDeleteEntity']
