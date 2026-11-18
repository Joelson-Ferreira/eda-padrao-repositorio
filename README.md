# EDA padrão: skill do Claude para análise exploratória de dados

Uma skill que ensina o Claude a fazer **análise exploratória de dados (EDA) sempre do mesmo jeito**, em português, com um relatório completo e gráficos.

Você envia um CSV ou uma planilha e pede algo como *"faça uma EDA desses dados"*. O Claude roda o roteiro da skill e devolve:

- visão geral do dataset (linhas, colunas, tipos)
- nulos e duplicados por coluna
- outliers pela regra do IQR
- distribuições (histogramas e boxplots)
- correlações fortes (mapa de calor)
- categorias com grafias diferentes para o mesmo valor (ex.: "Natal", "natal", "NATAL ")
- 5 principais achados e os próximos passos de limpeza, com o código pandas

O arquivo original **nunca é alterado**.

## Estrutura

```
eda-padrao.zip                # a skill pronta para instalar no Claude
eda-padrao/
├── SKILL.md                  # instruções que o Claude segue
└── scripts/
    └── perfil_dataset.py     # gera o relatório e os gráficos
exemplo/
├── dados_teste.csv           # base de teste "suja", de propósito
└── relatorio_eda/            # relatório gerado a partir dela
```

## Como instalar

### No Claude (web, desktop ou celular)

1. Ative a execução de código nas configurações do Claude (as skills precisam dela).
2. Baixe o arquivo `eda-padrao.zip`, já pronto para instalar, na [página da versão mais recente](https://github.com/Joelson-Ferreira/eda-padrao-repositorio/releases/latest). Ele também está na raiz deste repositório.
3. No Claude, abra **Customize > Skills** e envie o ZIP.
4. Ative a skill e envie um dataset pedindo uma análise exploratória.

### No Claude Code

Copie a pasta para o diretório de skills:

```bash
# para todos os seus projetos
cp -r eda-padrao ~/.claude/skills/

# só para um projeto
cp -r eda-padrao .claude/skills/
```

## Usar o script sem o Claude

O script também funciona sozinho:

```bash
pip install pandas matplotlib openpyxl
python eda-padrao/scripts/perfil_dataset.py meus_dados.csv --saida relatorio_eda
python eda-padrao/scripts/perfil_dataset.py planilha.xlsx --aba "Plan1" --saida relatorio_eda
```

Para CSV, ele detecta sozinho o separador (`,` ou `;`) e a codificação (`utf-8` ou `latin-1`, comum em dados públicos brasileiros).

## Segurança

Antes de instalar qualquer skill, inclusive esta, leia o `SKILL.md` e os scripts. Skills rodam instruções e código dentro da sua conversa com o Claude.

## Autor

Joelson Ferreira · [joelsonferreira.com.br](https://joelsonferreira.com.br) · Instagram [@joelsonferreirati](https://instagram.com/joelsonferreirati)
