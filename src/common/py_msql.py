import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB
from src.utils.config_util import load_common_config


class PySql:
    def __init__(self, config):
        mysql_config = config['mysql_config']
        # 初始化数据库连接池
        self.pool = PooledDB(
            creator=pymysql,
            maxconnections=mysql_config['pool_size'],  # 连接池允许的最大连接数
            mincached=2,  # 初始化时的空闲连接数
            maxcached=5,  # 连接池中允许的最大空闲连接数
            blocking=True,  # 连接池满了是否阻塞
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            port=mysql_config['port'],
            charset=mysql_config['charset']
        )

    def get_connection(self):
        # 从连接池中获取一个连接
        return self.pool.connection()

    def execute(self, sql, params=None):
        # 执行单条SQL语句
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, sql, params=None):
        # 查询单条记录
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, sql, params=None):
        # 查询多条记录
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    def insert(self, table, data):
        # 插入单条记录
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        params = tuple(data.values())
        return self.execute(sql, params)

    def insert_many(self, table, data_list):
        # 批量插入
        if not data_list:
            return 0
        keys = ', '.join(data_list[0].keys())
        values = ', '.join(['%s'] * len(data_list[0]))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        params = [tuple(data.values()) for data in data_list]
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, params)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()

    def update(self, table, data, condition):
        # 更新记录
        set_clause = ', '.join([f"{k}=%s" for k in data.keys()])
        where_clause = ' AND '.join([f"{k}=%s" for k in condition.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(condition.values())
        return self.execute(sql, params)

    def delete(self, table, condition):
        # 删除记录
        where_clause = ' AND '.join([f"{k}=%s" for k in condition.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        params = tuple(condition.values())
        return self.execute(sql, params)

    def close_pool(self):
        # 关闭连接池
        self.pool.close()


# 使用示例
if __name__ == '__main__':
    conf = load_common_config("../../../configs")
    db = PySql(config=conf)

    # 插入单条记录
    db.insert('products', {'name': 'product1', 'price': 100})

    # 批量插入
    db.insert_many('products', [{'name': 'product2', 'price': 200}, {'name': 'product3', 'price': 300}])

    # 查询
    print(db.fetch_one('SELECT * FROM products WHERE id = %s', (1,)))
    print(db.fetch_all('SELECT * FROM products'))

    # 更新
    db.update('products', {'price': 150}, {'name': 'product1'})

    # 删除
    db.delete('products', {'name': 'product3'})
