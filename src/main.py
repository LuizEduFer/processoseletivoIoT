from machine import Pin
import time

print("Sistema Kanban Inicializado")

DT = Pin(19, Pin.IN)
SCK = Pin(18, Pin.OUT)


def ler_hx711():
    # Se o HX711 ainda não está pronto, retorna None
    if DT.value() == 1:
        return None

    valor = 0

    # Leitura dos 24 bits
    for _ in range(24):
        SCK.value(1)
        valor = (valor << 1) | DT.value()
        SCK.value(0)

    # Pulso adicional para ganho 128
    SCK.value(1)
    SCK.value(0)

    # Conversão para inteiro com sinal
    if valor & 0x800000:
        valor -= 0x1000000

    return valor


while True:
    valor = ler_hx711()

    if valor is not None:
        print("Leitura HX711:", valor)
    else:
        print("HX711 aguardando dados...")

    time.sleep_ms(500)