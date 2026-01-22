import pandas as pd
import streamlit as st
import logging
import sys
#import io


# 1.1. Configuração do Logger
logger = logging.getLogger(__name__)

if not logger.handlers:
    logger.setLevel(logging.INFO)
    
    FORMATO_LOG = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    cabecalho = logging.StreamHandler(sys.stdout)
    cabecalho.setFormatter(FORMATO_LOG)
    logger.addHandler(cabecalho)

    
    try:      
        cabecalho_arquivo = logging.FileHandler('patrimonio_log.txt', encoding='utf-8') 
        cabecalho_arquivo.setFormatter(FORMATO_LOG)
        logger.addHandler(cabecalho_arquivo)
    except Exception as e:
        logger.warning(f"Não foi possível criar o arquivo de log: {e}")

# 1.2. Constantes de nomes de colunas
COLUNA_CLASSIFICACAO = 'Classificacao_Contabil'
COLUNA_PATRIMONIO = 'Numero_Patrimonio'
VALOR_CLASSIFICACAO_AUSENTE = 'CLASSIFICACAO_NAO_INFORMADA'

# 2. Envio e tratamento dos dados

def processar_patrimonios_para_transferencia(df_entrada: pd.DataFrame, limite_bloco: int):
   
    # Agrupa os números de patrimônio por Classificação Contábil.

    total_itens = len(df_entrada)
    logger.info(f"Ação: INÍCIO DO PROCESSO | Total Itens: {total_itens} | Limite Bloco: {limite_bloco}")

    
    # Validação de Colunas
    colunas_entrada = {COLUNA_CLASSIFICACAO, COLUNA_PATRIMONIO}
    if not colunas_entrada.issubset(set(df_entrada.columns)):
        logger.error(f"Ação: FALHA NA VALIDAÇÃO | Detalhe: Colunas obrigatórias ausentes.")
        st.error(f"O DataFrame deve conter as colunas exatas: '{COLUNA_CLASSIFICACAO}' e '{COLUNA_PATRIMONIO}'.")
        return None 

    # Tratamento da coluna Numero de Patrimônio para formato de 6 dígitos
    try:
        df_entrada[COLUNA_PATRIMONIO] = df_entrada[COLUNA_PATRIMONIO].astype(str).str.split('.').str[0].str.zfill(6)
        logger.info(f"Ação: FORMATAR PATRIMÔNIO | Detalhe: Coluna '{COLUNA_PATRIMONIO}' formatada com 6 dígitos.")
    except Exception as e:
        logger.exception(f"Ação: ERRO CRÍTICO | Detalhe: Falha ao formatar '{COLUNA_PATRIMONIO}'.")
        st.error(f"Erro CRÍTICO ao formatar a coluna '{COLUNA_PATRIMONIO}'. Detalhe: {e}")
        return None

    # Tratamento da Coluna de Classificação, se houver necessidade
    try:
        df_entrada[COLUNA_CLASSIFICACAO] = df_entrada[COLUNA_CLASSIFICACAO]\
            .fillna(VALOR_CLASSIFICACAO_AUSENTE)\
            .astype(str)
        df_entrada[COLUNA_CLASSIFICACAO] = df_entrada[COLUNA_CLASSIFICACAO].str.replace(r'\.0$', '', regex=True).str.strip()
        logger.info(f"Ação: LIMPAR CLASSIFICAÇÃO | Detalhe: Coluna '{COLUNA_CLASSIFICACAO}' tratada (NaN e .0 removidos).")
    except Exception as e:
        logger.exception(f"Ação: ERRO CRÍTICO | Detalhe: Falha ao limpar '{COLUNA_CLASSIFICACAO}'.")
        st.error(f"Erro ao tratar a coluna de classificação. Detalhe: {e}")
        return None


    # 2.4. Agrupamento e Geração de Blocos (AJUSTADO PARA O LOG)
    grupos_por_classificacao = df_entrada.groupby(COLUNA_CLASSIFICACAO)[COLUNA_PATRIMONIO].apply(list).to_dict()
    logger.info(f"Ação: AGRUPAMENTO | Classificações Únicas: {len(grupos_por_classificacao)}.")
    
    estrutura_saida = {}
    
    for classificacao_key, lista_patrimonios in grupos_por_classificacao.items():
        
        blocos_limitados = [
            lista_patrimonios[i:i + limite_bloco]
            for i in range(0, len(lista_patrimonios), limite_bloco)
        ]
        
        blocos_para_classificacao = []
        total_blocos = len(blocos_limitados)
        total_itens_classif = len(lista_patrimonios)

        logger.info(f"Ação: PROCESSAR CLASSIFICAÇÃO | Classificação: {classificacao_key.upper()} | Itens: {total_itens_classif} | Blocos Gerados: {total_blocos}")
        
        for indice_bloco, bloco_patrimonios in enumerate(blocos_limitados):
            
            string_patrimonios = ", ".join(bloco_patrimonios)
            
            if total_blocos == 1:
                nome_bloco_log = "ÚNICO"
                nome_bloco_display = "Bloco de Itens"
                indice_total_display = f"({total_itens_classif} itens)"
            else:
                nome_bloco_log = f"{indice_bloco+1}/{total_blocos}"
                nome_bloco_display = f"Bloco {indice_bloco+1}"
                indice_total_display = f"{indice_bloco+1} de {total_blocos}"


            blocos_para_classificacao.append({
                'nome_bloco': nome_bloco_display,
                'string_dados': string_patrimonios,
                'contagem_itens': len(bloco_patrimonios),
                'indice_total': indice_total_display
            })
                        
            logger.info(f"Ação: GERAR BLOCO | Classificação: {classificacao_key.upper()} | Bloco: {nome_bloco_log} | Itens: {len(bloco_patrimonios)}")

        estrutura_saida[classificacao_key] = {
            'total_itens_classificacao': total_itens_classif,
            'blocos': blocos_para_classificacao
        }
        
    logger.info("Ação: FIM DO PROCESSO | Detalhe: Processamento de todos os grupos concluído.")
    return estrutura_saida

