>
> 随着微软发布漏洞补丁，多家媒体先后报道，但对漏洞描述与官方公开文档有一定出入。微软内部人员称：部分媒体存在选择性说明事实、夸大事实、恶意揣测和发布不负责任的虚假内容的情况。基于此，笔者想和大家客观地梳理一下此次所谓的“微软超级漏洞”。

 **在微软例行公布的1月补丁更新列表中，有一个漏洞引起了大家的高度关注：一个位于 CryptoAPI.dll 椭圆曲线密码 ( ECC )
证书的验证绕过漏洞——CVE-2020-0601。  
**

有意思的是，在微软发布公告后，美国国家安全局（NSA）也发布了关于CVE-2020-0601漏洞的预警通告。根据通告可以得知，这个漏洞是由NSA率先独立发现并汇报给微软的（微软在报告中对NSA致谢）。

![捕获1.PNG](https://image.3001.net/images/20200115/15790781082199.png!small)

 **CVE-2020-0601介绍**  

**![2.PNG](https://image.3001.net/images/20200115/15790797114691.png!small)**NSA发布的预警通告**  
**

## 漏洞介绍

该漏洞位于Windows
CryptoAPI(Crypt32.dll)验证椭圆曲线加密算法证书的方式，可能影响信任的一些实例包括（不限于）：HTTPS连接、文件签名和电子邮件签名、以用户模式启动的签名可执行程序。

此外，该漏洞可以让攻击者伪造代码签名证书对恶意可执行文件进行签名，使文件看似来自可信的来源。例如，可以让勒索软件或其他间谍软件拥有看似有效的证书，从而促使用户安装。中间人攻击并解密用户连接到受影响软件的机密信息也是主要的攻击场景之一。

## 影响范围

> 目前，支持使用带有指定参数的ECC密钥的证书的Microsoft Windows版本会受到影响，包括了Windows 10、Windows Server
> 2016/2019以及依赖于Windows CryptoAPI的应用程序。

而Windows 10 之前的版本，如Windows 7、Windows Server 2008 R2 等均不受该漏洞的影响。

## 缓解措施

快速采用补丁是目前唯一已知的缓解措施。尽管尚未出现公开的攻击方式和案例，但建议大家及时安装安全更新。更新后，当检测到有人试图利用CVE-2020-0601进行攻击时，系统将在每次重新启动Windows日志后在事件查看器中生成事件ID
1。

## 安全建议

除了安装修补程序之外，企业还可以采取其他措施保护端点，比如：

> 1、从网络流量中提取证书，检查可疑的属性；
>
> 2、通过执行TLS检查，但不使用Windows进行证书验证的代理设备来承载流量；
>
> 3、在企业内部部署私有根证书颁发机构，并且在特定计算机/服务器位置控制第三方软件的部署和使用；
>
> 4、符合条件的企业可以申请加入微软 Security Update Validation Program (SUVP) 或 Microsoft
> Active Protections Program (MAPP)，从而提前从微软获得安全更新以进行相关的测试分析。

目前，多家媒体、多个安全厂商都跟踪报道了CVE-2020-0601，如希望了解更多，建议参考微软官方公告和360预警通告，如下：

> [_https://portal.msrc.microsoft.com/en-US/security-> guidance/advisory/CVE-2020-0601_](https://portal.msrc.microsoft.com/en-> US/security-guidance/advisory/CVE-2020-0601)
>
> _<https://www.zerodayinitiative.com/blog/2020/1/14/the-> january-2020-security-update-review>_
>
>
> [_https://cert.360.cn/warning/detail?id=ae1a55dda462ae805e7c54faa1fbe232_](https://cert.360.cn/warning/detail?id=ae1a55dda462ae805e7c54faa1fbe232)  
>

 ***本文作者：kirazhou，转载请注明来自FreeBuf.COM**

