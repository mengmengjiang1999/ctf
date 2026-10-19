移动互联网统治了我们世界，移动端安全越来越重要。终端安全最重要的原则是"不访问不安全的网站，不下载不明来源的应用，不安装不信任的APP，不给APP不必要的权限"。话虽如此，但是实际上有的时候，还需要安装一些未知的APP，这是后怎么办呢？

这就需要对其先进行一下安全评估，现在有很多在线安全检测平台，比如360捉虫猎手，企鹅家的金刚审计系统等。最近恰好要尝试一个apk扫描的时候发现前些年搞的大量在线评估系统基本上都不能用了（360捉虫猎手还ok）。所以，虫虫今天就给大家介绍下，基于开源的MobSF自建一个应用APP扫描云平台。

![1.png](https://image.3001.net/images/20191115/1573796299_5dce39cb6dc3d.png!small)

## MobSF简介

Mobile Security
Framework（MobS，移动安全框架）是一种自动化多平台移动应用程序，支持Android、iOS和Windows应用自动化测试。能够进行静态、动态分析，web
API测试，恶意软件分析和安全评估。MobSF支持对移动APP二进制文件，包括APK，IPA和APPX以及对压缩的源代码进行分析，提供Web界面进行任务管理和报告显示，并提供REST
API实现CI/CD或DevSecOps管道无缝集成。其中动态分析器可帮助我们执行运行时安全性评估和交互式检测。

![2.png](https://image.3001.net/images/20191115/1573796309_5dce39d5354c0.png!small)  

## 安装部署

### 安装要求

进行静态分析分析需要安装以下条件：

Git，Python 3.6以上版本，JDK 8以上版本。

Linux下可以通过发行版的包管理软件直接安装，比如Ubuntu下可以用：

苹果Mac OS用户：

Windows用户需要安装Microsoft Visual C ++ Build Tools和OpenSSL

Windows App静态分析需要Mac和Linux的Windows主机或Windows VM（略）。

为了生成PDF报告，需要单独安装wkhtmltopdf二进制文件。在Windows中，需要将包含wkhtmltopdf二进制文件的文件夹添加到环境变量PATH。

### 安装

安装过程很简单，首先从MobSF仓库clone下载源码：

    
    
    git clone https://github.com /MobSF/Mobile-Security-Framework-MobSF.git

然后，在Linux和Mac OS下执行./setup.sh，Windows下执行setup.bat即可。

### docker安装：

MobSF 2.0也新增加了docker方式安装，安装运行非常方便。方便起见可以直接拉取官方镜像：

也可以自己编译镜像或者需要额外功能要求的也必须找自编译镜像：

## 运行

Linux和Mac下通过：

Windows下运行：

![3.png](https://image.3001.net/images/20191115/1573796322_5dce39e284184.png!small)

然后默认会开启一个8080服务器监听，通过浏览器访问localhost:8080就可以访问。

![4.png](https://image.3001.net/images/20191115/1573796335_5dce39ef46384.png!small)

## 静态分析

通过浏览器访问localhost:8080，会弹出分析文件上传界面，可以把apk包通过拖放到虚线框里或者通过Upload &
Analyze选择文件就可以完成分析任务的设置。

左边栏目各种分析项目，右边窗体是该次分析的终结基本包括了四大组件扫描个数、export 情况），反编译源码（java、smali）、mainfest
文件分析、安全分析等。

本例中我上传了GPS测试仪的apk，结果如下：

![5.png](https://image.3001.net/images/20191115/1573796344_5dce39f811e32.png!small)

 **扫描项目设置和设计源码浏览：**

![6.png](https://image.3001.net/images/20191115/1573796353_5dce3a01bb974.png!small)

其中一个反编译的About.java源码：  

![6.png](https://image.3001.net/images/20191115/1573796466_5dce3a72a6a0d.png!small)

 **应用签名分析：**

![7.png](https://image.3001.net/images/20191115/1573796384_5dce3a20ee0ac.png!small)

 **权限和二进制库分析：**

![8.png](https://image.3001.net/images/20191115/1573796530_5dce3ab2f25e5.png!small)

红色提醒表示需要开放 定位权限，有风险，非法应用可以窃取位置信息，或者用它来消耗电池。

 **文件清单分析：**

![9.png](https://image.3001.net/images/20191115/1573796544_5dce3ac035acd.png!small)

可以被恶意信息拷贝，拖库。

## 动态分析

MobSF也支持动态分析，但是需要Genymotion模拟平台的支持，通过它来启动安卓虚拟机VM。

![10.png](https://image.3001.net/images/20191115/1573796553_5dce3ac9ce977.png!small)

MobSF动态分析需要Genymotion Android x86 VM 4.1至9.0版本。一般建议使用Android 7.0或更高版本。

首次运行时会自动MobSFyed Android 5及更高版本。对于小于5的Android版本，必须在第一次进行Dynamic
Analysis之前运行Android运行时。单击"动态分析"页面中的MobSFy Android运行时按钮以MobSFy Android运行时环境。

![11.png](https://image.3001.net/images/20191115/1573796563_5dce3ad378045.png!small)

如果Dynamic Analyzer无法检测的安卓设备，可通过MobSF/settings.py文件，手动配置ANALYZER_IDENTIFIER。

例如：

可以在Genymotion虚拟机列表中找到安卓设备的IP，默认端口为5555。

![12.png](https://image.3001.net/images/20191115/1573796573_5dce3add3a297.png!small)

## 批量分析

除了通过Web界面人工进行单任务分析以外，MobSF支持通过命令行进行批量分析。

批量分析需要用mass_static_analysis.py工具，使用方法是 mass_static_analysis.py [-h] [-d 目录]
[-s IP端口]

其中-h表示使用帮助。

-d选项来制定需要扫描APP包和源码压缩包所在的目录。

-s 用来制定MobSF服务器的地址和端口，比如127.0.0.1:8080

例如：

`pythonmass_static_analysis.py -s 127.0.0.1:8000 -d /opt/apks/`

## 分析报告

可以以PDF导出该次分析的报告，注意好像默认下对中文支持有问题：

![13.png](https://image.3001.net/images/20191115/1573796651_5dce3b2b69625.png!small)

## 总结

本文虫虫大家介绍了如何利用开源的MobSF平台自己移动APP自动扫描平台。MobSF功能强大的移动安全测试平台，支持静态，动态分析以Web API
Fuzzer测试。MobSF支持docker一键部署，Web界面进行管理、导出PDF分析报告，安装和使用都非常方便友好。

