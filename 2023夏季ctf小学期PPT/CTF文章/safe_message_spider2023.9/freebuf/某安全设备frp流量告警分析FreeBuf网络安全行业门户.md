# 前言

第一次使用某商设备，不同厂商的规则库不一样，总的来说流量监控很大一部分是基于规则库来实现的，所以在进行内网穿透的时候就要考虑如何bypass设备告警。

# 环境搭建

ubuntu 公网vps

win10内网主机

> wget
> <https://github.com/fatedier/frp/releases/download/v0.44.0/frp_0.44.0_linux_amd64.tar.gz>

![image-20220803131305941.png](https://image.3001.net/images/20220816/1660632774_62fb3ec611b2d12033f65.png!small)

服务端配置

    
    
    bind_port = 9666    //frp服务端端口  
    token = 123         //客户端连接时的token认证  
    dashboard_port=9999 //面板服务端口  
    dashboard_user=Ggoodstudy   //用户名  
    dashboard_pwd=xxxx         //密码  
    enable_prometheus=true  
    log_file=/var/log/frps.log  //日志存放位置  
    log_level=info  
    log_max_days=3       
    vhost_http_port=9998         //http服务端口

![image-20220803170717845.png](https://image.3001.net/images/20220816/1660632774_62fb3ec6bf56865debca5.png!small)

启动

> ./frps -c frps.ini

如果后台运行

> nohup ./frps -c frps.ini &

![image-20220803142552496.png](https://image.3001.net/images/20220816/1660632775_62fb3ec799b303e5f1439.png!small)

访问面板

> [http://xx.xxx.xx.xx:9666](http://xx.xxx.xx.xx:9666/)

输入账号密码登录

![image-20220803161613310.png](https://image.3001.net/images/20220816/1660632776_62fb3ec837578dd2574c7.png!small)

![image-20220803142443148.png](https://image.3001.net/images/20220816/1660632776_62fb3ec8e6e5b9595d36b.png!small)

此时服务端的配置已成功，客户端配置

    
    
    [common]  
    server_addr = xx.xxx.x.x  
    server_port = 9666  
    token = 123  
    [rdp]  
    type = tcp  
    local_ip = 127.0.0.1             
    local_port = 3389  
    remote_port = 7004  

这里设置代理本机的3389和8077端口

![image-20220803151704866.png](https://image.3001.net/images/20220816/1660632777_62fb3ec9e06d3d3e6f74c.png!small)

`mstsc`连接到主机

![image-20220803151630337.png](https://image.3001.net/images/20220816/1660632778_62fb3ecab4283976027ef.png!small)

抓取数据包

> host xx.xx.xx.xx

![image-20220803154450739.png](https://image.3001.net/images/20220816/1660632779_62fb3ecb795efccf8355f.png!small)

主机ip`192.168.43.246`

![image-20220803154642740.png](https://image.3001.net/images/20220816/1660632780_62fb3ecc2c0a0ea8eca91.png!small)

这里我们可以看到请求的流量包，在请求服务端的9666端口

![image-20220803155112096.png](https://image.3001.net/images/20220816/1660632780_62fb3eccc6df6e592f3fc.png!small)

详情内容就是

![image-20220803160707870.png](https://image.3001.net/images/20220816/1660632781_62fb3ecdb115695976ded.png!small)

可以看到详细数据包中`src_addr`为受害主机出口地址，目的端口`dst_port`为`vps`的穿透端口7004端口，目的ip为vps的`私网地址`。

![image-20220803161214576.png](https://image.3001.net/images/20220816/1660632782_62fb3ecebd68918d1b044.png!small)

此时的连接状态显示的，同时，查看远程时的连接远程桌面时会产生这样流量特征`run_id`

![image-20220803163900688.png](https://image.3001.net/images/20220816/1660632783_62fb3ecf672aac44078e3.png!small)

另外有特别的发现，虚拟机`winserver 2012 R2`在运行客户端之后，vps在连接的过程中也能获取到宿主机的用户名

![image-20220803164958158.png](https://image.3001.net/images/20220816/1660632784_62fb3ed0622a8cafe2c9b.png!small)

这是一个比较特别的点儿，剩余的流量就是vps和跳板机的流量交互，没有很明显的特征。

回头看某商设备对于`frp内网穿透的告警`

![image-20220803170847459.png](https://image.3001.net/images/20220816/1660632785_62fb3ed15db1ebc26db12.png!small)

![image-20220803165516341.png](https://image.3001.net/images/20220816/1660632786_62fb3ed21b0936f92ecbe.png!small)

我们可以对比之前的流量包，缺少的字段且仅有udp端口

![image-20220803165634213.png](https://image.3001.net/images/20220816/1660632787_62fb3ed3121b3862d113a.png!small)

这里可能某商的规则id是基于`udp_port`或者说是`version`字段而产生的告警行为。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

# 魔改

从几个方面规避流量监测

1.交互量加密

对frp的认证使用tls加密，修改服务端frps.ini

> tlsonly = true

客户端配置frpc.ini

> tlsenable = true

2.重写服务端

在上面的流量包中可以看到,在进行交互的时候

![image-20220808161235834.png](https://image.3001.net/images/20220816/1660632788_62fb3ed421958830b1961.png!small)

服务端会请求客户端配置文件内容`proxy_name`,那么在定义变量的服务端，可以重写方法

    
    
    case *msg.NewVisitorConn:  
    if err = svr.RegisterVisitorConn(conn, m); err != nil {  
    xl.Warn("register visitor conn error: %v", err)  
    msg.WriteMsg(conn, &msg.NewVisitorConnResp{  
    ProxyName: m.ProxyName,  
    Error:     util.GenerateResponseErrorString("register visitor conn error", err, svr.cfg.DetailedErrorsToClient),  
    })  
    conn.Close()  
    } else {  
    msg.WriteMsg(conn, &msg.NewVisitorConnResp{  
    ProxyName: m.ProxyName,  
    Error:     "",  
    })  
    }

在客户端和服务器连接的时候流量特征变成自定义变量即可。

# 总结

frp的特征比较明显,所以就单纯魔改frp的话除了流量上做加密外，简单的修改特征bypass设备也是可以实现的。

本文仅限于技术讨论与分享，严禁用于非法途径。若读者因此作出任何危害网络安全行为后果自负，与本人无关。

