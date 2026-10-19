**“撞库”是非常常见的一种黑产攻击事件。在常见的安全防护中，安全团队通常会在登陆接口设置安全策略来应对攻击。可是，一旦黑产更换攻击规则，就会导致策略失效。**

在这种的情况下，企业业务安全部门（或者是风控部门）需要的就不仅仅的表层的“防火墙”，而是一套完整的业务风控系统
，能够去快速的根据黑灰产的变化去做规则上的对抗。

本文主要是讲一下，如何利用一套开源的业务风控系统TH-Nebule（星云）防止“撞库”攻击。

我会从“撞库”的基本场景开始讲，逐渐深入到对这套开源系统的使用，包括：如何部署、如何使用、和为什么需要风控系统等。阐述为什么需要一套“系统”去解决业务安全问题，接着手把手教你部署本系统，以及如何利用这套开源的风控系统来阻断风险，并且也提供了模拟测试的方法和事例。

> TH-Nebula是由威胁猎人开源的风控系统，目前源码已放在Github上，完全开放所有源代码，文档，以及安装包。
> 地址：<https://github.com/threathunterX/nebula>

##  0x01 如何防止撞库

###  **1.** **什么是撞库？**

说到撞库，先得从”社工库”说起，社工库是社会工程学数据库的简称，这个数据库里找包含了每个人的各种行为记录（在不同网站上的账号、密码、分享的照片、信用卡记录、通话记录、短信记录、开房记录等等）。

所以当黑客想尝试登录某个网站或者app时，就会用”社工库”里的信息去挨个尝试登录，”撞”出一个个正确账号。

###  **2.** **如何防止撞库呢？** ****

首先从企业的web服务视角来看，如果发现以下几种情况，基本可以判定是在撞库：

> a.一个账号在某个较短的时间内，有多次密码尝试；
>
> b.一定时间内相同密码的出现频次非常高；
>
> c.同一个 IP 或同一个设备，在短时间内使用不同账号密码多次尝试登录。

在这种情况下， 最简单粗暴的方法就是直接在登陆接口加 **安全策略** 。

如：

> 针对a情况，就限制一天之内密码错误次数；
>
> 针对b情况，就针对频率特别高的密码禁止登录（或者校验手机短信/密保问题之后才能登录）；
>
> 针对c情况，就对IP或者设备唯一id进行阈值限制，如限制1分钟内访问登录接口次数<50次。

看起来简单粗暴的方法是可以起到防护作用，但实际 上，
道高一尺魔高一丈，业务安全就没有一劳永逸的方案。只要有利可图的前提下，黑灰产就会不断的变换自己的规则，来 “ 攻破 ” 业务的防护。

比如，业务限制的是1分钟访问限制<50次，那黑产很容易就可以改成40次就能绕过你的策略，这对于他来说只是改了一行代码。

再比如，现在互联网社会里，IP资源可以说是相当廉价，简单就从IP角度去判定可以说非常容易被绕过。

 **所以业务安全的防护不是简单做一层** **“** **防火墙** **”** **就** **可以**
**了，是需要有一套完整的能跟黑产持续对抗的** **“** **系统** **”。** ****

这套系统除了可以自定义策略，从各个维度在网络流量中发现风险以外，还得具备：

> 1）对业务访问流量的分析、统计 — 方便安全人员发现新的攻击行为从而制定新的策略；
>
> 2）策略的效果反馈的展示报表 — 方便安全人员根据策略有效性实时调整；
>
> 3）提供除了业务本身流量外的安全情报，如IP的代理标签、秒拨标签等 — 直接识别高危的流量来源。

TH- Nebula
（星云）就是这样一套系统。它能够让企业有能力主动发现业务风险，并快速的实施攻防对抗。星云采用旁路流量的方式进行数据采集，无需在业务逻辑上做数据埋点或侵入，同时支持本地私有化部署和Docker镜像云端部署，大大降低了使用门槛。

 **系统分为两块服务**

> 1）Nebula服务：包括风控配置分析系统，流量的接收和分析，策略引擎，风控web控制中心等模块；
>
> 2）Sniffer服务：流量的抓取服务。

其中，流量的抓取服务这块为了做到不对业务系统本身做代码修改，提供了多种配置方式。用户可以直接在web服务机器部署，采用旁路流量的方式获取流量；也可以通过标准化nginx或其他http服务的输出日志，采取抓取日志的方式获取流量。

下面就以防止撞库为例子，一步步教你把TH-Nebula风控系统跑起来。

##  0x02 部署TH-Nebula开源项目

如上所述 Nebula 开源项目分为 Sniffer 流量抓取服务、 Nebula
服务两块，建议直接采用docker方式部署，部署参考如下github文档：

