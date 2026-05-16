from rest_framework import status
from rest_framework.response import Response


def _envelope(data=None, message='OK', success=True, errors=None, meta=None):
    payload = {
        'success': success,
        'message': message,
        'data': data,
    }
    if errors is not None:
        payload['errors'] = errors
    if meta is not None:
        payload['meta'] = meta
    return payload


class ResponseEnvelopeMixin:
    """Wrap API responses in a consistent mobile-friendly envelope."""

    def _wrap(self, response, message='OK'):
        if not isinstance(response, Response):
            return response

        if isinstance(response.data, dict) and 'success' in response.data and 'data' in response.data:
            return response

        if response.status_code >= 400:
            response.data = _envelope(
                data=None,
                message='Request failed',
                success=False,
                errors=response.data,
            )
            return response

        if isinstance(response.data, dict) and {'count', 'results'}.issubset(response.data.keys()):
            meta = {
                'count': response.data.get('count'),
                'next': response.data.get('next'),
                'previous': response.data.get('previous'),
            }
            response.data = _envelope(data=response.data.get('results', []), message=message, meta=meta)
            return response

        response.data = _envelope(data=response.data, message=message)
        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return self._wrap(response, message='List fetched successfully')

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self._wrap(response, message='Record fetched successfully')

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            return self._wrap(response, message='Record created successfully')
        return self._wrap(response)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return self._wrap(response, message='Record updated successfully')

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return self._wrap(response, message='Record updated successfully')

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            response.status_code = status.HTTP_200_OK
            response.data = _envelope(data={'deleted': True}, message='Record deleted successfully')
            return response
        return self._wrap(response)
