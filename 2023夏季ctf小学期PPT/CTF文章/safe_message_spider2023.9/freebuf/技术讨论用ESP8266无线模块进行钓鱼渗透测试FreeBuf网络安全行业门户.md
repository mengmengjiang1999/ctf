***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：hacker by ljh，本文属FreeBuf原创奖励计划，未经许可禁止转载**

 **声明：本文仅作为技术分析，禁止用于其他非法用途**

 **至于无线网络安全方面大家都了解 802.11W 这个协议漏洞吧？黑客们经常利用这个漏洞对 wifi 用户发动 deauth 攻击来解除合法 wifi
用户的无线认证关系，从而使 wifi 用户无法连接到自己家的 wifi。运行于 Kali 系统平台上的钓鱼渗透测试工具 wifiphisher
正是利用了这个漏洞，对目标 wifi 进行 deauth 攻击使用户连接不上自己家 wifi，同时伪造一个与目标 wifi 同名，同信道，无密码的钓鱼
wifi，在这种情况下用户很有可能会连接上 wifiphisher 伪造的钓鱼 wifi。一旦用户连接上伪造的钓鱼
wifi，用户手机会自动弹出钓鱼页面，并且无论用户进入任何网址（https 除外）都会被重定向到钓鱼页面。当用户在钓鱼页面上输入 wifi
密码并且确认时，wifi 密码会被显示在电脑屏幕上。**  

但是由于 wifiphisher 使用麻烦，所需工具也比较多，所以用它来进行钓鱼渗透测试的人不多。因此我用 esp8266
做一次钓鱼渗透测试，在这里我给大家分享一下我的经验。

我参考了一个 TPYBoard-v202 钓鱼的源码，编译了一个适用于 ESP8266 的钓鱼固件，大小为 584kb。

下载地址：<https://pan.baidu.com/s/1gdZU_IdDf4OS2z6iqjErtw>

##  一. 制作

###  1\. 烧录

先准备一个 esp8266 无线模块，一个 USB 转 TTL
烧录器。推著使用esp8266-01，因为这个相对简单一些，不需要焊接。其它型号的经测试都可以正常使用。（注意：有的型号的 esp8266
需要焊接，焊接时要迅速，温度不要超过 280 度，否则会损坏 esp8266
无线模块！）![捕获.PNG](https://image.3001.net/images/20180815/1534342062_5b7433ae65591.png!small)

![1534169052_5b718fdc78a4f.png!small](https://image.3001.net/images/20180813/1534169052_5b718fdc78a4f.png!small)

连接好后将 GPIO0
管脚下拉进入烧录模式，如图。![1534169850_5b7192fa87011.jpg!small](https://image.3001.net/images/20180813/1534169850_5b7192fa87011.jpg!small)

连接至电脑，装好驱动。

准备刷固件 。

下载工具 nodemcu 链接：<https://pan.baidu.com/s/1VX9TeFR8wrYTm6ci6ByBmg>

先打开设备管理器，找到 TTL 的 com 端口

![1534169651_5b719233cea46.png!small](https://image.3001.net/images/20180813/1534169651_5b719233cea46.png!small)大家可以看到我这个的端口是
com3。

下面打开 nodemcu，开始烧录

![1533989016_5b6ed09817c38.jpg!small](https://image.3001.net/images/20180811/1533989016_5b6ed09817c38.jpg!small)

1\. 选择端口，在这里我是 com3

2\. 点击
config，然后点击齿轮图案![1533989043_5b6ed0b37a6fa.jpg!small](https://image.3001.net/images/20180811/1533989043_5b6ed0b37a6fa.jpg!small)

3\.
选择固件![1533989154_5b6ed1229a6b6.png!small](https://image.3001.net/images/20180811/1533989154_5b6ed1229a6b6.png!small)烧录地址
0x00000![1533989228_5b6ed16c13915.jpg!small](https://image.3001.net/images/20180811/1533989228_5b6ed16c13915.jpg!small)4\.
回到 operation 选卡，点击 flash
开始烧录![1533989265_5b6ed191ed14d.jpg!small](https://image.3001.net/images/20180811/1533989265_5b6ed191ed14d.jpg!small)如果出现一个绿色的勾就说明烧录成功了
![1533989301_5b6ed1b536603.jpg!small](https://image.3001.net/images/20180811/1533989301_5b6ed1b536603.jpg!small)如果烧录失败请擦除
flash 后重试

##  二. 开始进行测试

将 GPIO0 管脚上拉或悬空，然后复位重启 esp8266，打开串口调试器，这时 esp8266 会自动攻击信号最好的
wifi![1533989473_5b6ed2611628c.jpg!small](https://image.3001.net/images/20180811/1533989473_5b6ed2611628c.jpg!small)大家可以看到，esp8266
启动会搜索到了很多附近的 WIFI，然后它就判断出那 一个信号 最强，我这里刚好是我家的最强，于是 esp8266 开始攻击 Tend_01CB30 这个
WIFI，同时也会建立一个开放的 Tend_01CB30 热点。攻击时 ，esp8266 上的小蓝灯会常亮
。![1533989585_5b6ed2d19cdb0.jpg!small](https://image.3001.net/images/20180811/1533989585_5b6ed2d19cdb0.jpg!small)

此时手机已经连接不到原有路由器的 Tend_01CB30 的
WIFI。这时，如果换成完全不知情的别人，极有可能会去手机设置里面看，怎么连接不上网络了？此时，他只能连接到我们伪装的 WIFI 上来。当其成功连接到伪装的
WIFI 后，会自动弹出钓鱼网页，或者用户访问任何网页（https 除外），都会自动跳转到钓鱼网页。

![1534230910_5b72817e737ef.png!small](https://image.3001.net/images/20180814/1534230910_5b72817e737ef.png!small)测试输入
12345678 点击确认，串口调试器中可以看到获取到的 WIFI 密码，然后停止攻击，小蓝灯熄灭。同时，esp8266
会自己先去尝试连接，来验证密码的准确性，如果连接成功的话，会自动将密码在 串口调试器中显示出来；如果连接失败，esp8266 会继续进行 deauth
攻击，直到获取了正确的 WIFI 密码为止。
![1533989962_5b6ed44a35e7e.jpg!small](https://image.3001.net/images/20180811/1533989962_5b6ed44a35e7e.jpg!small)

这时候你就开心地知道了该 wifi 的密码。

##  三. 防范

如果大家遭到别人的 wifi 密码钓鱼攻击怎么办？下面我告诉大家一个防范方法。

1\. 隐藏 SSID。-（防，让你没法钓。）

当你隐藏 SSID 时，别人就不知道你的 wifi 名，也就无法对你进行 wifi 密码钓鱼。

2\. 绑定 MAC 地址，使用 MAC 过滤。-（坑，就算你知道密码，你也连不上！）

当你开启绑定 MAC 地址或者使用 MAC 过滤时，即使别人对你钓鱼成功，获得了正确的 wifi 密码，那他也连接不上你的 wifi。

3\. 当你发现有人正在对你的 wifi 进行 wifi 密码钓鱼时，你应该......-（躲……）

由于 deauth 攻击仅对无线设备有用，所以有线连接网络仍然正常。所以当你发现有人正在对你的 wifi 进行 wifi 密码钓鱼时，
你应该通过电脑进入路由器后台来修改 wifi 名称和 wifi 信道，这样 deauth 会攻击无效，你连接名称和信道被修改过的 wifi，就会绕过别人的
deauth 攻击，从而恢复网络连接。

 ***本文原创作者：hacker by ljh，本文属FreeBuf原创奖励计划，未经许可禁止转载**

