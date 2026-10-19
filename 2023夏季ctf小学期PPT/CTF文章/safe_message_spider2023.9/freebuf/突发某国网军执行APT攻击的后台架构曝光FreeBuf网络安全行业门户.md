奇安信威胁情报中心红雨滴团队在日常的APT组织跟踪过程中发现，国外推特一用户曝光了一张截图，上面显示了疑似木马控制后台的主机信息界面。

![图片.png](https://image.3001.net/images/20191030/1572400782_5db8ee8e07474.png!small)

  

经过排查发现，该推特实际上是评论了一个人的推特：

![图片.png](https://image.3001.net/images/20191030/1572400799_5db8ee9f1264c.png!small)

  

其中lmhostsvc.net在奇安信威胁情报中心Alpha威胁分析平台上可见，其为一个疑似印度来源的组织Bitter，中文名为蔓灵花。

![图片.png](https://image.3001.net/images/20191030/1572400811_5db8eeabdb9c0.png!small)

  

从曝光的后台界面来看，后台上端显示从左到右为状态，系统，任务，日志，还有登出按钮：

![图片.png](https://image.3001.net/images/20191030/1572400836_5db8eec4188c5.png!small)

  

而根据该域名对应的样本(c0679704a43f33f088de6759583b527e)进行分析后发现，其回连C2的格式均如下所示：

[ _http://lmhostsvc.net/healthne/accept.php?a=dori-PC &b=DORI-PC&c=Windows%207%20Ultimate&d=AdministratorAdministrator0c2fffe3-2bbf-4418-a252-fc560dbb8ee51565536040965860&e=_](https://www.virustotal.com/gui/url/4043becf6f89624dc8e53d113ab591344525d82ebf73a6e5fa423a85c03a12aa)

其中的相关字段正好可以对应后台的对应字段，下面的submit Task提交任务便暴露了Bitter组织下发木马的途径：

![图片.png](https://image.3001.net/images/20191030/1572400893_5db8eefdeddc8.png!small)  

而根据一些情报推测分析，下拉的样本大致如下：

![图片.png](https://image.3001.net/images/20191030/1572400905_5db8ef0942dc9.png!small)  

其中的样本分析并不是本文的主要目的，日后红雨滴团队将公布关于该组织的详细报告。

最后，由于该图片已经开始大范围传播，为了及时响应，我们负责任的披露了此次曝光事件。

*部分IP涉及国内受害者，因此采取打码方式隐去。

相关资料

[ _https://ti.qianxin.com/search?type=domain
&value=lmhostsvc.net_](https://ti.qianxin.com/search?type=domain&value=lmhostsvc.net)

