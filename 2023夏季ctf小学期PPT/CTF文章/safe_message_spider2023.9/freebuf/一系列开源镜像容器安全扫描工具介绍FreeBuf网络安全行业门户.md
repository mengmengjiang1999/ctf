## 1、前言

在 v1.0 版本中，veinmind-tools 支持了诸多 **针对镜像的安全扫描功能** ，如：

>   * log4j2安全检测
>   * 恶意文件检测
>   * webshell检测
>   * 敏感信息检测
>   * 资产和漏洞检测
>   * 弱口令检测
>   * ...
>

但基于目前的安全形势，仅仅针对于镜像所进行的安全扫描是远远不能满足用户的安全需求的，容器层面的安全问题同样值得安全人员的关注和重视。因此，问脉安全团队
**对问脉 sdk 进行了更新优化** ，随着问脉 sdk 的迭代发展，VeinMind-Tools 目前已支持对容器层面进行 **多种安全问题的检测**
。下文将选取其中几个安全扫描功能做简要介绍。

## 2、veinmind-weakpass

### 简介

veinmind-weakpass 是一款 **镜像弱口令扫描工具** 。它可以快速扫描镜像/容器中的弱口令，支持并发扫描，支持
dockerd\containerd 运行时，支持使用者自定义用户名以及字典。

### 业务场景

 **弱口令自检**  
如果容器内某个服务的密码过于简单，那么攻击者就可以通过多次尝试爆破服务的账号密码。获取账号密码后攻击者就可以登陆该服务，获取该服务的权限，从而获取敏感信息，进行敏感操作，甚至可能通过该服务的某些特性获得容器内的权限。

由此可见， **弱口令是十分常见同时危害又十分严重的安全问题** 。为了避免出现这类安全问题，使用者可以通过 veinmind-weakpass
插件提前进行自检，该插件会 **报告出容器/镜像内存在的弱口令**
。根据此报告，相关人员可以对这些弱口令问题进行修复，防止出现攻击者通过弱口令非法登陆服务的问题。

### ​使用

1\. 检查本地某个镜像有无弱口令风险。

    
    
    ./veinmind-weakpass scan image [imagename/imageid]

