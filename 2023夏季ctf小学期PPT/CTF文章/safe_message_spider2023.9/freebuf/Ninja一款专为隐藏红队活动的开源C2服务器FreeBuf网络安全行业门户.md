![](https://image.3001.net/images/20200404/1585987659_5e88404b5a0a0.jpg!small)

##  Ninja

**Ninja是一个开源的命令控制C2服务器，由Purple团队设计、开发和维护。在Ninjia的帮助下，红队研究人员可以隐藏他们的计算机和活动目录枚举活动，并且不会被SIEM和反病毒产品检测到。目前，Ninjia仍处于测试阶段，稳定版本发布后，将会包含更多隐蔽技术和反取证技术，这对于蓝队来说将会是一个真正的挑战，以帮助他们确保防御系统的安全性，以检测到更加复杂的攻击。**

Ninjia使用了Python来提供Payload并控制代理，代理基于C#和PowerShell以绕过大部分反病毒产品。Ninjia能够通过加密（AES-256）安全信道来与代理交互，而且密钥并非硬编码的，而是在活动中随机生成的，每一个连接至C2服务器的代理都会获得一个密钥，当C2重启并生成了新密钥之后，所有旧的代理和新的代理都将使用新的密钥。Ninjia还支持随机回调URL地址，以便绕过静态检测/分析。

###  工具要求

请注意，编译C#代码需要取决于System.Management.Automation.dll与SHA1哈希“c669667bb4d7870bc8bb65365d30071eb7fb86fe”的汇编结果。

某些Ninjia命令可能需要用到下列模块，因此用户需要从相应代码库获取这些模块：

Invoke-Kerberoast :

>
> <https://raw.githubusercontent.com/xan7r/kerberoast/master/autokerberoast.ps1>

Invoke-Mimikatz :

>
> <https://github.com/PowerShellMafia/PowerSploit/blob/master/Exfiltration/Invoke-> Mimikatz.ps1>

Sharphound :

>
> <https://github.com/BloodHoundAD/BloodHound/blob/master/Ingestors/SharpHound.ps1>

PowerView :

>
> <https://github.com/PowerShellEmpire/PowerTools/blob/master/PowerView/powerview.ps1>

##  工具安装

首先，请确保使用下列命令从项目代码库中获取最新版本的Ninjia：

    
    
    git clone https://github.com/ahmedkhlief/Ninja/

接下来，我们在命令行中切换到项目根目录，然后运行install.sh脚本来安装和配置Ninjia：

    
    
    chmod +x ./install.sh sudo ./install.sh

完成上述操作之后，你需要初始化活动：

    
    
    python start_campaign.py

现在，你就可以使用下列命令开启Ninjia服务器了：

    
    
    python Ninja.py

![](https://image.3001.net/images/20200404/1585987703_5e884077a9b2a.png!small)

运行之后，你将会看到终端屏幕出现下列内容：

![](https://image.3001.net/images/20200404/1585987731_5e884093a145d.png!small)

##  自定义回调URL

Ninjia C2允许我们以更安全的方法自定义回调URL，你需要编辑文件links.txt并添加连接中需要用到的单词。Ninjia
C2将会从中随机选择单词并用于URL地址中。如果你想使用静态连接，可以直接编辑core/config.py文件来进行功能修改。

##  Ninjia C2文件架构

> Ninjia C2拥有非常多的功能函数，并使用文件目录来存储这些函数的输出结果，下面给出的是所有目录以及部分重要文件：
>
> agents/ : 包含Ninjia所需的所有原始代理。
>
> core/ : 包含运行Ninjia的所有核心脚本。
>
> DA/ : 防御分析脚本将在此处编写其输出。
>
> downloads/ : 从目标设备下载的所有文件都将在此处。
>
> file/ : 要上传到目标设备的文件。
>
> images/ : 屏幕截图将上传到这里。
>
> kerberoast/ : kerberoast模块将在此处写入其输出。
>
> lib/ : 包括Ninjia C2使用的库。
>
> Modules/ : 可以将Powershell模块加载到目标设备。
>
> payloads/ : 需要在活动中使用的Payload。
>
> ninja.py : Ninjia C2主脚本.
>
> start_campaign.py : 用于初始化活动配置的Python脚本。
>
> links.txt : 包含要在回调链接中使用的单词的文件。
>
> install.sh : 用于安装依赖环境的Bash脚本。
>
> c2-logs.txt : 记录所有的命令执行结果。

##  创建自动化命令

你可以为较长的命令或一些列命令设置一个短指令，，这些命令必须存在于core/cmd.py之中：

![](https://image.3001.net/images/20200404/1585987763_5e8840b373a21.png!small)

    
    
    config.COMMAND[config.get_pointer()].append(encrypt(config.AESKey,"load SharpHound.ps1"))

在上述例子中，load SharpHound.ps1就是最终的命令样本。

##  工具运行截图

###  主屏幕：

![](https://image.3001.net/images/20200404/1585987777_5e8840c117bed.png!small)

###  Payload：

![](https://image.3001.net/images/20200404/1585987784_5e8840c83fd38.png!small)

###  代理列表：

![](https://image.3001.net/images/20200404/1585987793_5e8840d11b265.png!small)

###  域管理员：

![](https://image.3001.net/images/20200404/1585987837_5e8840fdbdcba.png!small)![](https://image.3001.net/images/20200404/1585987837_5e8840fd85312.png!small)![](https://image.3001.net/images/20200404/1585987836_5e8840fc7dffa.png!small)![](https://image.3001.net/images/20200404/1585987836_5e8840fcf3e32.png!small)

###  上传文件：

![](https://image.3001.net/images/20200404/1585987847_5e8841073d5fa.png!small)

###  下载文件：

![](https://image.3001.net/images/20200404/1585987853_5e88410dd8cd7.png!small)

##  项目地址

> Ninjia：【[GitHub传送门](https://github.com/ahmedkhlief/Ninja)】
>
> 详细使用：【[参考文档](https://shells.systems/introducing-ninja-c2-the-c2-built-for-> stealth-red-team-operations/)】

 ***
参考来源：[ahmedkhlief](https://github.com/ahmedkhlief/Ninja)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

