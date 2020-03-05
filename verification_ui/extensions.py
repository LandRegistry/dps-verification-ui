from verification_ui import config
from verification_ui.custom_extensions.cachebust_static_assets.main import CachebustStaticAssets
from verification_ui.custom_extensions.enhanced_logging.main import EnhancedLogging
from verification_ui.custom_extensions.gzip_static_assets.main import GzipStaticAssets
from verification_ui.custom_extensions.security_headers.main import SecurityHeaders
from verification_ui.custom_extensions.jinja_markdown_filter.main import JinjaMarkdownFilter
from verification_ui.custom_extensions.csrf.main import CSRF
from verification_ui.custom_extensions.content_security_policy.main import ContentSecurityPolicy
from verification_ui.custom_extensions.wtforms_helpers.main import WTFormsHelpers
from flask_login import LoginManager


# Create empty extension objects here
cachebust_static_assets = CachebustStaticAssets()
enhanced_logging = EnhancedLogging()
gzip_static_assets = GzipStaticAssets()
security_headers = SecurityHeaders()
jinja_markdown_filter = JinjaMarkdownFilter()
csrf = CSRF()
content_security_policy = ContentSecurityPolicy()
wtforms_helpers = WTFormsHelpers()
login_manager = LoginManager()


def register_extensions(app):
    """Adds any previously created extension objects into the app, and does any further setup they need."""
    enhanced_logging.init_app(app)
    security_headers.init_app(app)
    jinja_markdown_filter.init_app(app)
    csrf.init_app(app)
    content_security_policy.init_app(app)
    wtforms_helpers.init_app(app)
    login_manager.init_app(app)

    if config.STATIC_ASSETS_MODE == 'production':
        cachebust_static_assets.init_app(app)
        gzip_static_assets.init_app(app)

    # All done!
    app.logger.info("Extensions registered")
