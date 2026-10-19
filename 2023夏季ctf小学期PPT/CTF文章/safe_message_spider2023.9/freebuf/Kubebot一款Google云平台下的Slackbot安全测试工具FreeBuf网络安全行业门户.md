## Kubebot

 **今天给大家介绍的是一款名叫Kubebot的安全测试Slackbot，该工具基于Google 云平台搭建，并且提供了Kubernetes后端。**

![1.png](https://image.3001.net/images/20190430/1556623749_5cc83185a5e60.png!small)

## 项目架构

![2.png](https://image.3001.net/images/20190430/1556623756_5cc8318cbe680.png!small)

## 工具演示视频

## 数据流

1.API请求由Slackbot发起，发送至API服务器，API服务器以Kubernetes(K8s)集群中的Docker容器运行，可以根据需求调整规模大小。

![3.png](https://image.3001.net/images/20190430/1556623768_5cc831983f3cc.png!small)2.API服务器将请求以消息的形式转发至PubSub
ToolTopic。

3.消息发布至Tool Subscription。

4.Subscription Worker在K8s集群上以Docker容器运行，处理来自Tool
Subscription的消息，Worker的数量也可以根据需要进行调整。

5.根据终端用户传递过来的工具、目标和选项信息，工具会在同一K8s集群上初始化特定的Tool Worker，分析结果也会临时存储在容器的本地目录中。

6.工具会检测生成的结果文件是否存在，如果不存在，则会将其push到GitHub上，如果存在则会进行文件比对，并将新的文件push到GitHub上。

7.Tool Worker会将修改信息回传给Slack，并删除Tool Worker，因为它们已经完成了自己的任务。

注意：在部署K8s集群之前，请从Google Container
Registry中下载所有的API服务器Docker镜像、SubscriptionWorker以及Tool Worker。

## Kubebot目前集成的工具列表如下（持续更新中…）：

> [Custom
> Enumall](https://github.com/anshumanbh/kubebot/blob/master/tools/enumall/enumall-> ab.py)
>
> [git-all-secrets](https://github.com/anshumanbh/git-all-secrets)
>
> [gitrob](https://github.com/michenriksen/gitrob).
>
> [gitrob-> server](https://github.com/anshumanbh/kubebot/blob/master/docs/gitrob-> server.md)
>
> [git-secrets](https://github.com/awslabs/git-secrets)
>
> [gobuster](https://github.com/OJ/gobuster)
>
> [nmap](https://nmap.org/)
>
> [subbrute](https://github.com/TheRook/subbrute)
>
> [sublist3r](https://github.com/aboul3la/Sublist3r)
>
> [truffleHog](https://github.com/dxa4481/truffleHog)

## Kubebot整合的自动化工作流如下（持续更新中…）：

> [wfuzz basic authentication
> bruteforcing](https://github.com/anshumanbh/kubebot/blob/master/docs/automation-> workflow.md)

### Slack中的Slash命令样本：

![4.png](https://image.3001.net/images/20190430/1556623788_5cc831ac48552.png!small)

    
    
    /runtoolnmap|-Pn -p 1-1000|google.com
    
    /runtoolsublist3r|-t 50|test.com
    
    /runtoolgobuster|-m dns -w fierce_hostlist.txt -t 10 -fw|google.com
    
    /runtoolenumall|-s shodan-api-key|test.com
    
    /runtoolsubbrute|-s subfiles/names.txt -v|kubebot.io (This takes a long time)
    
    /runtoolgitrob|analyze --no-banner --no-server|test,abc
    
    /runtooltrufflehog||<https://github.com/KingAsius/iaquest.git>
    
    /runtoolgitsecrets||<https://github.com/pmyagkov/slack-emoji-bots.git>
    
    /runtoolgitallsecrets|-user|secretuser1,secretuser2
    
    /runtoolgitallsecrets|-toolName repo-supervisor -org|secretorg123
    
    /runtoolgitallsecrets|-repoURL|<https://github.com/anshumanbh/docker-lair.git>
    
    /runtoolgitallsecrets|-gistURL|<https://gist.github.com/anshumanbh/f48dc1d9d8b2158252f716a3719bf8e6>
    
    /runautomationwfuzzbasicauthbrute|<[www.target.com](http://www.target.com)>.

### 可选的字典文件：

    
    
    bitquark_20160227_subdomains_popular_1000000.txt
    
    deepmagic.com_top500prefixes.txt
    
    fierce_hostlist.txt
    
    namelist.txt
    
    names.txt
    
    sorted_knock_dnsrecon_fierce_recon-ng.txt
    
    subdomains-top1mil-110000.txt

![5.png](https://image.3001.net/images/20190430/1556623817_5cc831c9e715a.png!small)

## 视频教程合集

Kubebot使用教程：【[点我观看](https://youtu.be/RKvtyU3CcZk)】

Kubebot本地安装教程：【[点我观看](https://youtu.be/-ApGLGOV0vc)】

Nmap运行教程：【[点我观看](https://youtu.be/R2aMWGyldlI)】

子域名爆破工具教程：【[点我观看](https://youtu.be/6SdkjrRGFhI)】

Git搜索工具教程：【[点我观看](https://youtu.be/aip1Q0aCBhQ)】

## 项目地址

Kubebot：【[GitHub传送门](https://github.com/anshumanbh/kubebot)】

***参考来源：[anshumanbh](https://github.com/anshumanbh/kubebot)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

