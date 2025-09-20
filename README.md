# 🚀 Wind Turbine Data Pipeline - Apache Airflow Project

Este projeto foi desenvolvido como um pipeline de engenharia de dados utilizando **Apache Airflow**, com o objetivo de monitorar dados de turbinas eólicas, validar a temperatura e armazenar os dados em um banco de dados PostgreSQL. Além disso, o pipeline envia alertas por e-mail em casos de temperatura elevada.

---

## 📌 Visão Geral

O pipeline realiza as seguintes etapas:

1. **Sensor de Arquivo**: Aguarda a presença de um arquivo JSON contendo os dados da turbina.
2. **Extração e Processamento**: Lê os dados do arquivo e extrai informações específicas como:
   - `idtemp`
   - `powerfactor`
   - `hydraulicpressure`
   - `temperature`
   - `timestamp`
3. **Validação de Temperatura**: Verifica se a temperatura está acima de 24°C e:
   - Envia um alerta se estiver acima do limite.
   - Envia uma notificação padrão caso contrário.
4. **Armazenamento**: Cria uma tabela (caso não exista) e insere os dados no PostgreSQL.

---

## 🧠 Tecnologias Utilizadas

- [Apache Airflow](https://airflow.apache.org/)
- Python
- PostgreSQL
- SMTP (Gmail)
- Docker (opcional)
- JSON

---

## 📁 Estrutura do Projeto

```
├── dags/
│   └── windturbine.py
├── data/
│   └── data.json
└── README.md
```

---

## 📸 Pipeline (DAG)

![Pipeline DAG](/image_pipeline/pipeline_windturbine.png)

---

## 🔧 Configurações Necessárias no Airflow

### 🔐 Variáveis

Crie a seguinte variável no **Airflow UI**:

- `path_file`: `/opt/airflow/data/data.json`

### 🔗 Conexões

1. **fs_default**

   - Tipo: `Filesystem`
   - Caminho (Path): `/opt/airflow/data`

2. **postgres**

   - Tipo: `Postgres`
   - Configure com seu host, porta, login e senha do banco.

3. **gmail_smtp**
   - Tipo: `SMTP`
   - Host: `smtp.gmail.com`
   - Porta: `465`
   - Login: `seu_email@gmail.com`
   - Senha: `senha de app`
   - TLS: Desativado
   - SSL: Ativado
   - From Email: seu_email@gmail.com

---

## 📄 Exemplo de JSON de Entrada

```json
{
  "idtemp": "001",
  "powerfactor": "0.98",
  "hydraulicpressure": "55",
  "temperature": "26",
  "timestamp": "2025-07-12T18:00:00"
}
```

---

## 📬 Notificações por E-mail

O pipeline envia dois tipos de notificações:

- **Alerta de Temperatura**: Caso a temperatura seja igual ou superior a 24°C.
- **Mensagem Padrão**: Caso a temperatura esteja dentro do esperado.

---

## 🧪 Como Testar

1. Adicione um arquivo `data.json` no diretório monitorado (`/opt/airflow/data`).
2. Execute a DAG manualmente pelo Airflow UI.
3. Verifique o recebimento dos e-mails e os dados inseridos no banco PostgreSQL.

---

## 📃 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 👨‍💻 Autor

Dilley Andrade | Data engineer (81) 98663-2609 | dilleyandrade@gmail.com | linkedin.com/in/dilleyandrade | github.com/DilleyAndrade
