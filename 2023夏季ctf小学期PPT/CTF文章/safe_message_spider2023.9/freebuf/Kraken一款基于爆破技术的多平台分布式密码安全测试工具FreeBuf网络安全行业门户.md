## 关于Kraken

Kraken是一个功能强大的多平台在线分布式密码安全测试工具，该平台基于暴力破解技术来实现对密码安全性的测试，并允许广大研究人员在多台设备上以并行处理的方式遍历字典（基于crunch字典生成器）。除此之外，该工具不仅可以通过Web浏览器和Web应用程序的方式使用，而且还能够以独立的基于Electron的客户端执行。

易于使用、容错率高和可扩展性强也是Kraken的特性之一。

Kraken的主要目的是为了帮助广大研究人员更好地分析密码安全问题，并通过一个简单易用的解决方案，克服分布式爆破技术在单一设备上的负载限制。

## 工具安装

### 服务器和浏览器客户端

Kraken是一个使用了Docker-Compose实现的容器化应用，它将会启动数据库（Postgres）、S3文件存储（Minio）、服务器端和浏览器客户端等几个组件。

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/arcaneiceman/kraken.git

我们可以在项目代码库的根目录找到Docker-Compose文件，然后直接使用下列命令完成Kraken的部署：

    
    
    docker-compose up

Kraken的浏览器客户端可以通过下列形式访问：

> HTTP：localhost:8080
>
> HTTPS： https://localhost:8443

注意：如果需要从远程计算机运行浏览器客户端，这必须服务器URL和浏览器URL必须使用HTTPS。如果你托管服务器的本地地址为192.168.1.2，那么浏览器客户端的地址必须为https://192.168.1.2:8443，而服务器URL必须为https://192.168.1.2:8443/api。

如需上传密码列表或字典文件，请将它们上传到Minio控制台（localhost:9001），字典文件动态生成方式可以参考crunch使用手册【[
_传送门_](http://manpages.ubuntu.com/manpages/bionic/man1/crunch.1.html)】。

### 可移动桌面客户端

Kraken的桌面客户端是一个基于Electron的可移动应用程序，而且可以在macOS、Windows和Linux系统上运行。考虑到敏感权限方面的问题，我们建议广大研究人员使用下列方式编译代码库：

    
    
    git clone https://github.com/arcaneiceman/kraken.git
    
    cd kraken-client
    
    npm install
    
    npm run electron-start

### Windows安装和使用

Windows的exe客户端运行需要使用到hashcat依赖，Hashcat文件可以直接点击【[
_这里_](https://hashcat.net/files/hashcat-5.1.0.7z)】下载，或者，直接点击下列链接下载获取打包好的工具套件：

> exe客户端文件：【[
> _传送门_](https://github.com/arcaneiceman/kraken/releases/download/dockerUpdate/kraken-> client.1.2.0.exe)】
>
> 带有依赖组件的打包工具：【[
> _传送门_](https://github.com/arcaneiceman/kraken/releases/download/dockerUpdate/kraken-> client-with-dependencies.zip)】

## 向Kraken添加字典文件

如需将我们自己的字典文件添加到Minio，可以按照下列步骤进行操作：

1、打开浏览器，输入http://localhost:9001/来访问你的Minio控制台：

![](https://image.3001.net/images/20220424/1650791829_62651595a3cf6679d0df1.png!small)

2、使用<用户名：admin，密码：password>进行登录，此时将会看到Kraken的操作页面：

![](https://image.3001.net/images/20220424/1650791838_6265159e1364d68f5876a.png!small)

3、点击“Browse”来查看哪些文件可用，并使用“Upload”按钮添加我们自己的字典文件：

![](https://image.3001.net/images/20220424/1650791844_626515a4e44a2e1a1e553.png!small)

4、等待几分钟（或直接重启服务器）等服务器接收到之后，我们就可以通过日志来查看字典状态了，如果字典文件特别大的话，还需要等待服务器一段时间进行数据索引：

![](https://image.3001.net/images/20220424/1650791850_626515aa8ed661cee5340.png!small)

5、当我们在创建请求的时候，就可以查看到字典文件了：

![](https://image.3001.net/images/20220424/1650791858_626515b2e766eed3d6d08.png!small)

![](https://image.3001.net/images/20220424/1650791865_626515b9a639328f8c24c.png!small)

  

## 项目地址

 **Kraken：** 【[ _GitHub传送门_](https://github.com/arcaneiceman/kraken)】

## 参考资料

> [
> _http://manpages.ubuntu.com/manpages/bionic/man1/crunch.1.html_](http://manpages.ubuntu.com/manpages/bionic/man1/crunch.1.html)
>
> [
> _https://hashcat.net/files/hashcat-5.1.0.7z_](https://hashcat.net/files/hashcat-5.1.0.7z)
>
> [
> _https://github.com/arcaneiceman/kraken/releases/download/dockerUpdate/kraken-> client.1.2.0.exe_](https://github.com/arcaneiceman/kraken/releases/download/dockerUpdate/kraken-> client.1.2.0.exe)
>
> [
> _https://github.com/arcaneiceman/kraken/releases/download/dockerUpdate/kraken-> client-with-> dependencies.zip_](https://github.com/arcaneiceman/kraken/releases/download/dockerUpdate/kraken-> client-with-dependencies.zip)

