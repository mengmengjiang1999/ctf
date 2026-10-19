## 前言

**SSH是一种可以让你在不安全的网络上，安全的运行网络服务的网络协议。ssh的标准TCP端口为22端口，其最佳应用场景是用户远程登录至计算机系统。因此，SSH端口也是攻击者必扫的端口之一。本文将就SSH端口的安全性展开讨论，并为大家提供多种保护SSH端口安全性的建议和方法。**

在开始之前，让我们先在计算机上安装SSH server。命令如下：

    
    
    sudo apt-get install openssh-server

##
![安装SSH服务器](https://image.3001.net/images/20181004/1538613147_5bb55f9bd2d29.png!small)

## 端口转发

配置并运行SSH服务，然后我们使用NMAP进行扫描，可以看到当前SSH正在22端口上运行。

![端口转发](https://image.3001.net/images/20181004/1538613167_5bb55faf0ea7f.png!small)

切换至客户端机器的/etc/ssh目录下，我们可以看到一个名为sshd_config的配置文件。  

    
    
    cd /etc/ssh

![3.png](https://image.3001.net/images/20181004/1538613183_5bb55fbf73a2e.png!small)

使用nano命令打开sshd_config的文件。

![打开sshd_config的文件](https://image.3001.net/images/20181004/1538613240_5bb55ff8b9bca.png!small)

我们将其中的默认端口更改为2222（如下图所示），保存并关闭。通过这种方式，端口被我们从默认的22端口转发到了2222端口上。

![将端口从22转发到2222](https://image.3001.net/images/20181004/1538613260_5bb5600c40806.png!small)

现在，我们再次使用nmap进行扫描。  

    
    
    nmap 192.168.1.104

nmap的输出显示TCP端口2222已打开；但在服务描述中只显示了EthernetIP-1，并没有给出运行服务的详细描述。因此，让我们再来运行带有版本检测选项的nmap命令看看：  

    
    
    nmap  -sV 192.168.1.104

通过输出我们可以清楚地看到SSH服务当前正在TCP 2222端口运行以及OpenSSH版本的描述信息。

![OpenSSH版本的描述](https://image.3001.net/images/20181004/1538613292_5bb5602cb73a8.png!small)

## 公钥保护

首先，我们需要下载并安装PuTTY Key Generator。

 **注：** PuTTYgen是一个密钥生成器，用于为PuTTY创建SSH密钥并以自己的格式存储密钥（.ppk扩展名）

打开它，然后单击生成。

![单击生成](https://image.3001.net/images/20181004/1538613315_5bb56043e0184.png!small)

单击生成将启动生成公钥和私钥的过程，如图所示：

![生成将启动生成公钥和私钥](https://image.3001.net/images/20181004/1538613331_5bb56053ec41b.png!small)

生成公钥和私钥后，单击“ **Save Public Key** ”。这会将密钥作为一个公钥保存。

![将密钥作为一个公钥保存](https://image.3001.net/images/20181004/1538613354_5bb5606aa090f.png!small)

现在，我们打开服务器的Ubuntu终端并输入 **ssh-keygen** 。

![SSH-凯基](https://image.3001.net/images/20181004/1538613373_5bb5607df3f4a.png!small)

以上命令将创建一个名为.ssh的文件夹，然后我们在同一文件夹中创建一个名为authorized_keys的空文本文件。复制之前使用PuTTy Key
Generator创建的“ssh_login.ppk”文件，并将其粘贴到.ssh文件夹中，如下图所示：

![粘贴到的.ssh文件夹中](https://image.3001.net/images/20181004/1538613405_5bb5609dec612.png!small)

在终端中，进入.ssh文件夹并键入以下命令：

    
    
    puttygen -L "ssh_login.ppk"

此命令将会生成一个密钥。

![生成一个密钥](https://image.3001.net/images/20181004/1538613538_5bb561226947e.png!small)

现在，我们复制该密钥并使用 **nano** 命令将其粘贴到名为authorized_keys的空文件中并保存。

![粘贴到名为authorized_keys中的空文件中](https://image.3001.net/images/20181004/1538613564_5bb5613c8177c.png!small)

接着，我们打开putty配置选项卡，然后转到 **Session** 选项卡，为你的客户端机器提供IP地址和端口号。

![为你的客户端机器提供IP地址和端口号](https://image.3001.net/images/20181004/1538613586_5bb5615291874.png!small)

继续转到 **data** 选项卡，在 **data** 选项卡中提供 **Auto-login username** （自动登录用户名）。

![提供自动登录用户名（自动登录用户名）](https://image.3001.net/images/20181004/1538613604_5bb56164452d9.png!small)

导航到 **SSH >Auth**并提供ssh_login.ppk文件的路径（之前生成的公钥），然后单击“打开”。

![导航到SSH](https://image.3001.net/images/20181004/1538613622_5bb56176e2f7a.png!small)

此时，它将使用公钥登录SSH Server，而无需输入密码。

![使用公钥登录SSH服务器](https://image.3001.net/images/20181004/1538613644_5bb5618c0e35d.png!small)

使用gedit命令打开 **/etc/ssh** 下的sshd_config文件。修改#PasswordAuthentication选项，如下图所示。

 **当前配置**

> #PasswordAuthentication yes

**![当前配置](https://image.3001.net/images/20181004/1538613710_5bb561cee2a9e.png!small)**

现在，我们将参数值yes更改为no并去掉注释符（如下图所示），完成后保存并关闭文件。此更改将禁止任何用户使用密码登录 SSH Server。

> PasswordAuthentication no

**![当前配置](https://image.3001.net/images/20181004/1538613740_5bb561ecba8ef.png!small)**

正如你所看到的，这些设置已禁用基于密码的登录，并要求使用公钥登录。

![使用公钥登录](https://image.3001.net/images/20181004/1538613760_5bb562006c541.png!small)

## 禁用root登录并限制SSH用户的访问权限

该安全措施，需要我们先使用adduser命令创建一些新用户（这里我已经创建了： **h1，h2，h3，h4**
用户），然后使用gedit命令在sshd_config文件的 **#Authentication** 下添加以下行：

`#No root login allowed（h2 can login as sudo -s）`

``

`PermitRootLogin no`

``

`##only allow 1 users h2 （sysadmin）`

``

`AllowUsers h2`

``

切记！更改后及时进行保存，这将禁用Root登录，并且只允许h2用户远程登录SSH Server。

![只允许h2用户远程登录ssh服务器](https://image.3001.net/images/20181004/1538613782_5bb562163ebd5.png!small)

正如你所看到的，只有h2用户能够成功登录SSH Server，而h1和h3用户权限则被拒绝登录。

![H1和H3用户权限则被拒绝登录](https://image.3001.net/images/20181004/1538613798_5bb56226a7412.png!small)

##  **Google身份验证器**

要通过SSH Server进行双因素身份验证，首先你需要在手机上下载安装Google
Authenticator，并使用以下命令为Ubuntu安装所需的依赖包：

    
    
    sudo apt-get install libpam-google-authenticator

 **注** \- Google Authenticator在安装过程中会有多次询问，你只需选择Yes即可。

![在安装过程中会有多次询问](https://image.3001.net/images/20181004/1538613814_5bb56236074c7.png!small)

安装完成后，打开终端并输入以下命令：

    
    
    google-authenticator

此时，将会生成一个二维码，我们使用手机上的Google Authenticator进行扫描。

![成一个二维码](https://image.3001.net/images/20181004/1538613833_5bb5624929548.png!small)

成功扫描后，它将为我们生成一个动态口令，如图所示。

![生成一个动态口令](https://image.3001.net/images/20181004/1538613849_5bb5625986f70.jpg!small)

现在，我们使用的gedit命令打开sshd文件并进行以下更改：

> 在@include common-auth前添加注释符；

> 添加行（auth required pam_google_authenticator.so）到@include common-password下。

如图所示：

![进行以下更改](https://image.3001.net/images/20181004/1538613872_5bb56270edde4.png!small)

继续更改sshd_config文件中的以下选项。

> ChallengeResponseAuthentication yes

**![选项设置](https://image.3001.net/images/20181004/1538613891_5bb56283844a9.png!small)**

现在，当我们登录 SSH Server时，它会提示要求输入验证码。这里，我们必须输入在Google
Authenticator上生成的动态口令。如下图所示，我们已经使用一次性密码成功登录至SSH Server。

![成功登录至SSH服务器](https://image.3001.net/images/20181004/1538613909_5bb5629530506.png!small)

## 计划任务限制

在该安全措施中，我们将在服务器上设置SSH服务的时间限制。

 **Cron** 是一个用于调度任务的Linux的内置服务，它能够在指定的时间和日期自动运行服务器上的命令或脚本。

我们使用nano命令在 **/etc** 下打开crontab，创建一个计划任务让SSH服务每2分钟启动一次，4分钟停止一次。用于调度SSH服务的命令如下：

`* / 2 * * * * root service ssh start`

``

`* / 4 * * * * root service ssh stop`

``

保存更改并关闭文件。

![保存更改并关闭文件](https://image.3001.net/images/20181004/1538613925_5bb562a5dd00e.png!small)

等待服务重启，使用nmap扫描22端口。

    
    
    nmap  -p 22 192.168.1.104

运行扫描后，我们将观察端口22上的SSH服务是否已被关闭，因为它已持续运行了4分钟的时间。

现在，如果我们的命令正常工作，它应该每隔2分钟启动一次服务，为了进一步的确认我们将再次使用nmap进行扫描。

    
    
    nmap –p 22 192.168.1.104

可以看到端口现在处于开放状态。

![端口现在处于开放状态](https://image.3001.net/images/20181004/1538613945_5bb562b9eee9b.png!small)

## 禁用空密码

从安全最佳实践来看，我们应该始终禁用空密码登录SSH Server。要启用此设置，我们只需将sshd_config文件的以下参数值更改为no即可：

> PermitEmptyPasswords no

这将禁用空密码登录SSH Server。

![禁用空密码登录SSH服务器](https://image.3001.net/images/20181004/1538613967_5bb562cf814ad.png!small)

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/multiple-ways-to-secure-ssh-port/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

