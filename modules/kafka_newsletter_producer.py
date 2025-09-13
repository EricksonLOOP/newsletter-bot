# from confluent_kafka import Producer
# import json
#
# # Configuração básica do Kafka
# conf = {
#     'bootstrap.servers': 'localhost:9092',  # ou endereço do seu cluster
#     'client.id': 'newsletter-producer'
# }
#
# producer = Producer(conf)
#
# def delivery_report(err, msg):
#     """Callback chamado quando a mensagem é entregue ou falha"""
#     if err is not None:
#         print(f"Erro ao enviar mensagem: {err}")
#     else:
#         print(f"Mensagem enviada para {msg.topic()} [{msg.partition()}]")
#
# def send_newsletter_to_kafka(news_json:dict, topic:str='newsletters'):
#     """
#     Envia a newsletter (Pydantic model) para Kafka
#     """
#     producer.produce(
#         topic,
#         key=news_json['title'],
#         value=json.dumps(news_json),
#         callback=delivery_report
#     )
#     producer.flush()
