## ****概述****

在野的Powershell恶意脚本总是经过多重混淆、加密，直接静态分析难以得知脚本具体有什么恶意行为，所以需要对其进行动态调试。目前最常用的Powershell调试器是ISE，但ISE没有较友好的调试窗口，使得调试脚本时效率低下，下面，将介绍使用VSCode实现远程调试Powershell脚本，帮助你提升解密分析Powershell恶意脚本的效率。

##  ** **样本获取****

本次演示所使用的样本为一个Powershell后门，其特点是有多层恶意代码，会从C&C服务器多次加载不同payload。

![](https://image.3001.net/images/20200928/1601294097_5f71cf1129482bb01aa45.png!small)

母体为一个bat脚本，主要功能就是执行一段base64加密后的Powershell脚本。

![](https://image.3001.net/images/20200928/1601294123_5f71cf2b2bd34d7426b22.png!small)

解密后的代码，正是这个样本的核心代码，接下来就开始对其进行调试分析。

![](https://image.3001.net/images/20200928/1601294143_5f71cf3f308f1cd698b17.png!small)

###  ** **虚拟机环境搭建****

首先虚拟机建议使用Win10，因为VSCode的远程调试功能与Win10兼容性更好，同时，建立远程会话需要将虚拟机里的网络类型设置为专用。

![](https://image.3001.net/images/20200928/1601294172_5f71cf5c8a99274240e7a.png!small)

然后在虚拟机里运行：winrm quickconfig，即可开启Windows 远程管理(WinRM) 服务。

![](https://image.3001.net/images/20200928/1601294189_5f71cf6dc1ef53c50a901.png!small)

为了在虚拟机里成功运行调试Powershell脚本，还需开放脚本执行权限set-executionpolicy
unrestricted，以及关闭Windows Defender。

###  ** **本机VSCode环境搭建****

远程调试，需要安装Powershell插件，打开VSCode，直接在商店搜索直接安装即可。

![](https://image.3001.net/images/20200928/1601294218_5f71cf8a7c1a108be75df.png!small)

在Powershell控制台中输入：Enter-PSSession -ComputerName [虚拟机ip] -Credential
[虚拟机用户名]，敲入密码，即可远程登录到虚拟机。然后将待调试的脚本放入虚拟机中，输入：psedit [虚拟机中的脚本路径]，加载目标脚本。

![](https://image.3001.net/images/20200928/1601294237_5f71cf9d1250cb7183b49.png!small)

###  ** **远程调试分析****

在关键代码处下断点，按下F5调试便可以运行到断点处，右侧则是变量的值，通过调试我们可以得知该段代码的作用是从http://miranda.tattooforsure.com:8888/admin/get.php读取恶意代码并执行。

![](https://image.3001.net/images/20200928/1601294270_5f71cfbee5d853540dbfd.png!small)

VSCode远程调试也支持编辑脚本，可以新增一行代码：$payload = -JOIn [ChAr[]](& $R $Data ($IV +
$K))，将下载的恶意代码赋值给$payload，便可以从调试窗口中获取到$payload的值了。

![](https://image.3001.net/images/20200928/1601294296_5f71cfd8d4a73899860eb.png!small)

复制$payload的值，保存为payload.ps1进行调试。发现其结构很简单，声明Start-NEGOtiatE函数并进行调用。值得注意的是，函数执行需要传入母脚本的$ser、$u、$hop参数。

![](https://image.3001.net/images/20200928/1601294312_5f71cfe85be2841156a8c.png!small)

payload.ps1的功能为上传终端的域名、用户名、主机名、IP、OS版本以及Powershell版本信息，为了绕过检测，其会使用RC
4对上述信息进行加密，并在传输之前先上传RC 4秘钥。

![](https://image.3001.net/images/20200928/1601294360_5f71d0185acdcf859b58d.png!small)

上传的C&C地址为http://miranda.tattooforsure.com:8888/login/process.php，上传完毕后，C&C还会返回第二阶段的payload。

![](https://image.3001.net/images/20200928/1601294379_5f71d02bd585061572d4e.png!small)

将第二阶段的payload保存为payload2.ps1并打开，原来就是个函数定义，函数名为U5BS3，然后在payload.ps1中进行调用。

![](https://image.3001.net/images/20200928/1601294396_5f71d03ca65d35ccf9958.png!small)

为了方便调试，我们直接将U5BS3函数定义复制到payload.ps1中。单步步过：U5BS3 -Servers @(($s -split
"/")[0..2] -join "/") -StagingKey $SK -SessionKey $key -SessionID $ID
-WorkingHours "WORKING_HOURS_REPLACE" -KillDate "REPLACE_KILLDATE"
-ProxySettings $Script:Proxy，就能调试进U5BS3函数内部了。

![](https://image.3001.net/images/20200928/1601294411_5f71d04b658e2ad566b75.png!small)

通过搜索特征代码，可以确认这段代码就是开源的Empire代码，是个Powershell的攻击框架。

![](https://image.3001.net/images/20200928/1601294424_5f71d0587fa0a6b5fd323.png!small)

这段代码就是核心的后门代码了，根据C&C服务器下发的指令码，执行相对应的恶意操作，这里就不详细分析了。

![](https://image.3001.net/images/20200928/1601294437_5f71d0657b1e8815b74b9.png!small)

##  ** **总结****

对于恶意样本分析，都必须在虚拟机环境操作，所以远程调试是个不错的选择。而VSCode作为微软开发的脚本IDE，对Powershell远程调试的功能是很完善的，大家可以通过VSCode远程调试功能，提升解混淆分析恶意Powershell脚本的效率。

