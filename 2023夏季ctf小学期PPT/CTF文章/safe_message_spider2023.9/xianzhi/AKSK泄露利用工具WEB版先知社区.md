# AK/SK泄露利用工具

## 介绍

  * 越来越多资产转移到了云上，随之云平台就成为了主要的攻击目标。为了帮助红队更好地实现攻击效果，调用对应API开发了一款自动化工具，集成了丰富的AK/SK利用功能，帮助您快速获取目标云上资源信息，方便进一步深入测试。  
## 搭建&使用

  * github：<https://github.com/libaibaia/cloudSec>
  * docker-compose一键搭建
    
        services:
    java-app:
      container_name: java-app
      image: registry.cn-hangzhou.aliyuncs.com/lx_project/cloud:java-app-1.2
      environment:
        DB_PASSWORD: 111111
      depends_on:
        - db
    vue-web:
      container_name: vue-web
      image: registry.cn-hangzhou.aliyuncs.com/lx_project/cloud:vue-app-1.2
      ports:
        - "80:80"
      environment:
        - API_IP=192.168.61.131
      depends_on:
        - java-app
    db:
      container_name: db
      image: registry.cn-hangzhou.aliyuncs.com/lx_project/cloud:mysql-1.2
      restart: always
      environment:
        MYSQL_ROOT_PASSWORD: 111111
      volumes:
        - /home/cloud/data:/var/lib/mysql
    

## 功能&特点

  * 自动化发现云上资产信息，显示检测状态，方便进行资产管理及AK/SK管理
  * 操作界面WEB化，快速筛选资产，可针对性进行测试
  * 通过WEB界面针对存储桶可直接打包下载所有文件或上传文件，无需复杂更多复杂步骤
  * 数据库支持创建用户，同时可选择开通关闭外网访问，默认最高权限，否则继承当前AK/SK权限
  * 特定情况下无法执行命令可通过绑定密钥对的方式获取权限
  * 控制台用户创建，可直接登录云平台  
## 目前支持的厂商

  * 腾讯云
  * 七牛
  * 阿里云  
## 功能展示  
### AK/SK添加，选择直接扫描或手动执行

  * 支持批量扫描
  * 右边操作按钮对应:编辑>删除>重新扫描>创建控制台永久>列出权限组信息  
![](./img/6017058721026936094.png)  
### 实例操作

  * 执行命令
  * 右边按钮对应生成密钥对，还原密钥对（该操作会重启，主要是针对某些主机没有agent的情况下，或者没有运维助手的执行权限时使用慎用）  
![](./img/8355668549622819168.png)  
![](./img/2733764358918840461.png)  
### 存储桶

  * 上传文件
  * 下载文件（下载全部文件后会创建一个任务）  
![](./img/5725507953239929059.png)  
![](./img/7378941370751297477.png)  
![](./img/7061163256844144659.png)  
### 数据库

  * 如果存在数据库资源，操作方式同上，可直接创建用户，打开关闭外网访问，完成后数据库会刷新  
![](./img/393379050432959561.png)  
### 控制台用户

  * 在key管理处创建  
![](./img/9036936092848116344.png)  
### 关于工具

  * 因为很多资源都缺，没办法一个个去测试，如果方便的师傅可以提供测试一下，详细参考github

