# website/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import current_user, LoginManager


db = SQLAlchemy()

login_manager = LoginManager()

class RoleBasedCSRFProtect(CSRFProtect):
    def validate_csrf(self, data, secret_key=None, time_limit=None):
        # Role-based time limits 
        if current_user.is_authenticated:
            if current_user.role == 'parent':
                time_limit = 1800
            else :
                time_limit = 10800
                
        return super().validate_csrf(data, secret_key, time_limit)     

csrf = RoleBasedCSRFProtect()