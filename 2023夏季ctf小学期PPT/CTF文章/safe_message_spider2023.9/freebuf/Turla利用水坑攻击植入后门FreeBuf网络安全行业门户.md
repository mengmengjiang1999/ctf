**研究人员发现了针对Armenian知名网站的水坑攻击。 它依靠假的Adobe
Flash更新，欺骗目标下载两个以前未记录的恶意软件NetFlash和PyFlash。这次行动由活跃了十多年间谍组织Turla发起，其主要目标包括政府和军事组织，之前曾报道过该小组的多个活动，包括Mosquito和LightNeuron。**

##  目标网站

Turla至少破坏了四个Armenian网站，其中包括两个政府网站。 因此，目标可能包括政府官员和政客。以下网站遭到入侵：

> armconsul [.] ru：俄罗斯亚美尼亚大使馆领事处
>
> mnp.nkr [.] am：Artsakh共和国自然保护和自然资源部
>
> aiisa [.] am：亚美尼亚国际和安全事务研究所
>
> adgf [.] am：亚美尼亚存款担保基金

这些网站至少从2019年初就遭到了入侵。Turla利用非法访问向网站中插入恶意JavaScript代码。 例如，对于mnp.nkr [.]
am，在jquery-migrate.min.js（常见的JavaScript库）的末尾附加了混淆的代码，如图1所示:

