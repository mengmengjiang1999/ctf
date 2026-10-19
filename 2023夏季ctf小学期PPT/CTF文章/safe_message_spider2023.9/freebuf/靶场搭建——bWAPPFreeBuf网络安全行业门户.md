## 前言

靶场众多，为什么选择bWAPP？

bWAPP的练习跟OWASP TOP 10更匹配，能快速了解各种漏洞及其利用方法，适合入门

## 靶场搭建步骤

### 1\. 下载并安装PhpStudy(方便地搭建服务器和数据库)

### 2\. 下载bWAPP源码

  * 下载地址：https://github.com/raesene/bWAPP

### 3\. 部署bWAPP

我们采取本地搭建的方式

  * 1\. 将下载下来的bWAPP文件夹移动至PhpStudy的一个站点网站根目录下（默认的为WWW目录）
  * 2\. 修改 **app/db** 目录下的文件为 **bwapp.sql** ，该文件内容如下：

> CREATE DATABASE bwapp IF NOT EXISTS bwapp;
>
> \-- 使用数据库bwapp：  
> use bwapp;
>
>  
> \-- 创建blog表：
>
> CREATE TABLE blog (  
> id int(10) NOT NULL ,  
> owner varchar(100) DEFAULT NULL,  
> entry varchar(500) DEFAULT NULL,  
> date datetime DEFAULT NULL,  
> PRIMARY KEY (id)  
> );
>
> 创建heroes表：
>
> CREATE TABLE heroes (  
> id int(10) NOT NULL ,  
> login varchar(100) DEFAULT NULL,  
> password varchar(100) DEFAULT NULL,  
> secret varchar(100) DEFAULT NULL,  
> PRIMARY KEY (id)  
> );
>
> \-- heroes表添加数据：
>
> INSERT INTO heroes VALUES (1, 'neo', 'trinity', 'Oh why didn''t I took that
> BLACK pill?');  
> INSERT INTO heroes VALUES (2, 'alice', 'loveZombies', 'There''s a cure!');  
> INSERT INTO heroes VALUES (3, 'thor', 'Asgard', 'Oh, no... this is Earth...
> isn''t it?');  
> INSERT INTO heroes VALUES (4, 'wolverine', 'Log@N', 'What''s a Magneto?');  
> INSERT INTO heroes VALUES (5, 'johnny', 'm3ph1st0ph3l3s', 'I''m the Ghost
> Rider!');  
> INSERT INTO heroes VALUES (6, 'seline', 'm00n', 'It wasn''t the Lycans. It
> was you.');
>
> \-- 创建movies表：
>
> CREATE TABLE movies (  
> id int(10) NOT NULL ,  
> title varchar(100) DEFAULT NULL,  
> release_year varchar(100) DEFAULT NULL,  
> genre varchar(100) DEFAULT NULL,  
> main_character varchar(100) DEFAULT NULL,  
> imdb varchar(100) DEFAULT NULL,  
> PRIMARY KEY (id)  
> );
>
> \-- movies表添加数据：
>
> INSERT INTO movies VALUES (1, 'G.I. Joe: Retaliation', 2013, 'action',
> 'Cobra Commander', 'tt1583421');  
> INSERT INTO movies VALUES (2, 'Iron Man', 2008, 'action', 'Tony Stark',
> 'tt0371746');  
> INSERT INTO movies VALUES (3, 'Man of Steel', 2013, 'action', 'Clark Kent',
> 'tt0770828');  
> INSERT INTO movies VALUES (4, 'Terminator Salvation', 2009, 'sci-fi', 'John
> Connor', 'tt0438488');  
> INSERT INTO movies VALUES (5, 'The Amazing Spider-Man', 2012, 'action',
> 'Peter Parker', 'tt0948470');  
> INSERT INTO movies VALUES (6, 'The Cabin in the Woods', 2011, 'horror',
> 'Some zombies', 'tt1259521');  
> INSERT INTO movies VALUES (7, 'The Dark Knight Rises', 2012, 'action',
> 'Bruce Wayne', 'tt1345836');  
> INSERT INTO movies VALUES (8, 'The Incredible Hulk', 2008, 'action', 'Bruce
> Banner', 'tt0800080');  
> INSERT INTO movies VALUES (9, 'World War Z', 2013, 'horror', 'Gerry Lane',
> 'tt0816711');
>
> \-- 创建users表：
>
> CREATE TABLE users (  
> id int(10) NOT NULL ,  
> login varchar(100) DEFAULT NULL,  
> password varchar(100) DEFAULT NULL,  
> email varchar(100) DEFAULT NULL,  
> secret varchar(100) DEFAULT NULL,  
> activation_code varchar(100) DEFAULT NULL,  
> activated tinyint(1) DEFAULT '0',  
> reset_code varchar(100) DEFAULT NULL,  
> admin tinyint(1) DEFAULT '0',  
> PRIMARY KEY (id)  
> );
>
> \-- users表添加数据：
>
> INSERT INTO users VALUES (1, 'A.I.M.',
> '6885858486f31043e5839c735d99457f045affd0', 'bwapp-aim@mailinator.com',
> 'A.I.M. or Authentication Is Missing', null, 1, null, 1);  
> INSERT INTO users VALUES (2, 'bee',
> '6885858486f31043e5839c735d99457f045affd0', 'bwapp-bee@mailinator.com', 'Any
> bugs?', null, 1, null, 0);

  * 3\. 修改配置文件 **admin/settings.php**

我的本地MySQL数据库的服务器就是localhost，用户名为root，密码为123456。

>  
>
>
> // Database connection settings
>
> $db_server = "localhost";
>
> $db_username = "root";
>
> $db_password = "123456";
>
> $db_name = "bwapp";
>
>  
>
>
> // MySQL database name
>
> $db_sql = "db/bwapp.sql";

