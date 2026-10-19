![](https://image.3001.net/images/20220118/1642442284_61e5ae2ce490476d8aa10.png!small)

## 关于Mariana Trench

Mariana Trench是一款功能强大的静态代码分析平台，在该工具的帮助下，广大研究人员可以轻松针对Android和Java应用程序进行静态代码分析。

在这篇文章中，我们将带领大家在自己的设备上安装并配置好Mariana Trench，然后利用Mariana
Trench在一个小型的App中寻找出一个远程代码执行漏洞。

## 依赖组件

Mariana Trench的正常运行要求本地设备上安装并配置好最新版本的[
_Python_](https://www.python.org/downloads/)环境。在macOS上，我们可以通过[
_homebrew_](https://brew.sh/)来获取最新版本的Python：

    
    
    $ brew install python3

在Debian系统上（Ubuntu、Mint、Debian），我们可以使用apt-get来完成Python的安装：

    
    
    $ sudo apt-get install python3 python3-pip python3-venv

注意：大家还需要在本地设备上安装并配置好[ _Android_ __
_SDK_](https://developer.android.com/studio)，并将“$ANDROID_SDK”环境变量设置为指向SDK的安装路径。除此之外，我们还需要在一个[
_虚拟环境_](https://docs.python.org/3/tutorial/venv.html)中运行，这一步可以通过下列命令实现：

    
    
    $ python3 -m venv ~/.venvs/mariana-trench
    
    $ source ~/.venvs/mariana-trench/bin/activate
    
    (mariana-trench)$

如果你终端窗口的命令提示符前面显示了虚拟环境的名称，说明你的虚拟环境已经激活成功。

## 工具安装

在虚拟环境中安装Mariana Trench非常简单，只需要运行下列命令即可：

    
    
    (mariana-trench)$ pip install mariana-trench

## 工具运行

我们将使用一个简单的App来进行测试，运行下列命令即可获取测试App：

    
    
    (mariana-trench)$ git clone https://github.com/facebook/mariana-trench
    
    (mariana-trench)$ cd mariana-trench/documentation/sample-app

接下来，我们就可以执行静态代码分析了：

    
    
    (mariana-trench)$ mariana-trench \
    
      --system-jar-configuration-path=$ANDROID_SDK/platforms/android-30/android.jar \
    
      --apk-path=sample-app-debug.apk \
    
      --source-root-directory=app/src/main/java
    
    # ...
    
    INFO Analyzed 68886 models in 4.04s. Found 4 issues!
    
    # ...

使用Mariana Trench对测试App执行完分析后，会发现四个安全问题，分析的输出结果将包含针对应用程序中每一个方法的相关信息。

## 进一步处理

分析的输出结果其实并非人类可读的，因此我们还需要对这些信息进行进一步处理，这里将使用到[
_SAPP_](https://github.com/facebook/sapp)：

    
    
    (mariana-trench)$ sapp --tool=mariana-trench analyze .
    
    (mariana-trench)$ sapp --database-name=sapp.db server --source-directory=app/src/main/java
    
    # ...
    
    2021-05-12 12:27:22,867 [INFO]  * Running on http://localhost:5000/ (Press CTRL+C to quit)

输出的最后一行表明SAPP开启了一台本地Web服务器，并允许我们直接查看分析结果。

## 工具运行结果

![](https://image.3001.net/images/20220118/1642442411_61e5aeabaaa698dd4c3f7.png!small)

![](https://image.3001.net/images/20220118/1642442461_61e5aedddeb1836695d9d.png!small)![](https://image.3001.net/images/20220118/1642442471_61e5aee728273f3bf0813.png!small)

![](https://image.3001.net/images/20220118/1642442486_61e5aef6deb1ab07e39df.png!small)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

 **Mariana Trench：** 【[ _GitHub传送门_](https://github.com/facebook/mariana-trench)】

## 参考资料

> [ _https://mariana-tren.ch/docs/getting-started_](https://mariana-> tren.ch/docs/getting-started)
>
> [ _https://www.python.org/downloads/_](https://www.python.org/downloads/)
>
> [ _https://brew.sh/_](https://brew.sh/)
>
> [ _https://github.com/facebook/sapp﻿_](https://github.com/facebook/sapp)

