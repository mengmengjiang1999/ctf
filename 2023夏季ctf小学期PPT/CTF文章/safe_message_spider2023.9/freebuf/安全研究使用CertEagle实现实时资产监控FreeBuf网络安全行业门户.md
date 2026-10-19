![](https://image.3001.net/images/20210317/1615966309_6051b065c1d2168c47cb1.png!small)

## 介绍

在漏洞奖励计划中，只要你不是第一名，那你就是最后一名，银牌和铜牌都没有任何意义。在漏洞挖掘的过程中，网络侦察扮演着至关重要的角色，如果你能比其他人更早地发现/识别新添加的资产，那么你发现/报告该资产上的安全缺陷并因此获得奖励的几率就比其他人高。

就我个人而言，我监控域/子域的CT日志已经有相当长的一段时间了，它给了我很多成功的结果。我的灵感来源于“Sublert : By
yassineaboukir”，它可以检测子域的crt.sh，并且能够定期执行。然而，我选择使用了一些不同的方法，而不是去定期查询crt.sh。我的计划是从实时CT日志feed中提取域信息，因此与其他人相比，我更早地找到新资产的可能性将会更高。

## 工作流

> 监视实时CT日志feed并从该feed中提取域名；
>
> 根据要匹配的域/关键字匹配提取的子域/域；
>
> 如果域名匹配，则发送一条Slack通知；

## 工具要求

> 一台虚拟专用服务器（Unix）；
>
> Python 3.x环境（已在Python 3.6.9环境中测试）；
>
> Slack工作空间（可选）；

## 工具安装&使用

假设你已经安装好了Slack工作空间，接下来我们需要创建一个名为“subdomain-monitor”的信道，然后设置一个传入的Webhook。

### 启用Slack通知

编辑config.yaml文件，然后将你的Slack Webhook URL地址拷贝进去：

![](https://image.3001.net/images/20210317/1615966325_6051b075ce4ce5a134b38.png!small)

### 待匹配的关键词和域名

我们可以在domains.yaml文件中指定待匹配的关键词和域名。

### 待匹配的子域名

![](https://image.3001.net/images/20210317/1615966335_6051b07fc7df83d73963d.png!small)

注意：别忘了域名前面需要有一个[.]。

比如说“.facebook.com”，从实时CT日志中提取出来的域名将跟关键词“.facebook.com”进行匹配，如果能匹配上，则会记录在我们的输出文件（found-domains.log）中。虽然可能会出现假阳性，比如说“test.facebook.com.test.com”和“example.facebook.company”等等，但我们可以使用正则表达式来对结果进行过滤。

### 指定域名/子域名匹配关键词

假设您希望监视和记录其中包含“hackerone”字样的域/子域，然后我们的domains.yaml文件将类似如下所示：

![](https://image.3001.net/images/20210317/1615966345_6051b0896b1eb1c3bd113.png!small)

现在，所有提取的域/子域中都有单词“hackerone”将被匹配并记录（并且会向你发送一个Slack通知）。

很好，我们现在已经完成了工具的初始配置了，接下来我们需要安装所需的依赖组件并运行我们的工具：

    
    
    $ pip3 install -r requirements.txt
    
    $ python3 certeagle.py

![](https://image.3001.net/images/20210317/1615966354_6051b092c24b294949a11.png!small)

 **匹配的域名将出现如下图所示的输出结果：**

![](https://image.3001.net/images/20210317/1615966363_6051b09b2cb0c02d0a066.png!small)

 **Slack通知将如下图所示：**

![](https://image.3001.net/images/20210317/1615966369_6051b0a1e7b444789da9d.png!small)

## 输出文件

程序将会持续运行，并给用户输出所有匹配到的域名，然后将结果输出并存储在输出目录下的found-domains.log文件之中：

![](https://image.3001.net/images/20210317/1615966380_6051b0ac8d289565380d8.png!small)

## 项目地址

CertEagle：【[ _GitHub传送门_](https://github.com/devanshbatham/CertEagle)】

