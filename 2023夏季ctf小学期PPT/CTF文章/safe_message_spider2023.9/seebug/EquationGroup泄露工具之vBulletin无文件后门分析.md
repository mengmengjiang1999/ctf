作者：[风流@逢魔安全实验室](https://mp.weixin.qq.com/s/5WRXpljL7RFSPRQ2NdHhtA
"风流@逢魔安全实验室")

#### 一、背景介绍

方程式泄漏的几波样本虽然大都已是好些年前人家就在用的，但是时至今日我们再分析这些样本，所涉及的技术细节、攻击方法、思维和角度还是令人叹为观止，更有包括像Eternal系列的漏洞更是直接带来了巨大的影响。其中有一个泄漏了方程式本身ip的样本引得全球安全研究人员所注意，但目前公开的都是关于对该样本的猜想，并无技术分析。该样本是一个专门针对vBulletin论坛系统的功能远控工具，FormSec将在本文当中对该样本进行详细的技术分析和APT攻击解读。

[vBulletin](https://www.vbulletin.com/
"vBulletin")是一个强大，灵活并可完全根据自己的需要定制的论坛程序套件，在全球范围内使用都非常广泛，很多大型论坛都选择vBulletin作为自己的社区。

#### 二、Funnelout样本分析

样本来源：

  * Original file: <https://mega.nz/#!zEAU1AQL!oWJ63n-D6lCuCQ4AY0Cv_405hX8kn7MEsa1iLH5UjKU>

  * Passphrase: `CrDj"(;Va.*NdlnzB9M?@K2)#>deB7mN (as disclosedby the ShadowBrokers, source)`

  * <https://github.com/x0rz/EQGRP>

该功能远控名为FUNNELOUT共涉及四个版本，各版本功能基本一致，适用时间范围大概08年至13年之间，而且根据现有的分析结果来看，该工具和vBulletin系统的结合度非常高，利用的核心原理就是vBulletin框架加载template时的特殊逻辑，可以推断如果vBulletin的版本更新中框架不做大的调整，该工具就一直适用，可能现在已经有了更新的版本。

