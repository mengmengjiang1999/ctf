## 1.前言

1，后期会不断完善

  

##

## 2.信息收集常见的一些关键词：

子域名，有无cdn，有无waf，真实ip，端口，cms，操作系统，中间件，脚本语言，数据库，web容器，whois信息，敏感文件，后台目录，旁站，C段，泛解析，天眼查，app，公众号等等（后面遇到在加）

## 3.站长之家： _<http://whois.chinaz.com/>_

**常用功能：** whois查询及反查，备案信息，同ip网站查询（旁站），ping检测（有无CDN），子域名

### whois查询：

收集域名所有人、域名注册商、域名注册日期和过期日期等，使用邮箱，电话等信息。现在也只能看看信息了，不能指望太多，查不到真实信息，很多都是显示阿里云啥的。或者可以试试反查，看下其他信息，这些信息可能在社工的时候会用上。

### 备案信息：

没啥说的，看看就好，了解一下。

### 旁站：

(推荐工具：[ **https://www.webscan.cc**](https://www.webscan.cc))

就是查这台主机上还有没有其他的web站点，也叫 **同服IP站点查询** （ps：推荐工具： **https://www.webscan.cc**
，网页显示效果比站长之家好多了，站长之家有的域名不会显示标题，webscan都有显示，界面比较友好）

### 子域名：

更推荐：<https://phpinfo.me/domain>，这个在子域名后会跟ip地址（又可以找子域名，又可以辅助查找真实ip）。

其他工具：layer子域名挖掘机、御剑、subDomainsBrute、K8，搜索引擎查询（site:www.xxx.com）

### ping检测（有无CDN）：

检测到有多个地址的话，说明使用了CDN服务，只有一个说明没有。（使用win自带的ping也行）

### 找真实ip：

(个人用的多的也就前两个：历史解析和查子域名)

1.DNS历史解析

查看IP与域名绑定的历史记录，可能会存在使用CDN前的记录，相关网站：  
[ _https://dnsdb.io/zh-cn/_](https://dnsdb.io/zh-cn/)  
 _<https://tools.ipip.net/cdn.php>_

<https://viewdns.info/>

 **2.查询子域名：** （推荐子域名工具：<https://phpinfo.me/domain>，这个在子域名后会跟ip地址）

毕竟CDN不便宜，所以很多站都是主站做了CDN，而很多小站没做CDN所以可以，通过上面收集到的子域名查询到真实的IP地址

3.网络空间引擎搜索法  
通过shadan、fofa等搜索引擎，通过对目标网站的特征进行搜索，很多时候可以获取网站的真实IP

用fofa试一下：

用到的语法为`host="www.baidu.com" && domain="baidu.com"
```其中`host="www.baidu.com"`是`从url中搜索"www.baidu.com"`；`domain="baidu.com"`是`搜索根域名带有baidu.com的网站```

4.利用SSL证书查询（下面这个网址没用明白，仅了解）  
 _<https://censys.io/certificates/>_

了解：通过网站证书寻找真实IP：此方法适用于https的站点，首先获得网站证书序列号（不要挂代理），url那里加锁的，点击它，查找证书的序列号，复制下来，转10进制，https://tool.lu/hexconvert/，然后用fofa，语法：cert="xxx转换后的xxxx",然后在看（我试了个，还是有点迷糊，不是很了解）

5.邮件订阅  
一些网站有发送邮件的功能，如Rss邮件订阅，因为邮件系统一般都在内部，所以就可以通过邮箱获得真实的IP

6.国外访问  
一般的站点在国内可能会有CDN，但是在国外的用户覆盖率比较低，所以通过国外的节点进行请求往往能获取真实IP

7.其他

*可以通过Ping（win--cmd）来判断网站是否存在CDN。ping 域名。

*ping主域：如果是www开头的域名存在CDN，可以把www.去掉再ping，可能得到真实IP。

*网站的注册，订阅，找回密码功能会发送邮件，邮件头信息会有真实IP

8.验证真实IP地址

利用IP地址对Web站点进行访问，如果正常表明是真实IP地址，否则就是假的。

  

## 4.WAF防护：<https://scan.top15.cn/web/>

类似的有wafw00f（需要安装），可以识别是否有waf防护，是什么waf。

<https://scan.top15.cn/web/>：还可以查旁站及其他信息，自己可以多点点。

## 5.旁站，c段：

旁站：和目标网站在同一台服务器上的其它站点

C段：是和服务器IP处在一个C段的其他服务器

工具：

 _<http://whois.chinaz.com/>_

<https://chapangzhan.com/>

<https://www.webscan.cc>

其他：

goby 自动探测当前网络空间存活的IP及解析域名到IP

K8旁站 K8Cscan是款专用于大型内网渗透的高并发插件化扫描神器，可以用来扫描C段、旁站

## 6.操作系统：大小写，ttl值

win128 linux 64 ，linux大小写敏感。

## 7.cms： _<http://whatweb.bugscaner.com/look/>_

还有wappalyzer插件，结合使用。

## 8.wappalyzer插件：中间件，脚本语言，web容器

还可以burp抓包，或者浏览器F12查看

## 9.端口：nmap，zenmap，御剑端口高速扫描，railgun等

看开放哪些端口，服务，可能有数据库服务端口

## 10.目录，敏感文件，后台：dirmap

注意模式，配置信息，字典。

  

\---------（后续有内容在追加，其他没介绍的后面在看）---------
  

  

  

