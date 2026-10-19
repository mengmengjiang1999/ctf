**防喷符**

作者小菜鸟一枚，在学安全的路上一边自闭一边努力，记录行文潦草，欢迎各位指导交流学习～～～

文章中敏感信息均已做打码处理，文章仅做经验分享用途，切勿当真，未授权的攻击属于非法行为！

## 准备漏洞环境

### 1\. 下载 vulhub 仓库

    
    
    git clone https://github.com/vulhub/vulhub.git

### 2\. 修改 tomcat 弱口令漏洞环境配置

    
    
    vi vulhub/tomcat/tomcat8/tomcat-users.xml

将配置文件中的 user 和 password 修改为非弱口令

### 3\. 启动漏洞环境（根据实际 docker 环境选择下面两个命令）

    
    
    docker compose -f vulhub/tomcat/tomcat8/docker-compose.yml up -d
    # or
    docker-compose -f vulhub/tomcat/tomcat8/docker-compose.yml up -d

![876f17e1-ddae-45d4-a41b-69efe4af04b6.png](https://image.3001.net/images/20230824/1692866597_64e71825c96517a0f9e6b.png!small)

## 准备 HIDS 环境

### 1\. 安装 HIDS 探针（有什么装什么，不做演示？）

### 2\. 更新探针资产（初装探针无需更新）

## 入侵及 HIDS 告警分析

### 1\. 使用 webshell 管理工具（godzilla）生成 java webshell

![1b69049a-cdef-4e4d-ab1f-cce553e84b18.png](https://image.3001.net/images/20230824/1692866599_64e718270f3ac5132a969.png!small)

### 2\. 通过 tomcat 弱口令漏洞上传 webshell

  * 添加 shell.jsp 到 shell.jsp.war

  * 打开 tomcat manager app，使用默认账号密码登录![e47a34cf-3f2f-4767-a1c9-9b02d1968a46.png](https://image.3001.net/images/20230824/1692866600_64e718284bfaa5f6783a7.png!small)

  * 部署 shell.jsp.war 到 tomcat 中![66aa31d7-de6a-494c-aea4-c6588a2305bc.png](https://image.3001.net/images/20230824/1692866600_64e71828ed8b993a5356f.png!small)

  * 查看并分析 HIDS 告警信息![bce6834b-8bce-41c6-a3ab-620248548961.png](https://image.3001.net/images/20230824/1692866602_64e7182a37f506d27fdef.png!small)

![053d32d2-b2bd-4c40-bec8-71babcfb3f5a.png](https://image.3001.net/images/20230824/1692866602_64e7182ad8dc2266f10d8.png!small)![025b947a-df91-42a5-99f6-d930bd9b4984.png](https://image.3001.net/images/20230824/1692866603_64e7182bc626556000fdb.png!small)

  * 根据 webshell 告警中的容器 ID 关联信息，可以看到容器名为 vulhub/tomcat8.0 ![df00f84b-7a4e-46c5-b153-adf02ec3efd8.png](https://image.3001.net/images/20230824/1692866604_64e7182ccef032687a810.png!small)

  

### 3\. 连接 webshell 并执行系统命令

  * 使用 godzilla 连接 webshell![15681fd1-5a1c-40cf-8eb2-32634a8f5150.png](https://image.3001.net/images/20230824/1692866605_64e7182dab6f461d97330.png!small)

  * 执行 whoami 查看系统用户信息

![f7602123-332f-4b0c-a4a4-0235efb8e921.png](https://image.3001.net/images/20230824/1692866606_64e7182e831c0668b95d0.png!small)

  * HIDS 产生告警（网络应用执行基本信息查询命令）

![b4897bcf-7e83-49b7-983f-40a926f21cd1.png](https://image.3001.net/images/20230824/1692866607_64e7182f53ca42e54ec68.png!small)

  * 分析告警详情中进程树信息进程树

![9e18de26-2233-4d7b-b01e-a18072a49dd4.png](https://image.3001.net/images/20230824/1692866607_64e7182fd9f69b3836550.png!small)

通过告警详情中的进程树可以看到，HIDS 清晰记录了可疑命令的进程树以及详细的系统命令。根据进程树信息我们可以得知，攻击者执行的可疑命令为
whoami，被入侵的是一个在 docker 容器内由 java 启动的服务。攻击者执行系统命令的方法是通过 sh -c "{command}" 来实现的。

  * 分析告警应用信息中网络应用信息

![6eed256352114b8d945ee6db9844c5591722.png](https://image.3001.net/images/20230824/1692866608_64e71830b23b28d448ce3.png!small)

根据告警详情中的网络应用信息，可以得知本次入侵中被利用的服务是 tomcat，监听在 8080\8089\8005 端口，运行权限为 root。

### 4\. 判断主机是否出网

  * 打开 dnslog 平台获取 dnslog 地址![571611d7-949a-4d99-9325-7ba0107ae3bb.png](https://image.3001.net/images/20230824/1692866609_64e718313739f1c466eb2.png!small)

  * 通过 godzill 连接 shell 执行 ping dnslog 的命令![c1b6c76c-8b1d-4ab8-b78a-9b3591fed38d.png](https://image.3001.net/images/20230824/1692866609_64e71831c1fca7069032b.png!small)

  * 查看 dnslog 平台是否接收到信息![9d1cfbc6-aa63-43bf-afb8-67f3396fe481.png](https://image.3001.net/images/20230824/1692866610_64e7183240ee21a849731.png!small)

  * 查看 hids 告警信息（可疑命令 && 网络请求）![90e04fc5-a0fa-459b-908e-25a738c2f456.png](https://image.3001.net/images/20230824/1692866610_64e71832e77e94a0a77f2.png!small)

  * 通过告警信息分析入侵行为![2fbb1cba-af5c-4585-a6ae-028662f52810.png](https://image.3001.net/images/20230824/1692866611_64e718336cc8009c29a03.png!small)![3d349981-fba8-4b66-9ff8-ecb7674225c7.png](https://image.3001.net/images/20230824/1692866612_64e71834476d215980a76.png!small)

与上面分析执行系统命令的思路一致就不再赘述，唯一存在差异的点在于，dnslog 请求预期会触发两种类型的告警（进程检测 && 网络检测）。

因为我测试使用的 HIDS 网络异常请求可以关联进程及容器等信息，所以不展开分析进程异常告警了（偷懒）。

## 总结 && 建议

  1. 本文通过简单的漏洞环境及利用手段复现攻击者入侵 web 服务的过程；

  2. 以HIDS 运维人员角度进行分析，旨在帮助大家通过 HIDS 告警对攻击者的入侵链及行为进行分析；

  3. 本文中操作相对基础，建议大家可以作为告警分析练习题，类比到更多入侵场景及自己现阶段在使用的 HIDS 中（浅卷下各家HIDS）；

  4. 评论区欢迎大家晒出HIDS进程树呀，一起交流，共同进步（握拳）。

