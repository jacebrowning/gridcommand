import logging

from flask_api import FlaskAPI, exceptions

from . import routes
from . import services
from . import stores
from . import extensions


log = logging.getLogger('api')


def build(config):
    app = FlaskAPI(__name__)
    app.config.from_object(config)

    _configure_logging(app)

    _register_blueprints(app)
    _register_services(app)
    _register_extensions(app)

    return app


def _configure_logging(app):
    if app.config['DEBUG']:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    logging.getLogger('yorm').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.INFO)


def _register_blueprints(app):
    app.register_blueprint(routes.root.blueprint)
    app.register_blueprint(routes.games.blueprint)
    app.register_blueprint(routes.players.blueprint)
    app.register_blueprint(routes.turns.blueprint)
    app.register_blueprint(routes.moves.blueprint)


def _register_services(app):
    app.service = services.GameService(game_store=stores.GameMongoStore())
    app.service.exceptions.not_found = exceptions.NotFound
    app.service.exceptions.permission_denied = exceptions.PermissionDenied
    app.service.exceptions.missing_input = exceptions.ParseError
    app.service.exceptions.authentication_failed = \
        exceptions.AuthenticationFailed


def _register_extensions(app):
    extensions.mongo.init_app(app)
