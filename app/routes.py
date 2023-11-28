from flask import Blueprint, request
from .models import get_session_list
from .services import trainWord2Vec, getListCodeProductView, getListCodeProductSimilar

bp = Blueprint("app", __name__)


@bp.route("/")
def index():
    return get_session_list()


@bp.route("/train-word2vec/", methods=["POST"])
def handle_post_request():
    data = request.get_json()
    return trainWord2Vec(data)

@bp.route("/get-suggest/", methods=["POST"])
def get_suggest():
    data = request.get_json()
    return getListCodeProductView(data)


@bp.route("/get-similar/", methods=["POST"])
def get_similar():
    data = request.get_json()
    return getListCodeProductSimilar(data)
