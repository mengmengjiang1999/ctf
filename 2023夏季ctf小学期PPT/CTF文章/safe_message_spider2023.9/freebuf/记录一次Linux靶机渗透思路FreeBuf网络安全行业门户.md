本次主要知识点为：XFF头绕过限制，越权漏洞、sudo滥用提权

##  ** **#001环境搭建****

攻击机kali：192.168.136.129

靶机：192.168.136.142

##  ** **#002 实战writeup****

寻找靶机ip，netdiscover -i
eth0，发现靶机ip为168.136.146。![](https://image.3001.net/images/20230517/1684289003_646435eb69b37a68f5d90.png!small)

Nmap扫描以下端口开放情况，nmap -sV -T4 192.168.136.146，发现开启了80和22端口。

![](https://image.3001.net/images/20230517/1684289029_64643605bfa201970d749.png!small)

直接从80端口http服务入手，提示显示只能本地访问。（小星内心easy job！）

![](https://image.3001.net/images/20230517/1684289045_6464361511266f3c0b21b.png!small)

使用以下插件，增加一个header头XFF的值为0.0.1即可，看到访问即代表成功。

![](https://image.3001.net/images/20230517/1684289056_64643620a44c930a7f18e.png!small)

##  ** **#003 寻找突破口****

首先点击Home，发现url是?page=的传参方式。所以，我们必须要测试文件包含。但是小星测试了很多方式，貌似都不存在文件包含，只能暂缓该步骤。

![](https://image.3001.net/images/20230517/1684289068_6464362cc257b3f79a7a3.png!small)

尝试使用弱口令爆破Login，爆破失败；尝试注入，但是万能密码也无任何发现。

![](https://image.3001.net/images/20230517/1684289084_6464363cb4db92b9f6961.png!small)

Register注册，账号密码均为panda。

![](https://image.3001.net/images/20230517/1684289095_64643647846adb0c2d3c2.png!small)

以下为登录后页面，继续测试功能点。

![](https://image.3001.net/images/20230517/1684289106_646436523c37c20711868.png!small)

点击至Profile，能够查看到自己的账号密码信息，注意观察url，出现user_id。

![](https://image.3001.net/images/20230517/1684289116_6464365c89476d3533142.png!small)

##  ** **#004 进行突破****

如果看到user_id信息，常规是需要检测越权漏洞。开始遍历user_id参数，用户注册后，若user_id是12，那其他用户就是1-11，用burp进行遍历，并配置相关设置。

![](https://image.3001.net/images/20230517/1684289130_6464366ac5ee188830ebf.png!small)

遍历结果显示，除了1418肯定是不存在的用户，其他结果应该是存在的id，因为其长度相同。

![](https://image.3001.net/images/20230517/1684289140_6464367438d378e897862.png!small)

得出user_id的结果为1，2，3，4，5，9都是存在的用户。在url中进行手工验证，例如user_id=1，直接按f12审查元素即可看到密码。

![](https://image.3001.net/images/20230517/1684289150_6464367e0ac18ffc5aabd.png!small)

将密码整理为下图结果。

![](https://image.3001.net/images/20230517/1684289160_646436888d90d57483741.png!small)

##  ** **#005爆破22端口****

利用hydry，加载刚才得到的账号密码作为字典进行爆破。  
exe-P C:\Users\YHS\Desktop\pass.txt
ssh://192.168.136.146，用户alice，密码4lic3，成功爆破。

![](https://image.3001.net/images/20230517/1684289170_64643692d131d94751016.png!small)

利用alice登陆ssh，ssh alice@192.168.136.146。

![](https://image.3001.net/images/20230517/1684289180_6464369c5a394b3b911cb.png!small)

##  ** **#006 提权操作****

ls -la列出所有文件（含隐藏文件），发现一个my_secret（我的秘密），点击查看。

![](https://image.3001.net/images/20230517/1684289191_646436a70f3000be36f6b.png!small)

直接cat flag1.txt，获取到第一个flag。

![](https://image.3001.net/images/20230517/1684289204_646436b4cbaea757df1c4.png!small)

提权至root，暂不操作溢出提权。因为是linux主机，需要查看是否有sudo滥用提权，直接sudo -l
查看即可，看到php命令不需要root密码即可使用。

![](https://image.3001.net/images/20230517/1684289227_646436cb3bcf91017f163.png!small)

此处提供一个参考网址：[
_https://gtfobins.github.io/_](https://gtfobins.github.io/)，网站包含多种命令的用法。

CMD="/bin/sh"

sudo php -r
"system('$CMD');"![](https://image.3001.net/images/20230517/1684289260_646436eceb9048b31028e.png!small)

直接进root/目录，取得最后一个flag。

![](https://image.3001.net/images/20230517/1684289271_646436f7bdcad40a565e6.png!small)

##  ** **#007 总结归纳****

实战过程中，小星通过url参数，发挥fuzz思路，对各个漏洞进行尝试，并利用功能点进行测试。过程涉及到利用水平越权致使用户信息泄露、使用F12审查元素和Hydra工具、Sudo滥用之php命令提权等实战中常用的相关知识点。

  

