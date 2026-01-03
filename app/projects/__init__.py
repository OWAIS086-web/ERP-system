from flask import Blueprint

bp = Blueprint('projects', __name__)

# Import models to register them with SQLAlchemy
from app.projects import models
from app.projects import routes