简单的select 查询

[ Viewwei](https://www.jianshu.com/u/020953361eed)关注赞赏支持

# 简单的select 查询

#### MYSQL检索数据

  * 注意1:mysql 的关键字大小写不区别的.比如 SELECT 和 select是等同的
  * 注意2:mysql 的空格和换行都会被过滤掉的.因此可以把 sql 语句分为几段或者一行来写效果都是一样的

##### Select语句

sql 语句使用 Select 关键词对数据库进行检索.Select 的语法基本结构如下  
SELECT 列1,列 2,列 3 FROM 表格  
示例如下:下面这条 sql
语句标识在Products表格中查询prod_id这一列.当然,这个示例查询的是一列,您也可以查询多列,得到的数据结构的样式基本一致.

    
    
    SELECT  prod_id FROM  Products
    

简单的 select

##### Select 查询全部列

SELECT 使用通配符号(*)来查询一个表格的全部数据.其sql 查询语句的格式为  
SELECT * FROM 表名  
示例程序如下

    
    
    SELECT * FROM Products
    

查询所有列

##### DISTINCT

DISTINCT关键字表示过滤相同查询.把查询到的相同数据过滤掉.DISTINCT的使用需要注意以下几个方面

  * DISTINCT 必须使用在查询语句的头部
  * DISTINCT实际上是把所以的列拼接在一起,然后在对拼接的结果进行去重的.也就是说 DISTINCT 是对整个查询语句生效,而不是只对一个字段生效  
示例程序如下

    
    
    SELECT  DISTINCT  prod_id,prod_name,` prod_price` FROM Products
    

去重查询结果

##### 限定结果

查询语句查询的是表中所有的语句,很有可能是一行,也有可能是多行.使用 limit 语句可以返回指定行数.在 limit后面跟上
offset表示限定的数目从哪一行开始的

  * 注意1: 如果整个查询的结果数目小于限定的数目,那么就会返回全部数量,而不是返回限定的数量
  * 注意:Limit 数量 Offset数量这个查询可以使用缩写:Limit 限定数量,从哪一行开始限定

    
    
    SELECT  prod_id,prod_name FROM  Products LIMIT  3 OFFSET 1
    //或者,这两种效果是一致的
    SELECT  prod_id,prod_name FROM  Products LIMIT  3, 1
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [MYSQL学习——简单查询](https://www.jianshu.com/p/10affdf8deda)

一.结构化查询语言 1.结构化查询语言简介 结构化查询语言(Structured Query Language)简...

[思君_4cd3](https://www.jianshu.com/u/6bf16748c550)阅读 311评论 0赞 0

  * [Mysql(2.3) 简单查询（SELECT）、子查询](https://www.jianshu.com/p/ede4cb02702c)

结构化查询语言（sql） SQL概念和规则 关键字：SQL语言保留的字符串（SELECT FORM） 语句：一条完...

[Cx_330](https://www.jianshu.com/u/b42d8d4f5f68)阅读 381评论 0赞 0

  * [MySQL学习0：select、连接查询、子查询、limit、CRUD](https://www.jianshu.com/p/c0451c9a8e38)

IBM公司开发的eclipseOracle是做数据库起家的。Oracle收购了 MySQL AB公司。 常见的有哪...

[苦难_69e0](https://www.jianshu.com/u/387316438c8e)阅读 419评论 0赞 2

  * [小白的MySQL总结(一)--select篇](https://www.jianshu.com/p/55216426eb91)

写在前面 SQL注入算是CTF，网站安全的一大部分，为了挖掘更骚的姿势，方便以后使用，小白特地温习了MySQL的文...

[白里个白](https://www.jianshu.com/u/786b0e642b55)阅读 930评论 1赞 3

  * [MySql使用之select查询语句](https://www.jianshu.com/p/706bb51941b1)

前言: 终于开始老老实实地开始写博客啦,这是我整理的第一篇博客,在此之前要不就是忘记的内容临时需要用到的时候急急忙...

[不姓马的小马哥](https://www.jianshu.com/u/85bb71cb6bc9)阅读 1,756评论 0赞 7

 