# Viagens a serviço do governo federal em 2023

Uma análise exploratória, feita em Python, sobre a quantidade, a duração e as despesas registradas para viagens a serviço. O projeto usa dados do Portal da Transparência e apresenta resultados agrupados por cargo e por faixa de duração.

![Gráficos agregados de viagens por cargo e faixa de duração](assets/viagens_2023.png)

## Tecnologias

- **Python** para a análise;
- **pandas** para leitura, tratamento e agregação dos dados;
- **Matplotlib** para os gráficos;
- **Jupyter Notebook** para documentar o processo de forma reproduzível.

## Etapas da análise

- Leitura seletiva do CSV, carregando apenas as seis colunas necessárias;
- tratamento de datas, valores ausentes e categorias de cargo;
- cálculo da duração e das despesas consideradas;
- agregação por cargo e faixa de duração, com critérios explícitos para grupos pequenos;
- criação de gráficos e registro das limitações dos dados.

## O que a análise investiga

- Como o número de viagens se distribui entre os cargos?
- Como variam a quantidade de viagens e a mediana das despesas por cargo?
- Como a mediana das despesas muda entre faixas de duração?

O notebook explica as etapas, os cálculos e os limites da análise. As despesas consideradas são a soma de diárias, passagens e outros gastos, desde que os três valores estejam disponíveis; devoluções não entram nesse cálculo. A mediana ajuda a reduzir a influência de valores muito altos.

## Principais achados

- **Cobertura do cargo:** em 833.057 viagens, 325.565 (39,1%) não informam o cargo e 118.525 (14,2%) estão marcadas como protegidas por sigilo. A comparação por cargo considera as 388.967 viagens restantes (46,7%), com cargo divulgado.
- **Cargo mais frequente:** Professor do Magistério Superior aparece em 55.013 viagens, 14,1% das viagens com cargo divulgado.
- **Duração e despesa:** a mediana registrada vai de R$ 129,63 nas viagens de 0 dias (139.875 viagens) a R$ 86.478,88 nas viagens acima de 180 dias (2.169 viagens). O notebook agrupa durações em faixas e inclui apenas faixas com pelo menos 30 viagens.

Esses números descrevem os registros de 2023. A diferença entre as medianas não indica que a duração, por si só, cause despesas maiores; viagens longas podem ter características diferentes. A mediana das despesas considera diárias, passagens e outros gastos quando os três valores estão disponíveis, sem descontar devoluções.

As contagens representam registros de viagens, não o número de servidores únicos.

## Como reproduzir

1. Baixe o arquivo `2023_Viagem.csv` referente a 2023 na página de [dados de viagens do Portal da Transparência](https://portaldatransparencia.gov.br/download-de-dados/viagens).
2. Coloque o arquivo neste caminho: `data/raw/2023_Viagem.csv`.
3. Instale as bibliotecas: `pip install -r requirements.txt`.
4. Abra `analise_viagens_2023.ipynb` no Jupyter e execute as células na ordem.

O CSV não faz parte do repositório. Ele é grande, pode conter informações de pessoas e itinerários, e deve ser baixado diretamente da fonte indicada. O notebook lê somente seis colunas necessárias (cargo, datas e valores), sem carregar nomes, CPFs, identificadores ou detalhes de itinerário.

## Privacidade

O notebook preparado para publicação não salva resultados de execução nem mostra linhas individuais. A imagem deste README e as tabelas do notebook mostram grupos agregados; cargos sem informação ou protegidos por sigilo são omitidos dos gráficos, assim como faixas com menos de 30 viagens. O notebook original de trabalho e os arquivos CSV estão excluídos do Git por regras em `.gitignore`.

Antes de publicar, revise os arquivos preparados e evite adicionar dados brutos, capturas de tela com registros individuais, credenciais ou informações pessoais.

## Como interpretar

Este é um exercício exploratório, não uma auditoria. Registros incompletos podem afetar os resultados; a duração é a diferença entre as datas de início e fim; e as despesas não descontam devoluções. O total por cargo considera apenas registros com os três componentes de despesa preenchidos. Comparações entre grupos descrevem padrões e não demonstram causa e efeito.
