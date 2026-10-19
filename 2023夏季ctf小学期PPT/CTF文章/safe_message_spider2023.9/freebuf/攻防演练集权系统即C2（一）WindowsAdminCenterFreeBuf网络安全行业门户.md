**免责声明：**

本文章或工具仅供安全研究使用，请勿利用文章内的相关技术从事非法测试，由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，极致攻防实验室及文章作者不为此承担任何责任。

##  **前言：**

在红队渗透中，无论是边界突破后获得主机权限，还是内网横向获得主机权限，首要做的事就是上C2去巩固权限或者进行接下来的渗透行动，然而当目标主机终端防护能力较强时，免杀对抗又是一个让红队选手不得不面对的难题，特别是当“手里无货”时，疯狂的测试，使得某数字杀软后台一堆弹窗报警的场景屡见不鲜。集权系统即C2系列文章将介绍一种逆向思维，使用流行的集权系统充当C2,利用其自带官方签名buffer的天然优势，在某些场景下能减少免杀成本，甚至有特别的隐匿性。

 **下面使用目前很火的chatgpt来进行一场渗透测试：**

##  **一、什么是Windows Admin Center：**

![image](https://image.3001.net/images/20230801/1690895435_64c9044bb1f4a3f6d31e3.png!small)

##  **二、如何安装Windows Admin Center：**

![image](https://image.3001.net/images/20230801/1690895482_64c9047a12b3ee94724bc.png!small)
WindowsAdminCenter2211.msi下载地址：  
https://go.microsoft.com/fwlink/?linkid=2220149&clcid=0x804&culture=zh-cn&country=cn

 **静默安装：**  
但是很多场景是只有一个webshell command line或者远程命令执行，无交互式shell时这些安装步骤就显得很鸡肋了，所以：  
![image](https://image.3001.net/images/20230801/1690895547_64c904bb70454ef976789.png!small)

有时chatgpt还是喜欢说胡话的，测试一下，发现确实能够静默安装，只不过闪了几个黑框：

`msiexec /i WindowsAdminCenter2211.msi /qn`

![image](https://image.3001.net/images/20230801/1690895652_64c90524b86db34ec983f.png!small)

![image](https://image.3001.net/images/20230801/1690895674_64c9053a19c09f9349213.png!small)

安装完成后貌似进程不会自己启动，手动起一下进程：

`"C:\Program Files\Windows Admin Center\SmeDesktop.exe"`

##  **三、如何使用Windows Admin Center：**

 **如何连接：**

安装Windows Admin
Center后，默认连接端口为6516（静默安装可指定），但是连接需要安装时的证书，这里提供一个思路，使用powershell导出到某路径，然后使用webshell进行下载，再将端口映射或者socks5进行连接。

![image](https://image.3001.net/images/20230801/1690895753_64c905899e5dc819c4a83.png!small)

问问chatgpt如何导出证书：

![image](https://image.3001.net/images/20230801/1690895777_64c905a1c328e48812917.png!small)

有些错误，修改一下：

`$cert = Get-ChildItem -Path cert:\LocalMachine\My | Where-Object
{$_.FriendlyName -eq "Windows Admin Center"}`

`$certPath = "C:\WAC_Certificate.pfx"`

`$certPassword = "123456"`

`Export-PfxCertificate -Cert $cert -FilePath $certPath -Password (ConvertTo-SecureString -String $certPassword -AsPlainText -Force)`

![image](https://image.3001.net/images/20230801/1690895958_64c906561c5968311f2ea.png!small)

命令太多？甚至你还可以继续问chatgpt：

![image](https://image.3001.net/images/20230801/1690895983_64c9066f246ad5645a0a3.png!small)

 **如何使用：**

使用导出到证书导入到我们的攻击主机，然后连接到目标主机Windows Admin Center服务，选择刚刚导入的证书，即可成功登录Windows
Admin Center集权系统：

![image](https://image.3001.net/images/20230801/1690896033_64c906a13c022a0f860cd.png!small)

主机信息、用户管理、文件管理、计划任务、甚至主机开关等功能应有尽有，这不就是一个windows官方的c2么？（某数字杀软在角落静静看着）：

![image](https://image.3001.net/images/20230801/1690896051_64c906b38ce75b58a8b84.png!small)

![image](https://image.3001.net/images/20230801/1690896064_64c906c0305e966649e5d.png!small)

##  **四、局限**

  * 需要管理员权限进行安装和证书导出
  * windows 10以上版本
  * 貌似没有命令执行功能（但计划任务也能达到相应效果）

##  **五、参考**

https://learn.microsoft.com/zh-cn/windows-server/manage/windows-admin-center/deploy/prepare-environment

