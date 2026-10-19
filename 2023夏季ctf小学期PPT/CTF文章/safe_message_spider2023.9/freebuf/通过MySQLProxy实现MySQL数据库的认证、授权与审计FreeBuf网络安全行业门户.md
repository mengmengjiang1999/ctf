## 0x00 前言

**年初的时候从猪厂圆满毕业，入职了一家小公司组建“一个人的信息安全部”。正如同市面上大多数小公司一样，没有专职的DBA来抓数据库的工作，因此会有一批人时不时地突然跑过来求爷爷告奶奶似的要访问XX数据库。**

这种状况一次两次勉强可以接受，总来的话数据库里面的账号就会越来越多，账号授权也是一个蛋疼的工作。特别是还会有“mysql从删库到跑路”的问题，员工离职删除账号也会十分的麻烦。对于财大气粗的财阀来说这个问题很好解决，买一套设备就好了，但是对于创业公司要力争做到“零元党”，不然也没办法完全体现出自己的价值。

## 0x01 调研

最初的想法是对开源mysql的代理工具做一次二次开发，于是乎开始搜集类似工具的资料。无意中发现mysql-proxy居然预留了6个钩子允许用户通过Lua脚本去调用他们，也就是说我们可以自行编写Lua脚本来掌握“用户的命运”。

> connect_server() 当代理服务器接受到客户端连接请求时会调用该函数
>
> read_handshake() 当mysql服务器返回握手相应时会被调用
>
> read_auth() 当客户端发送认证信息时会被调用
>
> read_auth_result(aut) 当mysql返回认证结果时会被调用
>
> read_query(packet) 当客户端提交一个sql语句时会被调用
>
> read_query_result(inj) 当mysql返回查询结果时会被调用

显然，通过上述的read_auth和read_query两个钩子函数，我们可以实现对mysql数据库的认证、授权和审计的工作。

## 0x02 设计

我们的目标是认证、授权和审计，那么read_auth函数可以实现认证和授权，read_query可以实现审计的功能。read_query比较容易实现，只需要get到用户发来的sql语句写到消息队列里就好了，我这里就简单地写到redis的list中。

read_auth函数就要相对复杂些，不仅需要对用户提交的一次性password进行校验，还需要读取授权信息，让用户登录到mysql的时候华丽的变身成为我们指定的身份。

