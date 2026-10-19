## 一、隐藏用户（影子用户）的创建与利用进行权限维持

  

>  **利用条件：①获得管理员权限；** **②得到cmdshell等shell环境。**
>
>  
>
>
>  **系统：Windows10 x64 专业版**

  

### 操作步骤（以Windows10 为例）：

  

0×01、首先利用cmdshell添加一个用户名带$的用户，如：admin$：123456

  

 **命令：**

> net user admin$ 123456 /add #添加用户admin$
>
> net localgroup administrators admin$ /add #将admin$用户添加到管理员组administrators

  

![](https://image.3001.net/images/20210405/1617616104_606adce8f06b99f3b0ac8.png!small)

  

 **因为用户名后带有$（系统特性） ，在使用命令：net user 的时候，命令提示符中是看不到这个用户的**

  

![1617616121_606adcf9a24c25b20977f.png!small?1617616121900](https://image.3001.net/images/20210405/1617616121_606adcf9a24c25b20977f.png!small?1617616121900)

  

 **此时可以直接登录3389进行操作，但隐蔽性仍不足，可以在控制面板的管理工具中用户与用户组查看到该用户的存在，还需要进一步操作。**

  

![](https://image.3001.net/images/20210405/1617616197_606add45295c8e39c159f.png!small)

  

![1617616207_606add4f5d06fab725632.png!small?1617616207710](https://image.3001.net/images/20210405/1617616207_606add4f5d06fab725632.png!small?1617616207710)

  

  

 **0×02、对注册表进行修改，在 命令提示符与管理工具中无法查看**

  

 **当你利用shell创建了一个影子用户的时候，利用这个影子用户可以开启3389进行登录，在目标机上对注册表进行数据操作，达到提高影子用户的隐蔽性。**

  

利用 运行 输入regedit 打开注册表 ，找到如下图的项表：

  

![1617616372_606addf43fd3da146774b.png!small?1617616372685](https://image.3001.net/images/20210405/1617616372_606addf43fd3da146774b.png!small?1617616372685)

  

选择 **SAM 项** ，在工具栏上的 **“编辑 > 权限” **中设置权限 ，将 **Administrators组 的权限设置为完全控制**
后保存。

（
**拒绝修改不可逆，出错会造成大问题，别点到完全操控的拒绝项，该操作不可逆，利用这个思路，我们可以在修改注册表后再对System与Administrators权限进行拒绝访问，可防止管理员删除这个用户。**
）

  

![1617616452_606ade44ebd1381b4c31d.png!small?1617616453369](https://image.3001.net/images/20210405/1617616452_606ade44ebd1381b4c31d.png!small?1617616453369)

  

  

设置好后，回到注册表主页面 ，发现SAM项下出现了隐藏的子项，找到 **SAM > Domains > Account > Users 和 Names**

  

![1617616467_606ade5348f89e8bd53fa.png!small?1617616467547](https://image.3001.net/images/20210405/1617616467_606ade5348f89e8bd53fa.png!small?1617616467547)

  

  

分别找到 **Administrator用户** 和 **admin$用户** 的两个项

  

Administrator用户的F值（SID）：

  

![1617616494_606ade6e0432f4a718a36.png!small?1617616494408](https://image.3001.net/images/20210405/1617616494_606ade6e0432f4a718a36.png!small?1617616494408)

  

  

![1617616498_606ade72a98b0d7e4f5ce.png!small?1617616499037](https://image.3001.net/images/20210405/1617616498_606ade72a98b0d7e4f5ce.png!small?1617616499037)

  

  

然后将 **F表内的二进制数据** 复制下来，找到 **Users 下 用户admin$的F值** ，进行编辑粘贴 **修改**
成Administrator的值，保存。

  

 **admin$用户的users项与names项下的二进制数据值：**

  

![1617616524_606ade8c3c07fb3878675.png!small?1617616524568](https://image.3001.net/images/20210405/1617616524_606ade8c3c07fb3878675.png!small?1617616524568)

  

  

将Users项下的000003E9项（admin$用户的SID二进制数据值）下的值替换成Administrator用户的值， **替换后导出 Names项
下的 admin$项 与 000003E9项（右键选择项进行导出）** 。

  

![1617616561_606adeb19adacead16157.png!small?1617616561978](https://image.3001.net/images/20210405/1617616561_606adeb19adacead16157.png!small?1617616561978)

  

导出后：

  

![1617616568_606adeb8b894ad5f42e1c.png!small?1617616569031](https://image.3001.net/images/20210405/1617616568_606adeb8b894ad5f42e1c.png!small?1617616569031)

  

  

利用cmdshell（管理员权限）将admin$删除，删除后发现注册表中的admin$用户相关项已经消失，这时候我们导入已经备份好的项与数值（导出后双击进行导入或者在注册表中导入）

  

> 命令：net user admin$ /del

  

![1617616609_606adee13a0ddd72cf925.png!small?1617616609567](https://image.3001.net/images/20210405/1617616609_606adee13a0ddd72cf925.png!small?1617616609567)

  

注册表导入：

  

![1617616616_606adee8bd663d091e562.png!small?1617616617200](https://image.3001.net/images/20210405/1617616616_606adee8bd663d091e562.png!small?1617616617200)

  

  

  

导入成功：

![1617616641_606adf01ea855ca95aa46.png!small?1617616642359](https://image.3001.net/images/20210405/1617616641_606adf01ea855ca95aa46.png!small?1617616642359)

  

  

导入成功后回到管理工具中的查看用户与用户组的页面，发现用户组和用户已经没有admin$这个用户的存在了，但实则上我们仍可以用这个用户的密码进行登录RDP，而且可以相当于
**Administrator管理员** 进行登录操作。

  

![1617616657_606adf11321f4a9b450b5.png!small?1617616657449](https://image.3001.net/images/20210405/1617616657_606adf11321f4a9b450b5.png!small?1617616657449)

  

开启3389进行登录，发现问题：

  

![1617616670_606adf1e9c9f9c05aca34.png!small?1617616670961](https://image.3001.net/images/20210405/1617616670_606adf1e9c9f9c05aca34.png!small?1617616670961)

  

  

发现用户未授权，这时候又多了一个利用条件，要在右下的选择用户下，添加admin$用户的用户名，才能正常登录3389。

  

![1617616676_606adf24db3618bf268cf.png!small?1617616677180](https://image.3001.net/images/20210405/1617616676_606adf24db3618bf268cf.png!small?1617616677180)

  

![1617616681_606adf29c3619b9137a81.png!small?1617616682073](https://image.3001.net/images/20210405/1617616681_606adf29c3619b9137a81.png!small?1617616682073)

  

修改后成功登录：

  

![1617616688_606adf30c5bae9b86788e.png!small?1617616691510](https://image.3001.net/images/20210405/1617616688_606adf30c5bae9b86788e.png!small?1617616691510)

  

  

### 0×01 细节扩展：

  

  

那我们在实战中，是以远程登录界面为基础的。这时，我们又要拓展另一个权限，userauthentication权限 ，用于远程连接的身份验证。

  

 **我们以图片直观地查看该权限开启与关闭的区别：**

  

开启状态：

  

![1617616819_606adfb391d9d55845778.png!small?1617616820099](https://image.3001.net/images/20210405/1617616819_606adfb391d9d55845778.png!small?1617616820099)

  

关闭状态：

![1617623012_606af7e4caa85f34dfab2.png!small?1617623015089](https://image.3001.net/images/20210405/1617623012_606af7e4caa85f34dfab2.png!small?1617623015089)

### 重点！！！

  

 **鉴权开启时，我们在不知道账号密码的情况下无法登录到远程界面，但是鉴权关闭之后，无论我们输入的账号和密码是否正确，都可以进入远程界面窗口，。**

  

如何 **关闭鉴权模式** ，我们采用如下 **命令** ：

> REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal
> Server\WinStations\RDP-Tcp" /v UserAuthentication /t REG_DWORD /d 0

  

  

>  **0代表关闭，1代表开启**

  

 **关闭鉴权模式还不够，还需要关闭 securitylayer安全层验证 ：**

  

 **具体指：0 就是连接前使用 rdp 协议进行身份验证，rdp 即远程桌面连接，可以简单理解为就是关闭验证。1
是指在连接前两端协商来进行身份验证，这个是默认值。2 就是使用 tls 协议来进行。**

  

将其参数设置为0，命令如下：

> REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Terminal
> Server\WinStations\RDP-Tcp" /v SecurityLayer /t REG_DWORD /d 0

  

  

> 在笔者测试中，两个参数同时关闭 **（也存在关掉一个参数而不用验证的情况，但最好还是两个参数都关闭）** 才可以不用输入正确凭证进入3389的登录页面。

  

![1617616984_606ae05840cd9769268d4.png!small?1617616984655](https://image.3001.net/images/20210405/1617616984_606ae05840cd9769268d4.png!small?1617616984655)

  

以上操作的基础是 **目标机开启了远程桌面连接** ，所以我们这里也应了解一下如何开启远程桌面连接，咱们先配置一下防火墙，设置为 **允许远程桌面连接**
，命令：

> netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP
> dir=in localport=3389 action=allow

  

netsh 是 windows 的网络配置命令，advfirewall firewall 意思为防火墙的高级设置，add rule 是添加一条规则，name
指定规则名称，protocol 指定协议，dir 指定是出战还是入站，localport 指定端口，action 指定动作 allow 允许。

设置后，我们再通过 **注册表** 来设置一下允许远程桌面连接，执行以下命令：

> REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\TerminalServer" /v
> fDenyTSConnections /t REG_DWORD /D 0 /f

  

做好以上工作，服务器的RDP远程登录界面就可以在无输入正确密码的情况下打开，远程桌面连接输入 ip 就会直接跳到目标锁屏页。﻿

不用凭证验证进入到登录页面：

![1617617125_606ae0e5c8cedee0a46e8.png!small?1617617128097](https://image.3001.net/images/20210405/1617617125_606ae0e5c8cedee0a46e8.png!small?1617617128097)

  

### 0×02 思路扩展

  

**在这里展示的是代表新用户的影子用户的创建利用，如果遇上有意识的管理员，极有可能会在注册表中被发现，如果设置不可逆性的权限（查看访问设置完全控制的拒绝选项）可以暴力有效解决这个账号被删除的问题，但后面也会引发更大的问题。**

  

 **利用新的影子用户登录3389，会生成数据容易被发现，而且还需要在3389上添加条件才能进行正常登录（Windows10下是如此情况）。**

  

 **此处可以扩展两种方法：**

  

 **①所以说这里我们可以开启来宾账户Guest在注册表对其F值进行更换，开启Guest账户，我们就可以登录而且减少了一些不必要的关注。**

  

 **②在添加授权用户那个选项中，将所有已知的用户进行添加，防止管理员过早发现创建的影子用户的存在。**

  

  

  

