![使用Kali Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991608_5c25f5b8cc704.png!small)

**在进行渗透测试的过程中，绕过反病毒产品一直是一个“令人头疼”的事情。今天，我们将跟大家如何绕过目前市面上大部分的免费反病毒产品。**

由于很多新手用户喜欢使用AVAST或AVG这样的轻量级的不占用太多系统资源的反病毒产品，因此我们的实验环境使用免费的AVAST反病毒软件，运行系统为Windows
10。

## 测试工具

> 1、 Kali
>
> 2、 Veil框架
>
> 3、 Windows 10
>
> 4、 AVAST

Veil框架是一款很老的杀软绕过工具了，它可以生成几乎不可检测的Payload，而且Veil还可以通过命令行终端安装和运行：

    
    
    apt-get-y install git clone https://github.com/Veil-Framework/Veil-Evasion.git
    cd Veil-Evasion/
    cd setup
    setup.sh-c

详细信息请参考该项目的GitHub主页：【[传送门](https://github.com/Veil-Framework/Veil-Evasion)】

## 第一步

在Kali主机上打开命令行窗口，并切换到Veil框架目录中，然后输入：

    
    
    #python veil-evasion.py

![使用Kali Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991640_5c25f5d82f87e.png!small)

## 第二步

使用list命令列出所有可用的命令，检查Veil框架提供的可用Payload：

![使用Kali Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991654_5c25f5e618366.png!small)

## 第三步

选择编号37的Payload-“python/shellcode_inject/arc_encrypt”。这个Shellcode使用了arc4加密算法进行加密，并使用内存中的一个密钥文件进行解密。

我们可以使用info命令来查看相关信息，然后使用SET命令来使用phyrion解密器：

    
    
    SET USE_PHYRION Y

![使用Kali Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991676_5c25f5fc0fef1.png!small)

## 第四步

输入命令生成Payload，默认选择使用msfvenmon。这里我使用的是默认的reverse_tcphandler，并填写了[Kali
Linux](https://gbhackers.com/kalitutorials/)主机的LHOST和LPORT。

![使用Kali Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991690_5c25f60a58f55.png!small)

## 第五步

Payload成功生成之后，工具会显示Payload的生成地址以及msf的Handler文件地址。接下来，输入下列命令：

    
    
    #msfconsole -r /usr/share/veil-output/handlers/payload_handler.rc

![使用Kali Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991710_5c25f61e4037c.png!small)

## 第六步

![使用Kali Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991726_5c25f62e36f48.png!small)![使用Kali
Linux中的VEIL-Framework绕过防病毒软件](https://image.3001.net/images/20181228/1545991726_5c25f62e90114.png!small)

接下来，把我们生成的Payload拷贝到Windows主机中，然后执行Payload，我们这里测试的是最新版本的Avast。

### 演示视频

大家可以从视频中看到，Payload在执行之后Avast不会弹出任何的警告提示。

 **视频地址：**<https://youtu.be/J8CtWWeBuXA>

  

 ***参考来源：[gbhackers](https://gbhackers.com/bypassing-an-antivirus/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

