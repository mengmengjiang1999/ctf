## 一、漏洞分析

### 1.1 WebLogic组件介绍

WebLogic是美国Oracle公司出品的一个application
server，确切的说是一个基于JAVAEE架构的中间件，WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。

### 1.2 漏洞描述

Oracle官方在2020年7月份发布的最新安全补丁中披露此漏洞。该漏洞允许未经身份验证的攻击者通过IIOP,T3进行网络访问，未经身份验证的攻击者成功利用此漏洞可能接管Oracle
WebLogic Server。CVSS评分9.8。

### 1.3 漏洞分析

以WebLogic12.1.4.0作为漏洞环境进行分析，首先poc调用ClassIdentity构造方法，将构造的恶意类信息存入m_sPackage，m_sBaseName，m_sVersion三个属性中。

![](https://image.3001.net/images/20200811/1597115404.png!small)

使用Javassist类库获取构造的恶意类的字节流。并调用ClassDefinition构造方法，将获取的恶意字节流存入m_abClass属性中。

![](https://image.3001.net/images/20200811/1597115416.png!small)

调用RemoteConstructor构造函数，将上述获取到的属性，传入m_definition属性中。

![](https://image.3001.net/images/20200811/1597115437.png!small)

在反序列化过程中，序列化数据会进入到RemoteConstructor类中的readResolve()方法中，调用newInstance()方法。并进入realize方法中。

![](https://image.3001.net/images/20200811/1597115458.png!small)

在此方法中，由于调用的getRemotableClass()方法中的m_clz属性使用transient关键字，在反序列化过程中，此属性值为null。在经过两个if判断条件后，执行

    
    
    definition.setRemotableClass(this.defineClass(definition));

代码语句。

![](https://image.3001.net/images/20200811/1597115511.png!small)

在defineClass方法中获取恶意类，及其恶意字节流数据，调用父类ClassLoader的defineClass方法，实现自定义ClassLoader的创建。在加载过程中执行恶意代码，实现攻击。

![](https://image.3001.net/images/20200811/1597115526.png!small)

## 1.4 漏洞复现

搭建WebLogic12.1.4.0漏洞环境，构造恶意的反序列化数据，通过T3发送到目标服务器，当目标服务器解析反序列化数据，会触发恶意代码执行，效果如图：

![](https://image.3001.net/images/20200811/1597115549.png!small)

# 二、影响范围

目前受影响的WebLogic版本：

WebLogic Server 12.1.3.0.0

WebLogic Server 12.2.1.3.0

WebLogic Server 14.1.1.0.0

# 三、解决方案

### 3.1修复建议

1.官方已经针对此漏洞发布补丁，请受影响的用户参考以下链接安装补丁更新：<https://www.oracle.com/security-alerts/cpujul2020.html>

### 3.2临时修复建议

1.可通过关闭IIOP协议对此漏洞进行临时防御。操作如下：

在WebLogic控制台中，选择“服务”->”AdminServer”->”协议”，取消“启用IIOP”的勾选。并重启WebLogic项目，使配置生效。

![](https://image.3001.net/images/20200811/1597115610.png!small)

2.对T3服务进行控制

控制T3服务的方法:![](https://image.3001.net/images/20200811/1597115634.png!small)

在上图这个WebLogic界面中选择安全-筛选器，在下方出现的界面中找到“连接筛选器”，在里面输入

    
    
    security.net.ConnectionFilterImpl

然后在连接筛选器规则中输入

    
    
    127.0.0.1 * * allow t3 t3s，0.0.0.0/0 * * deny t3 t3s

最后保存并重启服务器即可生效。

# 四、时间轴

2020/7/14 Oracle发布2020年7月关键补丁更新公告，其中包括WebLogic组件CVE-2020-14644远程代码执行漏洞。

2020/7/16 深信服千里目安全实验室分析复现漏洞并发布了Oracle七月份高危漏洞安全公告。

2020/8/10 深信服千里目安全实验室复现CVE-2020-14644，并发布解决方案。

# 五、参考链接

> https://www.oracle.com/security-alerts/cpujul2020.html
>
> https://github.com/potats0/cve_2020_14644

