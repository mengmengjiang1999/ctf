![](https://image.3001.net/images/20200205/1580836256_5e39a5a06f8d5.png!small)

**Obfuscapk是一款模块化的Python工具，它可以帮助研究人员在无需应用程序源代码的情况下对Android
App进行混淆处理。Obfuscapk使用了apktool来对原始APK文件进行反编译，并构建出一个新的应用程序，最后再对反编译的smali代码、资源文件和Manifest文件应用混淆处理技术。混淆后的应用回保留原有的函数功能，但不同之处就在于，混淆后的应用源码会跟初始的应用源码有很大的区别。**

##  工具架构

![](https://image.3001.net/images/20200205/1580836262_5e39a5a67f7b4.png!small)

Obfuscapk基于模块化结构实现，以便进行功能扩展，而且还集成了一套插件系统。在Obfuscapk中，每一个混淆器都属于一个插件，并且都继承了一个抽象的基类，它们都需要实现obfuscate方法。当工具开始处理一个新的Android应用文件时，它回创建一个混淆对象来存储所有需要的信息，例如反编译的smali代码的位置，以及处理操作的状态。接下来，Obfuscapk会将混淆对象以参数的形式传递给obfuscate方法，最终发送给所有处于活动状态的插件或混淆器。

值得一提的是，广大研究人员可以根据自己的需要扩展和开发新的混淆器，研究人员可以直接向“src/obfuscapk/obfuscators”目录中添加混淆技术或插件元数据（<obfuscator-name>.obfuscator文件）的实现源码。工具将会自动检测新的插件，因此无需进行额外配置。

##  工具安装

我们有两种方法来在自己的设备上安装和使用Obfuscapk，第一种就是使用Docker，另一种就是在Python
3.7环境下直接使用项目源码。在这两种方式下，首先要做的就是将项目源码拷贝到本地目录中：

    
    
    $ git clone https://github.com/ClaudiuGeorgiu/Obfuscapk.git

##  Docker镜像

###  依赖组件

我们建议大家使用这种方式来安装Obfuscapk，因为这种方式只需要安装Docker的最新版本即可：

    
    
    $ docker --version             
    
     Docker version 19.03.0, build aeac949

###  官方Docker Hub镜像

我们可以直接在Docker Hub上下载官方的Obfuscapk Docker镜像：

    
    
    $ # Download the Docker image.
    
     $ docker pull claudiugeorgiu/obfuscapk
    
     $ # Give it a shorter name.
    
     $ docker tag claudiugeorgiu/obfuscapk obfuscapk

###  安装

如果你从Docker Hub下载了官方镜像，那么我们就可以直接开始使用了，否则你还需要执行下列命令来创建“Obfuscapk/src/
”目录（该目录中包含了Dockerfile）来构建Docker镜像：

    
    
    $ # Make sure to run the command in Obfuscapk/src/ directory.
    
     $ # It will take some time to download and install all the dependencies.
    
     $ docker build -t obfuscapk 

Docker镜像准备好之后，需要运行下列命令检测是否安装正确：

    
    
    $ docker run --rm -it obfuscapk --help
    
     usage: python3.7 -m obfuscapk.cli [-h] -o OBFUSCATOR [-w DIR] [-d OUT_APK]
    
     ...

现在，Obfuscapk已经可以使用了。

##  源码安装

###  依赖组件

确保设备上已安装了apktool、jarsigner和zipalign，并且能够直接通过命令行工具使用：

    
    
    $ apktool          
    
     Apktool v2.4.0 - a tool for reengineering Android apk files
    
     ...
    
     $ jarsigner
    
     Usage: jarsigner [options] jar-file alias
    
            jarsigner -verify [options] jar-file [alias...]
    
     ...
    
     $ zipalign
    
     Zip alignment utility
    
     Copyright (C) 2009 The Android Open Source Project
    
     ...

如需安装和使用apktool，则要求最新版本的Java。apktool、jarsigner和zipalign的可执行程序路径需要在下列环境变量中进行配置：APKTOOL_PATH、JARSIGNER_PATH和ZIPALIGN_PATH。当然了，除了上述组件之外，你还需要安装Python
3.7。

###  安装

在项目主目录中运行下列命令即可完成依赖组件的安装：

    
    
    $ # Make sure to run the commands in Obfuscapk/ directory.
    
     $ # The usage of a virtual environment is highly recommended, e.g., virtualenv.
    
     $ # If not using virtualenv (<https://virtualenv.pypa.io/>), skip the next 2 lines.
    
     $ virtualenv -p python3.7 venv
    
     $ source venv/bin/activate
    
     $ # Install Obfuscapk's requirements.
    
     $ python3.7 -m pip install -r src/requirements.txt

接下来，运行下列命令确保工具安装正确：

    
    
    $ cd src/
    
     $ # The following command has to be executed always from Obfuscapk/src/ directory
    
     $ # or by adding Obfuscapk/src/ directory to PYTHONPATH environment variable.
    
     $ python3.7 -m obfuscapk.cli --help
    
     usage: python3.7 -m obfuscapk.cli [-h] -o OBFUSCATOR [-w DIR] [-d OUT_APK]
    
     ...

现在，Obfuscapk已经可以使用了。

##  工具使用

Docker镜像-本地目录中包含了待混淆的应用程序，需将其加载进容器中的“/workdir”目录中：

    
    
    $ docker run --rm -it -u $(id -u):$(id -g) -v "${PWD}":"/workdir" obfuscapk [params...]

源码-所有的命令都需要在“Obfuscapk/src/”目录中运行：

    
    
    $ python3.7 -m obfuscapk.cli [params...]

###  查看帮助信息：

    
    
    $ obfuscapk --help
    
     obfuscapk [-h] -o OBFUSCATOR [-w DIR] [-d OUT_APK] [-i] [-p] [-k VT_API_KEY] <APK_FILE>

工具有两个强制参数，第一个是“<APK_FILE>”，即待混淆APK的路径；另一个就是需要使用的混淆技术列表：

> -w DIR：设置工作目录，并保存apktool生成的中间文件。
>
> -d OUT_APK：设置目的文件的路径。
>
> -i：设置是否在混淆过程中忽略第三方库。
>
> -p：是否显示混淆进程条。
>
> -k VT_API_KEY：设置VirusTotal API密钥，仅在使用VirusTotal时需要设置。

## 工具使用样例

###  Obfuscapk的简单使用样例：

    
    
    $ # original.apk is a valid Android apk file.
    
     $ obfuscapk -o RandomManifest -o Rebuild -o NewSignature -o NewAlignment original.apk

##  项目地址

> Obfuscapk：【[GitHub传送门](https://github.com/ClaudiuGeorgiu/Obfuscapk)】

***参考来源：[ClaudiuGeorgiu](https://github.com/ClaudiuGeorgiu/Obfuscapk)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

