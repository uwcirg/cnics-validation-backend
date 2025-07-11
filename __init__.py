try:
    from .app import app
except Exception:
    from app import app

__all__ = ['app']