# 3. Interface do usuário no streamlit
st.set_page_config(page_title="Automação de Transferência Patrimonial", layout="wide")

st.title("📦 Automação de Transferência Patrimonial")
st.markdown("Ferramenta para agrupar e formatar números de patrimônio por Classificação Contábil em blocos limitados.")

# 3.1. Barra Lateral de Configurações
st.sidebar.header("⚙️ Configurações")

limite_bloco = st.sidebar.number_input(
    "Limite de Bens por Bloco:", 
    min_value=1, 
    max_value=2000, 
    value=400, 
    step=50,
    help="Define o número máximo de patrimônios por string de pesquisa."
)

st.sidebar.markdown("""
**Instruções da Planilha:**
1. O arquivo deve ser CSV ou XLSX.
2. Deve conter as colunas com os **nomes exatos**: `Classificacao_Contabil` e `Numero_Patrimonio`.
""")

# 3.2. Upload do Arquivo
uploaded_file = st.file_uploader("Faça o upload do arquivo de Patrimônio (CSV ou Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    
    logger.info(f"Ação: UPLOAD | Detalhe: Arquivo carregado: {uploaded_file.name}")
    df_dados = None

    try:
        if uploaded_file.name.endswith('.csv'):
            uploaded_file.seek(0)
            try: df_dados = pd.read_csv(uploaded_file, encoding='utf-8')
            except: df_dados = pd.read_csv(uploaded_file, encoding='latin-1')
        elif uploaded_file.name.endswith('.xlsx'):
            df_dados = pd.read_excel(uploaded_file)
            
        if df_dados is not None and df_dados.empty:
             st.error("O arquivo foi lido, mas não contém dados (DataFrame está vazio).")
             df_dados = None
        
    except Exception as e:
        logger.exception(f"Ação: ERRO CRÍTICO | Detalhe: Falha na leitura do arquivo.")
        st.error(f"Erro ao ler o arquivo: {e}")
        df_dados = None


    if df_dados is not None and not df_dados.empty:
        st.success(f"Arquivo '{uploaded_file.name}' lido com sucesso. Total de {len(df_dados)} itens.")
        
        estrutura_final = processar_patrimonios_para_transferencia(df_dados, limite_bloco)
        
        if estrutura_final is not None and len(estrutura_final) > 0:
            
            st.header("✅ Blocos Formatados por Classificação")
            st.info("Clique na Classificação para expandir e, em seguida, use o botão 'Copiar Bloco' para obter os dados.")

            # 3.4. Exibição da Saída 
            for classificacao_key, dados_classificacao in estrutura_final.items():
                
                total_itens = dados_classificacao['total_itens_classificacao']
                
                with st.expander(f"**{classificacao_key.upper()}** ({total_itens} itens totais)"):
                    
                    st.markdown(f"**Total de Blocos:** {len(dados_classificacao['blocos'])}")
                    
                    for bloco in dados_classificacao['blocos']:
                        
                        bloco_nome = bloco['nome_bloco']
                        dados_para_copia = bloco['string_dados']
                        contagem_itens = bloco['contagem_itens']
                        indice_total = bloco['indice_total'] # Novo campo
                        
                        col1, col2 = st.columns([0.7, 0.3])
                        
                        with col1:

                            # Título do Bloco agora mostra X de Y, ex: Bloco 1 de 3
                            st.caption(f"**{bloco_nome}** ({contagem_itens} itens) - ({indice_total})")
                            st.text_area(
                                label="Números de Patrimônio",
                                value=dados_para_copia,
                                height=150,
                                label_visibility="collapsed",
                                key=f"{classificacao_key}_{bloco_nome}"
                            )
                        
                        with col2:
                            st.download_button(
                                label=f"⬇️ Baixar Bloco em .txt ({contagem_itens})",
                                data=dados_para_copia,
                                file_name=f"{classificacao_key.replace(' ', '_')}_{bloco_nome.replace(' ', '_')}.txt",
                                mime="text/plain",
                                key=f"btn_copy_{classificacao_key}_{bloco_nome}"
                            )
                            st.markdown("**(Dica:** Você também pode copiar o conteúdo da caixa de texto ao lado.)")
                            
                    st.divider()
        
        elif estrutura_final is not None:
            st.warning("Nenhum bloco foi gerado. Verifique se o arquivo continha dados válidos nas colunas obrigatórias.")
    
else:
    st.info("Aguardando o upload da planilha para iniciar o processamento.")
    logger.info("Ação: INICIALIZAÇÃO | Detalhe: Aplicativo Streamlit iniciado. Aguardando arquivo.")