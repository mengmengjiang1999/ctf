**研究人员在云端发现约8000个不安全的Redis，这些Redis未使用TLS加密且未设密码保护。Redis设计之初是在受信任环境中使用，如果允许其在互联网或物联网中使用，攻击者会利用不安全的Redis服务器来发起攻击，例如SQL注入，跨站攻击，恶意文件上传、远程代码执行等。**

## 什么是Redis？

Redis全称为Remote Dictionary
Server，是一种开源内存数据存储结构，常用在数据库，数据缓存等。由于Redis驻留在内存中，它可以为需要处理大量请求的程序提供毫秒级的响应，例如实时聊天，金融服务，医疗保健和游戏等。

据报道，2018年Redis上运行着9亿个容器，其拥有广泛的用户群，官方镜像已被下载超过10亿次，同时被GitHub，Craigslist和Twitter等公司使用。Redis还可部署在云中，利用缓存节省云存储空间。

## Redis分析

利用Shodan发现全球部署了8000多个不安全的Redis。其中一些部署在公共云中，如AWS、Azure和Google云。下图只列出超过50个不安全Redis的云：

![](https://image.3001.net/images/20200407/1586266868_5e8c82f4155c8.png!small)

全球分布：

![](https://image.3001.net/images/20200407/1586267021_5e8c838d150a5.png!small)

Redis官方文档中指出：

Redis旨在受信任环境中的供受信任客户端访问。将Redis直接暴露在互联网中或让不受信任的客户端直接访问会使Redis处于危险之中。

默认情况下，Redis监听6379端口。与SMTP协议相似，此协议通信不加密，虽然有TLS加密选项但不是Redis的默认设置，用户需要手动启用TLS。在Redis启用TLS时，攻击者无法嗅探传输数据。但是启用TLS无法阻止Redis服务器未授权访问。可在在redis.conf中配置requirepass来启用身份验证，也可以通过CONFIG
SET requirepass
password命令来启动。身份验证密码会以明文形式存储，所有可以看到配置信息的人都可以获得密码。但是即使设置了身份验证，未启用TLS时攻击者仍可以通过嗅探获得密码。

![](https://image.3001.net/images/20200408/1586304598_5e8d16562c699.png!small)

为了限制用户执行关键命令，Redis使用了两种方法：禁用命令或将命令重命名。Redis用户可以将命令重命名为空字符来完全禁用命令。

![](https://image.3001.net/images/20200408/1586304813_5e8d172dac50e.png!small)

当不安全的Redis服务器处于暴露状态时，攻击者可能会使用以下命令：

### DEBUG SEGFAULT

此命令可访问无效内存，导致Redis崩溃。攻击者可利用该命令进行拒绝服务攻击，关闭正在运行的Redis。

### EVAL

此命令可在服务器执行LUA脚本。Redis已经利用LUA沙盒对某些功能进行了限制，不加载关键库阻止远程执行，禁用诸如loadfile和dofile之类的功能，确保不会被读取任意文件。

### GET/SET

攻击者可利用该命令检索或修改数据。

### FLUSHALL

此命令能够清空或删除所有数据库中所有key，导致数据丢失，如果Redis上数据未正确备份，还可能导致服务出错。

### MONITOR

此命令显示服务器处理的请求，攻击者可利用它来嗅探流量，寻找目标中的重要文件。

![](https://image.3001.net/images/20200408/1586305422_5e8d198e4b05f.png!small)

## 安全建议

为确保Redis安全，建议采取以下措施：

> 1、确定Redis部署位置，确定访问人员权限设置。
>
> 2、确保环境安全配置正确，不允许其他部署干扰Redis。
>
> 3、同时启用TLS与密码身份验证。
>
> 4、密切注意命令执行情况，如DEBUG SEGFAULT和MONITOR。
>
> 5、正确网络分段。 防止Redis应暴露在其他不受信任的环境中。
>
> 6、不要在前端开发中使用Redis。

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/more-than-8000-unsecured-redis-instances-found-in-the-cloud/)，由Kriston编译，转载请注明来自FreeBuf.COM**

