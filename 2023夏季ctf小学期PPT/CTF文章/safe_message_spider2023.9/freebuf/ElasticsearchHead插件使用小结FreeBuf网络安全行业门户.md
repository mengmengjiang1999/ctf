**作者：崔雄华**

# 1 Elasticsearch Head是什么

ElasticSearch
head就是一款能连接ElasticSearch搜索引擎，并提供可视化的操作页面对ElasticSearch搜索引擎进行各种设置和数据检索功能的管理插件，如在head插件页面编写RESTful接口风格的请求，就可以对ElasticSearch中的数据进行增删改查、创建或者删除索引等操作。类似于使用navicat工具连接MySQL这种关系型数据库，对数据库做操作。

# 2 本地安装

下面简单介绍下ES环境安装和Elasticsearch Head在chrome浏览器中插件安装。

# 2.1 ES安装

安装链接：https://www.elastic.co/cn/webinars/getting-started-elasticsearch?elektra=what-is-elasticsearch&storm=hero-banner-cta&rogue=gs-with-elasticsearch-webinar  
1.双击运行

![04011e67-889d-41c5-aacd-4fea3f13530e20221208161212.png](https://image.3001.net/images/20221222/1671671568_63a3af1066fbbcbc22ce1.png!small)

2.启动成功日志

![33480aec-672b-4804-99f3-7f250fe38c8c20221208161235.png](https://image.3001.net/images/20221222/1671671569_63a3af112b50dc10d8225.png!small)

3.查看版本信息  
访问地址：http://localhost:9200/ 出现如下信息：

![bbac5b56-6355-42e2-8a51-79008f329ba420221208161308.png](https://image.3001.net/images/20221222/1671671569_63a3af11c0151480a5bf4.png!small)

# 2.2 head插件安装

安装链接：https://chrome.google.com/webstore/detail/multi-elasticsearch-head/cpmmilfkofbeimbmgiclohpodggeheim?hl=zh-CN  
git地址：https://github.com/mobz/elasticsearch-head  
1.打开head后效果

![bb695317-98f1-41c2-9d6e-15856b74e3ab20221208161415.png](https://image.3001.net/images/20221222/1671671570_63a3af128ff28508b1905.png!small)

![c4fa4f65-a2e1-4dfa-a1f4-cc00a0b5a52620221208161424.png](https://image.3001.net/images/20221222/1671671571_63a3af13518c7fcb4ee59.png!small)

重要信息，集群健康值。Elasticsearch 中其实有专门的衡量索引健康状况的标志，分为三个等级：

  * green，绿色。这代表所有的主分片和副本分片都已分配。你的集群是 100% 可用的。
  * yellow，黄色。所有的主分片已经分片了，但至少还有一个副本是缺失的。
  * red，红色。至少一个主分片以及它的全部副本都在缺失中。

# 3 基本查询

# 3.1 检索关键字

1.must子句  
文档必须匹配must所有子句查询

![be37b54e-820a-4934-8e78-31627dd1678420221208161627.png](https://image.3001.net/images/20221222/1671671572_63a3af140a2250c1a7014.png!small)

2.should子句  
文档应该匹配should子句查询的至少一个

![41fdfa12-ac29-42e6-a54a-24ea5b3e02ef20221208161652.png](https://image.3001.net/images/20221222/1671671572_63a3af14a3d4bb320f5b5.png!small)

3.must_not子句  
文档不能匹配该查询条件，相当于“！=”

![d8ca21e6-d6c8-43bf-893b-9a3510f6363620221208161718.png](https://image.3001.net/images/20221222/1671671573_63a3af15595e05cfac3dd.png!small)

# 3.2 检索条件

  * match：分词匹配
  * term：表示精确匹配
  * wildcard：通配符匹配
  * prefix：前缀匹配
  * range：区间查询
  * query_string：允许在单个查询字符串中指定AND
  * text：文本
  * missing： 无值（类似于sql中IS NULL）

# 4 复合查询

ES以RESTful接口风格的请求，使用json进行复杂的查询。请求格式：http://ip:port/索引/类型/文档Id

# 4.1 查询数据（GET）

user/user/BmH494EB0DXGzMoya1Bu

![7bd33a92-9a9c-4c89-881b-2aa8dc452ab320221208161821.png](https://image.3001.net/images/20221222/1671671574_63a3af1617079a1ac78bc.png!small)

查询官方文档：https://www.elastic.co/guide/cn/elasticsearch/guide/current/query-dsl-intro.html

# 4.2 插入数据（PUT、POST）

PUT方法需要指明id

![c4796d96-4f92-4018-b8b0-f5edfd298c5b20221208161854.png](https://image.3001.net/images/20221222/1671671574_63a3af16c4460f1bff070.png!small)

POST方法自动生成id

![2c013de7-d336-429f-bfb7-170fed32f81620221208161915.png](https://image.3001.net/images/20221222/1671671575_63a3af176f06c49d23a05.png!small)

![de93054e-5b3a-46b0-a980-2a8c8adf78d820221208161932.png](https://image.3001.net/images/20221222/1671671576_63a3af1845f02dab3b064.png!small)

# 4.3 更新数据（PUT）

![62bff998-dd32-44f9-800b-cf298a66b61b20221208161955.png](https://image.3001.net/images/20221222/1671671576_63a3af18e99aaf901ba09.png!small)

# 4.4 删除数据（DELETE）

![00de7b3d-6c20-4579-a92c-76c77637e8fb20221208162022.png](https://image.3001.net/images/20221222/1671671577_63a3af19af5d5e70bfe86.png!small)

# 4.5 给索引添加字段

user/user/_mapping也可以添加成功

![eeefd99a-d53f-4921-a65f-105b4216139420221208162046.png](https://image.3001.net/images/20221222/1671671578_63a3af1a59398a2f8bde1.png!small)

# 5 具体实践

纯配ECLP运单数据除了落mysql数据库同时也会存储ES，商家工作台导出、运单列表功能就是查询ES数据。  
例如下面就是根据运单号查询运单数据：

![249401d9-3dc9-4d39-a5fe-337b8bcd248d20221208162108.png](https://image.3001.net/images/20221222/1671671579_63a3af1b29925fc443dd9.png!small)

工作中需要在运单扩展表上增加字段，除了mysql数据表需要增加字段外，ES也要增加字段。lwb_main就是运单数据索引，给lwb_main索引增加字段执行语句如下：lwb_main/_mapping/lwb_main?pretty，pretty主要做美化作用，也可不要。

![96ebd601-e874-4f36-83a3-37ba0fc8f6a320221208162135.png](https://image.3001.net/images/20221222/1671671579_63a3af1bdf7c98ef37ef5.png!small)

# 6 总结

Elasticsearch
Head插件直接在chrome浏览器安装后就可以使用，非常方便，对于初学者大有益处，使用head插件可以快速实现ES索引数据的增删改查、创建或者删除索引等操作。

