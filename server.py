import mysql.connector
from mysql.connector import Error
import os
from typing import List, Tuple

# host_name='localhost'
# user_name='debian-sys-maint'
# user_password='5C1YHtV9Owb0dejD'
# database='information_schema'
# port=3306
# charset='utf8'

class DatabaseServer:
    def __init__(self,db_name="bytes_storage_db"):
        
        self.host = 'localhost'
        self.user = 'debian-sys-maint'
        self.password = 'input your password' 
        self.db_name = db_name
        self.connection = None

        try:
            server_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            if server_conn.is_connected():
                cursor = server_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
                print(f"database '{self.db_name}' create successfully or already exist.")
                server_conn.close()


            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            if self.connection.is_connected():
                print(f"connect database successfully '{self.db_name}'！")

        except Error as e:
            print(f"fail to connect or create: {e}")
            raise 

    def create_table(self, table_name: str):

        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data_column_1 BLOB,
                data_column_2 BLOB
            );
            """
            try:
                cursor.execute(query)
                print(f"table '{table_name}' create successfully or already exist.")
            except Error as e:
                print(f"can't create '{table_name}': {e}")

    def batch_insert(self, table_name: str, data_list: List[Tuple[bytes, bytes]]):

        if not data_list:
            print("no data insert。")
            return

        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            query = f"INSERT INTO {table_name} (data_column_1, data_column_2) VALUES (%s, %s)"
            try:
               
                cursor.executemany(query, data_list)
                self.connection.commit() 
                print(f"successfullt insert {cursor.rowcount} notes to '{table_name}' .")
            except Error as e:
                print(f"fail to insert {e}")

    def query_all(self, table_name: str) -> List[Tuple]:

        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            query = f"SELECT * FROM {table_name}"
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                print(f"\n--- search all data in '{table_name}' ---")
                if not results:
                    print("there is no data in table。")
                else:
                    print(f"{'ID':<5}{'first col data Hexadecimal':<40}{'second col data Hexadecimal'}")
                    print("-" * 100)
                    for row in results:
                        record_id, data1, data2 = row
                        print(f"{record_id:<5}{data1.hex():<40}{data2.hex()}")
                return results
            except Error as e:
                print(f"fail to search: {e}")
        return []

    def query_by_col1(self, table_name: str, col1_value: bytes) :
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            query = f"SELECT data_column_2 FROM {table_name} WHERE data_column_1 = %s"
            try:
                cursor.execute(query, (col1_value,))
              
                result = cursor.fetchone()
                if result:
                    
                    return result[0]
                else:
                    
                    return None
            except Error as e:
                print(f"fail to search by col: {e}")
        return None

    def clear_table(self, table_name: str):

        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            query = f"TRUNCATE TABLE {table_name}"
            try:
                cursor.execute(query)
                self.connection.commit()
                print(f"\n clean tbale '{table_name}' successfully")
            except Error as e:
                print(f"clean table '{table_name}' unsuccessfully: {e}")

    def delete_table(self, table_name: str):
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
          
            query = f"DROP TABLE IF EXISTS {table_name}"
            try:
                cursor.execute(query)
                self.connection.commit()
                print(f"\n delete table '{table_name}' successfully")
            except Error as e:
                print(f"delete table '{table_name}' unsuccessfully {e}")

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("\nThe database connection has been closed.")


