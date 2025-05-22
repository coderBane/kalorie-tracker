from app.core.settings import app_settings
from app.database import DatabaseContext


app_dbcontext = DatabaseContext(str(app_settings.DB_DSN))
