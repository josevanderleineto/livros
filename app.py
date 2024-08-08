import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Carregar a planilha de livros
@st.cache_data
def load_books(file_path):
    return pd.read_excel(file_path)

# Use o caminho correto do arquivo
books_df = load_books("VENDA_DE_LIVROS.xlsx")

# Ajustar o nome da coluna conforme necessário
book_titles = books_df['TÍTULO DO LIVRO'].tolist()

# Configurar a conexão com o banco de dados SQLite
conn = sqlite3.connect('vendas_livros.db')
c = conn.cursor()

# Criar a tabela de vendas se ela não existir
c.execute('''
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        data DATE,
        quantidade INTEGER,
        preco REAL
    )
''')
conn.commit()

# Título da página
st.title('Registro de Vendas de Livros')

# Formulário para registrar a venda de um livro
with st.form(key='venda_form'):
    titulo = st.selectbox('Selecione o Título do Livro', book_titles)
    data = st.date_input('Data da Venda', datetime.today())
    quantidade = st.number_input('Quantidade Vendida', min_value=1, step=1)
    preco = st.number_input('Preço Unitário (R$)', min_value=0.0, step=0.01)
    submit_button = st.form_submit_button(label='Registrar Venda')

    if submit_button:
        c.execute('INSERT INTO vendas (titulo, data, quantidade, preco) VALUES (?, ?, ?, ?)', 
                  (titulo, data, quantidade, preco))
        conn.commit()
        st.success('Venda registrada com sucesso!')

# Calcular e exibir o total de vendas por livro
total_vendas = pd.read_sql_query('SELECT titulo, SUM(quantidade * preco) as total FROM vendas GROUP BY titulo', conn)

# Calcular e exibir o total de livros vendidos e o total de valores pagos
totais = pd.read_sql_query('SELECT SUM(quantidade) as total_livros, SUM(quantidade * preco) as total_valor FROM vendas', conn)

st.subheader('Total de Vendas por Livro')
st.dataframe(total_vendas)

# Verificar se os valores são None e definir como 0 se for o caso
total_livros_vendidos = totais['total_livros'].iloc[0] if totais['total_livros'].iloc[0] is not None else 0
total_valor_recebido = totais['total_valor'].iloc[0] if totais['total_valor'].iloc[0] is not None else 0

st.subheader('Total de Livros Vendidos e Valor Total Recebido')
st.write(f"Total de Livros Vendidos: {total_livros_vendidos}")
st.write(f"Valor Total Recebido: R$ {total_valor_recebido:.2f}")

# Fechar a conexão com o banco de dados
conn.close()
