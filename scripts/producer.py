from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime

# Configuration
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

cities = ['Casablanca', 'Rabat', 'Marrakech', 'Fes', 'Tanger', 'Agadir']
sensor_ids = [f'SENSOR_{i:03d}' for i in range(1, 21)]

print("=" * 60)
print("🌡️  PRODUCTEUR IoT - DÉMARRAGE")
print("=" * 60)
print(f"📍 Villes : {', '.join(cities)}")
print(f"🔧 Capteurs : 20")
print(f"📡 Topic Kafka : iot-temperature")
print("=" * 60)

try:
    count = 0
    while True:
        data = {
            'sensor_id': random.choice(sensor_ids),
            'city': random.choice(cities),
            'temperature': round(random.uniform(15.0, 45.0), 2),
            'humidity': round(random.uniform(20.0, 90.0), 2),
            'timestamp': datetime.now().isoformat()
        }
        
        producer.send('iot-temperature', value=data)
        count += 1
        
        if count % 10 == 0:
            print(f"✅ {count} messages envoyés - Dernier: {data['city']} {data['temperature']}°C")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    print(f"\n⏹️  Arrêt - Total: {count} messages")
    producer.close()