[ https://github.com/threathunterX/ nebula
_doc/blob/master/chapter2/section2/section2.2.md](https://github.com/threathunterX/nebula_doc/blob/master/chapter2/section2/section2.2.md)

### **2.1** **Nebula** **服务** ****

参考github教程部署完之后，运行./ctrl.sh
status可查看Nebula服务的运行状态，如下图则代表部署成功，默认配置下Nebula的web控制中心是通过9001端口访问：

    
    
    Name Command State Ports              
    --------------------------------------------------------------------------------------------------              
    nebula /entrypoint.sh /usr/bin/su ... Up 0.0.0.0:9001->9001/tcp              
    nebula-aerospike /entrypoint.sh asd --foreg ... Up 3000/tcp, 3001/tcp,3002/tcp, 3003/tcp              
    nebula-db docker-entrypoint.sh mysqld Up 3306/tcp              
    nebula-redis docker-entrypoint.sh redis ... Up 0.0.0.0:16379->6379/tcp              
    cron RUNNING pid 27, uptime 4 days, 22:23:47              
    java_web RUNNING pid 33, uptime 4 days, 22:23:47              
    labrador RUNNING pid 10286, uptime 2 days, 21:26:41              
    nebula:incident_babel_db_writer RUNNING pid 19, uptime 4 days, 22:23:47              
    nebula:nebula_db_query_web RUNNING pid 12, uptime 4 days, 22:23:47              
    nebula:nebula_offline RUNNING pid 14, uptime 4 days, 22:23:47              
    nebula:nebula_online RUNNING pid 19720, uptime 0:29:22              
    nebula:nebula_query_web RUNNING pid 15, uptime 4 days, 22:23:47              
    nebula:nebula_web RUNNING pid 11, uptime 4 days, 22:23:47              
    nebula:notice_babel_db_writer RUNNING pid 13, uptime 4 days, 22:23:47              
    nginx RUNNING pid 29, uptime 4 days, 22:23:47 ** __**
    
     ** __**

**__**

### **2.2** **Sniffer** **服务**

这里为了方便后面模拟测试，建议就直接采用最简单旁路流量方式(bro驱动)启动 Sniffer 服务，即git上默认配置：

    
    
    ....              
    - SOURCES=default              
    #default driver              
    - DRIVER_INTERFACE=eth0              
    - DRIVER_PORT=80,8080,9001              
    ....

说明：

DRIVER_PORT代表监听的流量端口，此处除了监听80,8080外。还监听了9001端口的流量，这是为了方便测试，可以捕获到Nebula服务自身的web控制中心流量。实际生产环境可以去掉。

把Nebula和Sniffer两块服务正常启动起来，则可通过<http://IP:9001>端口的方式访问TH- Nebula界面了，如图：

![图片 1.png](https://image.3001.net/images/20190513/1557738448759.png!small)

###  **2.3** **配置防止撞库规则**

部署完Nebula服务之后，在策略管理tag中可以看到，Nebula系统针对账号风险规则，已经默认配置了基本的防撞库策略。如下图：

![图片 1.png](https://image.3001.net/images/20190513/15577384889725.png!small)

用户也可以自定义新规则或者修改默认规则，参考如下github文档：

[ https://github.com/threathunterX/ nebula
_doc/blob/master/chapter3/section3/section3.1.md
](https://github.com/threathunterX/nebula_doc/blob/master/chapter3/section3/section3.1.md)

##  0x03 模拟撞库测试

部署并配置好规则之后，接下来就是通过模拟撞库的过程，校验系统的风险检测逻辑。

模拟脚本原理就是针对 Sniffer
模块监听的9001端口连续发起1000次登录请求（这里为了方便测试没有在服务端实现login接口，但风控系统对于404的访问也同样会捕获到）。具体python代码如下

    
    
    #!/usr/bin/env python              
    # -*- coding: utf-8 -*-              
    from requests import get              
    from requests import put              
    from requests import post              
    from requests import delete              
                  
    port = 9001              
                  
                  
    class NewRequestsData(object):              
    def __init__(self, url, data, cookies, method='get'):              
    self.data = data              
    self.url = url              
    self.cookies = cookies              
    self.method = method              
                  
    def request(self):              
    m = dict(              
    get=get,              
    put=put,              
    post=post,              
    delete=delete,              
    )              
    method = m[self.method]              
    text = '默认模式'              
    code = 'None'              
    header = {              
    "connection": "close",              
    "content-type": 'application/json',              
    }              
    try:              
    if self.method in ['get', 'delete']:              
    response = method(self.url, params=self.data, cookies=self.cookies, timeout=10,              
    headers=header)              
    elif self.method in ['post', 'put']:              
    data = dumps(self.data, ensure_ascii=False).encode('utf8')              
    response = method(self.url, data=data, timeout=8, headers=header,cookies=self.cookies)              
    else:              
    raise ValueError              
    text = response.text              
    code = response.status_code              
    except Exception as e:              
    print("error", e)              
                  
    finally:              
    return (text, code)              
                  
                  
    def attack_login():              
    data = dict(              
    username="threathunter@threathunter.cn"              
    )              
    r = NewRequestsData('<http://127.0.0.1:>{}/login'.format(port), data, {})              
    code, text = r.request()              
                  
                  
    if __name__ == '__main__':              
    i = 0              
    for i in range(1000):              
    attack_login()              
    print('总访问次数:', i)

捕获流量的截图：

![图片 1.png](https://image.3001.net/images/20190513/15577385533092.png!small)

![图片 1.png](https://image.3001.net/images/20190513/15577385698306.png!small)

##  0x04 使用TH-Nebula阻断发现的风险

由于TH- Nebula属于旁路分析模式，所以无法主动拦截风险事件，需要与企业端应用进行集成后实现自动阻断的功能。

针对业务系统拉黑阻断，系统提供以下两种风险数据获取方法：

主动推送：TH- Nebula可以将分析发现的风险推送至拦截节点进行自动的风险阻断。

被动调用：TH- Nebula可以将分析发现的风险名单以接口方式提供给拦截节点调用判断风险。

详细请参考文档：

[ https://github.com/threathunterX/ nebula
_doc/blob/master/chapter3/section5.md](https://github.com/threathunterX/nebula_doc/blob/master/chapter3/section5.md)

以上就是通过部署TH-Nebula开源风控系统，配置防撞库策略的整套流程。

在系统使用过程中，如遇任何疑问，可在Github进行反馈：

<https://github.com/threathunterX/nebula>

***本文作者：威胁猎人ThreatHunter，转载请注明来自FreeBuf.COM**

