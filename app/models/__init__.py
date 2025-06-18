from .base import Entity, AuditableEntity, SoftDeleteEntity

# solve: sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[AppUser(app_user)], expression 'User' failed to locate a name ('User'). If this is a class name, consider adding this relationship() to the <class 'app.models.user.AppUser'> class after both dependent classes have been defined.
import app.models.auth as auth
import app.models.user as user


__all__ = ['Entity', 'AuditableEntity', 'SoftDeleteEntity']