![1.png](https://image.3001.net/images/20180613/15288543804633.png!small)

1.用户访问Openresty，后端的lua脚本会调用公司内部使用的im软件的消息接口，将生成的一次性口令发送给用户。与此同时，也会将该口令写入redis。

2.用户使用mysql客户端连接指定的mysql-proxy，此时进入read_auth钩子函数，先对用户提交的口令进行确认。然后会去redis请求当前数据库对应developer、master、owner三个role的授权名单，查看三个名单中是否含有当前用户，如果有则将用户以其对应的role跳转到数据库上。

3.当认证授权成功结束后，用户通过上一步授权的role来访问后端mysql，并且执行的所有sql语句都会进入read_query钩子函数被记录到redis的队列中。

## 0x03 代码

    
    
     local password =assert(require("mysql.password"))  
    local proto =assert(require("mysql.proto"))  
    assert(require("redis"))  
    --字符串切割  
    function string:split(sep)    
    local sep, fields = sep or ":", {}    
    local pattern = string.format("([^%s]+)", sep)    
    self:gsub(pattern, function (c) fields[#fields + 1] = c end)    
    return fields    
    end    
    function read_query( packet )  
    if packet:byte() == proxy.COM_QUERY then  
    local con = proxy.connection  
    local redis = Redis.connect('your_redis_ip',6379)  
    --获取ip对应的域名  
    redis:select('3')  
    local domain = redis:get(con.server.dst.name:split(':')[1])  
    --将执行的sql语句放入redis队列中  
    redis:select('2')  
    redis:lpush('mysql_command_queue',os.date("%Y-%m-%d%H:%M:%S",os.time())  
     .. " " .. con.client.src.address .. "" .. con.client.username .. " " ..  
     domain .. " [" ..packet:sub(2) .. "]")  
    if packet:sub(2) == "SELECT 1" then  
    proxy.queries:append(1, packet)  
    end  
    end  
    end  
    function read_auth()  
    local names = {}  
    --developer、master、owner三个角色权限逐级增大  
    local roles = {[1] = 'developer',[2] = 'master',[3] = 'owner'}  
    local con = proxy.connection  
    local s = con.server  
    local role = ''  
    --认证  
    local redis = Redis.connect('your_redis_ip', 6379)  
    local pass = redis:get(con.client.username)  
    ifpassword.scramble(s.scramble_buffer, password.hash(pass)) ~=con.client.scrambled_password then  
    --认证失败返回错误信息  
    proxy.response.type = proxy.MYSQLD_PACKET_ERR  
    proxy.response.errmsg ="Password error!"  
    return proxy.PROXY_SEND_RESULT  
    end  
    redis:del(con.client.username)  
    --获取ip对应的域名  
    redis:select('3')  
    local domain = redis:get(con.server.dst.name:split(':')[1])   
    redis:select('1')  
    --获取用户对于当前数据库的role  
    for i,v inipairs(roles) do  
    --查询“domain:role”返回相应的名单并将名单切割为table  
    names = redis:get(domain .. ":" .. v):split(',')  
    for k,name in ipairs(names) do  
    if name == con.client.username then  
    role = v  
    break  
    end  
    end  
    end  
    --无授权信息返回错误信息  
    if role == '' then  
    proxy.response.type = proxy.MYSQLD_PACKET_ERR  
    proxy.response.errmsg = "Unauthorized access!"  
    return proxy.PROXY_SEND_RESULT  
    end  
    --最新mysql-proxy加入的新属性  
    local protocol_41_default_capabilities = 8 + 512 + 32768   
    proxy.queries:append(1,    
    proto.to_response_packet({    
    username = role,     
    response = password.scramble(s.scramble_buffer, password.hash(“your_role_password”)),  
    --最新mysql-proxy加入的新属性  
    server_capabilities=protocol_41_default_capabilities   
    })    
    )  
    return proxy.PROXY_SEND_QUERY  
    end

## 0x04 效果

    
    
    [root@ip-172-31-24-123 ~]# mysql -u test -h your_mysql-proxy_ip -P your_mysql-proxy_port-p
    
    Enter password:
    
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    
    Your MySQL connection id is 30341
    
    Server version: 5.7.12 MySQL CommunityServer (GPL)
    
    Copyright (c) 2000, 2018, Oracle and/or itsaffiliates. All rights reserved.
    
    Oracle is a registered trademark of OracleCorporation and/or its
    
    affiliates. Other names may be trademarksof their respective
    
    owners.
    
    Type 'help;' or '\h' for help. Type '\c' toclear the current input statement.
    
    mysql> select user();
    
    +-------------------------+
    
    | user()                  |
    
    +-------------------------+
    
    | developer@your_ip|
    
    +-------------------------+
    
    1 row in set (0.01 sec)

显然，使用用户名test登录mysql-proxy，最终跳转到mysql上时用户已经变为developer。

## 0x05 总结

用于非业务场景连接数据库，比如开发运维人员在公司连接数据库。

管理脚本需要监控每个mysql-proxy进程的状态，负责他们的启动和停止，以及将他们的域名解析为ip存入redis中。

授权脚本读取一个yaml文件，将文件中的授权规则同步到redis中。

每个数据库中都只需要新建developer、master、owner三个账号，yaml配置文件中的内容决定用户使用以上哪种role登录到mysql。

mysql-proxy需要使用源码编译安装。

启动mysql-proxy的命令为:

    
    
    mysql-proxy/bin/mysql-proxy--proxy-address=mysql-proxy_ip:mysql-proxy_port --proxy-backend-addresses=mysql_ip:mysql_port--max-open-files=1024 --user=root --log-file=/var/log/mysql-proxy--log-level=debug --proxy-lua-script=your_lua_file &

## 参考文章

> <http://www.mamicode.com/info-detail-1377900.html>
>
> <https://blog.csdn.net/newzzorg/article/details/8743775?utm_source=tuicool>

 *** 本文作者：SixSixSix，转载注明来自FreeBuf.COM**

