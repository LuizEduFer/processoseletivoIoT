from machine import Pin
import time

print("Sistema Kanban Inicializado")

DT = Pin(19, Pin.IN)
SCK = Pin(18, Pin.OUT)

estado_atual = "cheio"
estado_pendente = None
leituras_consecutivas = 0
ultima_leitura = 0

VALOR_CHEIO = 2100
VALOR_REGULAR = 907

TOLERANCIA_CHEIO = 250
TOLERANCIA_REGULAR = 250
LIMITE_VAZIO = 200

CONFIRMACAO_ESTADO = 3
CONFIRMACAO_VAZIO = 5


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

    if abs(valor - VALOR_CHEIO) <= TOLERANCIA_CHEIO:
        return "cheio"

    if abs(valor - VALOR_REGULAR) <= TOLERANCIA_REGULAR:
        return "regular"

    if abs(valor) <= LIMITE_VAZIO:
        return "vazio"

    return None


def atualizar_estado(novo_estado):
    global estado_atual
    global estado_pendente
    global leituras_consecutivas

    if novo_estado is None:
        return

    if novo_estado == estado_atual:
        estado_pendente = None
        leituras_consecutivas = 0
        return

    if novo_estado == estado_pendente:
        leituras_consecutivas += 1
    else:
        estado_pendente = novo_estado
        leituras_consecutivas = 1

    if novo_estado == "vazio":
        limite = CONFIRMACAO_VAZIO
    else:
        limite = CONFIRMACAO_ESTADO

    if leituras_consecutivas < limite:
        return

    estado_anterior = estado_atual

    estado_atual = novo_estado
    estado_pendente = None
    leituras_consecutivas = 0

    if novo_estado == "vazio":
        print("Evento de reposição disparado! Caixa vazia detectada.")

    elif novo_estado == "regular":
        print("Status: Estoque Regular (2500g)")

    elif novo_estado == "cheio":
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