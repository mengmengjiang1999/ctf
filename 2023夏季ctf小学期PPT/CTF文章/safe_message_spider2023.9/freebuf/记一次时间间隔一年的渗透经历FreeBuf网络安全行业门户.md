原创： 梦呓233 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](https://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

![0Yq2JaKp26S](http://si1.go2yd.com/get-image/0Yq2JaKp26S)

​

前言 正如标题所写，这次渗透中间的时间间隔长达一年，为什么说是一年呢，是因为我在去年刚刚接触到漏洞盒子的时候曾经提交过这个漏洞。

当时平台显示漏洞已修复并且可公开细节，所以我就没再深入的研究，就在昨天我无聊翻动漏洞列表的时候，我发现这个漏洞竟然还未修复，于是就有了进一步测试的想法。

![0Yq2K9KA48m](http://si1.go2yd.com/get-image/0Yq2K9KA48m)

​

信息收集 我是通过目录扫描发现这个wwwroot压缩文件的，毕竟那会也是刚接触安全的萌新，整天琢磨着碰见个弱口令什么的。
在查看网站源码文件的时候并没有发现类似于登录入口的文件，反倒是发现了一个fd3000的文件夹，里边是另外一个站点的源码，这个站点倒是有登录接口和数据库文件。

![0Yq2K7hjvay](http://si1.go2yd.com/get-image/0Yq2K7hjvay)

​

第一个没有登录入口的站

![0Yq2K3M6iRs](http://si1.go2yd.com/get-image/0Yq2K3M6iRs)

​

fd3000文件夹中有登陆入口的站 于是直接根据文件路径在浏览器中访问后台管理页面：
<http://XXX.com/fd3000/admin/login.asp>

这里通过查看配置文件conn.asp获取到数据库文件的路径为：db/a23Jfi7fcFDf3.asp

![0Yq2JyTdMv2](http://si1.go2yd.com/get-image/0Yq2JyTdMv2)

​

一般的遇见后缀为asp的数据库文件，我们将后缀改为mdb即可打开，这里使用辅臣数据库浏览器打开

![0Yq2JuTBUno](http://si1.go2yd.com/get-image/0Yq2JuTBUno)

​

获取到账号密码之后成功进入后台，照例开始寻找上传点。

![0Yq2JvqNBSa](http://si1.go2yd.com/get-image/0Yq2JvqNBSa)

​

上传木马 首先上传一张正常的图片

虽然弹窗提醒上传成功但是却提示没有权限，查看空间文件列表，并未发现所上传文件，应该是管理员出于安全的目的限制了上传目录的写入权限。

开始寻找别的途径渗透。 在瞎翻文件的过程中，在上传目录找到了很久之前被人上传的图片马。

![0Yq2JqwQcSG](http://si1.go2yd.com/get-image/0Yq2JqwQcSG)

​

抱着试试看的心情尝试连接，果然404了。

![0Yq2JrWqWSu](http://si1.go2yd.com/get-image/0Yq2JrWqWSu)

​

![0Yq2Jogfeme](http://si1.go2yd.com/get-image/0Yq2Jogfeme)

​

爆破ftp 首先进行端口扫描，发现21端口是开启的，在使用数据库中的账号密码登陆无果之后，尝试爆破

![0Yq2JmRmtua](http://si1.go2yd.com/get-image/0Yq2JmRmtua)

​

这里使用一款Windows下的ftp爆破工具ftpscan，具体用法为：ftpscanip 线程
在爆破了长达半个小时之后终于拿到ftp密码，在这期间我开始在其他站点的后台寻找上传点，不过还好字典够强大，也幸亏是一家小服务商的主机，如果是阿X云之类估计早就被ban掉了。

![0Yq2Jp627c0](http://si1.go2yd.com/get-image/0Yq2Jp627c0)

​

![0Yq2Jo3NhEu](http://si1.go2yd.com/get-image/0Yq2Jo3NhEu)

​

上传大马 拿到ftp之后就开始尝试上传木马提权

![0Yq2JoPsYbY](http://si1.go2yd.com/get-image/0Yq2JoPsYbY)

​

上传asp木马后尝试连接，成功访问

![0Yq2JkB0HGi](http://si1.go2yd.com/get-image/0Yq2JkB0HGi)

​

尝试提权

![0Yq2JkGTa6a](http://si1.go2yd.com/get-image/0Yq2JkGTa6a)

​

由于并非是管理员权限，所以cmd能够执行的操作很有限，开始尝试使用IIS7提权，上传iis7.exe到服务器

![0Yq2JjuTeXg](http://si1.go2yd.com/get-image/0Yq2JjuTeXg)

​

上传完成后（嫌麻烦后来把exe丢到了根目录），尝试提权 这里直接新建一个管理员用户： C:\iis7up.exe"net user aaa aaa/add"

![0Yq2JjSSR9c](http://si1.go2yd.com/get-image/0Yq2JjSSR9c)

​

查看用户是否成功创建

![0Yq2JiKq1RI](http://si1.go2yd.com/get-image/0Yq2JiKq1RI)

​

将aaa用户加入管理组

![0Yq2Ji3zFzs](http://si1.go2yd.com/get-image/0Yq2Ji3zFzs)

​

查看端口，3389未开启

![0Yq2Jgy2RI8](http://si1.go2yd.com/get-image/0Yq2Jgy2RI8)

​

使用注册表命令开启3389 REGADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server/v
fDenyTSConnections /t REG_DWORD /d 00000000 /f

![0Yq2JhaMdyi](http://si1.go2yd.com/get-image/0Yq2JhaMdyi)

​

命令执行之后没有任何反应，再次查看端口，发现3389已经成功开启

尝试远程连接服务器，成功！

![0Yq2JefLIzA](http://si1.go2yd.com/get-image/0Yq2JefLIzA)

​

![0Yq2Jd4eCsS](http://si1.go2yd.com/get-image/0Yq2Jd4eCsS)

​

尝试渗透内网
很不幸的是，经过我的测试这应该是台独立服务器，甚至只是一台简单的windows7PC，别问我为啥，我在开始菜单发现了蜘蛛纸牌（无奈脸），初步猜测是同一栋办公楼的几家小公司合买的服务器，不然怎么会一台独立服务器放这么多乱七八糟不相关的站啊喂！！！
写在最后：
本次渗透能够成功的主要原因就是管理员的失误操作造成了敏感文件泄露，且ftp服务使用了弱口令，本人并未对服务器做出任何危害性操作，已经帮忙删除网站根目录敏感文件并且通知了网站管理员。
声明： 作者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关。

![0Yq2JePRvNI](http://si1.go2yd.com/get-image/0Yq2JePRvNI)

​

相关练习 FTP服务器安全配置实验：了解Serv-U软件的使用方法，掌握FTP服务器安全配置的原理。实现安装Serv-U配置FTP服务器和安全设置。
点击“[实验:FTP服务器安全配置实验(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015081917272400001)”，可预览学习（PC端操作最佳哟）

![0Yq2Jedmntw](http://si1.go2yd.com/get-image/0Yq2Jedmntw)

