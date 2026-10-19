## 一、Docker 远程访问TLS加密访问|蜻蜓

以下操作需要提前安装docker, 如果已安装docker请跳过这步, 安装docker命令如下:

    
    
    curl -sSL https://get.daocloud.io/docker | sh
    

#### 1.1 下载认证文件

    
    
    curl -L http://qingting.starcross.cn/static/server.zip > /server.zip   && cd / && unzip server.zip
    

![](https://image.3001.net/images/20220430/1651330903_626d4f57bf032827bece0.png!small)

#### 1.2 添加启动参数

    
    
    mkdir -p /etc/systemd/system/docker.service.d/
    

![](https://image.3001.net/images/20220430/1651330904_626d4f58635b1abbc3f23.png!small)

    
    
    echo "[Service]
    ExecStart=
    ExecStart=/usr/bin/dockerd -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2376 --tlsverify --tlscacert=/server/ca.pem --tlscert=/server/server-cert.pem --tlskey=/server/server-key.pem" > /etc/systemd/system/docker.service.d/override.conf
    

![](https://image.3001.net/images/20220430/1651330905_626d4f59d32f8072f36ec.png!small)

#### 1.3 重置并重启服务

    
    
    systemctl daemon-reload  && systemctl restart docker
    

## 二、FRPC 打通内网机器到公网

#### 2.1 下载FRPC

    
    
    curl -L http://qingting.starcross.cn/static/frpc > ~/frpc  && chmod 755 ~/frpc
    

![](https://image.3001.net/images/20220430/1651330906_626d4f5a138b4bced8549.png!small)

#### 2.2 添加配置

    
    
    vim ~/frpc.ini
    
    
    
    [common]
    server_addr = 49.233.184.147
    server_port = 7000
    
    [qingting-替换成你的用户名]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 2376
    remote_port = 50005(替换成任意50000~60000)
    

![](https://image.3001.net/images/20220430/1651330906_626d4f5a47f8395dbf824.png!small)

#### 2.3 启动FRPC

    
    
    cd ~/ && nohup ./frpc &
    

![](https://image.3001.net/images/20220430/1651330906_626d4f5a8293d9fcd2600.png!small)

查看nohup.out文件,来确定自己的设置的端口有没有冲突。

    
    
    cat nohup.out
    

#### 2.4 启动成功

下图为正确提示，说明59678端口没有被他人使用，建议直接跳到第三节、添加节点继续操作。  
![](https://image.3001.net/images/20220430/1651330906_626d4f5abd5a79bbb2a59.png!small)

#### 2.5 启动失败

下图为端口冲突提示：  
![](https://image.3001.net/images/20220430/1651330907_626d4f5b032dfadea91c8.png!small)

查询frpc进程，然后kill

    
    
    ps -ef |grep frp
    

![](https://image.3001.net/images/20220430/1651330907_626d4f5b3e63ca627dc4b.png!small)

    
    
    kill -9 ****
    

![](https://image.3001.net/images/20220430/1651330907_626d4f5b79a9b5b07447c.png!small)

重新设置端口

    
    
    vim ~/frpc.ini
    
    
    
    [common]
    server_addr = 49.233.184.147
    server_port = 7000
    
    [qingting-替换成你的用户名]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 2376
    remote_port = 50005(替换成任意50000~60000)
    

设置好了去启动它

    
    
    cd ~/ && nohup ./frpc &
    

![](https://image.3001.net/images/20220430/1651330906_626d4f5a8293d9fcd2600.png!small)

查看nohup.out文件,来确定自己的设置的端口有没有冲突。

    
    
    cat nohup.out
    

## 三、添加节点

现在需要回到蜻蜓安全工作台页面中(http://qingting.starcross.cn/node/index.html)

在添加节点的表单出，填写你要给节点的名字,节点地址则填写FRP服务端的地址，以上面的配置为例,地址则为  
这是我刚设置的用户名：chneting666，端口59678  
![](https://image.3001.net/images/20220430/1651330906_626d4f5a47f8395dbf824.png!small)  
添加工作节点处填：  
chenting666  
tcp://49.233.184.147:59678  
![](https://image.3001.net/images/20220430/1651330908_626d4f5c2a5ee83fe4c2a.png!small)

![](https://image.3001.net/images/20220430/1651330908_626d4f5c66f16759335f1.png!small)  
从上图可以看到节点已经配置成功，接下来去添加目标

## 添加目标

点击任务管理→目标管理→添加目标→提交，  
![](https://image.3001.net/images/20220430/1651330908_626d4f5c9f9067c6fc13c.png!small)

点击提交后，系统就会自己下发工具docker镜像到本地。这个过程会比较慢，可以通过命令查看镜像是否下载成功

    
    
    docker images
    docker ps -a
    

![](https://image.3001.net/images/20220430/1651330908_626d4f5ce6090193b9954.png!small)

工具下载成功后会自己启动，然后会对目标进行扫描，目标结果如下图所示。  
![](https://image.3001.net/images/20220430/1651330909_626d4f5d46bd628ac87e2.png!small)

![](https://image.3001.net/images/20220430/1651330909_626d4f5db33c9a3e21fd9.png!small)

