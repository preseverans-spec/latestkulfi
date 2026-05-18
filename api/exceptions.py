from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # If an exception happened that is not handled by the standard error handler,
    # response will be None.
    if response is None:
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'A server error occurred.',
            'data': None,
            'errors': str(exc) if hasattr(exc, 'args') else 'Internal Server Error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Wrap the standard response in our envelope
    response.data = {
        'success': False,
        'message': response.data.get('detail', 'Validation or authorization error'),
        'data': None,
        'errors': response.data
    }

    return response
