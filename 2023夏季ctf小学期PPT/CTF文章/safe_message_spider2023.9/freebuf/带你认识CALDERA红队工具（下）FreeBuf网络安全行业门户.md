在上一期《带你认识CALDERA红队工具（上）》的文章中，我们对该红队工具进行了初步的认识，以及学习了工具所需的环境配置和安装，并以Windows10作为靶机成功进行了远程代理，本章我们将继续深入了解该工具的使用，话不多说，Here
we go！

 **环境介绍：**

Kali (CALDERA主机):192.168.178.131

Windows10:192.168.178.195

  

##  **0x00 Adversaries（敌手）**

![image.png](https://image.3001.net/images/20210319/1616134163_605440137691372bcb3a2.png!small)

图1 Adversaries选项

  

 **Adversaries**
翻译中文为“敌手”，这一项的功能的配置文件包含了基于ATT&CK的大部分战术集合（大部分攻击配置还未完善），可以在红队端进行特定的攻击战术配置，还允许上传自定义payload来作为战术的一部分进行使用。

我们可以点击“VIEW”来自由搭配我们的战术集合，也可以点击下拉菜单“Select an existing
profile”来选择工具已经提供的一些战术，在原有的战术中进行添加或者调整。

![image.png](https://image.3001.net/images/20210319/1616134164_605440140a3b3ff9d95a1.png!small)

图2 自定义战术模式

  

![image.png](https://image.3001.net/images/20210319/1616134165_605440150fdf50b30b351.png!small)

图3 战术选择

可以看到，CALDERA为我们提供了多种选择方案，包括了检测、发现、枚举、捕获、端口、扫描、远程管理等等。

例如我们选择“Discovery”，就会显示该战术下多个不同类型的能力，也可以点击右上角的“add
adversaries”来添加现有战术文件，或者点击“add ability”来单独添加能力。

![image.png](https://image.3001.net/images/20210319/1616134166_605440160bd4bbad86338.png!small)

图4 discovery adversary

每个能力左下角的图标表示目前该能力支持测试的操作系统，点击单个能力能看到详细介绍,包括了该技术在ATT&CK中的编号、行为名、行为描述等。

![image.png](https://image.3001.net/images/20210319/1616134167_60544017d08121ed41bbe.png!small)

图5 indentify local users

最后如果有修改请点击“save”进行保存。

##  **0x01 Operations(行动)**

![image.png](https://image.3001.net/images/20210319/1616134169_605440195954c54550b3e.png!small)

图6 operations选项

顾名思义，这一项功能就是对设定好的攻击行为做出行动。

点击“operations”，再在弹出的功能框中点击“VIEW”添加行动。

![image.png](https://image.3001.net/images/20210319/1616134169_60544019e66d7a6e0746f.png!small)

图 7添加行动

  * Operation name ：填入行动名称

  * BASIC OPTIONS：基本配置

  * AUTONOMOUS：自动化设置

  * STEALTH：隐秘性设置

  * SCHEDULE：定时设置

我们填写行动名为“RED”,战术选择“Discovery”，其他选项保持默认。

设置完成后，点击“Start”后开始执行设定的行动。

![image.png](https://image.3001.net/images/20210319/1616134170_6054401a82a6a6ea5bd51.png!small)

图8 行动设置

从运行结果中可以看到，并不是所有的行动都能成功执行，这取决于系统的版本，payload的有效性和网络状态等多方面因素。执行成功的状态颜色为绿色(失败为红色、超时为蓝色)，可以通过点击每个行动后方的星星来查看反馈。

![image.png](https://image.3001.net/images/20210319/1616134171_6054401bd0842422d9b4d.png!small)

图9 行动过程

![image.png](https://image.3001.net/images/20210319/1616134173_6054401de0ac8e78d79c4.png!small)

图10 “Identify local users”的行动反馈

##  **0x02其他相关插件**

###  **【Plugins- >Debrief】**

该功能能够将已执行过的行动生成攻击流程图和行动关联图，便于攻击后的复盘分析。

![image.png](https://image.3001.net/images/20210319/1616134174_6054401eee6256a3e4aca.png!small)

图11Debrief

###  **【Plugins- >GameBoard】**

作为在演习中监视红队和蓝队的行动，看蓝队能否够检测到红队的行为，做出响应，中断攻击行为。以竞技的界面进行展示，任意一方只要做出有效的响应就能获得分数。

面板中显示选择的红队在这次实验中已经获得了6分。

![image.png](https://image.3001.net/images/20210319/1616134176_605440206219564fdf8bf.png!small)

图12 GameBoard

###  **【Advanced- >Configuration】**

可以对通讯连接的地址及插件进行配置，我们可以将各个服务的IP地址改为CALDERA主机的IP地址，方便以后的使用。

![image.png](https://image.3001.net/images/20210319/1616134177_60544021ab6846b86d19f.png!small)

图13 configuration

###  **【Advanced- >Obfuscators】**

介绍红队行动前混淆模式的介绍，方便红队使用该功能，用于逃避检测。

![image.png](https://image.3001.net/images/20210319/1616134179_605440233b01fffed1117.png!small)

图14 Obfuscators

目前提供的混淆模式：

  * plain-text：明文

  * base64：base64编码混淆

  * base64jumble：混淆base64中的命令，然后添加字符以逃避base64检测。这可能会导致重复连接运行。

  * caesar cipher：凯撒加密混淆

  * base64noPadding：base64编码混淆，然后删除填充

  * Steganography：图像隐写

 **【Advanced- >Planners】**

这是一个策略器，用于一个正在运行的操作应该如何决定使用哪些功能以及何种顺序。具体地说，策略器的逻辑包含执行操作的单个阶段的决策。

![image.png](https://image.3001.net/images/20210319/1616134180_605440245dd7b978208ad.png!small)

图15 Planners

  

##  **0x03 小结**

通过对CALDERA红队工具的学习和使用，有助于我们进一步提高对红队测试和ATT&CK框架的理解，感兴趣的小伙伴可以进一步学习CALDERA，发现更多有意思的功能。

  

 **免责声明：** 本文提及的技术仅可用于私人学习测试等合法场景中，任何不当利用该技术所造成的刑事、民事责任均与本文作者无关。

  

 **\---- END ----**

