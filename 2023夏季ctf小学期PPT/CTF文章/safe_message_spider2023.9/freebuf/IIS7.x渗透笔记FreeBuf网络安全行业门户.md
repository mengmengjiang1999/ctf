### 这里搭建IIS7.x环境的虚拟机为win7，ip：192.168.173.196

#### IIS7.x的环境搭建，默认页面以及路径如图所示：

![1.png](https://image.3001.net/images/20210618/1623957095_60cb9e670cebe93ea5d96.png!small)![2.png](https://image.3001.net/images/20210618/1623957116_60cb9e7cbecdf249677d9.png!small)![3.png](https://image.3001.net/images/20210618/1623957126_60cb9e868f44505f9e2ee.png!small)  
![4.png](https://image.3001.net/images/20210618/1623957148_60cb9e9ce43a16538082e.png!small)

这里安装的小皮是2016版本的，安装过程中会遇到v9库未安装的问题，安装一下，之后再打开小皮就没有问题了。（这里遇到一个坑，忘了截图了，在重启小皮之前因为点了mysqld的进程，导致重启一直没成功，去进程中关掉mysqld的进程就成功了）；

v9库下载链接：http://www.php.cn/xiazai/gongju/1351

![5.png](https://image.3001.net/images/20210618/1623957174_60cb9eb6e7842c3c4b366.png!small)![6.png](https://image.3001.net/images/20210618/1623957187_60cb9ec39160a1fdd5235.png!small)  
![7.png](https://image.3001.net/images/20210618/1623957200_60cb9ed01225203a7b9d1.png!small)![8.png](https://image.3001.net/images/20210618/1623957207_60cb9ed7b292c7b4b9294.png!small)

#### 这里点击切换版本，选择框里所示的版本；

![9.png](https://image.3001.net/images/20210618/1623957235_60cb9ef351be8dc8fdbe4.png!small)![10.png](https://image.3001.net/images/20210618/1623957244_60cb9efc74ec8e849cbd9.png!small)![11.png](https://image.3001.net/images/20210618/1623957248_60cb9f003784c273ba2ff.png!small)![12.png](https://image.3001.net/images/20210618/1623957252_60cb9f048baa931399031.png!small)  
![13.png](https://image.3001.net/images/20210618/1623957269_60cb9f1543ba0e7f847f1.png!small)![14.png](https://image.3001.net/images/20210618/1623957275_60cb9f1b16899c17ee1b3.png!small)![15.png](https://image.3001.net/images/20210618/1623957279_60cb9f1fbadea8cf2696a.png!small)![16.png](https://image.3001.net/images/20210618/1623957285_60cb9f259449a9acdc7c5.png!small)

这里，环境即搭好；

如果不用小皮安装，还有第二种方法，编辑ISAPI和CGI限制，右键点击添加，选择下载好的对应php版本的php-cgi.exe文件路径，描述部分随意，即可达到相同的iis与php联动效果；

![17.png](https://image.3001.net/images/20210618/1623957315_60cb9f43ba81a52cbc9d1.png!small)![18.png](https://image.3001.net/images/20210618/1623957321_60cb9f4978a5eeabe7a9c.png!small)

### 解析漏洞

定义：IIS7/7.5在Fast-CGI运行模式下,在一个文件路径(/xx.jpg)后面加上/xx.php会将/xx.jpg/xx.php 解析为 php
文件。

在网站根目录下创建一个新文件，并写入phpinfo，正常情况下访问图片是访问不了的；

![19.png](https://image.3001.net/images/20210618/1623957347_60cb9f631a9fb0db7d44a.png!small)![20.png](https://image.3001.net/images/20210618/1623957353_60cb9f69dd9b6efb8f5d4.png!small)

这里如果可以让其解析，需要修改win7上的处理程序映像，将请求限制取消，再在访问路径后加/.php即可解析成php文件；

![21.png](https://image.3001.net/images/20210618/1623957366_60cb9f766269b859ccede.png!small)![22.png](https://image.3001.net/images/20210618/1623957369_60cb9f79daa71507c7b10.png!small)![23.png](https://image.3001.net/images/20210618/1623957374_60cb9f7e97e2147bba697.png!small)![24.png](https://image.3001.net/images/20210618/1623957379_60cb9f834cb86849568a3.png!small)![25.png](https://image.3001.net/images/20210618/1623957383_60cb9f87037ee0575d811.png!small)

#### 解决方案： 配置cgi.pathinfo(php.ini中)为0并重启php-cgi程序。

![26.png](https://image.3001.net/images/20210618/1623957419_60cb9fabc50a636dc57eb.png!small)

### HTTP.SYS远程代码执行CVE-2015-1635(MS15-034)

远程执行代码漏洞存在于 HTTP 协议堆栈 (HTTP.sys) 中，当 HTTP.sys 未正确分析经特殊设计的 HTTP 请求时会导致此漏洞。
成功利用此漏洞的攻击者可以在系统帐户的上下文中执行任意代码。利用HTTP.sys的安全漏洞，攻击者只需要发送恶意的http请求数据包，就可能远程读取IIS服务器的内存数据，或使服务器系统蓝屏崩溃。主要影响了包括Windows
7、Windows Server 2008 R2、Windows 8、Windows Server 2012、Windows 8.1 和 Windows
Server 2012 R2在内的主流服务器操作系统。漏洞影响版本： IIS7.5、IIS8.0、IIS8.5；

访问iis7默认页面，修改请求头，在里面加上：Range: bytes=0-18446744073709551615，返送之后返回码有416则说明存在漏洞；

![27.png](https://image.3001.net/images/20210618/1623957446_60cb9fc6433f71e0e6af2.png!small)  
![28.png](https://image.3001.net/images/20210618/1623957456_60cb9fd05d5a0cc41418a.png!small)  
![29.png](https://image.3001.net/images/20210618/1623957463_60cb9fd7e79d94a0fb835.png!small)

修复方法：官方补丁下载：https://support.microsoft.com/zh-cn/kb/3042553

### 认证绕过漏洞

IIS默认包含FTP服务。IIS中存在认证绕过漏洞和源码泄露漏洞，该漏洞源于怼用户提供的输入未经正确的验证，攻击者可以利用这些漏洞在服务器进程上下文中获取密码保护资源和查看源代码文件的未授权访问，有助于进一步攻击；漏洞影响版本：
IIS6.0、IIS7.5；

### iis7.5 .NET源码公开和身份绕过漏洞复现：

认证绕过这里需要.net4的版本(这里出现了个玄学问题，我的win7安装不了.net4的环境，这里因为这个卡了好久，各种方法都试了，最后甚至连VMware的版本都换了，拿了师兄的安装好.net4环境的win7环境来还是不行，算了妥协了，毁灭吧，复现的截图能有的没有就算了，累了累了，tui！没错，下面这个是别人安装好的截图，可怜我就给了一个)

![30.png](https://image.3001.net/images/20210618/1624001693_60cc4c9dbf846b25441e4.png!small)  
![36.jpg](https://image.3001.net/images/20210618/1624001706_60cc4caa6eb7670faf472.jpg!small)

#### 这里在网站根目录下新建了admin文件夹，里面写入一个php文件，把匿名身份认证关闭，访问该页面时会显示没有权限访问

![31.png](https://image.3001.net/images/20210618/1624001721_60cc4cb98f107116668ab.png!small)![32.png](https://image.3001.net/images/20210618/1624001725_60cc4cbd8fc0b0322fb39.png!small)![33.png](https://image.3001.net/images/20210618/1624001729_60cc4cc111bdd109a4927.png!small)![34.png](https://image.3001.net/images/20210618/1624001732_60cc4cc49f10e5befd683.png!small)![35.png](https://image.3001.net/images/20210618/1624001735_60cc4cc7f2c35b58fdff5.png!small)

#### 这时利用$i30:$INDEX_ALLOCATION可绕过限制，远程访问

#### http://192.168.173.129/admin:$i30:$INDEX_ALLOCATION/index.php

#### 不过这里因为环境没配成功，所以这步没成功，给大家放个成功的截图长什么样，如下图：

![37.png](https://image.3001.net/images/20210618/1624001765_60cc4ce59cb9f99fd7c2d.png!small)

#### 这里扩展下思路，我们可以想到，身份认证绕过可以和文件解析联动使用，譬如在admin目录下放一个aspx文件，正常访问是乱码，无法解析：

![38.png](https://image.3001.net/images/20210618/1624001774_60cc4cee5a02e3035254d.png!small)

#### 这里加上解析绕过：

#### http://192.168.173.129/admin:$i30:$INDEX_ALLOCATION/index.aspx/.php

#### 正确页面应该是这样的，没错，这里因为上面那个玄学问题，这一步也没成功，那就给大家展示一下别人成功的截图吧，假装是我的。

![39.png](https://image.3001.net/images/20210618/1624001803_60cc4d0b4c0910bba06a9.png!small)

## 该漏洞防护思路

攻击者需要事先获取iis服务器受认证保护的目录