![](https://images.seebug.org/content/images/2018/01/69b5311c-c3e4-4889-aa7e-99522ab00d3c.jpg-w331s)

这里我们挑选v4.1.0.1版本进行分析。脚本运行环境需要perl支持，直接运行该脚本会展示出该工具的使用方法，其中包括数据库的连接方法、后门操作及其他可自定义参数等。

![](https://images.seebug.org/content/images/2018/01/eb86ffd8-f350-46fd-9eb8-b8f03bc2e329.jpg-w331s)

数据库连接分为两种，一种是直接通过定义数据库连接的相关参数进行数据库访问，包括数据库的ip地址、端口、vbulletin库名、用户名、密码等，在mysql可远程访问时可以通过这种方法连接至数据库进行远程控制；另一种方式就是脚本直接读取vBulletin的数据库配置文件config.php进行解析，获取host、port、dbuser、dbpass、dbname等再进行数据库连接，当然可能是在应用服务器上执行，也可能是将配置文件拖回来后本地解析再远程访问等情况。

对于远程控制的op选项大概分为backdoor、proxy及tag三大功能，其他都是围绕这三点的植入、清除和查看统计等功能，从其命名上也能猜的出来。

接下来我们对这三大块核心功能操作进行分析解读。

##### 01 Backdoor功能分析

door功能的实现比较简单粗暴，这里首先看一下door功能的实现代码，可以看出是直接将一句话后门经过base64编码后放在了数据库当中，默认拼接到了template表的footer
template当中。

![](https://images.seebug.org/content/images/2018/01/e351ce10-bcba-4b91-83c4-2895ec259ddb.jpg-w331s)
![](https://images.seebug.org/content/images/2018/01/35ab43e3-ca73-4498-83a3-0087bf8ab21e.jpg-w331s)

接下来进行复现，运行脚本指定door将后门插入到数据库当中。
![](https://images.seebug.org/content/images/2018/01/5c9db379-9b12-49aa-aef8-0296b7bbcd31.jpg-w331s)

通过showDoor可以看出后门代码通过base64已经拼接在template当中。
![](https://images.seebug.org/content/images/2018/01/dcd9255d-ef0c-4f73-ba04-83860f40dd90.jpg-w331s)

回过头来我们再看看vBulletin的代码，为什么会这样设置后门。

vBulletin的整个框架实现就将需要调用的各种template放在了数据库当中，当调用时会从template表中取出并eval执行，脚本的开发者正是利用了这个逻辑进行后门植入。比如说这里的door的实现，vBulletin的global.php中含有对header和footer模板的调用，funnelout默认是将proxy和door的后门代码植入到了这两个template表当中，如下图所示template代码被取出执行，其中包含的后门代码也被一并执行。

![](https://images.seebug.org/content/images/2018/01/0c82035c-4bba-4382-8bb4-18c42f570f72.jpg-w331s)
![](https://images.seebug.org/content/images/2018/01/2b97a927-f4a6-44cf-adaa-1afd546fbac0.jpg-w331s)

因此vBulletin论坛的维护人员若是在应用服务器进行恶意代码查杀肯定是无效的，只有进行数据库安全审计才可能触发告警，毕竟还要看是否有相关规则，这也就是该后门的厉害之处。

当然所有包含global.php的页面都可以触发后面执行，只需要将需要执行的代码放在请求头的Referrer自定义属性当中即可。

![](https://images.seebug.org/content/images/2018/01/c07d180d-b73e-41fb-92fb-06b83f0d1e1a.jpg-w331s)

##### 02 Proxy功能分析

funnelout的Proxy实现原理与door一致，不过proxy的代码相对复杂一些，proxy有一套模板代码，脚本使用者可以根据实际环境定义代理要访问的host及path等，最后生成特定的proxy代码。

![](https://images.seebug.org/content/images/2018/01/7b9009d2-4eb6-4c41-a901-4408876bb1b8.jpg-w331s)
![](https://images.seebug.org/content/images/2018/01/aa5520be-0a48-43f4-ac2d-1e8afa4f07c3.jpg-w331s)

接下来进行proxy功能复现，使用proxy时需要指定tag，我们根据代码构造一个简单的tag并插入
![](https://images.seebug.org/content/images/2018/01/faa0c84d-ede0-44e1-ba84-78a83c5a896a.jpg-w331s)

插入代理后可以使用对应的showProxy查看header template的内容，和door一样已经过base64编码后拼接在了数据库当中

![](https://images.seebug.org/content/images/2018/01/91d8e67e-8383-49d4-af46-9efea2e275a8.jpg-w331s)

我们看一下被植入base64解码后的proxy代码，如下图所示我已经在代码中进行了一些标注来方便大家理解代码，大概逻辑就是获取到了代理需要请求的内网web服务host，并封装出一个请求包来向内网web服务器发送通过匹配的url请求，可以是get请求也可以post请求，postdata就是向vbulletin请求提交的data。

![](https://images.seebug.org/content/images/2018/01/8933902d-b327-49e7-984e-fb1627e91a8c.jpg-w331s)

可以看出其中将64.38.3.50加入了黑名单中，在这里的具体意义还不确定，但可以确定这是攻击者所操作的一台server，威胁情报中也关联到很多和这个ip有关的方程式样本。

![](https://images.seebug.org/content/images/2018/01/c6176889-7882-459b-a447-1473b2f8f216.jpg-w331s)

最后proxy的复现情况如下，但是这里说的proxy不能说是完全意义上的代理，更有点像ssrf的那种意思

![](https://images.seebug.org/content/images/2018/01/88f16dd9-2bfd-4e6c-a433-0f3cb9dd4168.jpg-w331s)
![](https://images.seebug.org/content/images/2018/01/c7d06d06-f409-4bac-a487-f732e5614777.jpg-w331s)

##### 03 Tag功能分析

Tag代码大体上分为两种，第一种是在建立代理时，脚本会自动加一个proxytag，我们可以使用findAll查看，默认是植入在navbar
template当中。

![](https://images.seebug.org/content/images/2018/01/2211b44d-8de4-4c35-a2c3-71510ad19e26.jpg-w331s)

生成的Tag代码大致如下，相对复杂一些，可以发现tag代码和vBulletin代码高度融合，同样的我也在在代码当中加了一些注释方便大家理解，有兴趣的同学可以自己调试一下。tag代码的主要用途就是经过一些条件判断后触发page
view，比较有意思的是tag代码要触发show
page必须在第一次标记用户后的一天内，超过一天就无效了，只能进行reset，有点自毁程序的意思，并且在第一次标记用户后会产生一个默认为0-6的随机数，随机数随访问次数递减，直至为0时才会触发通过iframe标签触发pageview，触发后该数值会再次减1到-1，并返回用户已被标记等待重置，但该功能在这里的意图目前尚不清楚。

![](https://images.seebug.org/content/images/2018/01/a939816d-cfba-4866-b7a2-f1fa007927ed.jpg-w331s)
![](https://images.seebug.org/content/images/2018/01/5ee974ff-a0de-4388-b720-e8b39448a509.jpg-w331s)

看一下proxytag的复现过程

某vb论坛用户登录后访问了类似链接查看私信内容：

[http://127.0.0.1:8888/vbulletin/private.php?do=showpm&pmid=14](http://127.0.0.1:8888/vbulletin/private.php?do=showpm&pmid=14)

黑客可以通过showTagged可以查看到当前已被标记用户，并在该用户第一次访问时产生随机数4

![](https://images.seebug.org/content/images/2018/01/e81557cb-4998-42a5-915d-2f17e868e620.jpg-w331s)

也就是在该用户访问该页面4次后触发page view，发送携带当前用户名的hex编码的请求。猜测可能是用于标记特定用户再发起针对性攻击。

![](https://images.seebug.org/content/images/2018/01/44ce89d8-3bcb-4850-aa01-9fd7b01b1760.jpg-w331s)

再次使用showTagged查看发现该用户已被标记并等待重置

![](https://images.seebug.org/content/images/2018/01/299819c5-9435-429b-976a-49e514a713c5.jpg-w331s)

第二种则是使用tag命令直接插入的tag代码，这里要细分的话也可以按照是否使用nohttp分为两类，可以从代码上看出它们的区别

![](https://images.seebug.org/content/images/2018/01/4f2bff86-c9b3-453b-9a12-865917238127.jpg-w331s)

对Tag进行了一个总结

![](https://images.seebug.org/content/images/2018/01/a41ff28b-d3ed-4252-be1c-04f14e1b6ab9.jpg-w331s)

这里不使用 –nohttp进行功能复现，同样是通过base64加密后放在了navbar template中

![](https://images.seebug.org/content/images/2018/01/97a34b8b-d9f8-4de5-9e19-29dfc390ece9.jpg-w331s)
![](https://images.seebug.org/content/images/2018/01/a4d234a6-455a-40d2-b1d0-fe3a2a37b3fa.jpg-w331s)

当论坛用户访问时触发page view

![](https://images.seebug.org/content/images/2018/01/b5c1ee62-98be-4030-a453-6d7e56db7827.jpg-w331s)

到这里tag功能基本完成分析，我们在网上找到了一个被公开的攻击痕迹，根据以上分析，这里应该是tag的第三种情况

![](https://images.seebug.org/content/images/2018/01/656e7dfa-13e7-4daf-a130-9f5e0e62127b.jpg-w331s)

其中涉及的域名technology-revealed.com，历史解析记录也有很多国家。
![](https://images.seebug.org/content/images/2018/01/3c30eba3-dc82-4f8c-8405-a3f35a7a2661.jpg-w331s)

另外需要注意的是在tag代码中发现了两个特殊的md5，脚本会校验被标记用户的用户名是否与这两个md5相同

84b8026b3f5e6dcfb29e82e0b0b0f386 Unregistered (EN)

e6d290a03b70cfa5d4451da444bdea39 dbedd120e3d3cce1 (AR)

还有代码中排除标记了来自特殊地域的ip地址

    
    
    if(preg_match('/^(64.38.3.50|195.28.|94.102.|91.93.|41.130.|212.118.|79.173.|85.159.|94.249.|86.108.)/',IPADDRESS)){
                return "";
            }

除了之前提到的唯一确定ip——64.38.3.50，其余ip段涉及到约旦、土耳其和埃及等国家和地区。

最后根据以上信息，我们猜测technology-revealed.com为方程式所操控的服务器，它可以用来接收一些来自敏感话题讨论论坛的特殊地区用户的标记信息，从中可以筛选出特定目标，进行定点攻击，包括可以从vBulletin
访问日志中收集用户ip地址，数据库中收集用户密码信息等，再配合其他方式进行水坑攻击，比如再次利用vBulletin
template进行挂马，还有方程式的其他漏洞足以完成后续攻击，拓广战果。当然以上只是我对APT攻击环节中tag利用的猜想，具体的可能只有方程式自己人知道了。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/517/>

