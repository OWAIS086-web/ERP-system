from flask import Blueprint

bp = Blueprint('procurement', __name__)

# Import models to register them with SQLAlchemy
from app.procurement import models
from app.procurement import routes