# Automação de Transferência Patrimonial

Sistema desenvolvido em Python para otimização do processo de movimentação de bens.  A ferramenta realiza o tratamento de dados patrimoniais, agrupamento de números por classificação contábil e segue o formato de site de pesquisa múltipla,  respeitando 6 dígitos incluindo o 0, com números combinados separados por vírgula e espaço, por exemplo: 012345, 012346

## Funcionalidades

- **Normalização de Dados:** Conversão automática de números de patrimônio para o padrão de 6 dígitos.
- **Tratamento de Exceções:** Limpeza de sufixos de ponto flutuante (.0) e preenchimento de campos nulos.
- **Divisão por Blocos:** Segmentação de listas extensas em blocos menores para compatibilidade com campos de busca no sistema.
- **Sistema de Log:** Registro detalhado de operações e erros em arquivo local (`patrimonio_log.txt`).
- **Exportação:** Opção de download de cada bloco em formato `.txt`.

## Pré-requisitos

Para rodar a aplicação, é necessário ter o Python instalado e as seguintes bibliotecas:

- pandas
- streamlit
- openpyxl (para leitura de arquivos Excel)

```bash
pip install pandas streamlit openpyxl
