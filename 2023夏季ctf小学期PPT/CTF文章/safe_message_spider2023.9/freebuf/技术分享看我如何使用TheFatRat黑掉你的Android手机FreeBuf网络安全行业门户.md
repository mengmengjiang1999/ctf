**严正声明：本文仅限于技术讨论和教育目的，严禁用于其他用途。**

## 前言

**在这篇文章中，我们将教大家如何使用TheFatRat这款工具。这款工具可以帮大家构建后门程序，以及执行后渗透利用攻击等等。在主流Payload的帮助下，这款工具可以生成质量非常高的恶意软件，而这些恶意软件可以在Windows、[Android](https://gbhackers.com/vault-7-leaks-cia-android-hacking-tool-highrise-steals-data-from-compromised-android-phones-via-sms-wikileaks/)和macOS平台上运行。**

![TheFatRat](https://image.3001.net/images/20181110/1541819127_5be64af76d2f6.png!small)

值得一提的是，TheFatRat所生成的恶意软件能够[绕过反病毒产品](https://gbhackers.com/bypass-antivirus-using-payload/)，而这将允许攻击者拿到Meterpreter会话。

## 自动化Metasploit功能

> 1\. 针对Windows、Linux、Mac和Android创建后门；
>
> 2\. 后门可绕过反病毒产品；
>
> 3\. 检测/开启Metasploit服务；
>
> 4\. 针对Windows、Linux、Android和macOS创建meterpreterreverse_tcp Payload；
>
> 5\. 开启多个meterpreter reverse_tcp监听器；
>
> 6\. Searchsploit快速搜索；
>
> 7\. 绕过反病毒产品；
>
> 8\. 使用其他技术创建后门；
>
> 9\. 自动运行监听器脚本；

## 工具下载

下载地址：【[GitHub传送门](https://github.com/Screetsec/TheFatRat)】

下载命令：

    
    
    git clone <https://github.com/Screetsec/TheFatRat.git>
    
    cd TheFatRat

接下来，我们需要提供执行权限并运行setup.sh。

    
    
    chmod +x setup.sh && ./setup.sh

安装过程大概需要10到15分钟，程序会自动检测缺失的组件，并自动完成依赖安装。

安装完成之后，程序会显示一个Payload创建列表：

![Payload创建列表](https://image.3001.net/images/20181110/1541819155_5be64b139293a.png!small)

由于这篇文章主要介绍如何在原始APK文件中加入后门，所以我们需要选择第5个选项。

![选择第5个选项](https://image.3001.net/images/20181110/1541819163_5be64b1b7412c.png!small)

与此同时，我们还需要下载一个Android应用程序安装文件-APK文件，然后输入文件路径。

完成之后，我们要选择需要的Meterpreter，这里选择reverse_tcp。

![reverse_tcp](https://image.3001.net/images/20181110/1541819174_5be64b2696a01.png!small)

接下来，你需要选择APK创建工具：

![APK创建工具](https://image.3001.net/images/20181110/1541819187_5be64b330cf01.png!small)

![APK创建工具](https://image.3001.net/images/20181110/1541819187_5be64b33a3a07.png!small)

在APK的构建过程中，它会对原始APK进行反编译，并插入Payload，然后重新编译新的应用程序。它会使用混淆方法来嵌入Payload，并添加数字签名。

创建完成之后，你就可以把APK文件发送给目标手机了。接下来，我们需要通过msfconsole来设置设置哦我们的meterpreter会话。

![meterpreter会话](https://image.3001.net/images/20181110/1541819204_5be64b448ada6.png!small)

安装完成之后，你将会拿到meterpreter会话，然后完成设备的控制操作。

![设备的控制操作](https://image.3001.net/images/20181110/1541819212_5be64b4c969d9.png!small)

输入“help”命令能够查看所有可执行的命令：

![可执行的命令](https://image.3001.net/images/20181110/1541819224_5be64b58362c8.png!small)

你可以导出通话记录、通讯录、短信消息，伸直还可以远程截屏。

![远程截屏](https://image.3001.net/images/20181110/1541819235_5be64b631bc18.png!small)

 *** 参考来源：[gbhackers](https://gbhackers.com/android-rat-kali-linux-tutorial/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

