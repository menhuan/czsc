# mongdb操作的工具类
import os

# -*- encoding: utf-8 -*-

import pymongo


class MongoDBUtil:
    """
    MongoDB工具类
    """

    def __init__(self, db_name=None, port=27017,collect_name:str = "binance"):
        """构造函数"""
        self.client = pymongo.MongoClient(host= os.getenv("mongo_ip","101.43.210.78") ,port=port,
                                          username=os.getenv("mongodb_username","root"),
                                          password=os.getenv("mongodb_password","rootpassword"))
        self.database = self.client[db_name]
        self.collect_name = collect_name

    def __del__(self):
        """析构函数"""
        # print("__del__")
        self.client.close()

    def create_database(self, db_name):
        """创建数据库"""
        return self.client.get_database(db_name)

    def drop_database(self, db_name):
        """删除数据库"""
        return self.client.drop_database(db_name)

    def select_database(self, db_name):
        """使用数据库"""
        self.database = self.client[db_name]
        return self.database

    def get_database(self, db_name):
        """使用数据库"""
        # return self.client[db_name]
        return self.client.get_database(db_name)

    def list_database_names(self):
        """获取所有数据库列表"""
        return self.client.list_database_names()

    def create_collection(self, collect_name):
        """创建集合"""
        collect = self.database.get_collection(collect_name)
        if (collect is not None):
            print("collection %s already exists" % collect_name)
            return collect
        return self.database.create_collection(collect_name)
    def create_collection(self):
        return self.create_collection(self,self.collect_name)

    def drop_collection(self, collect_name):
        """获取所有集合名称"""
        return self.database.drop_collection(collect_name)

    def get_collection(self):
        """获取集合"""
        return self.database.get_collection(self.collect_name)

    def list_collection_names(self):
        """获取所有集合名称"""
        return self.database.list_collection_names()

    def insert(self, documents):
        """插入单条或多条数据"""
        return self.get_collection().insert(documents)

    def insert_one(self, document):
        """插入一条数据"""
        return self.get_collection().insert_one(document)

    def insert_many(self, documents):
        """插入多条数据"""
        return self.get_collection().insert_many(documents)

    def delete_one(self, filter, collation=None, hint=None, session=None):
        """删除一条记录"""
        return self.get_collection().delete_one(filter, collation, hint, session)

    def delete_many(self, filter, collation=None, hint=None, session=None):
        """删除所有记录"""
        return self.get_collection().delete_many(filter, collation, hint, session)

    def find_one_and_delete(self, filter, projection=None, sort=None, hint=None, session=None, **kwargs):
        """查询并删除一条记录"""
        return self.get_collection().find_one_and_delete(filter, projection, sort, hint, session,
                                                                              **kwargs)

    def count_documents(self, filter, session=None, **kwargs):
        """查询文档数目"""
        return self.get_collection().count_documents(filter, session, **kwargs)

    def find_one(self, filter=None, *args, **kwargs):
        """查询一条记录"""
        return self.get_collection().find_one(filter, *args, **kwargs)

    def find(self, *args, **kwargs):
        """查询所有记录"""
        return self.get_collection().find(*args, **kwargs)

    def update_one(self, filter, update, upsert=False, bypass_document_validation=False,
                   collation=None, array_filters=None, hint=None, session=None):
        """更新一条记录"""
        return self.get_collection().update_one(filter, update,
                                                                     upsert, bypass_document_validation, collation,
                                                                     array_filters, hint, session)

    def update_many(self, filter, update, upsert=False, array_filters=None,
                    bypass_document_validation=False, collation=None, hint=None, session=None):
        """更新所有记录"""
        return self.get_collection().update_many(filter, update,
                                                                      upsert, array_filters, bypass_document_validation,
                                                                      collation, hint, session)

    def find_one_and_update(self, filter, update, projection=None, sort=None, upsert=False,
                            return_document=False, array_filters=None, hint=None, session=None, **kwargs):
        """查询并更新一条记录"""
        return self.get_collection().find_one_and_update(filter, update, projection,
                                                                              sort, upsert, return_document,
                                                                              array_filters, hint, session, **kwargs)


binance_mongo = MongoDBUtil(db_name="coin")

def get_coin_db(collection:str = "binance"):
    return mongoUtil



if __name__ == "__main__":
    print("------------------start-------------------------")
    mongoUtil = MongoDBUtil(db_name="xl01")
    """数据库操作"""
    stat = mongoUtil.create_database(db_name="xl01")
    # stat = mongoUtil.drop_database(db_name="xl01")
    stat = mongoUtil.list_database_names()
    stat = mongoUtil.get_database(db_name="xl01")
    """集合操作"""
    stat = mongoUtil.create_collection(collect_name="xl_collect_01")
    # stat = mongoUtil.drop_collection(collect_name="xl_collect_01")
    stat = mongoUtil.get_collection(collect_name="xl_collect_01")
    stat = mongoUtil.list_collection_names()
    """文档操作：增加"""
    document = {"name": "hao123", "type": "搜索引擎", "url": "http://www.hao123.com/"}
    stat = mongoUtil.insert_one(collect_name="xl_collect_01", document=document)
    # documents = [{'x': i} for i in range(2)]
    documents = [{"name": "hao123", "type": "搜索引擎"} for i in range(2)]
    # stat = mongoUtil.insert(collect_name="xl_collect_01", documents=documents)
    stat = mongoUtil.insert_many(collect_name="xl_collect_01", documents=documents)
    """文档操作：查询"""
    stat = mongoUtil.find_one(collect_name="xl_collect_01")
    print(type(stat), stat)
    rows = mongoUtil.find(collect_name="xl_collect_01")
    # for row in rows:
    #     print(row)
    filter = {'name': 'hao123'}
    # filter = {'x': 1}
    count = mongoUtil.count_documents(collect_name="xl_collect_01", filter=filter)
    print(type(stat), count)
    """文档操作：删除"""
    stat = mongoUtil.delete_one(collect_name="xl_collect_01", filter=filter)
    stat = mongoUtil.find_one_and_delete(collect_name="xl_collect_01", filter=filter)
    # stat = mongoUtil.delete_many(collect_name="xl_collect_01", filter=filter)
    print(type(stat), stat)
    """文档操作：修改"""
    spec = {"url": "http://www.baidu.com/"}
    update = {"$set": spec}
    stat = mongoUtil.update_one(collect_name="xl_collect_01", filter=filter, update=update)
    print(type(stat), stat.modified_count, stat)
    stat = mongoUtil.update_many(collect_name="xl_collect_01", filter=filter, update=update)
    # print(type(stat), stat.modified_count, stat)
    stat = mongoUtil.find_one_and_update(collect_name="xl_collect_01", filter=filter, update=update)
    print(type(stat), stat)
    print("-------------------end--------------------------")