import os
import redis
import json
import logging

class WordPublisher:
    def __init__(self, host='localhost', port=6379, queue_name='words_queue'):
        #se conecta a Redis.
        host = os.environ.get('REDIS_HOST', 'localhost')
        self.queue_name = queue_name
        try:
            # decode_responses=True hace que Redis nos devuelva strings normales y no bytes
            self.redis_client = redis.Redis(host=host, port=port, decode_responses=True)
            # se hace un 'ping' para verificar que la conexión funciona
            self.redis_client.ping()
            logging.info(f"Conectado exitosamente a Redis en {host}:{port}")
        except redis.ConnectionError:
            logging.error("No se pudo conectar a Redis. Asegúrate de que el servidor esté corriendo.")

    def publish(self, words: list[str], language: str):
        #recibe la lista de palabras limpias y las empuja a la cola de Redis.
        if not words:
            return
        for word in words:
            #se empaqueta la palabra y el lenguaje en un formato JSON
            payload = json.dumps({
                "word": word,
                "language": language
            })
            
            # rpush (Right Push) mete el dato al final de la lista en Redis
            self.redis_client.rpush(self.queue_name, payload)
            
        logging.info(f"Publicadas {len(words)} palabras de {language} en la cola '{self.queue_name}'")
