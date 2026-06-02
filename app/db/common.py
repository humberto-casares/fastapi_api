import logging
import os
from urllib.parse import quote

import orjson
import structlog
from dotenv import load_dotenv
from structlog.processors import CallsiteParameter

# Load environment variables from .env file
load_dotenv()

# Get environment variables
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')
db_user = os.getenv('DB_USER')

def configure_structlog():
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.CallsiteParameterAdder(
            [
                CallsiteParameter.FILENAME,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            ],
        ),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if os.environ.get("DEBUG") is not None:
        # Configuración para desarrollo local con colores
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
        logger_factory=structlog.PrintLoggerFactory()
    else:
        # Configuración para producción con JSON
        processors.extend([
            structlog.processors.JSONRenderer(serializer=orjson.dumps)
        ])
        logger_factory=structlog.BytesLoggerFactory()

    structlog.configure(
        context_class=dict,
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=processors,
        logger_factory=logger_factory,
    )


kyc_common_logger = None


def configure_logger(service_name="unknown"):
    global kyc_common_logger
    if kyc_common_logger is not None:
        return kyc_common_logger

    configure_structlog()
    kyc_common_logger = structlog.get_logger(service_name).bind(
        service_name=service_name
    )
    logging.getLogger(service_name).setLevel(logging.DEBUG)

    return kyc_common_logger


def cwd(file=__file__):
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file)))


def db_connection_uri(
        scheme="postgresql",
        user=db_user,
        password=db_password,
        host=os.environ.get("DB_HOST", db_host),
        port=os.environ.get("DB_PORT", db_port),
        database=os.environ.get("DB_NAME", db_name),
):
    password = quote(password)
    return f'{scheme}://{user}:{password}@{host}:{port}/{database}'
