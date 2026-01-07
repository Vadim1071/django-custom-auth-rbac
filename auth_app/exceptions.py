from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для правильной обработки 401 и 403 ошибок
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Если это ошибка аутентификации (401)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data = {
                'error': 'Unauthorized',
                'message': 'Требуется аутентификация',
                'detail': str(exc)
            }
            response.data = custom_response_data
        
        # Если это ошибка доступа (403)
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data = {
                'error': 'Forbidden',
                'message': 'Доступ запрещен',
                'detail': str(exc)
            }
            response.data = custom_response_data
    
    return response
