# Import every blueprint file
from verification_ui.views import general
from verification_ui.views import verification
from verification_ui.views import login


def register_blueprints(app):
    """
    Adds all blueprint objects into the app.
    """
    app.register_blueprint(general.general)
    app.register_blueprint(verification.verification, url_prefix='/verification/worklist')
    app.register_blueprint(login.authentication)

    # All done!
    app.logger.info("Blueprints registered")
