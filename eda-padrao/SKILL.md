---
name: eda-padrao
description: Análise exploratória de dados (EDA) padronizada, em português. Use quando a pessoa enviar um dataset (CSV ou Excel) e pedir para explorar, entender, conhecer, perfilar ou fazer uma EDA dos dados, ou perguntar sobre qualidade, nulos, duplicados, outliers ou correlações de uma base.
---

# EDA padrão

Siga sempre o mesmo roteiro, para que toda análise exploratória tenha a mesma qualidade e o mesmo formato.

## Passo 1: gerar o perfil do dataset

Rode o script que acompanha esta skill. Ele não altera o arquivo original.

```bash
python scripts/perfil_dataset.py caminho/do/arquivo.csv --saida relatorio_eda
```

- Aceita `.csv`, `.xlsx` e `.xls`. Para CSV, detecta sozinho o separador (`,` ou `;`) e a codificação (`utf-8` ou `latin-1`, comum em dados públicos brasileiros).
- Para Excel com várias abas, use `--aba "Nome da aba"`.
- O script gera, dentro da pasta de saída:
  - `relatorio.md`: resumo completo
  - `resumo_colunas.csv`: uma linha por coluna (tipo, nulos, valores únicos, estatísticas)
  - `graficos/`: histogramas, boxplots, mapa de correlação e gráfico de nulos

## Passo 2: ler o relatório com atenção

Abra `relatorio.md` e os gráficos. Verifique, nesta ordem:

1. **Tamanho e tipos:** quantas linhas e colunas, e se algum tipo está errado (ex.: número lido como texto, data lida como texto).
2. **Nulos:** colunas com mais de 5% de ausentes merecem atenção; acima de 40%, questione se a coluna é útil.
3. **Duplicados:** linhas repetidas por inteiro.
4. **Outliers (regra do IQR):** valores fora de Q1 − 1,5×IQR e Q3 + 1,5×IQR. Diga se parecem erro de digitação ou casos reais.
5. **Distribuições:** assimetria forte, valores impossíveis (idade negativa, percentual acima de 100).
6. **Correlações:** pares com |r| ≥ 0,7. Lembre que correlação não é causalidade.
7. **Colunas categóricas:** categorias com grafias diferentes para a mesma coisa (ex.: "Natal", "natal", "NATAL").

## Passo 3: confirmar o contexto

Se não estiver claro, pergunte à pessoa antes de concluir:
- O que cada coluna significa, quando o nome não for óbvio.
- Se existe uma variável-alvo (o que ela quer prever ou explicar).

## Passo 4: entregar o resultado

Responda em português, em linguagem simples, com esta estrutura:

1. **Visão geral** (2 ou 3 frases sobre o dataset)
2. **5 principais achados**, cada um com o número que o sustenta
3. **Problemas de qualidade** encontrados (nulos, duplicados, tipos, outliers, inconsistências)
4. **Próximos passos sugeridos** para a limpeza, com o código pandas de cada um

## Regras

- Nunca altere nem sobrescreva o arquivo original. Sugira o tratamento e só aplique se a pessoa pedir, salvando em um arquivo novo.
- Não remova outliers automaticamente: explique e deixe a decisão para a pessoa.
- Se o dataset tiver dados pessoais (CPF, nome, telefone, endereço), avise e não reproduza esses valores na resposta.
- Mostre números com vírgula decimal, no padrão brasileiro, no texto da resposta.
