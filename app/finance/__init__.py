from flask import Blueprint

bp = Blueprint('finance', __name__)

# Import models to register them with SQLAlchemy
from app.finance import models
from app.finance import routes