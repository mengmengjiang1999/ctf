# 一 CVE-2021-30461

（1）前言：

VoIPmonitor是“具有在Linux上运行的SIP RTP和RTCP VoIP协议的具有商业前端的开源网络数据包嗅探器”

（2）漏洞影响和版本：

影响：执行任意系统命令；版本：VoIPmonitor <= 24.60

（3）漏洞原理：

由于对恶意功能的过滤不当，攻击者可以通过VoIPMonitor的Web UI的PHP应用程序运行命令。

使用SPOOLDIR和recheck参数对index.php文件发出POST请求时，可以触发该漏洞。

这是由于以下事实：将SPOOLDIR值引入到config/configuration.php文件中，该文件随后由UI界面调用。

该SPOOLDIR值按原样放置在PHP源代码中，允许远程攻击者插入任意命令以及该参数的预期值。

（4）漏洞复现：

Ⅰ寻找目标

使用fofa搜索搜索并选择其他国家

搜索语法：title="VoIPmonitor"

Ⅱ开始测试

![](https://image.3001.net/images/20220219/1645263887_6210bc0fab5d93c653827.jpeg)

返回值200无回显

Ⅲ成功执行

![](https://image.3001.net/images/20220219/1645264012_6210bc8c75d95c17ab5d6.jpg)

利用网上的exp发现测试目标并没有漏洞，选取其他目标发现有漏洞存在

![](https://image.3001.net/images/20220219/1645264137_6210bd09bd5b3c9c7bdbf.jpg)

以上为exp代码中的payload

Exp: <https://www.seebug.org/vuldb/ssvid-99239>

（5）思考

在进行漏洞验证时我是手工选择目标进行测试这样效率很低，在成功执行之后才想起来执行可以把目标制作成.txt格式让脚本跑，或者使用脚本直接跑出fofa搜索后的目标。

（6）参考链接

<https://ssd-disclosure.com/ssd-advisory-voipmonitor-unauth-rce/>

<https://www.seebug.org/vuldb/ssvid-99239>

<https://blog.csdn.net/weixin_44146996/article/details/116534946>

# 二 CVE-2021-32849

（1）前言：

Gerapy是一款基于Scrapy、Scrapyd、Django和Vue.js的分布式爬虫管理框架。

（2）漏洞影响和版本：

影响：执行任意系统命令；版本：Gerapy <=0.9.6

（3）漏洞原理;

披露漏洞出现的url地址在:/api/project/clone, gerapy/server/core/views.py
中project_clone方法,当请求方法为POST时，使用Json.load对请求正文进行解析。对json中的address键值内容进行判断是否为http开头。如果判断成功，就会带入到cmd变量中，然后使用Popen进行代码执行。

(4) 漏洞复现

Ⅰ寻找目标

使用fofa语法

搜索语法：title=" Gerapy "

Ⅱ开始测试

![](https://image.3001.net/images/20220219/1645264431_6210be2f5ee88aaff3cb0.jpg!small)

后台尝试弱口令，而发现对登陆没有使用验证码验证，存在爆破的可能性。

测试多次后都未能成功。所以选择配置本地环境进行验证。

下载Gerapy版本

![](https://image.3001.net/images/20220219/1645264455_6210be47c895195b11fdb.jpg!small)

使用docker进行启动

![](https://image.3001.net/images/20220219/1645264480_6210be60b5f2ecb3cc116.jpg!small)

成功启动

![](https://image.3001.net/images/20220219/1645264505_6210be7993566ca73166e.jpg!small)

![](https://image.3001.net/images/20220219/1645264533_6210be95dd351bd8b81dd.jpg!small)

Ⅲ 成功执行

![](https://image.3001.net/images/20220219/1645264860_6210bfdc76f519bc0746c.jpg!small)

构造数据包，利用访问远程服务器，但是未能监听到

![](https://image.3001.net/images/20220219/1645264906_6210c00ae9d10cb5b1245.jpg!small)

构造数据包dns带外查询

（5）思考

在配置环境使用wincp传输文件未想到centos8默认禁用root链接，查询了很久才找到原因。而且漏洞需要授权才能利用。

（6）参考链接

<https://mp.weixin.qq.com/s/sYiBtoIEoY56MOIBSonkvw>

<http://blog.seals6.top/index.php/archives/17/>

<https://blog.csdn.net/Destiny_one/article/details/121637212>

# 三 CVE-2021-22205

  * 前言

GitLab 是一个用于仓库管理系统的开源项目，使用Git作为代码管理工具，并在此基础上搭建起来的web服务

  * 漏洞影响和版本：

影响：任意系统命令执行；版本： 11.9 <= GitLab（CE/EE）< 13.8.8 13.9 <= GitLab（CE/EE）< 13.9.6

13.10 <= GitLab（CE/EE）< 13.10.3

  * 漏洞原理：

GitLab 没有正确验证传递给文件解析器的图像文件

  * 漏洞复现：

Ⅰ目标选取：

依旧采取fofa语法进行搜索

Ⅱ开始测试

利用网上exp进行验证（阿里云服务器搭建的环境）

![](https://image.3001.net/images/20220219/1645265399_6210c1f7f17f91e375112.jpg!small)

Exp: <https://github.com/Al1ex/CVE-2021-22205>

发现越界

![](https://image.3001.net/images/20220219/1645265525_6210c2757b6b56030eec1.jpg!small)

一开始我以为是国内的ip进行限制，所以fofa找了一个国内的地址发现并未越界，只有47的ip地址会越界。查询了很久也未曾找到错误。只能本地搭建服务

![1645265539_6210c2836b8fe220bf840.jpg](https://image.3001.net/images/20220219/1645265539_6210c2836b8fe220bf840.jpg)

成功访问

![1645265575_6210c2a7025cc11dd28f4.jpg!small](https://image.3001.net/images/20220219/1645265575_6210c2a7025cc11dd28f4.jpg!small)

使用工具进行验证

![1645265596_6210c2bc330c4f5e1b7ad.jpg!small](https://image.3001.net/images/20220219/1645265596_6210c2bc330c4f5e1b7ad.jpg!small)

Ⅲ 成功执行

![1645265689_6210c319a0f609ca2728a.jpg!small](https://image.3001.net/images/20220219/1645265689_6210c319a0f609ca2728a.jpg!small)

成功带外查询

构造数据包进行未授权访问，获取到cookie

![1645265712_6210c33084d547928dbe4.jpg!small](https://image.3001.net/images/20220219/1645265712_6210c33084d547928dbe4.jpg!small)

修改数据包成功接受类型 成功获取csrf token

![1645265716_6210c33473484338ffde8.jpg!small](https://image.3001.net/images/20220219/1645265716_6210c33473484338ffde8.jpg!small)

利用获取到的cookie和csrf token 进行上传图片马

![1645265743_6210c34fe3b13962d9a6a.jpg!small](https://image.3001.net/images/20220219/1645265743_6210c34fe3b13962d9a6a.jpg!small)

服务器端成功接受

![1645265754_6210c35ac7b9c1569c1ff.jpg!small](https://image.3001.net/images/20220219/1645265754_6210c35ac7b9c1569c1ff.jpg!small)

  * 思考

在使用exp脚本时，缺少lxml安装时报错c++版本不对，查询资料之后发现py3对于的c++编译应该在vs2014版本之上，安装完成之后还是报错。在此上面耗费了很多的时间，最后采用离线安装。在搭建本地服务器时，未将docker设置未开机启动,导致docker-compose up -d
无法成功。使用虚拟机第一次搭建服务器时给的运存有点低，测试各种失败。在第二次搭建时给了运存。发现才有了uses/sign_in页面。突然明白第一次为什么失败，人麻了。未能找到第一次搭建服务器为什么没有uses/sign_in页面，猜测可能和运存给的比较低有关。

  * 参考链接

[https://www.freebuf.com/articles/web/303375.html](articles/web/303375.html)

<https://hackerone.com/reports/1154542>

# 四 CVE-2020-17530

  * 前言：

Struts2是一个基于MVC设计模式的Web应用框架，它本质上相当于一个servlet，在MVC设计模式中，Struts2作为控制器来建立模型与视图的数据交互。

  * 漏洞影响及版本:

影响：任意系统命令执行；版本： 2.0.0 <=Struts <=2.5.25

  * 漏洞原理:

Apache Struts2-061（CVE-2020-17530）远程代码执行漏洞是s2-059漏洞的绕过，所以其漏洞原理与s2-59一样，Struts2
会对某些标签属性 (比如 id ，其他属性有待寻找) 的属性值进行二次表达式解析，因此当这些标签属性中使用了 % {x} 且 x
的值用户可控时，用户再传入一个 % {payload} 即可造成OGNL表达式执行。

  * 漏洞复现

搭建本地环境

![1645265958_6210c42649a08a214555d.png!small](https://image.3001.net/images/20220219/1645265958_6210c42649a08a214555d.png!small)

成功搭建页面

![1645265967_6210c42f862c045080352.png!small](https://image.3001.net/images/20220219/1645265967_6210c42f862c045080352.png!small)

验证是否存在漏洞，可以看到返回值为test2020所以存在漏洞

![1645265976_6210c4381bba402ac5f66.png!small](https://image.3001.net/images/20220219/1645265976_6210c4381bba402ac5f66.png!small)

构造数据包进行验证，返回数据包执行成功

![1645265985_6210c44158f53b0e88c88.png!small](https://image.3001.net/images/20220219/1645265985_6210c44158f53b0e88c88.png!small)

出网验证

![1645265995_6210c44ba1bb8bb507d8f.png!small](https://image.3001.net/images/20220219/1645265995_6210c44ba1bb8bb507d8f.png!small)

  * 思考：

在复现过程中发现漏洞是基于CVE-2019-0230的修复的绕过（官方CVE-2019-0230的修复方式是加强OGNL表达式沙盒），%{和}是ognl的标志前缀和后缀。

  * 参考链接：

<https://cloud.tencent.com/developer/article/1766304>

[https://www.freebuf.com/vuls/257626.html](vuls/257626.html)

<https://cloud.tencent.com/developer/article/1774734>

