*****本文原创作者：Jokong，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **作为一名菜鸟，第一次写文章，有点紧张，希望大佬们轻点。** **我写这个是对自己的一个总结和记录，也希望对新手有所帮助。**

## 信息收集

**信息收集是指通过各种方式获取所需要的信息，以便我们在后续的渗透过程更好的进行。最简单的比如说目标站点的IP、中间件、脚本语言、端口、邮箱等等。我觉得信息收集在我们渗透测试的过程当中，是最重要的一环，这一环节没做好，没收集到足够多的可利用的信息，我们很难进行下一步的操作。**

信息收集主要收集什么呢？该如何进行收集呢？

## 一、 **whois信息**

很多网站上都可以收集到whois信息，比如说：

> 国外的who.is：[ _https://who.is/_](https://who.is/)
>
> 站长之家：[ _http://whois.chinaz.com/_](http://whois.chinaz.com/)
>
> 爱站：[ _https://whois.aizhan.com/_](https://whois.aizhan.com/)
>
> 微步：[ _https://x.threatbook.cn/_](https://x.threatbook.cn/)

这些网站都可以收集whois信息，而且还很全面，我主要关注：注册商、注册人、邮件、DNS解析服务器、注册人联系电话。

有需要的还可以查企业的备案信息，主要有三种方式：

> 天眼查：[ _https://www.tianyancha.com/_](https://www.tianyancha.com/)
>
> ICP备案查询网：[ _http://www.beianbeian.com/_](http://www.beianbeian.com/)
>
> 国家企业信用信息公示系统：[
> _http://www.gsxt.gov.cn/index.html_](http://www.gsxt.gov.cn/index.html)

注意：国外的服务器一般来说是查不到的，因为他们不需要备案。国内的基本上都可以查到。

![1.png](https://image.3001.net/images/20190127/1548565685_5c4d3cb53f78e.png!small)

小技巧：如果在站长之家上隐藏了信息，可在who.is上再次查看。

## 二、 **子域名**

子域名是在顶级域名下的域名，收集的子域名越多，我们测试的目标就越多，渗透的成功率也越大。往往在主站找不到突破口的时候，我们从子域名入手，有时候你会发现惊喜就到了（然后还是挖不到，和我一样，哈哈哈哈，皮一下，很开心！）。

大佬们都有自己用的顺手的一套方法或工具，我就简单收集了一些：

### 1.Google语法

可以利用Google和Bing这样的搜索引擎进行搜索查询（site:[www.xxx.com](http://www.xxx.com)）

Google还支持额外的减号运算符，以排除我们对“网站:wikimedia.org -www -store ”不感兴趣的子域名。

![图片2.png](https://image.3001.net/images/20190127/1548565731_5c4d3ce30260f.png!small)

### 2.有许多第三方服务聚合了大量的DNS数据集，并通过它们来检索给定域名的子域名。

（1）VirusTotal：[
_https://www.virustotal.com/#/home/search_](https://www.virustotal.com/#/home/search)

（2）DNSdumpster：[ _https://dnsdumpster.com/_](https://dnsdumpster.com/)

![图片3.png](https://image.3001.net/images/20190127/1548565752_5c4d3cf881866.png!small)

### 3.基于SSL证书查询

查找一个域名证书的最简单方法是使用搜索引擎来收集计算机的CT日志，并让任何搜索引擎搜索它们。前两种比较常用。

（1）[ _https://crt.sh/_](https://crt.sh/)

（2）[ _https://censys.io/_](https://censys.io/)

（3）[
_https://developers.facebook.com/tools/ct/_](https://developers.facebook.com/tools/ct/)

（4）[
_https://google.com/transparencyreport/https/ct/_](https://google.com/transparencyreport/https/ct/)

![图片4.png](https://image.3001.net/images/20190127/1548565777_5c4d3d112df28.png!small)

### 4.简单的在线子域名收集（不推荐）

（1）[ _https://phpinfo.me/domain/_](https://phpinfo.me/domain/)

（2） _<http://i.links.cn/subdomain/>_

### 5.爆破枚举

这个就有很多工具可以用了，大佬们都有自己用的顺手的工具，比较常见的是：

（1）layer子域名挖掘机

（2）subDomainsBrute

（3）K8

（4）orangescan

（5）DNSRecon

这里重点推荐 layaer 和 subDomainsBrute 工具，可以从子域名入侵到主站。

小技巧：在[ _https://github.com/_](https://github.com/) 上也可以搜索子域名，运气好的话，会有意想不到的收获。

## 三、 **IP段的收集**

一般IP的话，我们在收集子域名的时候，就大概知道目标网站的IP段了。

也可以通过whois命令获取。即通过中国互联网信息中心[
_http://ipwhois.cnnic.net.cn/_](http://ipwhois.cnnic.net.cn/)进行查询：

![图片5.png](https://image.3001.net/images/20190127/1548565811_5c4d3d33d4573.png!small)

## 四、 **开放端口探测**

很多时候，网站都会开启CDN加速，导致我们查询到的IP不是真实的IP，所以得先查询到真实的IP地址。方法有很多，百度一大把。就说我觉得最准确的几种方法吧！

（1）通过让服务器给你发邮件(看邮箱头源 ip )找真实ip（最可靠）。

（2）通过 zmpap 全网爆破查询真实ip（可靠）。

（3）通过查询域名历史ip，[
_http://toolbar.netcraft.com_](http://toolbar.netcraft.com)（借鉴）。

（4）通过国外冷门的DNS的查询：nslookup xxx.com国外冷门DNS地址（借鉴）。

收集到大量IP，那就要进行端口扫描了，看看有什么常见的漏洞。

最常用的就是神器Nmap了。命令：nmap -T4 -sT -p- -sV ip

端口服务对应图：

![图片6.png](https://image.3001.net/images/20190127/1548565846_5c4d3d5644e5b.png!small)

常见端口漏洞：

端口  
| 服务  
| 说明  
  
---|---|---  
21  
| FTP  
| 主要看是否支持匿名，也可跑弱口令  
  
22  
| SSH  
| 弱口令爆破  
  
22  
| SSH  
| 弱口令爆破  
  
23  
| telnet  
| 弱口令爆破  
  
80-90  
| WEB  
| 常见WEB漏洞以及一些为管理后台  
  
161  
| snmp  
| public弱口令  
  
389  
| ldap  
| 是否为匿名访问  
  
443  
| openssl  
| 心脏出血以及一些WEB漏洞测试  
  
445  
| smb  
| 跑弱口令，检测是否有ms_08067等溢出  
  
873  
| rsync  
| 是否为匿名访问，也可以跑弱口令  
  
1025  
| RPC  
| NFS匿名访问  
  
1099  
| java rmi  
| 远程命令执行漏洞  
  
1433  
| mssql  
| 弱口令爆破  
  
1521  
| oracle  
| 弱口令爆破  
  
2082/2083  
| cpanel主机管理系统登陆  
| 弱口令爆破  
  
2222  
| DA虚拟主机管理系统登陆  
| 弱口令爆破  
  
2601,2604  
| zebra路由器  
| 默认密码zebra  
  
3128  
| squid代理默认端口  
| 如果没设置口令很可能就直接漫游内网  
  
3306  
| mysql  
| 弱口令爆破  
  
3312/3311  
| kangle主机管理系统登陆  
| 说明  
  
3389  
| RDP  
| 弱口令爆破，SHIFT后门，放大镜，输入法漏洞  
  
4440  
| rundeck  
| web  
  
4848  
| GlassFish web中间件  
| 弱口令admin/adminadmin  
  
5432  
| postgres  
| 弱口令爆破  
  
5560,7778  
| iSqlPlus  
|  
  
5900,5901,5902  
| vnc  
| 弱口令爆破  
  
5984  
| CouchDB  
| <http://xxx:5984/_utils/>  
  
6082  
| varnish  
|  
  
6379  
| redis  
| 一般无验证，直接访问  
  
7001,7002  
| weblogic  
| 弱口令爆破  
  
7778  
| Kloxo  
| 主机控制面板登录  
  
8080  
| tomcat\jboss  
| 弱口令爆破，jboss后台可能不验证  
  
8649  
| ganglia  
|  
  
8080-8090  
| 常见WEB端口  
|  
  
8083  
| Vestacp主机管理系统 （国外用较多）  
|  
  
8649  
| ganglia  
|  
  
8888  
| amh/LuManager  
| 主机管理系统默认端口 说明  
  
9000  
| fcgi  
| fcgi php命令执行漏洞  
  
9200  
| elasticsearch  
| 代码执行  
  
9043  
| websphere  
| 弱口令爆破  
  
10000  
| Virtualmin/Webmin  
| 服务器虚拟主机管理系统  
  
11211  
| memcache  
| 内存泄露  
  
27017,28017  
| mongodb  
| 未授权访问  
  
50000  
| Upnp  
| SAP命令执行  
  
50060,50030  
| hadoop  
| WEB 未授权访问  
  
  
常见端口列表整理如下：

    
    
    21,22,23,80-90,161,389,443,445,873,1099,1433,1521,1900,2082,2083,2222,2601,2604,3128,3306,3311,3312,3389,4440,4848,5432,5560,5900,5901,5902,6082,6379,7001-7010,7778,8080-8090,8649,8888,9000,9200,10000,11211,27017,28017,50000,50030,50060

## 五、 **网站架构探测**

当我们探测目标站点网站架构时，比如说：操作系统，中间件，脚本语言，数据库，服务器，web容器等等，可以使用以下方法查询。

> （1）wappalyzer插件——火狐插件
>
> （2）云悉：[ _http://www.yunsee.cn/info.html_](http://www.yunsee.cn/info.html)
>
> （3）查看数据包响应头
>
> （4）CMS指纹识别：[
> _http://whatweb.bugscaner.com/look/_](http://whatweb.bugscaner.com/look/)

CMS指纹识别又有很多方法，比如说御剑指纹识别、Webrobot工具、whatweb工具、还有在线查询的网站等等。

![图片7.png](https://image.3001.net/images/20190127/1548565865_5c4d3d69c62ad.png!small)

## 六、 **敏感文件、敏感目录探测**

通常我们所说的敏感文件、敏感目录大概有以下几种：

> （1）Git
>
> （2）hg/Mercurial
>
> （3）svn/Subversion
>
> （4）bzr/Bazaar
>
> （5）Cvs
>
> （6）WEB-INF泄露
>
> （7）备份文件泄露、配置文件泄露

敏感文件、敏感目录挖掘一般都是靠工具、脚本来找，当然大佬手工也能找得到。

常用的工具有：

> （1）御剑（真的很万能，文末附上全家桶）
>
> （2）爬虫（AWVS、Burpsuite等）
>
> （3）搜索引擎（Google、Github等）
>
> （4）wwwscan
>
> （5）BBscan（一位巨佬写的python脚本：[
> _https://github.com/lijiejie/BBScan_](https://github.com/lijiejie/BBScan) ）
>
> （6）GSIL（也是一位巨佬写的python脚本：[
> _https://github.com/FeeiCN/GSIL_](https://github.com/FeeiCN/GSIL) ）

（7）社交平台（有事没事多加一些QQ群，本人亲身经历，在一个QQ群查找到某平台后台账号密码，水了一波操作提交之后，发现被前辈提交过了。。。。。）

## 七、 **目标域名邮箱收集**

一定要养成收集站点邮箱账号收集的习惯（因为好多官方后台都是用内部邮箱账号登录的，指不定哪天你就得到一个进后台的机会）。

> （1）通过说明文档以及网站页面收集，或者网站发表者以及留言板信息处收集账号
>
> （2）通过 teemo，metago，burpusit，awvs，netspker 或者 google 语法收集
>
> （3）搜索相关 QQ 群收集相关企业员工的社交账号

用途： 可用来进行爆破或者弱口令登录以及撞裤攻击。

## 八、 **WAF探测**

Waf也叫Web应用防火墙，是通过执行一系列针对HTTP/HTTPS的安全策略来专门为Web应用提供保护的一款产品。Waf的探测很多人都会忽略掉，其实当我们遇到Waf，第一想法是溜了溜了、告辞告辞（我是这样，别赞，要脸）。但当我们知道是什么Waf时，又有种去绕过它的冲动，很多大牛都喜欢挑战Waf，于是网上就出现了很多绕过Waf的教学视频。毕竟成功绕过之后的那种自豪感真的真的很舒服。

我常用的两种方式：

> （1）手工（提交恶意数据，简单粗暴）
>
> （2）Kaili工具（WAFW00F、Nmap）

Nmap探测WAF有两种脚本。

一种是http-waf-detect。

    
    
    命令：nmap  -p80,443  --script=http-waf-detect  ip

一种是http-waf-fingerprint。

    
    
    命令：nmap  -p80,443  --script=http-waf-fingerprint  ip

WAFW00F探测WAF

    
    
    命令：wafw00f  -a  域名

![图片8.png](https://image.3001.net/images/20190127/1548565886_5c4d3d7e27213.png!small)

## 九、 **旁站、C段**

旁站：是和目标网站在同一台服务器上的其它的网站。

C端：是和目标服务器ip处在同一个C段的其它服务器。

旁站和C段的查询方式：

> （1）利用Bing.com，语法为：[
> _http://cn.bing.com/search?q=ip:111.111.111.111_](http://cn.bing.com/search?q=ip:111.111.111.111)
>
> （2）站长之家：[ _http://s.tool.chinaz.com/same_](http://s.tool.chinaz.com/same)
>
> （3）利用Google，语法：site:125.125.125.*
>
> （4）利用Nmap，语法：nmap -p 80,8080 --open ip/24
>
> （5）K8工具、御剑、北极熊扫描器等
>
> （6）在线：[ _http://www.webscan.cc/_](http://www.webscan.cc/)

![图片9.png](https://image.3001.net/images/20190127/1548565897_5c4d3d891ce20.png!small)

最后，附上几个常用的搜索引擎：

> ZoomEy：[ _https://www.zoomeye.org/_](https://www.zoomeye.org/)
>
> FoFa：[ _https://fofa.so/_](https://fofa.so/)
>
> Dnsdb：[ _https://www.dnsdb.io/zh-cn/_](https://www.dnsdb.io/zh-cn/)
>
> Shodan：[ _https://www.shodan.io/_](https://www.shodan.io/)
>
> Censys：[ _https://censys.io/_](https://censys.io/)
>
> 御剑全家桶：[
> _http://www.moonsec.com/post-753.html_](http://www.moonsec.com/post-753.html)

写的不全面，大佬有好的操作望指点指点，谢谢！

 ***本文原创作者：Jokong，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