![](https://image.3001.net/images/20200314/1584163885_5e6c6c2dbf453.png!small)改代码会从'skategirlchina[.]com/wp-includes/data_from_db_top.php.'下载额外的JavaScript脚本。从2019年11月开始发现该网站不再传播恶意脚本,Turla组织似乎是暂停了他们的活动。

##  用户指纹与传播链

访问受感染的网页后，skategirlchina
[.]com会植入第二阶段的恶意JavaScript，并为访问者的浏览器添加指纹。图2显示了此脚本的主要功能。

如果这是用户浏览器第一次执行该脚本，它将添加一个evercookie，该cookie具有由服务器提供的随机MD5值，该值在每次执行脚本时都不同。
evercookie是基于[GitHub](https://github.com/samyk/evercookie)代码实现的。它使用多个存储位置（例如本地数据库，Flash
cookie，Silverlight存储等）来存储cookie值。与常规Cookie相比，它的持久性更高，如果用户只是删除浏览器的Cookie，它不会被删除。

该evercookie将用于识别用户是否再次访问了受感染的网站。当用户第二次访问时，先前存储的MD5值可以用来识别第二次访问行为。

它会收集浏览器插件列表，屏幕分辨率和各种操作系统信息，由POST发送到C＆C服务器。如果有答复，则认为它是JavaScript代码，并使用eval函数执行。

![](https://image.3001.net/images/20200314/1584164424_5e6c6e48c9ec9.png!small)

如果攻击者对感染目标感兴趣，服务器会用一段JavaScript代码进行答复。此活动中Turla只对非常有限的访问网站目标感兴趣。之后会向用户显示假的Adobe
Flash更新警告，如图3所示，目的是诱使他们下载恶意的Flash安装程序。

![](https://image.3001.net/images/20200314/1584164571_5e6c6edbd3ff7.png!small)

没有观察到任何浏览器漏洞的利用技术，活动中仅依靠社会工程技巧。如果用户手动启动了该可执行文件，则会安装Turla恶意软件和合法的Adobe
Flash程序。图4是从最初访问受感染的亚美尼亚网站后恶意负载的传递过程。

![](https://image.3001.net/images/20200314/1584164694_5e6c6f56a73aa.png!small)

##  恶意软件

一旦用户执行了伪造的安装程序，它将同时执行Turla恶意软件和合法的Adobe Flash安装程序。 因此，用户可能认为更新警告是合法的。

###  Skipper

在2019年8月前，受害人将收到一个RAR-SFX，其中包含一个合法的Adobe Flash v14安装程序和另一个RAR-SFX。
后者包含后门的各种组件。 最新版本是由Telsy在2019年5月记录。

Skipper通讯模块使用的远程JavaScript和恶意文件服务器为C＆C服务器，Skategirlchina [.com / wp-includes /
ms-locale.php。

###  NetFlash and PyFlash

8月末发现了新的恶意负载，新的恶意负载是一个.NET程序，它在％TEMP％\ adobe.exe中删除了Adobe Flash
v32的安装程序，在％TEMP％\
winhost.exe中删除了NetFlash（.NET下载程序）。根据编译时间戳记，恶意样本是在2019年8月底和2019年9月初编译的。

NetFlash负责从硬编码URL下载其第二阶段恶意软件，并使用Windows计划任务建立持久性。
图5显示了NetFlash功能，下载名为PyFlash的第二阶段恶意软件。还发现另一个NetFlash样本，该样本在2019年8月底编译，具有不同的硬编码C＆C服务器：134.209.222
[.] 206:15363。

![](https://image.3001.net/images/20200314/1584165690_5e6c733aa043b.png!small)

第二阶段后门是py2exe可执行文件。 py2exe是一个Python扩展，用于将Python脚本转换为Windows可执行文件。
这是Turla开发人员第一次在后门使用Python语言。

后门通过HTTP与硬编码的C＆C服务器通信。 在脚本的开头指定了C＆C URL以及用于加密网络通信的其他参数（例如AES密钥和IV），如图6所示。

![](https://image.3001.net/images/20200314/1584165776_5e6c7390b0ef2.png!small)该脚本的主要功能（如图7所示）将机器信息发送到C＆C服务器，还包括与OS相关的命令（systeminfo，tasklist）和与网络相关的命令（ipconfig，getmac，arp）的输出结果。

![](https://image.3001.net/images/20200314/1584165886_5e6c73fe78845.png!small)

C＆C服务器还可以以JSON格式发送后门命令。命令有：

> 1、从给定的HTTP（S）链接下载其他文件。
>
> 2、使用Python函数subprocess32.Popen执行Windows命令。
>
> 3、修改Windows任务，定期（每X分钟；默认为5分钟）启动恶意软件。
>
> 4、杀死（卸载）恶意软件。 为了确认此指令，恶意软件使用以下字符串将POST请求发送到C＆C服务器：

![](https://image.3001.net/images/20200314/1584166013_5e6c747da7e3a.png!small)

##  总结

Turla仍将水坑攻击作为其初始入侵目标的策略之一。 此活动依社交工程学技巧，利用虚假的Adobe
Flash更新警告来诱使用户下载并安装恶意软件。另一方面，有效载荷发生了变化，可能是为了逃避检测，恶意负载为NetFlash，并安装名为PyFlash的后门，该后门是使用Python语言开发的。

##  IoCs

website

>
> [http://www.armconsul](http://www.armconsul/)[.]ru/user/themes/ayeps/dist/js/bundle.0eb0f2cb2808b4b35a94.js
>
> [http://mnp.nkr](http://mnp.nkr/)[.]am/wp-includes/js/jquery/jquery-> migrate.min.js
>
>
> [http://aiisa](http://aiisa/)[.]am/js/chatem/js_rA9bo8_O3Pnw_5wJXExNhtkUMdfBYCifTJctEJ8C_Mg.js
>
> adgf[.]am

C&C servers

> [http://skategirlchina](http://skategirlchina/)[.]com/wp-> includes/data_from_db_top.php
>
> [http://skategirlchina](http://skategirlchina/)[.]com/wp-includes/ms-> locale.php
>
> [http://37.59.60](https://www.freebuf.com/wp-> admin/post.php?post=230436&action=edit)[.]199/2018/.config/adobe
>
> [http://134.209.222](https://www.freebuf.com/wp-> admin/post.php?post=230436&action=edit)[.]206:15363
>
> [http://85.222.235](https://www.freebuf.com/wp-> admin/post.php?post=230436&action=edit)[.]156:8000

样本

![](https://image.3001.net/images/20200314/1584166217_5e6c754989947.png!small)

MITRE ATT&CK techniques

![](https://image.3001.net/images/20200314/1584166254_5e6c756e23b2e.png!small)

***参考来源：[welivesecurity](https://www.welivesecurity.com/2020/03/12/tracking-turla-new-backdoor-armenian-watering-holes/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

