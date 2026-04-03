from rest_framework.response import Response
import secrets, hashlib
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


class APIResponse:
    @staticmethod
    def success(message="Success", data=None, meta=None, status=HTTP_200_OK):
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
                "meta": meta,
                "errors": None,
            },
            status=status,
        )

    @staticmethod
    def error(
        message="Error", errors=None, code=None, meta=None, status=HTTP_400_BAD_REQUEST
    ):
        return Response(
            {
                "success": False,
                "message": message,
                "data": None,
                "errors": errors,
                "code": code,
                "meta": meta,
            },
            status=status,
        )


def generate_code():
    return str(secrets.randbelow(900000) + 100000)  # 6 digits


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()
