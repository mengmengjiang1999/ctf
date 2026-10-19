# CVE2022-26923复现分析

 **利用前提** ：

> 拥有一个普通用户的凭证
>
> 开启了 Certificate Service 服务
>
> 能访问到445、636端口

## 搭建域环境

攻击机kali：192.168.116.128

域控：windows server 2019 ip：192.168.116.137

安装配置证书服务（已经安装好了AD服务）

![1](https://image.3001.net/images/20220522/1653218030_628a1aee5e2e3b17c3b12.png!small)

一直下一步即可。

记一下CA名称。（为了方便）

![2](https://image.3001.net/images/20220522/1653218066_628a1b1257ce692e42e9e.png!small)

添加一个普通的用户。至此环境搭建完成。

![3](https://image.3001.net/images/20220522/1653218077_628a1b1d6122e2f94a4aa.png!small)

## 请求证书流程

假设此时已经获得了一个普通用户（test）的凭据。

使用certipy工具可以在已知用户账户密码的情况下，请求一个证书。这里的-ca的参数就是之前配置域控证书服务时候的名称，为了方便直接使用了，正常情况下不知道可以使用bloodhound等工具获取。

![4](https://image.3001.net/images/20220522/1653218091_628a1b2b24b524f7a8387.png!small)

抓包：

可以看到是通过SMB发起的证书请求。

![6](https://image.3001.net/images/20220522/1653218102_628a1b3625ef29da7e49d.png!small)

然后使用得到的test.pfx证书对KDC进行身份验证。使用证书进行身份验证时，certipy将尝试请求Kerberos TGT 并检索帐户的 NT
哈希。（当使用证书进行kerberos认证的时候，返回的票据的PAC包里面含有NTLM票据。）

![13](https://image.3001.net/images/20220522/1653218113_628a1b41181902b8c5cc4.jpg!small)

![5](https://image.3001.net/images/20220522/1653218122_628a1b4aa7d6ac2274190.png!small)

抓包：

![7](https://image.3001.net/images/20220522/1653218130_628a1b52f026372c1ef47.png!small)

## 漏洞利用

### 创建机器账户

尝试创建一个新的机器帐户，请求证书，然后使用证书进行身份验证。（-template参数machine）

下面的操作是添加了一个计算机账户，然后把这个账户的dns hostname改成和域控的一样。然后再用certipy去请求的时候，会去根据dns
host去解析身份。

> 关于认证：简而言之，用户账户和计算机账户的认证方式不一样，而漏洞就是利用了这一点
>
> 用户账户的认证有一个 User Principal Name (UPN)机制
>
> 计算机账户认证不通过UPN，而是有一个SubjectAltRequireDns

实际上这里如果直接把dNSHostName改成dc的话是报错的，因为有一个servicePrincipalName属性会检查唯一性，当修改了个一模一样的dNSHostName会导致约束冲突。

想要修改成功，需要包含 dNSHostName 值的 servicePrincipalName 属性值必须符合 dNSHostName
属性。但是我们可以删除包含 dNSHostName 的 servicePrincipalName ，删除了之后再修改dNSHostName就ok了。

这里有一个疑惑，既然有两个一样的hostname，那么为什么请求的时候会映射到我们希望的账户上，而不是DC上的machine account？

这涉及到PKINIT & Certificate
Mapping一个工作流程，可以看[这篇文章](https://research.ifcr.dk/certifried-active-directory-domain-privilege-escalation-cve-2022-26923-9e098fe298f4)

![8](https://image.3001.net/images/20220522/1653218153_628a1b6959d6c7c4f58f3.png!small)

请求证书：

![9](https://image.3001.net/images/20220522/1653218161_628a1b71435e95230df0a.png!small)

获取哈希：

![10](https://image.3001.net/images/20220522/1653218170_628a1b7ac6ab10316e512.png!small)

至此得到了域控账户的NT哈希。

### 获取域控权限

使用 NT 哈希执行 DCSync 攻击以转储所有用户的哈希。

![11](https://image.3001.net/images/20220522/1653218179_628a1b838ecef99b502bf.png!small)

通过wmiexec连接，管理员权限

![12](https://image.3001.net/images/20220522/1653218187_628a1b8b74f7a1c61895a.png!small)

## 参考

> <https://research.ifcr.dk/certifried-active-directory-domain-privilege-> escalation-cve-2022-26923-9e098fe298f4>
>
> <https://xz.aliyun.com/t/10064#toc-11>

