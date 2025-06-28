from __future__ import annotations

import importlib
import os
import pkgutil
try:  # Allow importing this module without Flask installed
    from flask import Flask, Blueprint
except Exception:  # pragma: no cover - used only in minimal test envs
    Flask = object  # type: ignore
    Blueprint = object  # type: ignore
from config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    """Application factory."""
    # Determine paths to static and template folders relative to this file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    static_folder = os.path.join(base_dir, "static")
    template_folder = os.path.join(base_dir, "templates")

    app = Flask(__name__, static_folder=static_folder, template_folder=template_folder)
    app.config.from_object(config_class)
    # Expose Celery settings for extensions that rely on Flask config
    app.config.setdefault("CELERY_BROKER_URL", config_class.BROKER_URL)
    app.config.setdefault("CELERY_RESULT_BACKEND", config_class.CELERY_RESULT_BACKEND)

    _register_blueprints(app)
    return app


def _register_blueprints(app: Flask) -> None:
    """Register application blueprints if their modules are available."""
    # Attempt to register blueprint defined in auth.py
    try:
        module = importlib.import_module("app.auth")
    except ImportError:
        module = None
    if module is not None:
        for attr in ("bp", "auth_bp"):
            blueprint = getattr(module, attr, None)
            if isinstance(blueprint, Blueprint):
                app.register_blueprint(blueprint)
                break

    # Register any blueprints in the views package
    views_path = os.path.join(os.path.dirname(__file__), "views")
    if os.path.isdir(views_path):
        for _, name, _ in pkgutil.iter_modules([views_path]):
            try:
                mod = importlib.import_module(f"app.views.{name}")
            except ImportError:
                continue
            # Also look for a module-specific blueprint name like ``index_bp``
            for attr in ("bp", "blueprint", f"{name}_bp", "index_bp"):
                blueprint = getattr(mod, attr, None)
                if isinstance(blueprint, Blueprint):
                    app.register_blueprint(blueprint)
                    break
