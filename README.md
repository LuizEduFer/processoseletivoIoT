# Relatório do Candidato

---

## Identificação do Candidato

- **Nome completo:** Luiz Eduardo Fernandes Cruz
- **GitHub:** LuizEduFer

---

## Visão Geral da Solução

O projeto consiste basicamente em um sistema Kanban automatizado para gestão de estoque, sendo simulado em um microcontrolador ESP32 e utilizando MicroPython. O objetivo principal é monitorar o peso das caixas armazenadas, usando uma célula de carga simulada com o sensor HX711 e classificar o status do estoque em tempo real. O sistema identifica automaticamente os cenários de estoque regular, consumo parcial, necessidade de reposição (caixa vazia) e anomalias (como a remoção da caixa ou ausência de leitura), garantindo a logística e evitando falhas operacionais.

---

## Arquitetura do Sistema Embarcado

A lógica principal (main.py) utiliza um loop contínuo estruturado em uma arquitetura de máquina de estados não-bloqueante:

- Leitura e Filtragem: Os dados brutos do HX711 passam por um buffer deslizante de tamanho 7 combinado com a remoção de extremos, o que garante imunidade alta a ruídos do simulador.
- Classificação: Mapeia os valores filtrados em faixas definidas de peso:
  - 0 a 15: Estado de Alerta (Caixa ausente ou erro).
  - 16 a 400: Estado Vazio (Disparo de reposição).
  - 401 a 1600: Estado Regular (Estoque estabilizado).
  - >1600: Estado Cheio (Estoque completo).
- Máquina de Estados com Confirmação: Utiliza um contador de leituras consecutivas para evitar falsos positivos antes de alterar o status do sistema e imprimir as mensagens oficiais exigidas pelo Wokwi.

---

## Componentes Utilizados na Simulação

- Placa Microcontroladora (ESP32): Responsável pelo processamento lógico, leitura dos pinos digitais e controle do firmware em MicroPython.
- Sensor de Peso (HX711): Simula a variação de peso das caixas de estoque conectados através dos pinos de dados (DT no pino 19) e clock (SCK no pino 18).

---

## Decisões Técnicas Relevantes

1. Filtro de Média Móvel: Essencial para suavizar as oscilações e ruídos injetados pelo simulador do Wokwi sem causar atrasos grandes.
2. Blindagem de Transição Regular: Implementação de travas lógicas que impedem que quedas rápidas de leitura durante o consumo parcial gerem falsos alarmes de reposição ou ausência de caixa.
3. Gerenciamento de Zeros Intermitentes: Ajustes de sensibilidade nas confirmações consecutivas para permitir que ciclos dinâmicos de reabastecimento fossem validados normalmente.

---

## Resultados Obtidos

- Funcionamento Completo: A solução atendeu rigorosamente a todos os requisitos de integração contínua (Wokwi CI).
- Testes Validados: Os cenários de consumo parcial (Teste 1), ciclo completo de reposição (Teste 2) e detecção de anomalias e remoção de caixa (Teste 3) executam e passam sem as falhas de timeout.

---

## Comentários Adicionais (Opcional)

- Durante o desenvolvimento, uma das principais dificuldades foi garantir a compatibilidade entre a leitura do sensor HX711 simulado no Wokwi e a lógica de classificação dos níveis de estoque. Foi necessário analisar os valores brutos retornados pelo sensor e ajustar a lógica de confirmação para evitar os disparos incorretos causados por variações nas leituras.
- Outra dificuldade encontrada foi a validação do projeto por meio do GitHub Actions e dos testes automatizados do Wokwi CI. Durante esse processo, foram analisados os logs das execuções para identificar problemas relacionados ao comportamento do sensor, ao tempo de resposta da simulação e à transição entre os estados do sistema.
- O desenvolvimento permitiu entender melhor a integração entre firmware, simulação de hardware, sensores, controle de estados e integração contínua, além de reforçar a importância de analisar os logs e validar o comportamento do sistema em diferentes condições.