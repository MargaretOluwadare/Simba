from rest_framework.views import exception_handler
import uuid, logging
from rest_framework.exceptions import ValidationError, APIException
from .response import APIResponse
from rest_framework.status import HTTP_400_BAD_REQUEST

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    request = context.get('request')
    response = exception_handler(exc, context)

    request_id = getattr(request, 'request_id', str(uuid.uuid4())[:8])

    if isinstance(exc, ValidationError):
        fields = {}
        print('RESPONSE!!!', response.data)

        if isinstance(response.data, dict):
            # assign only first error message to fields dict
            for field, messages in response.data.items():
                fields[field] = messages[0]

        return APIResponse.error(
            message="Validation failed",
            errors=fields,
            code="validation_error",
            meta={"request_id": request_id},
            status=HTTP_400_BAD_REQUEST,
        )

    if response is not None:
        logger.error(f"Exception in custom exception {str(exc)}, {getattr(response, 'status_code', 'unknown')}")
        return APIResponse.error(
            message=getattr(exc, 'default_detail', str(exc)),
            code=getattr(exc, 'default_code', "api_error"),
            meta={"request_id": request_id},
            status=response.status_code if response.status_code else HTTP_400_BAD_REQUEST,
        )


class InsufficientFunds(APIException):
    status_code = 400
    default_detail = "Insufficient wallet balance"
    default_code = "insufficient_funds"

class EmailAlreadyExists(APIException):
    status_code = 400
    default_detail = "Email already exists"
    default_code = "email_exists"