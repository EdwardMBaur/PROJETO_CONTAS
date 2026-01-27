import streamlit as st
import psycopg2 as pg
import pandas as pd
from datetime import date
import time
from configs.settings import get_db_config
from Extract.Extract import Extract
from configs import paths

st.set_page_config(layout="wide", page_title="Sistema de Dívidas")

SPREADSHEET_ID = paths.SHEET

def init_connection():
    config = get_db_config()
    return pg.connect(**config)

def check_password():
    """Verifica login e salva o TIPO_PERFIL na sessão"""
    if st.session_state.get("password_correct"):
        return True

    st.subheader("🔐 Acesso ao Sistema")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username_input = st.text_input("Usuário (Nome)", key="login_user")
        password_input = st.text_input("Senha", type="password", key="login_pass")
        btn_entrar = st.button("Entrar")

    if btn_entrar:
        try:
            conn = init_connection()
            cursor = conn.cursor()
            query = """
                SELECT SENHA, TIPO_PERFIL, NOME 
                FROM PUBLIC.TB_USUARIOS 
                WHERE NOME = %s AND ATIVO = TRUE
            """
            cursor.execute(query, (username_input,))
            result = cursor.fetchone()
            conn.close()

            if result:
                db_password = result[0]
                db_tipo_perfil = result[1]
                db_nome = result[2]

                if password_input == db_password:
                    st.session_state["password_correct"] = True
                    st.session_state["user_type"] = db_tipo_perfil # 1 = Admin
                    st.session_state["user_name"] = db_nome
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Usuário não encontrado ou inativo.")
        except Exception as e:
            st.error(f"Erro de conexão no login: {e}")

    return False

