作者：京东零售 石磊

TiDB 作为开源 NewSQL 数据库的典型代表之一，同样支持 SQL，支持事务 ACID 特性。在通讯协议上，TiDB 选择与 MySQL
完全兼容，并尽可能兼容 MySQL 的语法。因此，基于 MySQL 数据库开发的系统，大多数可以平滑迁移至
TiDB，而几乎不用修改代码。对用户来说，迁移成本极低，过渡自然。

然而，仍有一些 MySQL 的特性和行为，TiDB 目前暂时不支持或表现与 MySQL 有差异。除此之外，TiDB
提供了一些扩展语法和功能，为用户提供更多的便利。

TiDB 仍处在快速发展的道路上，对 MySQL 功能和行为的支持方面，正按 路线图 的规划在前行。

## 兼容策略

先从总体上概括 TiDB 和 MySQL 兼容策略，如下表：

通讯协议| SQL语法| 功能和行为  
---|---|---  
完全兼容| 兼容绝大多数| 兼容大多数  
  
截至 4.0 版本，TiDB 与 MySQL 的区别总结如下表：

| MySQL| TiDB  
---|---|---  
隔离级别| 支持读未提交、读已提交、可重复读、串行化，默认为可重复读| 乐观事务支持快照隔离，悲观事务支持快照隔离和读已提交  
锁机制| 悲观锁| 乐观锁、悲观锁  
存储过程| 支持| 不支持  
触发器| 支持| 不支持  
事件| 支持| 不支持  
自定义函数| 支持| 不支持  
窗口函数| 支持| 部分支持  
JSON| 支持| 不支持部分 MySQL 8.0 新增的函数  
外键约束| 支持| 忽略外键约束  
字符集| | 只支持 ascii、latin1、binary、utf8、utf8mb4  
增加/删除主键| 支持| 通过 [alter-primary-key](https://pingcap.com/docs-cn/dev/reference/configuration/tidb-server/configuration-file/#alter-primary-key)配置开关提供  
CREATE TABLE tblName AS SELECT stmt| 支持| 不支持  
CREATE TEMPORARY TABLE| 支持| TiDB 忽略 TEMPORARY 关键字，按照普通表创建  
DML affected rows| 支持| 不支持  
AutoRandom 列属性| 不支持| 支持  
Sequence 序列生成器| 不支持| 支持  
  
## 三种方案比较

双写方案：同时往mysql和tidb写入数据，两个数据库数据完全保持同步

•优点：此方案最安全，作为兜底方案不需担心数据库回滚问题，因为数据完全一致，可以无缝回滚到mysql

•缺点：新方案，调研方案实现，成本较高

读写分离：数据写入mysql，从tidb读，具体方案是切换到线上以后，保持读写分离一周时间左右，这一周时间用来确定tidb数据库没有问题，再把写操作也切换到tidb

•优点: 切换过程，mysql和tidb数据保持同步，满足数据回滚到mysql方案

•缺点：mysql和tidb数据库同步存在延时，对部分写入数据要求实时查询的会导致查询失败，同时一旦整体切换到tidb，无法回切到mysql

直接切换：直接一步切换到tidb

•优点：切换过程最简单，成本最低

•缺点：此方案没有兜底方案，切换到tidb，无法再回切到mysql或者同步数据回mysql风险较大，无法保证数据是否可用

## Django双写mysql与tidb策略

    
    
    settings.py中新增配置
    
    
    
    # Dev Database settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'name',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': 'db',
        },
        'replica': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'name',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': 'db',
        },
        'bak': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'name',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': 'db',
        },
    }
    # 多重写入数据库配置
    MULTI_WRITE_DB = "bak"
    

