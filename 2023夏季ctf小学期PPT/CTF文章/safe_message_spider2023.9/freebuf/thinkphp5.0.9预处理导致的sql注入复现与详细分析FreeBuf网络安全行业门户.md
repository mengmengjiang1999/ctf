# thinkphp5.0.9预处理导致的sql注入

thinkphp5.0.9预处理导致的sql注入， 比较鸡肋，只能执行user(),database()这些函数，但是可以学习下思路  
造成这个漏洞的原因一是thinkphp没有对输入进行过滤，直接将输入拼接。二是由于PDO的特性导致的问题

## 复现

先搭建thinkphp5.0.9环境

配置下测试环境  
![](https://image.3001.net/images/20211206/1638774792_61adb808bbea4a0030921.png)  
![](https://image.3001.net/images/20211206/1638774793_61adb809e482ca31b6520.png)  
![](https://image.3001.net/images/20211206/1638774794_61adb80ac78bd1e9c2188.png)

然后访问

>
> [http://tptest.cc/index.php/index/index/getage?names[0,updatexml(0,concat(0xa,user()),0)]=1](http://tptest.cc/index.php/index/index/getage?names%5B0,updatexml\(0,concat\(0xa,user\(\)\),0\)%5D=1)

![](https://image.3001.net/images/20211206/1638774795_61adb80be40826088821d.png)  
复现成功

## 漏洞分析

先看看传进来了什么  
![](https://image.3001.net/images/20211206/1638774797_61adb80d071083ea679bb.png)  
是一个关联数组

跟进where  
![](https://image.3001.net/images/20211206/1638774798_61adb80e2266bed936ab0.png)  
跟进parseWhereExp，看了一番，就是普通的对where参数解析

继续跟进select

Query的select函数从这里开始，构造的sql语句就出问题了  
![](https://image.3001.net/images/20211206/1638774799_61adb80f7c67903f69f31.png)  
继续跟进builder->select -> parseWhere -> buildWhere -> parseWhereItem

在这里将关联数组的key拼接了上去  
![](https://image.3001.net/images/20211206/1638774800_61adb810e0af505dc2427.png)

正常查询，传参names[]=li，构造出来的应该是这样  
![](https://image.3001.net/images/20211206/1638774801_61adb811e903639c5c809.png)  
生成的预处理sql应该是这样，where_name_in_0会被替换为li  
![](https://image.3001.net/images/20211206/1638774803_61adb81312ae898a0529c.png)

而恶意payload，生成的是  
![](https://image.3001.net/images/20211206/1638774804_61adb81405aadb4239d33.png)

看一下最终生成的sql语句

调试发现，预处理发生了错误，但是报错注入成功，语句被执行了？预处理时执行了sql语句？  
![](https://image.3001.net/images/20211206/1638774805_61adb815282b60d6a8682.png)  
想调试下，但是这条语句，进不去，不能调试，，不知道什么原因，  
`$this->PDOStatement = $this->linkID->prepare($sql);`

在网上看到了p神的文章

> https://www.leavesongs.com/PENETRATION/thinkphp5-in-sqlinjection.html

就是说在PDO::ATTR_EMULATE_PREPARES => false模式下，预处理是假的，边替换边执行，这就可以解

释得通了

找一下不能子查询的原因

构造payload：

    
    
    ?names[0,updatexml(0,concat(0xa,(select group_concat(SCHEMA_NAME) from information_schema.SCHEMATA
    )),0)]=1
    

预处理没有报错

但在`$result = $this->PDOStatement->bindValue($param, $val[0], $val[1]);`时报错

应该是PDO的预处理，不能解析这一长串  
![](https://image.3001.net/images/20211206/1638774806_61adb816aa5f9d64a878d.png)  
那就从param入手看一下，

param来自$bind

$bind来自上面遇到过的  
![](https://image.3001.net/images/20211206/1638774807_61adb817d0e08e942b103.png)

想绕过就要让$bindKey变为where_name_in_0，，但是构造的sql语句不变，做不到，立刻放弃

令我疑惑的两个点

> user()查询是在预处理时报错退出的，子查询是在绑定key-value时退出的
>
> 而且使用子查询，PDO是解析成功了的，在mysql日志看到如下

![](https://image.3001.net/images/20211206/1638774808_61adb818c6609cb94cc00.png)  
使用user()查询日志：  
![](https://image.3001.net/images/20211206/1638774825_61adb829c03d0e8b0645f.png)  
直接用sql语句查日志  
![](https://image.3001.net/images/20211206/1638774826_61adb82a97d1742f8c60c.png)

为什么PDO调用user()，在mysql日志看不到记录

搞不懂

## 总结

thinkphp没有对输入过滤，直接做拼接

众所周知预处理不能处理in，order by这些动态的变量，所以审计的时候可以重点看一下

这个漏洞没什么用，不过可以当个练习了

造成这个漏洞的原因一是thinkphp没有对输入进行过滤，直接将输入拼接。二是由于PDO的特性，在预

处理时把代码执行了

## 如何修复

看5.0.22，已经修复  
![](https://image.3001.net/images/20211206/1638774827_61adb82bb42a11817be90.png)  
select生成的语句没有我们构造的内容了  
![](https://image.3001.net/images/20211206/1638774828_61adb82cc5ea18827c7e2.png)

继续调试，bindkey后面不使用key拼接了，而是使用递增的i  
![](https://image.3001.net/images/20211206/1638774829_61adb82dcf1c3bbf79222.png)

