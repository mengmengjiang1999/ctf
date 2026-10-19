## **一、引言**

金万维旗下系列产品存在信息泄漏、sql注入等漏洞，配合后台应用的功能可直接获取服务器权限。

说起金万维可能有的小伙伴没听过，但以下界面经常做攻防演练的小伙伴应该不会陌生：

![](https://image.3001.net/images/20220919/1663565761_6327ffc14b52f5aa4d4e5.png!small)![](https://image.3001.net/images/20220919/1663565768_6327ffc847c5d1b2b8493.png!small)![](https://image.3001.net/images/20220919/1663565775_6327ffcff3ea245b5471c.png!small)通过搜索指纹
body="GNRemote.dll"，发现公网上就存在大量案例：

![](https://image.3001.net/images/20220919/1663565850_6328001aeede5ec97c4ea.png!small)![](https://image.3001.net/images/20220919/1663565858_6328002268aac22edfe9e.png!small)
**本文以安全研究为目的，分享对该套系统的代码审计和漏洞挖掘过程，文中所提到的漏洞均已提交给CNVD &CITIVD，请勿用做非法用途。**

##  **二、环境搭建**

金万维官网上就能直接下载和搭建系统，如“天联高级版”下载地址为：

https://www.gnway.com/prod/res.php?id=tkpro_server

ps：事实上“易速联”、 “易联通”、“畅捷通”、“天联”、“天联高级版”、“云联”、“远程通”、“路路通”等都是其直属产品或oem合作产品，均存在漏洞。

下载以后直接安装即可，安装目录默认在C:\GNWay目录下：

![](https://image.3001.net/images/20220919/1663565901_6328004d72bb29bf713c4.png!small)Web路径为：C:\GNWay\TeamLinkPro
Server\Web，安装完成后根目录有phpinfo.php，index.php等，但并不能解析，主要由GNRemote.dll来调用功能，其余为静态文件。

![](https://image.3001.net/images/20220919/1663565926_632800665ccec6dfaf55f.png!small)安装后界面如下：

![](https://image.3001.net/images/20220919/1663565954_632800824ef290a61aa51.png!small)

##  **三、信息泄露**

通过代码审计发现发现一处未鉴权接口，可获取用户名：

![](https://image.3001.net/images/20220919/1663565974_6328009642408a548d8ca.png!small)

对应的url地址为：/GNRemote.dll?GNFunction=GetUsers

![](https://image.3001.net/images/20220919/1663565997_632800add2e97796f4e6a.png!small)有了用户名以后可以尝试通过弱口令登录后台。

##  **四、SQL注入**

用户名泄漏+弱口令当然不是最稳妥的进入后台方法，通过代码审计找到一处注入点， userid直接拼接导致注入。

![](https://image.3001.net/images/20220919/1663566029_632800cdbb61c37ea05da.png!small)该接口是将用户添加到管理员的接口，所以需要通过遍历userid获取用户信息。如果返回00代表该用户存在，反之不存在，而注入需要获取存在的userid，每个站userid不同，遍历一下找到一个存在userid便可进行注入。

![](https://image.3001.net/images/20220919/1663566054_632800e6546765bca0b9d.png!small)![](https://image.3001.net/images/20220919/1663566062_632800eea1b12518d8001.png!small)注入点还是挺好找的，通过注入可获取用户密码。比较麻烦的是密码解密，该密码的加密方式并不是传统的MD5。

![](https://image.3001.net/images/20220919/1663566081_6328010124c32367e9c78.png!small)PS：信息泄漏的漏洞适用于全版本，sql注入的漏洞适用于2018以上的版本。

##  **五、密码解密分析**

首先IDA反编译GNRemote.dll文件，再其中搜索password关键字，发现相关的sql语句，然后找一处相对比较简单的语句（涉及的字段比较少，便于分析），如下图所示：

![](https://image.3001.net/images/20220919/1663566110_6328011e44d3361cd8fec.png!small)经过交叉引用分析，发现该语句位于导出函数ChangePassword函数中，从字面意思可以理解为修改密码，如下图所示：

![](https://image.3001.net/images/20220919/1663566131_632801339381ac87113ea.png!small)

在这个函数中，通过其中的一些字符串可以看出，该函数可能是和修改用户密码相关，那么分析下能否找到这个语句中的password值的来源。简单分析后，发现多处对该值有操作，不太好定位分析，所以改为动态调试分析。

经过分析，加载GNRemote.dll这个文件的进程名为GNCore.exe。使用windbg附加后在ChangePassword函数下断点，发现在web界面中的修改密码处，可以触发断点，也就是修改密码的功能确实在这个ChangePassword函数中，如下图所示：

![](https://image.3001.net/images/20220919/1663566150_63280146d10e2510ff1cd.png!small)

结合刚才定位的sql语句，使用动态调试，反复查看password的值的来源，最终在地址100758C2出发现对输入的原始密码进行操作，最后将结果格式化到sql语句中，完成密码修改功能，如下图所示：

![](https://image.3001.net/images/20220919/1663566174_6328015ef2666dcdf802a.png!small)那么在该地址处的函数即为加密操作的关键函数，应该着重分析。在这个函数内部，可以看到对原始密码的长度进行判断，如果不是8的倍数，则在原始密码后面追加空格字符，一直填充到满足8的倍数为止，如下图所示：

![](https://image.3001.net/images/20220919/1663566193_63280171c061ff6f6f2aa.png!small)然后将原始密码进行一系列的异或操作，如下图所示：

![](https://image.3001.net/images/20220919/1663566211_6328018308c80dbb3d0f7.png!small)分析发现，异或的KEY来着上一函数100D6220，在该函数内部，发现复制两处固定值数据，如下图所示：

![](https://image.3001.net/images/20220919/1663566232_632801981cdfeef0fbf76.png!small)查看其数值，发现这正式是Blowfish算法使用的p_box和s_box数据，如下所示：

![](https://image.3001.net/images/20220919/1663566253_632801adc02368d62bcb0.png!small)那么该算法的KEY是什么？分析后发现KEY来自上一层函数10154BC0，可以看到这里有两个KEY，分别是地址101D0480和101D0440，这里使用的是101D0480的KEY，如下图所示：

![](https://image.3001.net/images/20220919/1663566288_632801d0f2c33faecd493.png!small)![](https://image.3001.net/images/20220919/1663566296_632801d8981e8b0672e7e.png!small)![](https://image.3001.net/images/20220919/1663566332_632801fcc6d75d8ee7912.png!small)到目前为止，分析清楚了对原始密码加密的算法是Blowfish，并且找到了KEY。因为这是对称加密算法，所以可以完成对加密后的密码进行解密，还原出原始密码，完成对分析结果正确性的验证，如下图：

![](https://image.3001.net/images/20220919/1663566362_6328021a67d9fca05fb8e.png!small)
****

##  **六、后台getshell**

登录后台后可以看到服务端配置的应用程序，一般分为以下几种。

###  **6.1 远程桌面**

服务端在安装完毕后会映射一个远程桌面端口，默认为55366，对用户配置了远程桌面可以直接通过客户端进行连接。（在易速联服务端新建用户后系统也会创建GNWay前缀的系统用户）

![](https://image.3001.net/images/20220919/1663566413_6328024d4652a1c7cfdbf.png!small)通过客户端连接到系统桌面。

![](https://image.3001.net/images/20220919/1663566453_63280275b57fb1c09bf69.png!small)![](https://image.3001.net/images/20220919/1663566462_6328027e0048ebceb56e9.png!small)

###  **6.2 服务端**

配置服务端应用可以通过该用户配置远程登录，直接连接服务器。

![](https://image.3001.net/images/20220919/1663566488_63280298403d1c0ad1b70.png!small)

发布桌面后该用户应用中便会添加远程登录的应用，添加完成后即可远程连接。

![](https://image.3001.net/images/20220919/1663566515_632802b3428d268c635c2.png!small)

###  **6.3 第三方程序**

如用友u8等程序，一般情况都可以通过弱口令进入应用，或者本身就已经勾选了记住密码了的。利用思路也比较简单，在与系统有交互的地方shift+右键即可调出cmd。

![](https://image.3001.net/images/20220919/1663566539_632802cbda3a2fbf58e53.png!small)

![](https://image.3001.net/images/20220919/1663566551_632802d7caf411e9e97b3.png!small)

[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485389&idx=1&sn=b2f35e1b9509f99a6cc415626cac88f3&chksm=c2a1d344f5d65a52084fe7bb79b631f63310bc91ad7d024d314b1b673d0e732411d10dc9adc9&token=1552730260&lang=zh_CN#rd)