双写中间件 basemodel.py

    
    
    import copy
    import logging
    import traceback
    from django.db import models, transaction, router
    from django.db.models.deletion import Collector
    from django.db.models import sql
    from django.db.models.sql.constants import CURSOR
    from jcdp.settings import MULTI_WRITE_DB, DATABASES
    
    multi_write_db = MULTI_WRITE_DB
    
    
    # 重写QuerySet
    class BaseQuerySet(models.QuerySet):
    
        def create(self, **kwargs):
            return super().create(**kwargs)
    
        def update(self, **kwargs):
            try:
                rows = super().update(**kwargs)
                if multi_write_db in DATABASES:
                    self._for_write = True
                    query = self.query.chain(sql.UpdateQuery)
                    query.add_update_values(kwargs)
                    with transaction.mark_for_rollback_on_error(using=multi_write_db):
                        query.get_compiler(multi_write_db).execute_sql(CURSOR)
            except Exception:
                logging.error(traceback.format_exc())
                raise
            return rows
    
        def delete(self):
            try:
                deleted, _rows_count = super().delete()
                if multi_write_db in DATABASES:
                    del_query = self._chain()
                    del_query._for_write = True
                    del_query.query.select_for_update = False
                    del_query.query.select_related = False
                    collector = Collector(using=multi_write_db)
                    collector.collect(del_query)
                    collector.delete()
            except Exception:
                logging.error(traceback.format_exc())
                raise
            return deleted, _rows_count
    
        def raw(self, raw_query, params=None, translations=None, using=None):
            try:
                qs = super().raw(raw_query, params=params, translations=translations, using=using)
                if multi_write_db in DATABASES:
                    super().raw(raw_query, params=params, translations=translations, using=multi_write_db)
            except Exception:
                logging.error(traceback.format_exc())
                raise
            return qs
    
        def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
            try:
                for obj in objs:
                    obj.save()
            except Exception:
                logging.error(traceback.format_exc())
                raise
            # objs = super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
            # if multi_write_db in DATABASES:
            #     self._db = multi_write_db
            #     super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
            return objs
    
        def bulk_update(self, objs, fields, batch_size=None):
            try:
                super().bulk_update(objs, fields, batch_size=batch_size)
                if multi_write_db in DATABASES:
                    self._db = multi_write_db
                    super().bulk_update(objs, fields, batch_size=batch_size)
            except Exception:
                logging.error(traceback.format_exc())
                raise
    
    
    class BaseManager(models.Manager):
        _queryset_class = BaseQuerySet
    
    
    class BaseModel(models.Model):
        objects = BaseManager()
    
        class Meta:
            abstract = True
    
        def delete(
                self, using=None, *args, **kwargs
        ):
            try:
                instance = copy.deepcopy(self)
                super().delete(using=using, *args, **kwargs)
                if multi_write_db in DATABASES:
                    super(BaseModel, instance).delete(using=multi_write_db, *args, **kwargs)
            except Exception:
                logging.error(traceback.format_exc())
                raise
    
        def save_base(self, raw=False, force_insert=False,
                      force_update=False, using=None, update_fields=None):
            try:
                using = using or router.db_for_write(self.__class__, instance=self)
                assert not (force_insert and (force_update or update_fields))
                assert update_fields is None or update_fields
                cls = self.__class__
                # Skip proxies, but keep the origin as the proxy model.
                if cls._meta.proxy:
                    cls = cls._meta.concrete_model
                meta = cls._meta
                # A transaction isn't needed if one query is issued.
                if meta.parents:
                    context_manager = transaction.atomic(using=using, savepoint=False)
                else:
                    context_manager = transaction.mark_for_rollback_on_error(using=using)
                with context_manager:
                    parent_inserted = False
                    if not raw:
                        parent_inserted = self._save_parents(cls, using, update_fields)
                    self._save_table(
                        raw, cls, force_insert or parent_inserted,
                        force_update, using, update_fields,
                    )
                if multi_write_db in DATABASES:
                    super().save_base(raw=raw,
                                      force_insert=raw,
                                      force_update=force_update,
                                      using=multi_write_db,
                                      update_fields=update_fields)
                # Store the database on which the object was saved
                self._state.db = using
                # Once saved, this is no longer a to-be-added instance.
                self._state.adding = False
            except Exception:
                logging.error(traceback.format_exc())
                raise
    

上述配置完成以后，在每个应用的models.py中引用新的BaseModel类作为模型基类即可实现双写目的

    
    
    class DirectoryStructure(BaseModel):
        """
        目录结构
        """
        view = models.CharField(max_length=128, db_index=True)  # 视图名称 eg：部门视图 项目视图
        sub_view = models.CharField(max_length=128, unique=True, db_index=True)  # 子视图名称
        sub_view_num = models.IntegerField()  # 子视图顺序号
    

注：目前该方法尚不支持多对多模型的双写情景，如有业务需求，还需重写ManyToManyField类，方法参考猴子补丁方式

迁移数据库过程踩坑记录

TIDB配置项差异：确认数据库配置：ONLY_FULL_GROUP_BY 禁用 （mysql默认禁用）

TIDB不支持事务savepoint，代码中需要显式关闭savepoint=False

TIDB由于是分布式数据库，对于自增主键字段的自增策略与mysq有差异，若业务代码会与主键id关联，需要注意