![](https://image.3001.net/images/20230424/1682304488_6445ede835a80051bdd0c.jpeg!small)  

2\. 检查本地某个容器有无弱口令风险。

    
    
    ​./veinmind-weakpass scan container [containername/containerid]

![](https://image.3001.net/images/20230424/1682304501_6445edf53e884eebc0737.jpeg!small)  

3\. 检查本地所有镜像有无弱口令风险。

    
    
    ./veinmind-weakpass scan image

![](https://image.3001.net/images/20230424/1682304520_6445ee084d97c1b9d1c81.jpeg!small)  

4\. 检查本地所有容器弱口令风险。

    
    
    ./veinmind-weakpass scan container

![](https://image.3001.net/images/20230424/1682304537_6445ee1996e2a37870fd4.jpeg!small)  

5\. 检查某个用户名是否存在弱口令风险。

    
    
    ./veinmind-weakpass scan container/image -u username

![](https://image.3001.net/images/20230424/1682304554_6445ee2aa12593e40addf.jpeg!small)  

6\. 自定义字典。

    
    
    ./veinmind-weakpass scan container/image -d ./pass.dict

![](https://image.3001.net/images/20230424/1682304568_6445ee3815eb02035ab16.jpeg!small)  

7\. 检查某个服务是否存在弱口令风险。

    
    
    ./veinmind-weakpass scan container/image -a ssh,mysql,redis

> >  **目前已支持的服务**
>>

>> serverName| version  
>> ---|---  
>> ssh| all  
>> mysql| 8.X  
>> redis| all  
>> tomcat| all  
  
  8. 解压默认字典到本地磁盘。

    
    
    ./veinmind-weakpass extract

  9. 指定输出 html 报告。

    
    
    ./veinmind-weakpass scan container/image -f html

生成的 html 报告如图：

![](https://image.3001.net/images/20230424/1682304579_6445ee4326f2c15b556fc.jpeg!small)  

  

## ​3、veinmind-webshell

### 简介

veinmind-webshell 是一款 **webshell 扫描工具** ，支持 **dockerd\containerd 运行时** 。

### 业务场景

 **webshell自检**

webshell 是以 asp、php、jsp 或者 cgi
等网页文件形式存在的一种代码执行环境，也可以将其称做为一种网页后门。如果攻击者通过文件上传等漏洞将 webshell 上传至容器内，那么他们就可以通过
webshell
获取容器内的权限。通过容器内的权限，攻击者可能会非法获取到一些敏感数据，或者进行一些具有破坏性的操作。甚至如果容器内还存在逃逸漏洞的话，攻击者还可以通过容器内的权限进行逃逸，获取到宿主机的权限，实施更进一步的入侵。

因此，容器内存在 webshell 是一个十分严重的安全问题。为了避免出现这类安全问题，使用者可以 **通过 veinmind-webshell
插件提前进行自检** ，该插件会报告出存在的 webshell。根据此报告，相关人员可以对这些风险问题进行修复，防止出现因存在 webshell
导致的安全问题。

### 使用

使用前需要先去百川平台获取「关山 token」，详细步骤请见 **veinmind-webshell：**
https://github.com/chaitin/veinmind-tools/tree/master/plugins/go/veinmind-webshell

  1. 检查本地某个镜像有无 webshell。

    
    
    ./veinmind-webshell scan image [imageID/imageName] --token [关山token]

![](https://image.3001.net/images/20230424/1682304860_6445ef5c740b831324ebd.jpeg!small)  

2\. 检查本地所有镜像有无 webshell。

    
    
    ./veinmind-webshell scan image --token [关山token]

![](https://image.3001.net/images/20230424/1682304872_6445ef688fcc6a2cc3978.jpeg!small)  

3\. 检查本地某个容器有无webshell。

    
    
    ./veinmind-webshell scan container [containerID/containerName] --token [关山token]

![](https://image.3001.net/images/20230424/1682304915_6445ef93c882ae1cb9471.jpeg!small)  

4\. 检查本地所有容器有无webshell。

    
    
    ./veinmind-webshell scan container --token [关山token]

![](https://image.3001.net/images/20230424/1682304933_6445efa526967b40636bd.jpeg!small)  

5\. 输出 html 格式报告。

    
    
    ./veinmind-webshell scan container/image --token [关山token] -f html

生成的 html 报告如图：

![](https://image.3001.net/images/20230424/1682304942_6445efae5d3bea2108043.jpeg!small)  

## 4、veinmind-log4j2

### 简介

veinmind-log4j2 用于 **扫描容器/镜像的内存在 log4j2 漏洞的文件** ，支持 dockerd\containerd 运行时。

### 业务场景

 **log4j2 漏洞自检**

Apache Log4j2 是对 Log4j 的升级，它比其前身 Log4j 1.x 做出了重大改进，并提供了 Logback 中许多可用的改进，同时修复了
Logback 架构中的一些问题。是目前最优秀的 Java 日志框架之一，许多应用都是用其作为日志框架。由于 Apache Log4j2
某些功能存在递归解析功能，攻击者可直接构造恶意请求，触发远程代码执行漏洞，漏洞利用无需特殊配置，影响范围十分广泛，漏洞危害十分严重。如果某些文件存在该漏洞，攻击者可以通过其直接获取容器内的权限，这可能会造成十分严重的安全后果。

因此，容器内存在 log4j2 漏洞是一个十分严重的安全问题。为了避免出现这类安全问题，使用者可以 **通过 veinmind-log4j2
插件提前进行自检** ，该插件会报告出存在 log4j2 的文件。根据此报告，相关人员可以对这些风险问题进行修复，防止出现因存在 log4j2
漏洞而导致的安全问题。

### 使用

  1. 检查本地指定镜像有无漏洞。

    
    
    ./veinmind-log4j2 scan image [imageID/imageName]

![](https://image.3001.net/images/20230424/1682305098_6445f04aaf80963f6540d.jpeg!small)  

2\. 检查本地所有镜像有无漏洞。

    
    
    ./veinmind-log4j2 scan image

![](https://image.3001.net/images/20230424/1682305108_6445f054c10f8791c8460.jpeg!small)  

3\. 检查本地指定容器有无漏洞。

    
    
    ./veinmind-log4j2 scan container [containerId/containerName] 

![](https://image.3001.net/images/20230424/1682305119_6445f05facb110e85a9d6.jpeg!small)  

4\. 检查本地所有容器有无漏洞。

    
    
    ./veinmind-log4j2 scan container 

![](https://image.3001.net/images/20230424/1682305130_6445f06abb37242fc1865.jpeg!small)  

5\. 输出 html 格式报告。

    
    
    ./veinmind-log4j2 scan container/image -f html 

生成的 html 报告如图：

![](https://image.3001.net/images/20230424/1682305146_6445f07a29e7bdd4d7aad.jpeg!small)  

  

## 未来 Feature

### 插件构想

随着越来越多的开发者参与，插件的数目逐步增长，我们将会面临一个很现实的问题：如果将这些插件全部打包进入平行容器内，镜像的体积将达到一个很尴尬的大小。

当更多的插件参与到 Veinmind-Tools 生态后，我们将开启一个全新的社区模式：插件市场。

开发者可以将自己的插件发布至插件市场，除了非官方内置的插件外，还可以通过宿主直接从插件市场获取各种自定义插件来进行扫描。

  

使用工具：https://stack.chaitin.com/tool/detail?id=3

