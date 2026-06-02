from http import HTTPStatus

import aiohttp

from app.db.common import configure_logger
from app.utils.definitions import SERVICE_NAME

logger = configure_logger(service_name=f"{SERVICE_NAME}-service")


class ExternalServiceError(Exception):
    """Base exception for external service errors."""
    pass


class ExternalServiceNotFoundError(ExternalServiceError):
    """Exception for resources not found in the external service."""
    pass


class ExternalServiceBadRequestError(ExternalServiceError):
    """Exception for bad requests to the external service."""
    pass


class ExternalServiceUnauthorizedError(ExternalServiceError):
    """Exception for authentication errors with the external service."""
    pass


class ExternalServiceInternalServerError(ExternalServiceError):
    """Exception for internal server errors from the external service."""
    pass


def handle_aiohttp_error(error: aiohttp.ClientResponseError):
    """Handles aiohttp.ClientResponseError exceptions and converts them to custom exceptions."""
    logger.error(f"Error interacting with the external service: {error}")
    if error.status == HTTPStatus.BAD_REQUEST:
        raise ExternalServiceBadRequestError("Bad request to the external service.")
    elif error.status == HTTPStatus.UNAUTHORIZED:
        raise ExternalServiceUnauthorizedError(
            "Authentication error with the external service."
        )
    elif error.status == HTTPStatus.NOT_FOUND:
        raise ExternalServiceNotFoundError(
            "Resource not found in the external service."
        )
    elif error.status >= HTTPStatus.INTERNAL_SERVER_ERROR:
        raise ExternalServiceInternalServerError(
            "Internal server error from the external service."
        )
    else:
        raise ExternalServiceError(
            "Unknown error interacting with the external service."
        )
