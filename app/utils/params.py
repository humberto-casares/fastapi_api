import os
from pathlib import Path

import yaml

SYSTEM_CONFIG_PATH = str(
    Path(__file__).resolve().parents[1] / "resource" / "system_config.yml"
)

with open(SYSTEM_CONFIG_PATH, "r") as stream:
    SYS_CONF = yaml.safe_load(stream)


def cont_str(data):
    if isinstance(data, list):
        return '\n'.join(cont_str(item) for item in data)
    elif isinstance(data, str):
        return data
    return ''

import dotenv
dotenv.load_dotenv()

USE_MOCK = os.getenv("USE_MOCK") == "true"
WHATSAPP_OTP_FLAG = os.getenv("WHATSAPP_OTP_FLAG") == "true"

MEX_TIMEZONE = "America/Mexico_City"

PRODUCER_REQUEST_TIMEOUT_MS = SYS_CONF["producer_request_timeout_ms"]
PRODUCER_RETRY_BACKOFF_MS = SYS_CONF["producer_retry_backoff_ms"]
PRODUCER_CONNECTIONS_MAX_IDLE_MS = SYS_CONF["producer_connections_max_idle_ms"]
PRODUCER_TRANSACTION_TIMEOUT_MS = SYS_CONF["producer_transaction_timeout_ms"]

CONSUMER_FETCH_MAX_WAIT_MS = SYS_CONF["consumer_fetch_max_wait_ms"]
CONSUMER_REQUEST_TIMEOUT_MS = SYS_CONF["consumer_request_timeout_ms"]
CONSUMER_RETRY_BACKOFF_MS = SYS_CONF["consumer_retry_backoff_ms"]
CONSUMER_MAX_POLL_INTERVAL_MS = SYS_CONF["consumer_max_poll_interval_ms"]
CONSUMER_SESSION_TIMEOUT_MS = SYS_CONF["consumer_session_timeout_ms"]
CONSUMER_HEARTBEAT_INTERVAL_MS = SYS_CONF["consumer_heartbeat_interval_ms"]
CONSUMER_CONSUMER_TIMEOUT_MS = SYS_CONF["consumer_consumer_timeout_ms"]
CONSUMER_CONNECTIONS_MAX_IDLE_MS = SYS_CONF["consumer_connections_max_idle_ms"]

REQUESTS_TIMEOUT_SECONDS = SYS_CONF["requests_timeout_seconds"]
MAX_RETRIES = SYS_CONF["requests_max_retries"]
WAIT_RETRIES = SYS_CONF["requests_wait_retries"]

FACTOR_MULT = SYS_CONF["factor_mult"]
CONSUMER_JOBS = SYS_CONF["consumer_jobs"]
EXECUTE_TASKS_PARALLEL = SYS_CONF["execute_tasks_parallel"]
SLEEP_TASKS = SYS_CONF["sleep_tasks"]
LOOK_WAIT = SYS_CONF["look_wait"]
LOOK_EXPIRE = SYS_CONF["look_expire"]
DB_POOL_MIN = SYS_CONF["pool_min"]
DB_POOL_MAX = SYS_CONF["pool_max"]
DB_RETRIES = SYS_CONF["db_retries"]
DB_WAIT_FACTOR = SYS_CONF["db_wait_factor"]
RETRIEVER_TASKS_LIMIT = SYS_CONF["retriever_tasks_limit"]

SQL_RETRIEVER_USERS = """
SELECT * FROM users 
WHERE magic_token IS NULL 
    AND created_at < now() - INTERVAL '5 minutes' 
    ORDER BY created_at ASC 
    LIMIT $1;
    """

SPANISH_MONTHS = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre'
}