def page_usuarios():
    st.title("👥 Gerenciar Usuários")

    if st.session_state.get("user_type") != 1:
        st.error("⛔ Acesso Negado. Você não tem permissão para ver esta página.")
        return

    tab_cad, tab_ger = st.tabs(["➕ Cadastrar Novo", "⚙️ Gerenciar (Status/Excluir)"])

    with tab_cad:
        st.markdown("### Novo Usuário")
        with st.form("form_new_user"):
            c1, c2 = st.columns(2)
            with c1:
                new_nome = st.text_input("Nome do Usuário")
                new_pass = st.text_input("Senha", type="password")
            with c2:
                tipo_visual = st.selectbox("Tipo de Perfil", ["Administrador (1)", "Visualizador (2)"])
            
            if st.form_submit_button("Salvar Usuário"):
                if new_nome and new_pass:
                    val_tipo = 1 if "Administrador" in tipo_visual else 2

                    conn = init_connection()
                    cursor = conn.cursor()
                    try:
                        q_insert = """
                            INSERT INTO PUBLIC.TB_USUARIOS (NOME, SENHA, TIPO_PERFIL) 
                            VALUES (%s, %s, %s)
                        """
                        cursor.execute(q_insert, (new_nome, new_pass, val_tipo))
                        conn.commit()
                        st.success(f"Usuário {new_nome} criado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")
                    finally:
                        conn.close()
                else:
                    st.warning("Preencha Nome e Senha.")

    with tab_ger:
        st.markdown("### Alterar ou Remover Usuário")

        c_input1, c_input2, c_null_i3, c_null_i4 = st.columns(4)
        with c_input1:
            id_action = st.number_input("ID do Usuário", min_value=1, format="%i", help="Olhe a tabela abaixo para ver o ID")
        
        st.markdown("")

        c_btn_status, c_btn_del, c_null_b3, c_null_b4 = st.columns(4)

        with c_btn_status:
            if st.button("🔄 Ativar / Desativar", use_container_width=True):
                conn = init_connection()
                cursor = conn.cursor()
                try:
                    q_toggle = 'UPDATE PUBLIC.TB_USUARIOS SET ATIVO = NOT ATIVO WHERE ID = %s'
                    cursor.execute(q_toggle, (id_action,))
                    rows = cursor.rowcount
                    conn.commit()
                    
                    if rows > 0:
                        st.success(f"Status do ID {id_action} alterado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("ID não encontrado.")
                except Exception as e:
                    st.error(f"Erro: {e}")
                finally:
                    conn.close()

        with c_btn_del:
            if st.button("🗑️ Excluir Permanentemente", type="primary", use_container_width=True):
                if st.session_state.get('user_name') == id_action: 
                     st.error("Você não pode deletar a si mesmo enquanto logado.")
                else:
                    conn = init_connection()
                    cursor = conn.cursor()
                    try:
                        q_del = 'DELETE FROM PUBLIC.TB_USUARIOS WHERE ID = %s'
                        cursor.execute(q_del, (id_action,))
                        rows = cursor.rowcount
                        conn.commit()
                        
                        if rows > 0:
                            st.success(f"Usuário ID {id_action} deletado!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("ID não encontrado.")
                    except Exception as e:
                        st.error(f"Erro ao deletar: {e}")
                    finally:
                        conn.close()

    st.markdown("---")
    st.subheader("Lista de Usuários")
    conn = init_connection()
    try:
        query_list = 'SELECT ID, NOME, TIPO_PERFIL, ATIVO, CRIADO_EM FROM PUBLIC.TB_USUARIOS ORDER BY ID'
        df_users = pd.read_sql_query(query_list, conn)

        st.dataframe(
            df_users, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "ATIVO": st.column_config.CheckboxColumn(
                    "Ativo?",
                    help="Indica se o usuário pode logar no sistema",
                )
            }
        )
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
    finally:
        conn.close()

def page_dividas():
    conn = init_connection()
    try:
        tb_carro_sql = 'SELECT * FROM PUBLIC."TB_CARRO" ORDER BY "id_carro"'
        tb_notebook_sql = 'SELECT * FROM PUBLIC."TB_NOTEBOOK"' 
        
        df_carro = pd.read_sql_query(tb_carro_sql, conn)
        df_notebook = pd.read_sql_query(tb_notebook_sql, conn)

        if not df_notebook.empty:
            coluna_id_note = df_notebook.columns[0]
            df_notebook = df_notebook.sort_values(by=coluna_id_note)

    except Exception as e:
        st.error(f"Erro ao ler tabelas. Verifique se as colunas 'id_carro' existem: {e}")
        df_carro = pd.DataFrame()
        df_notebook = pd.DataFrame()

    st.title('Pagamentos de Dívidas')
    
    is_admin = st.session_state.get("user_type") == 1

    if is_admin:
        tab_add, tab_del = st.tabs(["➕ Adicionar Pagamento", "🗑️ Remover Pagamento"])

        with tab_add:
            st.markdown("### Preencha os dados:")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                tipo_divida = st.selectbox("Qual dívida?", ["Carro", "Notebook"])
                sheet_tab_name = "CARRO" if tipo_divida == "Carro" else "NOTEBOOK"
            with c2:
                novo_id = st.number_input("ID / Mês", min_value=1, format="%i")
            with c3:
                data_input = st.date_input("Data do Pagamento", value=date.today())
            with c4:
                valor_input = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

            st.markdown("")

            c_btn1, c_btn2, c_vazia3, c_vazia4 = st.columns(4)

            with c_btn1:
                if st.button("💾 Salvar (BD)", use_container_width=True):
                    try:
                        cursor = conn.cursor()
                        if tipo_divida == "Carro":
                            query = 'INSERT INTO PUBLIC."TB_CARRO" ("id_carro", "Mês", "pagamento") VALUES (%s, %s, %s)'
                        else:
                            query = 'INSERT INTO PUBLIC."TB_NOTEBOOK" ("id_notebook", "Mês", "pagamento") VALUES (%s, %s, %s)'

                        cursor.execute(query, (novo_id, data_input, valor_input))
                        conn.commit()
                        cursor.close()
                        st.success(f"✅ ID {novo_id} salvo!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro SQL: {e}")

            with c_btn2:
                if st.button("📊 Salvar (Planilha)", use_container_width=True):
                    try:
                        data_formatada = data_input.strftime("%d/%m")
                        valor_str = f"{valor_input:,.2f}"
                        valor_br = valor_str.replace(',', 'X').replace('.', ',').replace('X', '.')
                        valor_final = f"R$ {valor_br}"
                        dados_para_planilha = [novo_id, valor_final, data_formatada]
                        
                        st.info("Enviando...")
                        Extract.add_row(SPREADSHEET_ID, sheet_tab_name, dados_para_planilha)
                        st.success(f"✅ Enviado!")
                    except Exception as e:
                        st.error(f"Erro Planilha: {e}")

        with tab_del:
            st.warning("Selecione o ID e escolha onde deseja deletar.")
            c_del1, c_del2, c_del3, c_del4 = st.columns(4)
            with c_del1:
                tipo_del = st.selectbox("Dívida para remover", ["Carro", "Notebook"], key="sel_del")
                sheet_tab_del = "CARRO" if tipo_del == "Carro" else "NOTEBOOK"
            with c_del2:
                id_to_del = st.number_input("ID para remover", min_value=0, format="%i", key="num_del")
            
            st.markdown("")

            c_btn_del1, c_btn_del2, c_vazia_del3, c_vazia_del4 = st.columns(4)

            with c_btn_del1:
                if st.button("🗑️ Deletar (BD)", type="primary", use_container_width=True):
                    conn_del = init_connection()
                    cursor_del = conn_del.cursor()
                    try:
                        tabela = 'PUBLIC."TB_CARRO"' if tipo_del == "Carro" else 'PUBLIC."TB_NOTEBOOK"'
                        coluna_id = 'id_carro' if tipo_del == "Carro" else 'id_notebook'
                        
                        cursor_del.execute(f'DELETE FROM {tabela} WHERE "{coluna_id}" = %s', (id_to_del,))
                        rows = cursor_del.rowcount
                        conn_del.commit()
                        if rows > 0:
                            st.success("Deletado!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("ID não encontrado.")
                    except Exception as e:
                        st.error(f"Erro SQL: {e}")
                    finally:
                        conn_del.close()

            with c_btn_del2:
                 if st.button("🗑️ Deletar (Panilha)", type="primary", use_container_width=True):
                    try:
                        sucesso = Extract.delete_row_by_id(SPREADSHEET_ID, sheet_tab_del, id_to_del, id_column_index=1)
                        if sucesso: st.success("Removido!")
                        else: st.warning("ID não encontrado.")
                    except Exception as e: st.error(f"Erro Planilha: {e}")
    else:
        st.info("👁️ Modo Visualização (Logue como Admin para editar)")

    if not df_carro.empty and not df_notebook.empty:
        lista_meses = df_carro['Mês'].unique().tolist()
        opcao_mes = st.sidebar.selectbox('Selecione o Mês:', options=['Todos'] + lista_meses)

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
        
        pct_carro = min(pago_carro / v_carro if v_carro > 0 else 0, 1.0)
        pct_notebook = min(pago_notebook / v_notebook if v_notebook > 0 else 0, 1.0)

        st.divider()
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1: st.subheader("Acompanhamento mensal")
        with col2:
            st.metric(label="Falta Carro", value=f"R$ {falta_carro:,.2f}")
            st.progress(pct_carro, text=f"Pago: {pct_carro:.1%}")
        with col3:
            st.metric(label="Falta Notebook", value=f"R$ {falta_notebook:,.2f}")
            st.progress(pct_notebook, text=f"Pago: {pct_notebook:.1%}")

        col_tab1, col_tab2 = st.columns(2)
        with col_tab1:
            st.subheader("🚗 Tabela Carro")
            st.dataframe(df_carro_filtrado, hide_index=True, use_container_width=True)
            st.markdown(f"**Total:** :green[R$ {df_carro_filtrado[coluna_valor].sum():,.2f}]")

        with col_tab2:
            st.subheader("💻 Tabela Notebook")
            st.dataframe(df_notebook_filtrado, hide_index=True, use_container_width=True)
            st.markdown(f"**Total:** :green[R$ {df_notebook_filtrado[coluna_valor].sum():,.2f}]")

    conn.close()

if check_password():
    user_name = st.session_state.get('user_name', 'Usuário')
    user_type = st.session_state.get('user_type', 2)

    st.sidebar.markdown(f"Olá, **{user_name}**")

    if user_type == 1:
        pagina_selecionada = st.sidebar.radio("Navegação:", ["💰 Dívidas", "👥 Gerenciar Usuários"])
    else:
        pagina_selecionada = "💰 Dívidas"
        st.sidebar.markdown("---")
        st.sidebar.caption("Visualização Limitada")

    if st.sidebar.button("Sair / Logout"):
        st.session_state["password_correct"] = False
        st.session_state["user_type"] = None
        st.rerun()

    if pagina_selecionada == "💰 Dívidas":
        page_dividas()
    elif pagina_selecionada == "👥 Gerenciar Usuários":
        page_usuarios()