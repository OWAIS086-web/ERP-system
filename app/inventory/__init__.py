from flask import Blueprint

bp = Blueprint('inventory', __name__)

# Import models to register them with SQLAlchemy
from app.inventory import models
from app.inventory import routes