import json
import time
import random
from datetime import datetime
from typing import Dict, List
import sqlite3
from dataclasses import dataclass, asdict
import threading
import queue

# Veri modelleri
@dataclass
class SensorData:
    device_id: str
    timestamp: str
    temperature: float
    humidity: float
    location: str

@dataclass
class Alert:
    device_id: str
    timestamp: str
    alert_type: str
    message: str
    value: float

# Veritabanı yöneticisi
class DatabaseManager:
    def __init__(self, db_name: str = "iot_data.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Sensör verileri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                location TEXT NOT NULL
            )
        ''')
        
        # Uyarılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                value REAL NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_sensor_data(self, data: SensorData):
        """Sensör verisini kaydet"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sensor_readings (device_id, timestamp, temperature, humidity, location)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.device_id, data.timestamp, data.temperature, data.humidity, data.location))
        conn.commit()
        conn.close()
    
    def save_alert(self, alert: Alert):
        """Uyarıyı kaydet"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (device_id, timestamp, alert_type, message, value)
            VALUES (?, ?, ?, ?, ?)
        ''', (alert.device_id, alert.timestamp, alert.alert_type, alert.message, alert.value))
        conn.commit()
        conn.close()
    
    def get_latest_readings(self, device_id: str, limit: int = 10) -> List[Dict]:
        """Son okumaları getir"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM sensor_readings 
            WHERE device_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (device_id, limit))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results

# IoT Cihaz Simülatörü
class IoTDevice:
    def __init__(self, device_id: str, location: str):
        self.device_id = device_id
        self.location = location
        self.base_temp = 22.0
        self.base_humidity = 50.0
    
    def read_sensor(self) -> SensorData:
        """Sensör okumalarını simüle et"""
        # Gerçekçi veri üretmek için rastgele değişim
        temp_variation = random.uniform(-2, 2)
        humidity_variation = random.uniform(-5, 5)
        
        temperature = round(self.base_temp + temp_variation, 2)
        humidity = round(self.base_humidity + humidity_variation, 2)
        
        return SensorData(
            device_id=self.device_id,
            timestamp=datetime.now().isoformat(),
            temperature=temperature,
            humidity=humidity,
            location=self.location
        )

# Uyarı Yöneticisi
class AlertManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.temp_threshold_high = 28.0
        self.temp_threshold_low = 18.0
        self.humidity_threshold_high = 70.0
        self.humidity_threshold_low = 30.0
    
    def check_thresholds(self, data: SensorData) -> List[Alert]:
        """Eşik değerlerini kontrol et ve uyarı oluştur"""
        alerts = []
        
        if data.temperature > self.temp_threshold_high:
            alert = Alert(
                device_id=data.device_id,
                timestamp=data.timestamp,
                alert_type="HIGH_TEMPERATURE",
                message=f"Yüksek sıcaklık algılandı: {data.temperature}°C",
                value=data.temperature
            )
            alerts.append(alert)
            self.db_manager.save_alert(alert)
        
        elif data.temperature < self.temp_threshold_low:
            alert = Alert(
                device_id=data.device_id,
                timestamp=data.timestamp,
                alert_type="LOW_TEMPERATURE",
                message=f"Düşük sıcaklık algılandı: {data.temperature}°C",
                value=data.temperature
            )
            alerts.append(alert)
            self.db_manager.save_alert(alert)
        
        if data.humidity > self.humidity_threshold_high:
            alert = Alert(
                device_id=data.device_id,
                timestamp=data.timestamp,
                alert_type="HIGH_HUMIDITY",
                message=f"Yüksek nem algılandı: {data.humidity}%",
                value=data.humidity
            )
            alerts.append(alert)
            self.db_manager.save_alert(alert)
        
        elif data.humidity < self.humidity_threshold_low:
            alert = Alert(
                device_id=data.device_id,
                timestamp=data.timestamp,
                alert_type="LOW_HUMIDITY",
                message=f"Düşük nem algılandı: {data.humidity}%",
                value=data.humidity
            )
            alerts.append(alert)
            self.db_manager.save_alert(alert)
        
        return alerts

# IoT Hub - Merkezi Yönetim
class IoTHub:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.alert_manager = AlertManager(self.db_manager)
        self.devices: Dict[str, IoTDevice] = {}
        self.data_queue = queue.Queue()
        self.running = False
    
    def register_device(self, device_id: str, location: str):
        """Yeni cihaz kaydet"""
        device = IoTDevice(device_id, location)
        self.devices[device_id] = device
        print(f"✓ Cihaz kaydedildi: {device_id} ({location})")
    
    def collect_data(self):
        """Tüm cihazlardan veri topla"""
        while self.running:
            for device in self.devices.values():
                data = device.read_sensor()
                self.data_queue.put(data)
            time.sleep(5)  # 5 saniyede bir oku
    
    def process_data(self):
        """Toplanan verileri işle"""
        while self.running:
            try:
                data = self.data_queue.get(timeout=1)
                
                # Veriyi kaydet
                self.db_manager.save_sensor_data(data)
                
                # Uyarıları kontrol et
                alerts = self.alert_manager.check_thresholds(data)
                
                # Konsola yazdır
                print(f"\n📊 {data.device_id} ({data.location})")
                print(f"   🌡️  Sıcaklık: {data.temperature}°C")
                print(f"   💧 Nem: {data.humidity}%")
                print(f"   🕒 Zaman: {data.timestamp}")
                
                if alerts:
                    for alert in alerts:
                        print(f"   ⚠️  UYARI: {alert.message}")
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Veri işleme hatası: {e}")
    
    def start(self):
        """Hub'ı başlat"""
        self.running = True
        print("\n🚀 IoT Hub başlatılıyor...\n")
        
        # Veri toplama thread'i
        collect_thread = threading.Thread(target=self.collect_data, daemon=True)
        collect_thread.start()
        
        # Veri işleme thread'i
        process_thread = threading.Thread(target=self.process_data, daemon=True)
        process_thread.start()
        
        print("✓ IoT Hub aktif\n")
        print("Durdurmak için Ctrl+C basın\n")
        print("="*50)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Hub'ı durdur"""
        print("\n\n🛑 IoT Hub durduruluyor...")
        self.running = False
        time.sleep(2)
        print("✓ IoT Hub durduruldu\n")
    
    def get_statistics(self, device_id: str):
        """Cihaz istatistiklerini göster"""
        readings = self.db_manager.get_latest_readings(device_id, limit=100)
        
        if not readings:
            print(f"❌ {device_id} için veri bulunamadı")
            return
        
        temps = [r['temperature'] for r in readings]
        humidities = [r['humidity'] for r in readings]
        
        print(f"\n📈 {device_id} İstatistikleri:")
        print(f"   Ölçüm Sayısı: {len(readings)}")
        print(f"   Ortalama Sıcaklık: {sum(temps)/len(temps):.2f}°C")
        print(f"   Min/Max Sıcaklık: {min(temps):.2f}°C / {max(temps):.2f}°C")
        print(f"   Ortalama Nem: {sum(humidities)/len(humidities):.2f}%")
        print(f"   Min/Max Nem: {min(humidities):.2f}% / {max(humidities):.2f}%\n")

# Ana program
def main():
    # IoT Hub oluştur
    hub = IoTHub()
    
    # Cihazları kaydet
    hub.register_device("SENSOR-001", "Salon")
    hub.register_device("SENSOR-002", "Yatak Odası")
    hub.register_device("SENSOR-003", "Mutfak")
    
    # Hub'ı başlat
    hub.start()

if __name__ == "__main__":
    main()
