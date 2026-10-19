***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **vulnhub 是我喜爱的游乐场之一，上面的每个靶机都是很酷的一个游戏。完整找出所有 flag
只是基本任务，实现提权才是终极目标。我并不追求最快夺旗，而是尽可能运用完整攻击链入侵靶机，所以，这篇攻略中，或许某些内容对夺旗无直接帮助，但在应对真实目标时，你应该考虑。**

靶机 "JIS-CTF: VulnUpload" 含有 5 个 flag、初级难度，平均耗时 1.5 小时可完成攻击。你可以从
<https://www.vulnhub.com/entry/jis-ctf-vulnupload,228/> 获取 virtualbox
格式的镜像，导入后立即可玩：

![image.png](https://image.3001.net/images/20180616/15291136565590.png!small)JIS
虚拟机为 DHCP，我得想法找出它的 IP。nmap 的 -sn 选项用于探测主机存活性：

![image.png](https://image.3001.net/images/20180616/15291137881183.png!small)很快，找到
4 个存活 IP。其中，56.1 为我主系统 IP，56.2 为 DHCP 服务器，56.5 显示 localhost-response
为本机（kali），所以，JIS 的 IP 为 192.168.56.6。

## 一、系统服务发现

拿到 IP 第一要务当然是分析服务。nmap 的 -O、-sV 两个命令行参数可用于此：

![image.png](https://image.3001.net/images/20180616/15291137984714.png!small)可知，JIS
在 22 端口开启了 SSH（OpenSSH 7.2p2）、80 端口开启 HTTP（Apache httpd 2.4.18）等两个服务。另外，操作系统为
ubuntu。这三个信息将成为下个阶段的主要攻击面。

## 二、系统漏洞分析

针对 SSH 服务，我习惯从弱口令和系统漏洞两方面进行攻击。弱口令方面，我用常见用户名和常见密码进行暴破，虽然几率不大：

![image.png](https://image.3001.net/images/20180616/15291138131913.png!small)短时间跑不完，先放这儿，后续再看。

SSH 服务的系统漏洞查找方面，我推荐 searchsploit 工具。精确搜索 OpenSSH
7.2p2：![image.png](https://image.3001.net/images/20180616/15291138331714.png!small)

存在用户名可枚举漏洞，刚好，要能找到有效用户名，将有助于暴破 SSH 口令。立即用 EXP
试试：![image.png](https://image.3001.net/images/20180616/15291138908332.png!small)

试过几次，结果都不一样，感觉这个 EXP 不可靠。或许是搜索条件太苛刻，不带版本号，直接搜索 openssh
看看有无其他漏洞：![image.png](https://image.3001.net/images/20180616/15291139011168.png!small)

其中，有两个可考虑，依次为本地提权的漏洞、远程命令执行漏洞。哇，很诱人，不过很遗憾，都用不了。对前者而言，当前没用任何据点（如
webshell），还谈不上提权操作，当前只能先放放，后续可能用的上；对后者来说，利用条件非常严苛，攻击者必须拿到 forwarded agent-socket 的控制权，而且目标必须 SSH 登录攻击者所控制 forwarded agent-socket 的那台机器，才可能让目标加载指定
*.so，实现远程命令执行。罢了，SSH 系统漏洞暂时就不深入了。

apache
服务看下有无可利用的漏洞：![image.png](https://image.3001.net/images/20180616/15291139071021.png!small)

先前服务探测时找到的准确版本为 apache httpd 2.4.18，那么只有一个漏洞内存泄漏的漏洞，没多大价值。

这个阶段系统漏洞只能分析到这个程度，虽然知道发行套件为
ubuntu，但不知道具体版本、系统架构，很难准确的找到可用的操作系统漏洞，所以，没必要继续在系统漏洞层面耗时，后续如果能拿到
webshell，提权时再来深入分析，现在移步 web 应用层面。

## 三、web 内容发现

访问之前找到的 web 端口自动重定向到
<http://192.168.56.6/login.php>：![image.png](https://image.3001.net/images/20180616/15291139158846.png!small)

看了下 html 源码，没啥有价值的信息；枚举用户名也不能；或许可以暴破下弱口令，刚才的 SSH 暴破还没完呢，web
登录暴破还是先放一放，看看有无其他页面。

大概 2015 年之前，扫 web 端口 – 找 web 后台 – 弱口令登后台 –
上传一句话，是常见的高成功率的攻击手法，其中，能否找到后台地址，是成功的关键。换言之，我需要发现更多 web
内容。具体而言，我希望找到更多文件、页面、子目录，最好能找到源码打包的敏感文件、后台运维的管理页面、存放业务逻辑的子目录，以拓展攻击面。通常，我习惯结合枚举和爬虫两种方式来发现
web 内容。

枚举 web 内容的工具很多，其实，你手上的 burp 内置了强大的子目录枚举功能，但常被你忽略。访问
<http://192.168.56.6/>，让流量过 burp
后，立即展示出初始站点目录结构：![image.png](https://image.3001.net/images/20180616/15291139253994.png!small)

通过 engagement tools - discover
content，启用子目录枚举功能：![image.png](https://image.3001.net/images/20180616/15291139307885.png!small)

枚举之前，借助 firefox 插件 wappalyzer 确认后端语言为
php：![image.png](https://image.3001.net/images/20180616/15291139364109.png!small)

简单设置，让 burp 只枚举 php 类型的页面，忽略 aspx、jsp
等等其他语言，以提高效率：![image.png](https://image.3001.net/images/20180616/15291139417443.png!small)

很快，枚举出不少新页面：![image.png](https://image.3001.net/images/20180616/15291139491897.png!small)

你看，比先前多了些页面和目录，如，logout.php、server-status/。逐一查看，没啥有价值的内容。

接下来，我用另一个工具 dirsearch 再次枚举子目录，与 burp 互补，获得更多 web 内容。高效和可配置是 dirsearch 的特色，同样，用
--extension 选项设定只枚举 php 类型的页面，忽略 aspx、jsp
等等其他语言：![image.png](https://image.3001.net/images/20180616/15291139553956.png!small)

从输出结果 out.txt 中查看 HTTP 应答成功（200）的页面有 5
个：![image.png](https://image.3001.net/images/20180616/1529113960205.png!small)

依次访问这几个页面且让流量过
burp，站点目录结构如下：![image.png](https://image.3001.net/images/20180616/15291139654409.png!small)

子目录枚举，大概就到这个程度，接下来，爬取站点。

爬站，还是借助
burp：![image.png](https://image.3001.net/images/20180616/15291139708694.png!small)

很快，爬取完毕，又新增不少页面：![image.png](https://image.3001.net/images/20180616/15291139767724.png!small)

朋友，玩了这么久，连个 flag 的影子都没看到？别急，这就来了。在 burp 的 site map 中搜索 flag 关键字，第一个匹配项是
<http://192.168.56.6/admin_area/>：![image.png](https://image.3001.net/images/20180616/15291139823426.png!small)

拿到第一个 flag{7412574125871236547895214}；另外还拿到一组账号 admin/3v1l_H@ck3r，可能是 web
的登录账号、也可能是 SSH 的账号，一会试试。搜索 flag 得到的第二个匹配项是
<http://192.168.56.6/flag/>：![image.png](https://image.3001.net/images/20180616/1529113987143.png!small)

得到第二个 flag{8734509128730458630012095}。

## 四、web 应用漏洞分析

用 admin/3v1l_H@ck3r 尝试登录
<http://192.168.56.6/login.php>：![image.png](https://image.3001.net/images/20180616/15291139957622.png!small)

成功，有个文件上传功能，检查下是否存在任意文件上传漏洞。

随便上传一个 php 的 webshell
试试：![image.png](https://image.3001.net/images/20180616/15291140008531.png!small)

icesword.php 上传成功，存在任意文件上传漏洞，但没回显上传目录。还记得先前 web 内容发现时找到的
uploads/、uploaded_files/ 两目录么，尝试访问 <http://192.168.56.6/uploads/icesword.php>，
报错，资源不存在，访问
<http://192.168.56.6/uploaded_files/icesword.php>，没报错但页面无内容，没事，至少清楚上传目录是
uploaded_files/。

我用 msfvenom 生成 MSF 的 php 反弹木马
msf_private.php：![image.png](https://image.3001.net/images/20180616/15291140071362.png!small)

启动 MSF 并监听，随后访问 <http://192.168.56.6/uploaded_files/msf_private.php>，立即获得
meterpreter
会话：![image.png](https://image.3001.net/images/20180616/1529114013145.png!small)

简单翻下文件：![image.png](https://image.3001.net/images/20180616/15291140228356.png!small)

flag.txt、hint.txt 引起我的注意。查看之，flag.txt 无访问权限；hint.txt 中拿到第三个
flag{7645110034526579012345670}，以及一个提示信息，要想查看 flag.txt 先得找出账号 technawi
的密码：![image.png](https://image.3001.net/images/20180616/15291140303484.png!small)

接下来，我需要查找用户 technawi 的密码。我计划从文件名和文件内容两方面入手查找与 technawi 相关的信息。

我用 meterpreter 内置的 search 命令来查找文件名中含有关键字 technawi
的文件：![image.png](https://image.3001.net/images/20180616/15291140354806.png!small)

显示未找到。奇怪，有 technawi 用户，那肯定有 /home/technawi/，怎么会一个都找不到。进 shell
再确认下：![image.png](https://image.3001.net/images/20180616/15291140406591.png!small)

这才对嘛。所以，你看，meterpreter 内置的 search 不可靠。逐一查看，没发现有价值的内容。

查找文件内容中含有关键字 technawi
的文件：![image.png](https://image.3001.net/images/20180616/15291140455469.png!small)

逐一查看，在 /etc/mysql/conf.d/credentials.txt 中找到第四个
flag{7845658974123568974185412}，以及一组账号
technawi/3vilH@ksor：![image.png](https://image.3001.net/images/20180616/15291140526330.png!small)

## 五、登录系统

用账号 technawi/3vilH@ksor
成功登录系统：![image.png](https://image.3001.net/images/20180616/15291140781534.png!small)

再次查看 flag.txt，拿到第五个
flag{5473215946785213456975249}：![image.png](https://image.3001.net/images/20180616/15291140845693.png!small)

## 六、提权

最开始我就说过，flag 并不是我玩靶机的唯一目标，提权也很有意思。刚要查看内核版本准备对应 exp 时，朦胧记得在 technawi 的 home/
目录中，看过 .sudo_as_admin_successful
文件：![image.png](https://image.3001.net/images/20180616/15291140959506.png!small)

哇，运气不错，这说明 technawi 可以用自己的密码切换为 root
用户：![image.png](https://image.3001.net/images/20180616/15291140998690.png!small)

就这样，完成所有 flag 搜集、成功提权！

 *** 本文作者：yangyangwithgnu，转载注明来自FreeBuf.COM**

