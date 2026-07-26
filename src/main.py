from machine import Pin
import time

print("Sistema Kanban Inicializado")

DT = Pin(19, Pin.IN)
SCK = Pin(18, Pin.OUT)

estado_atual = "cheio"
estado_pendente = None
leituras_consecutivas = 0
ultima_leitura = 0

CONFIRMACAO_NORMAL = 4
CONFIRMACAO_VAZIO = 4
CONFIRMACAO_ALERTA = 2

buffer_leituras = []
TAMANHO_BUFFER = 5


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


def obter_leitura_filtrada():
    valor_bruto = ler_hx711()
    if valor_bruto is None:
        return None

    if valor_bruto > 5000:
        valor_bruto = valor_bruto // 1000

    if valor_bruto <= 15 and buffer_leituras and max(buffer_leituras, default=0) > 500:
        buffer_leituras.clear()
        return valor_bruto

    if valor_bruto <= 5:
        buffer_leituras.clear()
        return valor_bruto

    buffer_leituras.append(valor_bruto)
    if len(buffer_leituras) > TAMANHO_BUFFER:
        buffer_leituras.pop(0)

    if len(buffer_leituras) < 3:
        return sum(buffer_leituras) // len(buffer_leituras)

    ordenados = sorted(buffer_leituras)
    centrais = ordenados[1:-1]
    return sum(centrais) // len(centrais)


def classificar(valor):
    if valor is None:
        return None

    if valor <= 15:
        return "alerta"
    elif valor <= 400:
        return "vazio"
    elif valor <= 1600:
        return "regular"
    else:
        return "cheio"


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
        if estado_atual != "alerta":
            estado_atual = "alerta"
            print("ALERTA: Caixa ausente ou erro de calibração no sensor HX711!")
        return

    if novo_estado == "vazio":
        if estado_atual != "vazio":
            estado_atual = "vazio"
            print("Evento de reposição disparado! Caixa vazia detectada.")
        return

    if novo_estado == "regular":
        if estado_atual != "regular":
            estado_atual = "regular"
            print("Status: Estoque Regular (2500g)")
        return

    if novo_estado == "cheio":
        if estado_atual != "cheio":
            estado_atual = "cheio"
            if estado_anterior == "vazio":
                print("Abastecimento concluído. Caixa cheia.")


while True:
    agora = time.ticks_ms()

    if time.ticks_diff(agora, ultima_leitura) >= 100:
        ultima_leitura = agora

        valor_filtrado = obter_leitura_filtrada()

        if valor_filtrado is not None:
            print("VALOR BRUTO:", valor_filtrado)

            estado = classificar(valor_filtrado)
            atualizar_estado(estado)

    time.sleep_ms(10)