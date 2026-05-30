from flask import Flask, request, jsonify
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException, ConnectionException
import logging
import time
# Flask Webhook-Server initialisieren
app = Flask(__name__)

# Modbus TCP Client Setup
MODBUS_SERVER_IP = "192.168.40.231"  # IP der Siemens LOGO!
MODBUS_SERVER_PORT = "510" # Siemens Logo Port, vorher 510
MODBUS_SERVER_TIMEOUT = 10

# Logging aktivieren
logging.basicConfig(level=logging.INFO)

# Funktion zum Senden eines Modbus-Signals
def send_modbus_signal():
    client = ModbusTcpClient(MODBUS_SERVER_IP, port=MODBUS_SERVER_PORT, timeout=MODBUS_SERVER_TIMEOUT)

    try:
        logging.info("Verbindung zur Siemens LOGO! wird hergestellt...")

         # Falls die Verbindung fehlschlägt: 3-mal erneut versuchen
        for attempt in range(3):
            if client.connect():
                break  # Falls es klappt, verlasse die Schleife
            logging.warning(f"Verbindungsversuch {attempt + 1} fehlgeschlagen. Erneuter Versuch in 2 Sekunden...")
            time.sleep(3.0)
        else:
            logging.error("Verbindung zur LOGO! konnte nach 3 Versuchen nicht aufgebaut werden!")
            return

        # Warten, damit die LOGO! Zeit zur Verarbeitung hat
        time.sleep(3.0)

        # Teste, ob die LOGO! auf Modbus-Befehle reagiert (MIT EINEM ARGUMENT)
        rr = client.read_coils(4)
        if rr.isError():
            logging.error("Fehler: LOGO! antwortet nicht auf Modbus-Befehl.")
            return
        else:
            logging.info(rr)

        # Wartezeit vor Schaltung, um Timeout-Fehler zu vermeiden
        time.sleep(2.0)

        # Q6 EIN (Adresse 5)
        coil_address = 8197
        logging.info(f"Sende Modbus-Befehl: Coil {coil_address} EIN")
        res = client.write_coil(address=coil_address, value=True)
        logging.info(res)

        # 2 Sekunden warten
        time.sleep(0.5)

        # Q6 AUS
        logging.info(f"Sende Modbus-Befehl: Coil {coil_address} AUS")
        client.write_coil(coil_address, False)

    except ModbusIOException as e:
        logging.error(f"Modbus Fehler: {e}")
    except ConnectionException as e:
        logging.error(f"Verbindungsfehler: {e}")
        logging.warning("Versuche, die Verbindung neu aufzubauen...")
        client.close()
        time.sleep(1)  # Wartezeit vor Neuverbindung
        client.connect()  # Verbindung erneut aufbauen
    except Exception as e:
        logging.error(f"Allgemeiner Fehler: {e}")
    finally:
        if client and client.connected:
            time.sleep(1.0)  # Wartezeit, bevor die Verbindung geschlossen wird
            client.close()
            logging.info("Modbus-Verbindung zur LOGO! wurde erfolgreich geschlossen.")

@app.route('/print', methods=['POST'])
def doorbell_trigger():
    try:
        data = request.get_json()
        logging.info(f"Webhook-Daten empfangen: {data}")

        # Modbus-Signal senden
        send_modbus_signal()

        return jsonify({"message": "Siemens LOGO! wurde per Webhook getriggert."}), 200

    except Exception as e:
        logging.error(f"Webhook-Fehler: {e}")
        return jsonify({"error": str(e)}), 500

# Starte den Flask-Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)