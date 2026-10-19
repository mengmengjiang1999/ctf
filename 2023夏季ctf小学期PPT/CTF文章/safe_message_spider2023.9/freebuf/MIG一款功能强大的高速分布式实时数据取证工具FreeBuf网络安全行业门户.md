***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

 **MIG，全称为Mozilla
InvestiGator，它是一款基于Mozilla平台的高速分布式实时数据取证工具，广大研究人员可以利用MIG来对远程终端进行安全诊断和取证分析。**

![1.jpg](https://image.3001.net/images/20190721/1563718566_5d3473a6b02fb.jpg!small)

## 注意事项

> Mozilla目前已不再维护Mozilla InvestiGator(MIG)项目。
>
> 同时Mozilla也不再在内部使用该项目源码。
>
> 本项目仅出于研究目的，请不要将其用于恶意用途。

## 快速使用/Docker

你可以使用Docker在本地配置MIG项目，容器环境不适合正式版使用，但可以允许我们进行快速实验，并提供一个具备大多数MIG组件的单一容器环境。

从Dockers Hub获取项目源码：

    
    
    $docker pull mozilla/mig
    
    $docker run -it mozilla/mig

或者，你也可以使用项目源码构建自己的镜像文件：

    
    
    $ cd $GOPATH/src/github.com/mozilla/mig
    
    $docker build -t mozilla/mig:latest .
    
    $docker run -it mozilla/mig

在容器环境内，你可以使用MIG工具来查询本地代理：

    
    
    mig@5345268590c8:~$/go/bin/mig file -t all -path /usr/bin -sha25c1956eba492b2c3fffd8d3e43324b5c477c22727385be226119f7ffc24aad3f
    
    1agents will be targeted. ctrl+c to cancel. launching in 5 4 3 2 1 GO
    
    Followingaction ID 7978299359234.
    
     1 / 1[=========================================================] 100.00% 0/s4s
    
    100.0%done in 3.029105958s
    
    1sent, 1 done, 1 succeeded
    
    ed11f485244a/usr/bin/wget [lastmodified:2016-07-05 15:32:42 +0000 UTC, mode:-rwxr-xr-x,size:419080] in search 's1'
    
    1agent has found results

如需了解更多MIG的功能，可以参考这篇【[文档](https://github.com/mozilla/mig/blob/master/doc/cheatsheet.rst)】。

## 工具机制

![2.jpg](https://image.3001.net/images/20190721/1563718597_5d3473c5ccc2d.jpg!small)

MIG由基础架构中所有系统上的代理终端所组成，这些代理要求可以对终端的文件系统、网络状态、内存情况以及配置信息进行实时审计。

![3.png](https://image.3001.net/images/20190721/1563718602_5d3473ca98a04.png!small)

想象一下，假设现在是星期天的早上七点钟，有人发布了一个严重的PHP安全漏洞（包括漏洞利用代码和入侵威胁指标IoC），而你的PHP应用程序正好就存在这个漏洞。那你这个周末就崩了，而且你还需要手动审计大量系统中成千上万行代码，想想就可怕。

此时，MIG就派上用场了，我们可以使用MIG的file模块并基于签名来搜索存在漏洞的PHP应用程序（基于文件的MD5、正则表达式或文件名）。类似的，我们还可以用MIG来调查特定的日志条目、后门文件、僵尸网络IP地址或内存中的特定字符串。仅仅通过几行命令，我们就可以远程审计数千个系统，以验证安全风险是否存在。

MIG采用的是轻量级代理，安全性有保证，而且容易部署，我们可以将它们添加到系统的基础部署中，而不必担心影响现有的生产网络。MIG采用了快速的异步传输机制，可以使用AMQP将操作命令分发到各个端点，并依赖Go信道来防止阻塞事件发生。运行的操作指令将存储到PostgreSQL数据库和磁盘缓存中，以实现平台可靠性。值得一提的是，大多数操作在代理上只需要几百毫秒即可完成。

## 技术分析

MIG采用Go编程语言开发，并且使用了REST
API和RabbitMQ来向终端代理发送和接收已签名的JSON消息，接下来MIG会将所有数据存储在一个Postgres数据库中。

### 工具优势：

> 1、 大规模分布式意味着速度非常快；
>
> 2、 易于部署和跨平台特性；
>
> 3、 使用OpenPGP保证数据安全；
>
> 4、 高度隐私安全性，不会从终端获取元数据；

![5.jpg](https://image.3001.net/images/20190721/1563718643_5d3473f3a127a.jpg!small)

## 工具演示视频

【演示视频1】

【演示视频2】  
  

### MIG论坛

欢迎加入#mig论坛：【[irc.mozilla.org](https://wiki.mozilla.org/IRC)】【[mibbit](https://chat.mibbit.com/)】

## 参考文档

> <https://github.com/mozilla/mig/blob/master/doc/concepts.rst>
>
> <https://github.com/mozilla/mig/blob/master/doc/configuration.rst>

## 项目地址

> Mozilla InvestiGator：【[GitHub传送门](https://github.com/mozilla/mig)】

***参考来源：[mozilla](https://github.com/mozilla/mig)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

