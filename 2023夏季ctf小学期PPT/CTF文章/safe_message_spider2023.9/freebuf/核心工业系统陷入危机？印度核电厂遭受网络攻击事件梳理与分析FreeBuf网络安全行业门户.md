# **背景** ****

2019年10月29日，有Twitter用户声称印度Kudankulam核电厂遭到网络攻击，奇安信威胁情报中心结合公开情报将主要事件时间线整理如下。

##  **重要时间线** ****

l 9月4日以前，第三方机构发现针对印度核电厂的网络攻击活动，并告知Twitter用户Pukhraj
Singh，其是一名印度的威胁情报分析师，现工作于印度本土的安全公司Bhujang
Innovations，于9月4日通报了英国NCSC机构，并在9月7日对外提起了此事件。

![图片.png](https://image.3001.net/images/20191031/1572496951_5dba66378a021.png!small)

l 9月23日，卡巴发布了一篇关于Dtrack的恶意代码报告，从上述推文来看该RAT和攻击事件相关。

l 10月19日，印度IANS新闻来源表示，其Kudankulam核电厂第二座核电机组于当日停止发电，其原因为“SG level
low”，通过查阅资料，其应该是蒸汽发生器（Steam Generator）故障，而蒸汽发生器是作为反应堆冷却剂系统压力边界的一部分。

![图片.png](https://image.3001.net/images/20191031/1572496967_5dba66475000e.png!small)

l 10月28日，某Twitter用户披露了VT上DTrack样本(md5:
4f8091a5513659b2980cb53578d3f798)，并且指出其内嵌了疑似与印度核电厂相关的用户名KKNPP，随后引发热议。

![图片.png](https://image.3001.net/images/20191031/1572496977_5dba6651deff9.png!small)

l 10月29日，各大新闻媒体公开披露该事件，并且印度安全人员对历史情况进行一些解释和说明，并且披露攻击来源已经获取核电厂内部域控级别的访问权限。

![图片.png](https://image.3001.net/images/20191031/1572496988_5dba665c720e8.png!small)

l 随后，核电厂官员公开否认遭受网络攻击，其事件属于虚假新闻。

![图片.png](https://image.3001.net/images/20191031/1572497004_5dba666ccd3d2.png!small)

# **相关样本分析** ****

##  **DTrack** ******Dropper** ****

Dropper（md5：b7c3039203278bc289fd3756571bd468）程序是一个MFC编写的应用。编译时间为Fri Jul 05
02:02:58 2019，整个MFC主体是一个空壳，实际的代码是在CRT部分一开始从PE文件指定偏移处读取shellcode。

![图片.png](https://image.3001.net/images/20191031/1572497020_5dba667c9549a.png!small)![图片.png](https://image.3001.net/images/20191031/1572497025_5dba6681cb07c.png!small)

![图片.png](https://image.3001.net/images/20191031/1572497032_5dba6688dd2d2.png!small)

![图片.png](https://image.3001.net/images/20191031/1572497039_5dba668f66a64.png!small)

并在CRT结尾进行shellcode的解密和执行。

![图片.png](https://image.3001.net/images/20191031/1572497069_5dba66ad6a2f3.png!small)

解密后的shellcode：

![图片.png](https://image.3001.net/images/20191031/1572497076_5dba66b429af1.png!small)

接着可以发现其又从PE文件读取内容：

![图片.png](https://image.3001.net/images/20191031/1572497084_5dba66bc72fb5.png!small)

最终解密后可以看到是一个PE：

![图片.png](https://image.3001.net/images/20191031/1572497092_5dba66c42aa8f.png!small)

将PE文件dump后计算其md5为4f8091a5513659b2980cb53578d3f798，即twitter上提到的样本。

##  **DTrack** ******RAT** ****

这里以4f8091a5513659b2980cb53578d3f798样本为例，也是twitter上提到的样本，可以看到卡巴检测为DTrack。其编译时间为Mon
Jul 29 13:36:26 2019。

![图片.png](https://image.3001.net/images/20191031/1572497101_5dba66cd1e666.png!small)

其首先通过动态获取API地址。

![图片.png](https://image.3001.net/images/20191031/1572497107_5dba66d3f054c.png!small)

这里值得注意的是其使用了一个特殊的字符串变化函数，如果传入字符串以CCS_开头，则去掉前缀返回，否则从第二个字符开始和首字符异或。

![图片.png](https://image.3001.net/images/20191031/1572497116_5dba66dc819dd.png!small)

然后开始获取系统注册信息，获取Mac地址：

![图片.png](https://image.3001.net/images/20191031/1572497122_5dba66e25206a.png!small)

然后根据上述的信息计算设备指纹：

![图片.png](https://image.3001.net/images/20191031/1572497128_5dba66e834949.png!small)![图片.png](https://image.3001.net/images/20191031/1572497132_5dba66ec5827c.png!small)

然后进入主流程，首先收集信息，包括浏览器历史记录：

![图片.png](https://image.3001.net/images/20191031/1572497142_5dba66f65cff2.png!small)

获取IP地址、进程列表、网络连接等信息：

![图片.png](https://image.3001.net/images/20191031/1572497149_5dba66fd970be.png!small)

接着会对硬编码的4个内网地址进行探测，尝试连接80端口：

![图片.png](https://image.3001.net/images/20191031/1572497155_5dba67034974b.png!small)

然后其会将相关文件加密Zip压缩，这里使用了两个不同的密钥“dkwero38oerA^t@#”、“abcd@123”。

![图片.png](https://image.3001.net/images/20191031/1572497161_5dba6709d6b6d.png!small)![图片.png](https://image.3001.net/images/20191031/1572497168_5dba671077be6.png!small)

最后通过IPC$将文件传到10.38.1.35这台机器上。

![图片.png](https://image.3001.net/images/20191031/1572497174_5dba6716f17ee.png!small)

## **D** **Track** **变种样本** ****

有国外安全研究人员在Pastebin上也给出了其他几个文件hash，其和上述分析的DTrack
RAT略有不同，这里以acd7aafa65d0dc4bdb5f04940107087b为例，其编译时间为Tue May 21 12:20:03 2019。

其主体代码入口如下：

![图片.png](https://image.3001.net/images/20191031/1572497183_5dba671f9db8b.png!small)

该样本遗留了大量的日志，并且所有字符串进行加密，加密的种子密钥为“rcmgmg3ny3pa”：

![图片.png](https://image.3001.net/images/20191031/1572497190_5dba6726286df.png!small)

在主线程中其首先计算设备ID，代码实现和DTrack RAT完全一样。

![图片.png](https://image.3001.net/images/20191031/1572497196_5dba672ce7502.png!small)

初始化了3个外连URL地址，从URL连接来看，应该是使用了被黑的网站。

![图片.png](https://image.3001.net/images/20191031/1572497203_5dba67335d067.png!small)

接着其会判断URL结尾，.php,.jsp,.asp,然后从远程下载命令文件并解析执行：

![图片.png](https://image.3001.net/images/20191031/1572497219_5dba67437e7bb.png!small)

其支持多种持久化方式安装，包括在Startup路径下生成LNK文件，安装服务，创建任务计划。

该样本具备和DTrack RAT完全相同的设备指纹计算算法和文件加密压缩方式。

#  **关联分析** ****

以VT上通过检索172.22.22.156，可以关联到其他的两个样本：

![图片.png](https://image.3001.net/images/20191031/1572497227_5dba674b51075.png!small)

MD5为b5ab935d750be8b5b7c9cf3b87c772ca的样本编译于Fri Mar 01 00:07:25
2019，从功能来看，其是上面分析的阉割版本，实现功能不完全，但是内嵌了相关内网IP地址。

![图片.png](https://image.3001.net/images/20191031/1572497234_5dba67523f22a.png!small)

而另一个MyStub.exe则为前文分析的Dropper程序。

对变种样本中的URL进行扩展，可以发现两个编译于2月份的样本。

![图片.png](https://image.3001.net/images/20191031/1572497239_5dba67575aa78.png!small)

其中一个名为Safe Banking Launcher。

![图片.png](https://image.3001.net/images/20191031/1572497243_5dba675bb0288.png!small)

而伪装的是印度的一家IT公司，Safe Banking是其下的一款防护应用。

![图片.png](https://image.3001.net/images/20191031/1572497251_5dba67635e469.png!small)![图片.png](https://image.3001.net/images/20191031/1572497259_5dba676b19c5e.png!small)

#  **归属分析** ****

有趣的是，在分析DTrack RAT的过程中，其中的字符串变换函数和卡巴发布的DTrack报告中提到的几乎完全一样（下图左为卡巴报告截图）：

![图片.png](https://image.3001.net/images/20191031/1572497290_5dba678a350bb.png!small)

并且其中Zip压缩所使用的密码也曾出现在McAfee在2013年披露的Operation Troy报告中使用，并且代码块极为相似。

![图片.png](https://image.3001.net/images/20191031/1572497300_5dba67946a852.png!small)![图片.png](https://image.3001.net/images/20191031/1572497306_5dba679a264dc.png!small)

而Operation Troy已经归属为Lazarus Group的历史活动。

#  **总结** ****

卡巴在其9月的Dtrack报告中披露从2018年夏末发现的针对印度银行的恶意软件Dtrack。而此次Twitter上曝光的样本4f8091a5513659b2980cb53578d3f798由于其内嵌了KKNPP的内网访问用户名，认为是和核电厂被网络攻击事件高度相关的，并且和卡巴披露的Dtrack家族归属同一攻击组织。

结合上述分析和公开情报，我们可以比较确认的是：

该攻击组织至少从2018年起开始针对印度的银行、核电站领域实施APT攻击，并且至今仍在进行中。我们推测针对银行的活动可能从2018年夏至2019年上半年，而针对核电站的攻击活动可能从2019年7月甚至更早开始。

Twitter上披露的4f8091a5513659b2980cb53578d3f798样本和b7c3039203278bc289fd3756571bd468样本应该和核电厂攻击事件高度相关，并主要用于横向移动阶段，根据编译时间可能发生在9月初。

安全研究人员披露的另外的Dtrack变种样本，我们并不能确认其和核电厂被攻击活动的关联性，由于其存在外连行为和控制功能，其可能用于攻击立足阶段。我们推测攻击组织开发了一套完整攻击框架，并按需编译和行动。

从相关样本技术中，存在比较明显的和历史Lazarus组织使用的攻击样本的指纹特征，背后的攻击组织归属还有待更多的证据支持。

我们也发现有罗马尼亚黑客于2018年3月就曾披露过印度范围的SCADA系统存在漏洞。

我们将事件相关元素关联性整理成下图：

![图片.png](https://image.3001.net/images/20191031/1572497318_5dba67a6e233b.png!small)

由于目前暂时没有更多证据，奇安信威胁情报中心红雨滴团队将继续持续跟踪该事件的发展并为我们所服务的类似客户提供检测支持，有需要的话可以联系奇安信威胁情报中心。

# **IOC** ****

公开的IOC：

4f8091a5513659b2980cb53578d3f798

b5ab935d750be8b5b7c9cf3b87c772ca

b7c3039203278bc289fd3756571bd468

ebb52f45ff1483e82ff3258b7f086571

acd7aafa65d0dc4bdb5f04940107087b

d10781f6b0a420ba0a9addfa5411fd97

<http://heromessi.com/wp-public/career/car_add.php>

<http://hawai-tour.com/wp/wp-imgs/luxury/scenes/view.php>

# **参考链接** ****

<https://mp.weixin.qq.com/s/mqBLVuIiOXCRjRhOX1HXbA>

<https://securityaffairs.co/wordpress/93148/hacking/kudankulam-nuclear-power-plant-cyberattack.html>

<https://economictimes.indiatimes.com/industry/energy/power/second-nuclear-plant-at-tns-kudankulam-stops-operation/articleshow/71661290.cms?from=mdr>

<https://twitter.com/a_tweeter_user/status/1188811977851887616>

<https://twitter.com/RungRage/status/1188853620541775872>

<https://securelist.com/my-name-is-dtrack/93338/>

<https://www.mcafee.com/enterprise/en-us/assets/white-papers/wp-dissecting-operation-troy.pdf>

<https://factordaily.com/romanian-hacktivist-ghostshell-india-scada-systems-vulnerable/>

#  **附：字符串解密IDC脚本** ****

auto srcaddr = ScreenEA();

auto v3 = (Byte(srcaddr+1) << 8) + Byte(srcaddr); // dword

auto start_index = 2;

auto seed = "rcmgmg3ny3pa";

auto seedlen = 12;

auto seed_arr = CreateArray("seed");

seed_arr = GetArrayId("seed");

auto i;

for ( i = 0; i < 256; i++) {

SetArrayLong(seed_arr, i, i); // byte

}

auto new_i = 0;

auto tmp;

auto j;

for ( j = 0; j < 256; j++) {

new_i = (ord(seed[j%seedlen]) + new_i + GetArrayElement(AR_LONG, seed_arr, j))
& 0xff;

tmp = GetArrayElement(AR_LONG, seed_arr, j);

SetArrayLong(seed_arr, j, GetArrayElement(AR_LONG, seed_arr, new_i));

SetArrayLong(seed_arr, new_i, tmp);

}

auto result_arr = CreateArray("result");

result_arr = GetArrayId("result");

auto v7=0;

auto v6=0;

auto ii;

for ( i = 0; i < v3; i++) {

v7 = (v7+1)&amp0xff

v6 = (v6+GetArrayElement(AR_LONG, seed_arr, v7))&amp0xff

tmp = GetArrayElement(AR_LONG, seed_arr, v7);

SetArrayLong(seed_arr, v7, GetArrayElement(AR_LONG, seed_arr, v6));

SetArrayLong(seed_arr, v6, tmp);

ii=(GetArrayElement(AR_LONG, seed_arr, v6)+GetArrayElement(AR_LONG, seed_arr,
v7))&amp0xff

SetArrayLong(result_arr, i, (Byte(srcaddr+2+i) ^ GetArrayElement(AR_LONG,
seed_arr, ii)) & 0xff);

Message((Byte(srcaddr+2+i) ^ GetArrayElement(AR_LONG, seed_arr, ii)) & 0xff);

}

Message("\n");

