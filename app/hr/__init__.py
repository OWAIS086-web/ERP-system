from flask import Blueprint

bp = Blueprint('hr', __name__)

# Import models to register them with SQLAlchemy
from app.hr import models
from app.hr import routes