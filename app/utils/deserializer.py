from typing import Tuple, Optional, Dict

from aiokafka import ConsumerRecord
from google.protobuf.json_format import MessageToDict

from app.db.common import configure_logger
from app.utils.definitions import MessageEnvelopeHeaderRow, EventClasses, SERVICE_NAME

logger = configure_logger(service_name=f'{SERVICE_NAME}-service')


class ProtoDeserializer:
    def __init__(self, kafka_serialisation_header_to_proto_class_map: Dict):
        self.kafka_serialisation_header_to_proto_class_map = kafka_serialisation_header_to_proto_class_map

    async def deserialize(self, message: ConsumerRecord) -> Tuple[Optional[Dict], Optional[MessageEnvelopeHeaderRow]]:
        target_proto_class = None
        deserialization_header_value = None
        try:
            if message.headers is None:
                await logger.aerror("Missing header: {0}".format(str(message)))
                return None, None
            for header in message.headers:
                if header[0] == EventClasses.KAFKA_SERIALIZATION:
                    deserialization_header_value = str(header[1], "ascii")
                    target_proto_class = self.kafka_serialisation_header_to_proto_class_map.get(
                        deserialization_header_value)

            if target_proto_class is None:
                await logger.awarning("Missing target class: {0}".format(str(message)))
                return None, None
            target_object = target_proto_class()
            target_object.ParseFromString(message.value)
            msg = MessageToDict(target_object)
            return msg, MessageEnvelopeHeaderRow(name=deserialization_header_value,
                                                 topic=str(message.topic),
                                                 offset=message.offset,
                                                 partition=message.partition,
                                                 timestamp=message.timestamp)
        except Exception as e:
            await logger.aexception(f"Failed to deserialize message: {str(message)}. error: {e}")
            return None, None
