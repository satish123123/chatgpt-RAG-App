import os
from pydantic.v1 import BaseModel
from langchain.tools import Tool
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError

def get_db_url():
    db_config = {
                    'drivername': 'mssql+pyodbc',
                    'username': os.environ["SQL_SERVER_USERNAME"] +'@'+ os.environ["SQL_SERVER_NAME"],
                    'password': os.environ["SQL_SERVER_PASSWORD"],
                    'host': os.environ["SQL_SERVER_NAME"],
                    'port': 1433,
                    'database': os.environ["SQL_SERVER_DATABASE"],
                    'query': {'driver': 'ODBC Driver 17 for SQL Server'}
                }

    #Create a URL object for connecting to the database
    db_url = URL.create(**db_config)
    return db_url

def run_sql_query(sql_query):
    # Fetch db url
    db_url = get_db_url()

    # Test the connection
    try:
     # Connect to the Azure SQL Database using the URL string
        engine = create_engine(db_url)

        conn = engine.connect()
        print("Connection successful!")
        print(sql_query)
        query = text(sql_query)
        results = conn.execute(query)
        rows = results.fetchall()
        return rows
                
    except OperationalError as op_err:
        error_string = f"An OperationalError occurred: {op_err}"
        print(error_string) 
        return error_string
    except Exception as e:
    # Catch other exceptions
        error_string = f"An unexpected error occurred: {e}"
        print(error_string)
        return error_string
    finally:
        conn.close()


class RunSQLQuerySchema(BaseModel):
    execute: str


run_sql_query_tool = Tool.from_function(
    name="run_sql_query",
    description="Use this function to run any query on the SQL Server. Pass the SQL query to be run as an argument to this function.",
    func=run_sql_query,
    args_schema=RunSQLQuerySchema
)

def fetch_tables():
    tables = run_sql_query("SELECT table_name FROM information_schema.tables WHERE table_type = \'BASE TABLE\'")
    return tables

def describe_table(table_name):
    result = run_sql_query(
        f"""SELECT 
            c.name AS ColumnName,
            t.name AS DataType
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        WHERE object_id = OBJECT_ID(\'{table_name}\');"""
    )
    return result

class DescribeTableSchema(BaseModel):
    execute: str


describe_table_tool = Tool.from_function(
    name="describe_table",
    description="Use this function to describe any table on the SQL Server. Pass the table name in the string format as an argument to this function.",
    func=describe_table,
    args_schema=DescribeTableSchema
)
