# 前言

随着数字化时代的到来，数据量正在经历爆炸式增长，选择使用Elasticsearch的企业变得越来越多。京东云搜索Elasticsearch（JCS for
Elasticsearch，简称ES）是基于开源Elasticsearch的分布式全文搜索服务，产品能够提供高可用、易扩展以及近实时的搜索能力，致力于海量数据存储搜索和实时日志分析，旨在为用户提供更稳定、实时、可靠的云搜索服务。上云过程中不可避免的就会遇到数据迁移的问题。

 **迁移的方式包括不停机迁移上云和停机迁移上云两种，今天我们谈下停机迁移上云中比较常用的快照迁移方式和reindex迁移。**

# 一．快照迁移

 **迁移准备**

 **云上es集群、同vpc下的云oss、自建es**

  *  **源es集群**

用户自建ES，需要提前在ES上安装S3插件并修改ES安全配置：

1\. 安装s3插件：

安装s3插件./bin/elasticsearch-plugin install repository-s3，并重启

注：不安装，创建快照仓库会有报错：repository type [s3] does not exist

2\. ES6版本需要修改JVM参数，避免ak sk认为不安全，修改完后需要重启ES：

在config/jvm.options中写入配置 -Des.allow_insecure_settings=true，并启动es

注：不修改JVM参数，创建快照仓库会出现报错：Setting [access_key] is insecure, but property
[allow_insecure_settings] is not set

    
    
    //设置快照仓库
    
    PUT _snapshot/my_backup
    
    {
    
    "type": "s3",
    
    "settings": {
    
    "bucket": "test666",
    
    "region": "cn-north-1",
    
    "access_key":"XXX",
    
    "secret_key":"XXX",
    
    "base_path":"instance01",
    
    "protocol":"http",
    
    "endpoint":" s3.cn-north-1.jdcloud-oss.com ", #如果自建es部署在和oss相同可用区的云主机上，此时可以使用云存储的内网地址
    
    "compress":"true"
    
    }
    
    }
    
    //查看仓库
    
    GET _snapshot/my_backup/*
    
    //创建并上传快照
    
    POST /_snapshot/my_backup/snapshot_1
    
    //指定索引创建快照并上传到快照仓库
    
    POST /_snapshot/my_backup/snapshot_3
    
    {
    
    "indices": "blog_index1",
    
    "ignore_unavailable": "true",
    
    "include_global_state": "false",
    
    "partial": "false"
    
    }

  *  **目的es集群**

    
    
    //设置快照仓库
    
    PUT _snapshot/my_backup
    
    {
    
     "type": "s3",
    
     "settings": {
    
     "bucket": "test666",
    
     "region": "cn-north-1",
    
     "access_key":"XXX",
    
     "secret_key":"XXX",
    
     "base_path":"instance01",
    
     "protocol":"http",
    
     "endpoint":"s3-internal.cn-north-1.jdcloud-oss.com",
    
     "compress":"true"
    
     }
    
    }
    
     //查看仓库
    
    GET _snapshot/my_backup/*
    
     //恢复快照
    
    POST /_snapshot/my_backup/snapshot_1/_restore

 **备注**

云es和云oss在不同vpc下或使用的是其他厂商的oss，由于云es没有公网地址，此时可以配置nat网关，云es通过nat网关访问公网oss地址。

 **版本兼容性**

https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshot-restore.html

A snapshot of an index created in 6.x can be restored to 7.x.

A snapshot of an index created in 5.x can be restored to 6.x.

A snapshot of an index created in 2.x can be restored to 5.x.

A snapshot of an index created in 1.x can be restored to 2.x.

# 二．reindex迁移

 **迁移准备**

 **云上es集群、自建es**

  *  **源es集群**

 **1.创建索引**

    
    
    PUT blog_index_77
    
    {
    
    "mappings":
    
    {
    
    "user":{
    
    "properties":{
    
    "name":{"type":"text"},
    
    "title":{"type":"text"},
    
    "age":{"type":"integer"}
    
    }
    
    }
    
    }
    
    }

 **2.写入数据**

    
    
    POST blog_index_77/user{
    
    "title": "manager",
    
    "name": "Tom Jerry",
    
    "age": 34
    
    }
    
    

  * **目的es集群**

 **1.由于云es没有公网地址，配置nat网关，使目的es通过nat可以访问到自建集群**

 **2.创建索引**

    
    
    PUT blog_index_66
    
    {
    
    "mappings":
    
    {
    
    "user":{
    
    "properties":{
    
    "name":{"type":"text"},
    
    "title":{"type":"text"},
    
    "age":{"type":"integer"}
    
    }
    
    }
    
    }
    
    }

 **3.配置 reindex.remote.whitelist 参数，指明能够reindex 的远程集群的白名单**

在elasticsearch.yml文件中添加：reindex.remote.whitelist: "116.196.106.13:9200" 并重启

 **4.reindex迁移数据**

    
    
    POST _reindex
    
    {
    
    "source": {
    
    "remote": {
    
    "host": "http://116.196.106.13:9200",
    
    "socket_timeout": "1m",
    
    "connect_timeout": "10s"
    
    },
    
    "index": "blog_index_77"
    
    },
    
    "dest": {
    
    "index": "blog_index_66"
    
    }
    
    }

 **5.迁移部分数据：查询条件为 title 字段为manager，将结果写入当前集群的 blog_index_66索引。**

    
    
    POST _reindex
    
    {
    
    "source": {
    
    "remote": {
    
    "host": "http://116.196.106.13:9200",
    
    "socket_timeout": "1m",
    
    "connect_timeout": "10s"
    
    },
    
    "index": "blog_index77",
    
    "query":{
    
    "match":{
    
    "title":"manager"
    
    }
    
    }
    
    },
    
    "dest": {
    
    "index": "blog_index_66"
    
    }
    
    }
    

