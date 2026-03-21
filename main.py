import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pymssql
import uuid
import json
from dotenv import load_dotenv
load_dotenv()


blobConnectionString = os.getenv('BLOB_CONNECTION_STRING')
blobContainerName = os.getenv('BLOB_CONTAINER_NAME')
bloboaccountName = os.getenv('BLOB_ACCOUNT_NAME')

SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USERNAME = os.getenv('SQL_USERNAME')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')

#Formulário de cadastro de produtos

st.title('Cadastro de Produtos')

product_name = st.text_input('Nome do Produto')
product_description = st.text_area('Descrição do Produto')
product_price = st.number_input('Preço do Produto', min_value=0.0, format='%.2f')
product_image = st.file_uploader('Imagem do Produto', type=['jpg', 'jpeg', 'png'])

#salvar produto no banco de dados e imagem no blob storage

def upload_image_to_blob(image_file):
    blob_service_client = BlobServiceClient.from_connection_string(blobConnectionString)
    container_client = blob_service_client.get_container_client(blobContainerName)
    blob_name = f'{uuid.uuid4()}_{image_file.name}'
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(image_file, overwrite=True)
    image_url =f'https://{bloboaccountName}.blob.core.windows.net/{blobContainerName}/{blob_name}'
    return image_url

def insert_product(product_name, product_description, product_price, product_image):
     try:
        image_url = upload_image_to_blob(product_image)
        conn = pymssql.connect(server=SQL_SERVER, database=SQL_DATABASE, user=SQL_USERNAME, password=SQL_PASSWORD)
        cursor = conn.cursor()
        insert_sql = ("INSERT INTO produtos (nome, descricao, preço, imagem_url) ") + ("VALUES (%s, %s, %s, %s)")
        print(insert_sql)
        cursor.execute(insert_sql, (product_name, product_description, product_price, image_url))
        conn.commit()
        cursor.close()
        conn.close()

        return True
     except Exception as e:
        st.error(f'Erro ao salvar produto: {e}')
        return False  

def list_products():
    try:
        conn = pymssql.connect(server=SQL_SERVER, database=SQL_DATABASE, user=SQL_USERNAME, password=SQL_PASSWORD)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, descricao, preço, imagem_url FROM produtos")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return products
    except Exception as e:
        st.error(f'Erro ao listar produtos: {e}')
        return []

def delete_all_products():
    try:
        conn = pymssql.connect(server=SQL_SERVER, database=SQL_DATABASE, user=SQL_USERNAME, password=SQL_PASSWORD)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos")
        conn.commit()
        cursor.close()
        conn.close()
        st.success('Lista de produtos limpa com sucesso!')
        return True
    except Exception as e:
        st.error(f'Erro ao limpar produtos: {e}')
        return False
    

def list_products_screen():
    products = list_products()
    print(products)
    if products:
        cards_por_linha = 3
        cools = st.columns(cards_por_linha)
        for i, product in enumerate(products):
            col = cools[i % cards_por_linha]
            with col:
                st.markdown(f"### {product[1]}")
                st.write(f"**Descrição:** {product[2]}")
                st.write(f"**Preço:** R$ {product[3]:.2f}")
                if product[4]:
                    html_img = f'<img src="{product[4]}" alt="{product[1]}" style="width:100%; height:auto;">'
                    st.markdown(html_img, unsafe_allow_html=True)
                st.markdown("---")
        if (i + 1) % cards_por_linha != 0 and (i + 1) == len(products):
            cols = st.columns(cards_por_linha)      
     
        else:
         st.info('Nenhum produto cadastrado.')

if st.button('Salvar Produto'):
    return_message = 'Produto salvo com sucesso!'
    list_products_screen()

    insert_product(product_name, product_description, product_price, product_image)
    return_message = 'Produto salvo com sucesso!'

st.header('Produtos Cadastrados')
  
if st.button('Listar Produtos'):
    list_products_screen()
    return_message = 'Produtos listados com sucesso!'

if st.button('Limpar Lista de Produtos', key='clear_products'):
    delete_all_products()

