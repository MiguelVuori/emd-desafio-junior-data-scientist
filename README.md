# Desafio Técnico - Cientista de Dados Júnior

## Descrição

O projeto está dividido da seguinte forma:
- No arquivo "requirements.txt" contém as bibliotecas necessárias para a visualização do dashboard.
- O arquivo "analise_sql.sql" contém todas as consultas realizadas no BigQuery.
- O arquivo "analise_python.ipynb" contém todas as consultas utilizando a biblioteca pandas do python.
- "streamlit_app.py" é o aplicativo em python utlizado para a visualização dos dados (Dashboard).

## Visualização

Para visualizar os dados no dashboard é necessário seguir os seguintes passos:
- Clone o repositório
- Instale as bibliotecas presentes no arquivo "requirements.txt"
- Utilize o comando "streamlit run streamlit_app.py" para rodar o aplicativo

## Observação

Talvez seja necessário criar uma conta no Google Cloud Platform (GCP), para acessar os dados do BigQuery. Depois de criada substitua a id do projeto
nas linhas 25-27 do arquivo "streamlit_app.py" no parâmetro "billing_project_id".
