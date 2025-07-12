from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import json
import os

def process_file(**kwarg):
    with open(Variable.get('path_file')) as document: #In the UI airflow create a variabla called path_file, with value /opt/airflow/data/data.json
        data = json.load(document)
        ti = kwarg['ti']
        ti.xcom_push(key='idtemp', value=data['idtemp'])
        ti.xcom_push(key='powerfactor', value=data['powerfactor'])
        ti.xcom_push(key='hydraulicpressure', value=data['hydraulicpressure'])
        ti.xcom_push(key='temperature', value=data['temperature'])
        ti.xcom_push(key='timestamp', value=data['timestamp'])
    os.remove(Variable.get('path_file'))

def temp_validator(**context):
    number_temp = float(context['ti'].xcom_pull(task_ids='get_data', key='temperature'))
    if number_temp >= 24:
        return 'group_check_temp.send_email_alert'
    else:
        return 'group_check_temp.send_email'

default_args = {
    'depends_on_past': False,
    'email': ['seu@email.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=10)
}

with DAG(
    'windturbine',
    description='Turbine datas',
    schedule=None,
    start_date=datetime(2025, 7, 10),
    catchup=False,
    default_args=default_args,
    doc_md='## Dag to register windturbines datas'
) as dag:

    file_sensor_task = FileSensor(
        task_id='file_sensor_task',
        filepath=Variable.get('path_file'),
        fs_conn_id='fs_default', #In the UI airflow create a fs connection called fs_default and connection type fs
        poke_interval=10,
        mode='reschedule'
    )


    get_data = PythonOperator(
        task_id='get_data',
        python_callable=process_file,
    )

    with TaskGroup('group_check_temp') as group_check_temp:
        check_temp_branch = BranchPythonOperator(
            task_id='check_temp_branch',
            python_callable=temp_validator
        )

        send_email_alert = EmailOperator(
            task_id='send_email_alert',
            to='dilleyandrade@gmail.com',
            subject='Airflow alert',
            html_content='''
                <h3>Temperature alert.</h3>
                <p>DAG: windturbine</p>
            ''',
            conn_id='gmail_smtp' 
            #In the UI airflow create a smtp connection called gmail_smtp and connection type smtp
            #Host: smtp.gmail.com
            #Login: your email
            #Password: your app password without spaces
            #Port: 465
            #From email: your email
            #Disable TLS: activate
            #Disable SSL: desactivate
        )

        send_email = EmailOperator(
            task_id='send_email',
            to='dilleyandrade@gmail.com',
            subject='Airflow advise',
            html_content='''
                <h3>Normal temperature.</h3>
                <p>DAG: windturbine</p>
            ''',
            conn_id='gmail_smtp'
        )

        check_temp_branch >> [send_email_alert, send_email]

    with TaskGroup('group_database') as group_database: 
        #In the UI airflow create a postgres connection called postgres and connection type postgre, define your password and login
        create_table = PostgresOperator(
            task_id='create_table',
            postgres_conn_id='postgres',
            sql='''
                CREATE TABLE IF NOT EXISTS SENSORS(
                    idtemp varchar(255),
                    powerfactor varchar(255),
                    hydraulicpressure varchar(255),
                    temperature varchar(255),
                    timestamp varchar(255)
                );
            '''
        )

        insert_data = PostgresOperator(
            task_id='insert_data',
            postgres_conn_id='postgres',
            parameters=(
                '{{ ti.xcom_pull(task_ids="get_data", key="idtemp") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="powerfactor") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="hydraulicpressure") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="temperature") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="timestamp") }}'
            ),
            sql='''
                INSERT INTO sensors(idtemp, powerfactor, hydraulicpressure, temperature, timestamp)
                VALUES(%s, %s, %s, %s, %s);
            '''
        )

        create_table >> insert_data

    file_sensor_task >> get_data
    get_data >> [group_check_temp, group_database]
