import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

def handle_exception(request, e, user_message="Something went wrong."):
    """Generic error handler for views"""
    # Log the full traceback in development/production logs
    logger.error(f"[{request.path}] {type(e).__name__}: {str(e)}")
    
    messages.error(request, user_message)
