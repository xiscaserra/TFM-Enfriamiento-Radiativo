import time
import board
import adafruit_dht
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # NEW

from datetime import datetime


# --- CONFIGURACIÓN ---
try:
    sensor1 = adafruit_dht.DHT22(board.D4)
    sensor2 = adafruit_dht.DHT22(board.D17)
except Exception as e:
    print(f"Error inicializando sensores: {e}")

nombre_fichero = "datos_sensores.csv"

# Crear el fichero con cabeceras si no existe
if not os.path.exists(nombre_fichero):
    with open(nombre_fichero, mode='w', newline='') as f:
        escritor = csv.writer(f)
        escritor.writerow(["Fecha y Hora", "Temp_Salon(C)", "Hum_Salon(%)", "Temp_Cocina(C)", "Hum_Cocina(%)"])

print(f"Guardando datos en {nombre_fichero}. Pulsa Ctrl+C para parar.")


# --- NUEVO: DATOS PARA GRÁFICA ---
tiempos = []
temp1_vals = []
temp2_vals = []
hum1_vals = []
hum2_vals = []

plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

# Formato de tiempo bonito
locator = mdates.AutoDateLocator()
formatter = mdates.DateFormatter('%H:%M:%S')
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(formatter)


# --- BUCLE DE LECTURA ---
try:
    while True:
        ahora_str = time.strftime('%Y-%m-%d %H:%M:%S')
        ahora = datetime.now()

        try:
            # Lecturas del Sensor 1
            t1 = sensor1.temperature
            h1 = sensor1.humidity

            # Lecturas del Sensor 2
            t2 = sensor2.temperature
            h2 = sensor2.humidity

            # Guardar en el CSV
            with open(nombre_fichero, mode='a', newline='') as f:
                escritor = csv.writer(f)
                escritor.writerow([ahora_str, t1, h1, t2, h2])

            print(f"[{ahora_str}] S1: {t1}ºC | {h1}% | S2: {t2}ºC | {h2}% -> Guardado.")

            # --- NUEVO: GUARDAR DATOS ---
            tiempos.append(ahora)
            temp1_vals.append(t1)
            temp2_vals.append(t2)
            hum1_vals.append(h1)
            hum2_vals.append(h2)

            # Limitar tamaño
            tiempos = tiempos[-50:]
            temp1_vals = temp1_vals[-50:]
            temp2_vals = temp2_vals[-50:]
            hum1_vals = hum1_vals[-50:]
            hum2_vals = hum2_vals[-50:]

            # --- NUEVO: ACTUALIZAR GRÁFICAS ---
            ax1.clear()
            ax2.clear()

            # Temperatura
            ax1.plot(tiempos, temp1_vals, label="S1")
            ax1.plot(tiempos, temp2_vals, label="S2")
            ax1.set_title("Temperatura")
            ax1.set_ylabel("°C")
            ax1.legend()
            ax1.grid(True)

            # Humedad
            ax2.plot(tiempos, hum1_vals, label="S1")
            ax2.plot(tiempos, hum2_vals, label="S2")
            ax2.set_title("Humedad")
            ax2.set_ylabel("%")
            ax2.set_xlabel("Tiempo")
            ax2.legend()
            ax2.grid(True)

            # Reaplicar formato de tiempo (necesario tras clear)
            ax2.xaxis.set_major_locator(locator)
            ax2.xaxis.set_major_formatter(formatter)

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.pause(0.1)

        except RuntimeError as e:
            # Captura errores comunes de lectura del DHT (ej. checksum errors)
            print(f"Fallo temporal en la lectura (RuntimeError): {e.args[0]}. Reintentando...")
            time.sleep(2.0)
            continue

        except OverflowError as e:
            # Captura el error de desbordamiento específico que tienes en tu terminal
            print("Fallo en la sincronización de pulsos del sensor (OverflowError). Reintentando...")
            time.sleep(2.0)
            continue

        except Exception as e:
            # Captura cualquier otro error para que sepas qué pasa antes de salir
            print(f"Error inesperado y crítico: {e}")
            # sensor2.exit() # Descomentar si necesitas limpiar el pin antes de un cierre forzado
            continue


        time.sleep(2)

except KeyboardInterrupt:
    print("\nPrograma detenido por el usuario.")
    sensor1.exit()
    sensor2.exit()
