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
    """
    一个用于管理MySQL数据库的服务器类。
    提供了创建数据库/表、批量插入和查询两列bytes类型数据的功能。
    """

    def __init__(self,db_name="bytes_storage_db"):
        """
        初始化数据库服务器连接。

        Args:
            host (str): 数据库主机名或IP地址。
            user (str): 数据库用户名。
            password (str): 数据库密码。
            db_name (str): 要创建或连接的数据库名称。
        """
        self.host = 'localhost'
        self.user = 'debian-sys-maint'
        self.password = '5C1YHtV9Owb0dejD'
        self.db_name = db_name
        self.connection = None

        try:
            # 1. 首先连接到MySQL服务器（不指定数据库）以创建数据库
            server_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            if server_conn.is_connected():
                cursor = server_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
                print(f"数据库 '{self.db_name}' 已成功创建或已存在。")
                server_conn.close()

            # 2. 连接到目标数据库
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            if self.connection.is_connected():
                print(f"成功连接到数据库 '{self.db_name}'！")

        except Error as e:
            print(f"数据库连接或初始化失败: {e}")
            raise  # 抛出异常，让调用者知道连接失败

    def create_table(self, table_name: str):
        """
        在数据库中创建一个用于存储两列bytes类型数据的表。

        Args:
            table_name (str): 要创建的表的名称。
        """
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            # 使用 BLOB 类型来存储任意长度的二进制数据
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data_column_1 BLOB,
                data_column_2 BLOB
            );
            """
            try:
                cursor.execute(query)
                print(f"表 '{table_name}' 已成功创建或已存在。")
            except Error as e:
                print(f"创建表 '{table_name}' 失败: {e}")

    def batch_insert(self, table_name: str, data_list: List[Tuple[bytes, bytes]]):
        """
        向指定表中批量插入多行bytes数据。

        Args:
            table_name (str): 目标表的名称。
            data_list (List[Tuple[bytes, bytes]]): 一个包含元组的列表，
                                                  每个元组代表一行，包含两个bytes对象。
        """
        if not data_list:
            print("没有数据可插入。")
            return

        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            query = f"INSERT INTO {table_name} (data_column_1, data_column_2) VALUES (%s, %s)"
            try:
                # executemany 是批量插入的最高效方式
                cursor.executemany(query, data_list)
                self.connection.commit()  # 提交事务
                print(f"成功向表 '{table_name}' 中批量插入 {cursor.rowcount} 条记录。")
            except Error as e:
                print(f"批量插入数据失败: {e}")

    def query_all(self, table_name: str) -> List[Tuple]:
        """
        查询并返回指定表中的所有记录。

        Args:
            table_name (str): 要查询的表的名称。

        Returns:
            一个包含元组的列表，每个元组代表一行数据。如果出错则返回空列表。
        """
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            query = f"SELECT * FROM {table_name}"
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                print(f"\n--- 查询 '{table_name}' 表中的所有数据 ---")
                if not results:
                    print("表中没有数据。")
                else:
                    print(f"{'ID':<5}{'第一列数据 (十六进制)':<40}{'第二列数据 (十六进制)'}")
                    print("-" * 100)
                    for row in results:
                        record_id, data1, data2 = row
                        print(f"{record_id:<5}{data1.hex():<40}{data2.hex()}")
                return results
            except Error as e:
                print(f"查询失败: {e}")
        return []

    def query_by_col1(self, table_name: str, col1_value: bytes) :
        """
        根据第一列的指定数据，返回对应的第二列数据。

        Args:
            table_name (str): 要查询的表的名称。
            col1_value (bytes): 第一列中要匹配的bytes数据。

        Returns:
            如果找到匹配项，则返回第二列的bytes数据；否则返回 None。
        """
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            # 使用参数化查询来防止SQL注入
            query = f"SELECT data_column_2 FROM {table_name} WHERE data_column_1 = %s"
            try:
                cursor.execute(query, (col1_value,))
                # fetchone() 用于获取查询结果的第一行
                result = cursor.fetchone()
                if result:
                    # fetchone() 返回的是一个元组，例如 (b'some_data',)，所以我们取第一个元素
                    return result[0]
                else:
                    # 如果没有找到匹配项，fetchone() 返回 None
                    return None
            except Error as e:
                print(f"按列查询失败: {e}")
        return None

    def clear_table(self, table_name: str):
        """
        清空指定表中的所有数据。
        Args:
            table_name (str): 要清空的表的名称。
        """
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            # TRUNCATE TABLE 是一种高效的清空表的方式
            query = f"TRUNCATE TABLE {table_name}"
            try:
                cursor.execute(query)
                self.connection.commit()
                print(f"\n表 '{table_name}' 已被成功清空。")
            except Error as e:
                print(f"清空表 '{table_name}' 失败: {e}")

    def delete_table(self, table_name: str):
        """
        从数据库中删除指定的表。

        Args:
            table_name (str): 要删除的表的名称。
        """
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            # 使用 "DROP TABLE IF EXISTS" 即使表不存在也不会报错
            query = f"DROP TABLE IF EXISTS {table_name}"
            try:
                cursor.execute(query)
                self.connection.commit()
                print(f"\n表 '{table_name}' 已被成功删除。")
            except Error as e:
                print(f"删除表 '{table_name}' 失败: {e}")

    def close(self):
        """ 关闭数据库连接 """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("\n数据库连接已关闭。")



# --- `server.py` 的自我演示/测试部分 ---
# if __name__ == "__main__":
#     print("--- 正在运行 server.py 作为主程序进行演示 ---")
#
#     # --- 请在此处修改为您自己的MySQL连接信息 ---
#     # DB_HOST = "localhost"
#     # DB_USER = "your_username"  # 例如 'root'
#     # DB_PASSWORD = "your_password"  # 您的密码
#     #
#     TABLE_NAME = "secure_byte_data"
#
#     try:
#         # 1. 初始化Server，这将自动连接并创建数据库
#         db_server = DatabaseServer()
#
#         # 2. 创建表
#         db_server.create_table(TABLE_NAME)
#
#         # 3. 准备一批bytes数据用于批量插入
#         #    os.urandom 是生成密码学安全随机字节的理想方式
#         s = os.urandom(16)
#         records_to_insert = [
#             (s, os.urandom(32)),
#             (os.urandom(16), os.urandom(32)),
#             (os.urandom(16), os.urandom(32))
#         ]
#
#         print("\n--- 准备批量插入以下数据 ---")
#         for i, (d1, d2) in enumerate(records_to_insert):
#             print(f"记录 {i + 1}: 列1={d1.hex()}, 列2={d2.hex()}")
#
#         # 4. 执行批量插入
#         db_server.batch_insert(TABLE_NAME, records_to_insert)
#
#         # 5. 查询所有数据以验证
#         all_data = db_server.query_all(TABLE_NAME)
#         print(db_server.query_by_col1(TABLE_NAME, s))
#         db_server.clear_table(TABLE_NAME)
#         db_server.delete_table(TABLE_NAME)
#     except Exception as e:
#         print(f"\n在演示过程中发生错误: {e}")
#
#     finally:
#         # 6. 关闭连接
#         if 'db_server' in locals() and db_server.connection:
#             db_server.close()

