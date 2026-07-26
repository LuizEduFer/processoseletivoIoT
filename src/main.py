from machine import Pin
import time

print("Sistema Kanban Inicializado")

DT = Pin(19, Pin.IN)
SCK = Pin(18, Pin.OUT)

estado_atual = "cheio"
estado_pendente = None
leituras_consecutivas = 0
ultima_leitura = 0

CONFIRMACAO_NORMAL = 3
CONFIRMACAO_VAZIO = 3
CONFIRMACAO_ALERTA = 3


def ler_hx711():
    if DT.value() == 1:
        return None

    valor = 0

    for _ in range(24):
        SCK.value(1)
        time.sleep_us(1)
        valor = (valor << 1) | DT.value()
        SCK.value(0)
        time.sleep_us(1)

    SCK.value(1)
    time.sleep_us(1)
    SCK.value(0)

    if valor & 0x800000:
        valor -= 0x1000000

    return valor


def classificar(valor):
    if valor is None:
        return None

    if abs(valor) <= 30:
        return "alerta"

    if abs(valor - 2100) <= 250:
        return "cheio"

    if abs(valor - 907) <= 250:
        return "regular"

    if 30 < valor <= 150:
        return "vazio"

    return None


def atualizar_estado(novo_estado):
    global estado_atual
    global estado_pendente
    global leituras_consecutivas

    if novo_estado is None:
        return

    if novo_estado == estado_pendente:
        leituras_consecutivas += 1
    else:
        estado_pendente = novo_estado
        leituras_consecutivas = 1

    if novo_estado == "alerta":
        limite = CONFIRMACAO_ALERTA
    elif novo_estado == "vazio":
        limite = CONFIRMACAO_VAZIO
    else:
        limite = CONFIRMACAO_NORMAL

    if leituras_consecutivas < limite:
        return

    estado_anterior = estado_atual

    estado_pendente = None
    leituras_consecutivas = 0

    if novo_estado == "alerta":
        print("ALERTA: Caixa ausente ou erro de calibração no sensor HX711!")
        return

    if novo_estado == "vazio":
        if estado_atual != "vazio":
            estado_atual = "vazio"
            print("Evento de reposição disparado! Caixa vazia detectada.")
        return

    if novo_estado == "regular":
        estado_atual = "regular"

        if estado_anterior != "regular":
            print("Status: Estoque Regular (2500g)")

        return

    if novo_estado == "cheio":
        estado_atual = "cheio"

        if estado_anterior == "vazio":
            print("Abastecimento concluído. Caixa cheia.")


while True:
    agora = time.ticks_ms()

    if time.ticks_diff(agora, ultima_leitura) >= 100:
        ultima_leitura = agora

        valor = ler_hx711()

        if valor is not None:
            estado = classificar(valor)
            atualizar_estado(estado)

    time.sleep_ms(10)