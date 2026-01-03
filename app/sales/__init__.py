from flask import Blueprint

bp = Blueprint('sales', __name__)

# Import models to register them with SQLAlchemy
from app.sales import models
from app.sales import routes