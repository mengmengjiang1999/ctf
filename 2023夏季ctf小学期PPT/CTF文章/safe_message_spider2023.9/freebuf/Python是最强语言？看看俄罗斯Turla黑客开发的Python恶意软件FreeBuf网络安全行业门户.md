****

_大家好，我是 **零日情报局** 。_  

 _本文首发于公众号 **零日情报局** ，微信ID： **lingriqingbaoju** 。_

  

Turla，一个圈内人尽皆知的俄罗斯背景APT间谍组织。这次这只毒蛇开发了一种新型恶意软件，盯上亚美尼亚开启了持续性攻击，领事馆网站、能源部无一幸免。

值得说道的，这次攻击中，Turla在惯用的Adobe Flash更新诱饵中，
**一次性增加了两个从未被记录的恶意组件NetFlash和PyFlash，甚至还第一次出现了使用Python语言的情况。**

![1.png](https://image.3001.net/images/20200313/1584107992_5e6b91d8416eb.png!small)

（Turla水坑攻击目标）

你没看错，一次性增加了两个从未被记录的新恶意组件，还启用了Turla几乎未涉及的编程语言。对此， **零日不得不猜测，Turla工具库可能又要扩大了。**

  

# **为新恶意组件铺路的Turla水坑攻击**

甭管安装执行什么恶意软件，入侵都是第一步，所以在聊新增恶意组件前，都得知道Turla是怎么入侵的。

首先，Turla在目标网站暗中植入恶意代码JavaScript。拿mnp.nkr [.] am来说，Turla就在常见的JavaScript库
jquery-migrate.min.js 末尾，附加了一段混淆代码。

![2.jpg](https://image.3001.net/images/20200313/1584108049_5e6b921129613.jpg!small)

（混淆JavaScript代码注入mnp.nkr [.] am网站）

有了这串不起眼的代码，就能在skategirlchina [.] com / wp-includes /data_from_db_top.php
加载外部JavaScript。

一旦有人访问受感染网站，skategirlchina.com就会释放恶意JavaScript，并在访问者浏览器上添加指纹。

就像这样

![3.png](https://image.3001.net/images/20200313/1584108062_5e6b921e24220.png!small)![4.png](https://image.3001.net/images/20200313/1584108194_5e6b92a28a3a8.png!small)（恶意URL被伪装的指纹脚本）

接下来上演的就是大家都熟悉的，指纹识别和恶意软件交付危险行为。有意思的是，Turla会筛选用户价值，分别处理。

比如说，你是第一次执行脚本的低价值目标，就会在浏览器上添加一个由服务器提供的随机MD5值evercookie。

这样这个值在后续的每一次执行脚本中都不同，进而长期持续的跟踪用户，甚至你直接删除浏览器cookie，也无法停止evercookie的运行。

而 **当你是潜在的高价值目标时，Turla的服务器则会给你展示一个创建iframe的JavaScript代码，开始对你下套。**

你看到的界面，就会变成这种诱导更新的画面。

![5.jpg](https://image.3001.net/images/20200313/1584108223_5e6b92bf7a100.jpg!small)

（伪造的Adobe Flash更新iframe）

这时回过头梳理Turla的整个攻击过程，会发现从最初访问受感染网站到恶意负载的传递，是这样一个过程：

![6.png](https://image.3001.net/images/20200313/1584108241_5e6b92d140920.png!small)

也是完成了上述流程，Turla才真正开始执行恶意软件，也就是零日开篇提到新增的两种恶意软件。

  

  

# **新增恶势力：NetFlash和PyFlash**

如果分阶段的话，前面说的其实是Turla攻击的入侵阶段，后面的则是Turla部署的新恶意软件了。

**恶意组件1：NetFlash（.NET下载器）**

这个新发现的有效载荷NetFlash是一个. NET应用程序。

  
 **它在%TEMP%\adobe.exe中删除了一个Adobe Flash v32安装程序，并在%TEMP%\winhost.exe中删除了一个.
NET下载程序。**

从ESET捕获的恶意样本来看，2019年8月底和2019年9月初被编译后，NetFlash才被上传到水坑攻击的C＆C服务器。

NetFlash会从硬编码URL下载其第二阶段恶意软件，并使用Windows计划任务保持新后门的持久性，以便于后续攻击。

  

![7.jpg](https://image.3001.net/images/20200313/1584108293_5e6b93054eab5.jpg!small)

通过NetFlash，可下载名为PyFlash的第二阶段恶意软件。

**恶意组件2：PyFlash**

第二个新发现的恶意软件，其实是一个py2exe可执行文件。

所谓的py2exe，指的是一个Python扩展，主要功能是将Python脚本转换为独立的Windows可执行文件。

PyFlash通过HTTP与硬编码的C＆C服务器通信，在脚本的开头指定了C＆C URL以及用于加密所有网络通信的其他参数（例如AES密钥和IV）。

![8.jpg](https://image.3001.net/images/20200313/1584108337_5e6b9331bac26.jpg!small)

（PyFlash Python脚本中的全局变量）

通过脚本的指定，直接让这个脚本能够把相关计算机信息反馈给C＆C服务器。

![9.png](https://image.3001.net/images/20200313/1584108352_5e6b934062277.png!small)

（PyFlash的主要功能）

值得一提的是，C＆C服务器还能以JSON格式发送后门命令，进行特定操作。 在目前新发现的PyFlash中，能进行的命令主要有这几种：

  

![10.png](https://image.3001.net/images/20200313/1584108386_5e6b936265baa.png!small)  

总的来说，Turla虽然一直以自主开发著称，但这还是零日第一次看到Turla开发人员在后门程序中使用Python语言。

  

# **政府国防注意**

Turla组织最早可追溯到90年代“月光迷宫”（Moonlight Maze），在其异常活跃的近十年，也始终以政府、外交和军事组织的为目标，尤其是北约国家。

对于这样一个APT里异常活跃的麻烦制造机，攻击武器一般的恶意软件开始更新，无疑就意味着威胁的扩大，毕竟即使只有一种网络武器，也能不受限制的攻击所有目标。

![11.jpg](https://image.3001.net/images/20200313/1584108433_5e6b9391b80c6.jpg!small)

再联想到Turla的俄罗斯背景，以及此次新增恶意软件攻击的目标亚美尼亚，考虑到双方微妙的地缘关系，这背后的地缘政治博弈，可能又暗藏着一出大戏。

  

#  
**零日反思**

跳出技术维度，防不胜防的APT，很难用好坏去评判。

  
就像Turla，对攻击目标来说，无疑是安全的破坏者，而对Turla背后的政治利益集团来说，Turla则更像一把好用的武器。对Turla或者APT有想法的，咱评论区见。

**零日情报局** 作品

微信公众号： **lingriqingbaoju**

如需转载，请后台留言

欢迎分享朋友圈

**参考资料：**

 **ESET** **《TrackingTurla：新的后门通过亚美尼亚水坑提供》**  
  

![640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=](https://mmbiz.qpic.cn/mmbiz_gif/ogxqTSgGMasGVL9aHDxN6cMicXEfsic0iaLQKNnmgZFBvtgQSy2acqibbyVkbicnWhSiaAMgIY8cC61BnbGxw2yUiavSA/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

 ****

