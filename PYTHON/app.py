import streamlit as st
import psycopg2 as pg
import pandas as pd
from datetime import date
import time
from configs.settings import get_db_config

st.set_page_config(layout="wide", page_title="Sistema de Dívidas")

def init_connection():
    config = get_db_config()
    return pg.connect(**config)

def check_password():
    """Retorna True se o login for bem sucedido"""
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        return False
    
    elif not st.session_state["password_correct"]:
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        st.error("😕 Usuário ou senha incorretos")
        return False
    
    else:
        return True

def main_app():
    if st.sidebar.button("Sair / Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

    conn = init_connection()

    tb_carro_sql = 'SELECT * FROM PUBLIC."TB_CARRO"'
    tb_notebook_sql = 'SELECT * FROM PUBLIC."TB_NOTEBOOK"'

    df_carro = pd.read_sql_query(tb_carro_sql, conn)
    df_notebook = pd.read_sql_query(tb_notebook_sql, conn)

    st.title('Pagamentos de Dívidas')

    with st.expander("➕ Adicionar Novo Pagamento", expanded=False):
        with st.form("form_pagamento"):
            col_form1, col_form2, col_form3, col_form4 = st.columns(4)
            
            with col_form1:
                tipo_divida = st.selectbox("Qual dívida?", ["Carro", "Notebook"])

            with col_form2:
                novo_id = st.number_input("ID", min_value=0, format="%i")
            
            with col_form3:
                data_input = st.date_input("Data do Pagamento", value=date.today())
            
            with col_form4:
                valor_input = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

            submitted = st.form_submit_button("Salvar Pagamento")

            if submitted:
                try:
                    cursor = conn.cursor()

                    if tipo_divida == "Carro":
                        query = 'INSERT INTO PUBLIC."TB_CARRO" ("id_carro", "Mês", "pagamento") VALUES (%s, %s, %s)'
                    else:
                        query = 'INSERT INTO PUBLIC."TB_NOTEBOOK" ("id_notebook", "Mês", "pagamento") VALUES (%s, %s, %s)'

                    cursor.execute(query, (novo_id, data_input, valor_input))

                    conn.commit()
                    cursor.close()
                    
                    st.success(f"Pagamento de {tipo_divida} salvo com sucesso!")
                    time.sleep(1)
                    st.rerun() 

                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    lista_meses = df_carro['Mês'].unique().tolist()

    opcao_mes = st.sidebar.selectbox(
        'Selecione o Mês:',
        options=['Todos'] + lista_meses
    )

    if opcao_mes != 'Todos':
        df_carro_filtrado = df_carro[df_carro['Mês'] == opcao_mes]
        df_notebook_filtrado = df_notebook[df_notebook['Mês'] == opcao_mes]
    else:
        df_carro_filtrado = df_carro
        df_notebook_filtrado = df_notebook

    v_carro = 22000
    v_notebook = 1010.4
    coluna_valor = 'pagamento'

    pago_carro = df_carro[coluna_valor].sum()
    pago_notebook = df_notebook[coluna_valor].sum()

    falta_carro = v_carro - pago_carro
    falta_notebook = v_notebook - pago_notebook

    pct_carro = pago_carro / v_carro if v_carro > 0 else 0
    pct_notebook = pago_notebook / v_notebook if v_notebook > 0 else 0

    pct_carro = min(pct_carro, 1.0)
    pct_notebook = min(pct_notebook, 1.0)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.subheader("Acompanhamento mensal")

    with col2:
        st.metric(label="Falta Carro", value=f"R$ {falta_carro:,.2f}")
        st.progress(pct_carro, text=f"Pago: {pct_carro:.1%}")

    with col3:
        st.metric(label="Falta Notebook", value=f"R$ {falta_notebook:,.2f}")
        st.progress(pct_notebook, text=f"Pago: {pct_notebook:.1%}")

    st.divider()

    col_tab1, col_tab2 = st.columns(2)

    with col_tab1:
        st.subheader("🚗 Tabela Carro")
        st.dataframe(df_carro_filtrado, hide_index=True, use_container_width=True)
        total_view_carro = df_carro_filtrado[coluna_valor].sum()
        st.markdown(f"**Total neste período:** :green[R$ {total_view_carro:,.2f}]")

    with col_tab2:
        st.subheader("💻 Tabela Notebook")
        st.dataframe(df_notebook_filtrado, hide_index=True, use_container_width=True)
        total_view_notebook = df_notebook_filtrado[coluna_valor].sum()
        st.markdown(f"**Total neste período:** :green[R$ {total_view_notebook:,.2f}]")

    conn.close()

if check_password():
    main_app()