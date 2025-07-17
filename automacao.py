import requests
from bs4 import BeautifulSoup
import pymysql
from datetime import datetime
import yagmail
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

URL = "https://www.stuttgart.com.br/bomboniere/barras-de-chocolate.html"
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "pascoa"
}
EMAIL = os.getenv("EMAIL")
SENHA = os.getenv("SENHA")

# Fazer scraping dos produtos
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

produtos = []
for item in soup.select(".product-item-info"):
    nome_tag = item.select_one(".product.name a")
    preco_tag = item.select_one(".price")

    if nome_tag and preco_tag:
        nome = nome_tag.text.strip()
        preco = preco_tag.text.strip()
        produtos.append((nome, preco))

# Salvar no banco de dados
conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chocolates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_produto VARCHAR(255),
    preco VARCHAR(50),
    data_coleta DATETIME
)
""")

data_coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for nome, preco in produtos:
    cursor.execute(
        "INSERT INTO chocolates (nome_produto, preco, data_coleta) VALUES (%s, %s, %s)",
        (nome, preco, data_coleta)
    )

conn.commit()
cursor.close()
conn.close()

# Montar HTML do e-mail
tabela_html = "".join(
    f"<tr><td>{nome}</td><td>{preco}</td></tr>" for nome, preco in produtos
)

html_email = f"""
<h2>🐣 Feliz Páscoa!</h2>
<p>Confira abaixo as barras de chocolate disponíveis na Stuttgart:</p>
<table border="1" cellpadding="5" cellspacing="0">
    <tr><th>Produto</th><th>Preço</th></tr>
    {tabela_html}
</table>
<p>Data da coleta: {data_coleta}</p>
<p><a href="{URL}">🔗 Acesse a loja Stuttgart</a></p>
"""

# Enviar o e-mail
yag = yagmail.SMTP(EMAIL, SENHA)
yag.send(
    to=EMAIL,
    subject="🐰 Ofertas de Páscoa - Chocolates Stuttgart",
    contents=html_email
)

print("✅ E-mail enviado com sucesso!")
