![](https://image.3001.net/images/20210110/1610290017_5ffb13612344f26b63853.png!small)

## APKLab

APKLab是一款针对VS Code的高级Android逆向工程工具，在该工具的帮助下，广大研究人员可以轻松在Visual
Studio中测试你的Android应用代码。APKLab已经将目前最好的一些开源工具，比如说[
_Apktool_](https://github.com/ibotpeaches/apktool/)、[
_Jadx_](https://github.com/skylot/jadx)、[ _uber-apk-signer_](https://github.com/patrickfav/uber-apk-signer)和[ _apk-mitm_](https://github.com/shroudedcode/apk-mitm/)等无缝集成到了Visual
Studio中，这样一来，广大研究人员就可以专注于Android应用程序分析并在不离开IDE的情况下完成所有的任务。

## 功能介绍

  * 解码目标APK中的所有资源；

  * 将APK反汇编为Dalvik字节码（Smali）；

  * 将APK反编译为Java资源；

  * 使用功能丰富的VS代码有效地分析和破解；

  * 通过MitM中间人攻击实现HTTPS流量检查；

  * 根据Smali和其他资源构建一个APK；

  * 将APK重构为调试模式代码以便进行动态分析；

  * 在构建过程中无缝签名APK；

  * 直接从Visual Studio安装APK；

  * 支持Apktool风格的项目(apktool.yml工具)；

  * 支持大多数Apktool CLI参数；

  * Android资源管理框架（即将推出！）

  * 支持用户为APK签名提供密钥库；

  * 下载并配置缺少的依赖项；

  * 使用[ _Smalise_](https://marketplace.visualstudio.com/items?itemName=LoyieKing.smalise)提供出色的Smali语言支持；

  * 支持Linux、Windows和macOS；

## 工具依赖

JDK 8+：在Shell中运行下列命令，或点击【[ _这里_](https://adoptopenjdk.net/)】下载：

    
    
    java -version

adb：在Shell中运行下列命令，或点击【[ _这里_](https://www.xda-developers.com/install-adb-windows-macos-linux/)】查看文档：

    
    
    adb devices

Smalise（推荐）：可以让使用Smali文件变得更加轻松。

## 工具下载

广大研究人员可以直接运行下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Surendrajat/APKLab.git

## 扩展配置

### 依赖路径

apklab.apktoolPath：apktool.jar的完整路径，或使用下列方式修改其版本：

    
    
    "apklab.apktoolPath": "/home/oozer/downloads/apktool_2.4.1.jar"

apklab.apkSignerPath：uber-apk-signer.jar的完整路径，或使用下列方式修改其版本：

    
    
    "apklab.apkSignerPath": "/home/oozer/downloads/uber-apk-signer-1.1.0.jar"

apklab.jadxDirPath：jadx-x.y.z目录的完整路径，或使用下列方式修改其版本：

    
    
    "apklab.jadxDirPath": "/home/oozer/downloads/jadx-1.1.0"

### 密钥库配置

apklab.keystorePath：Java密钥库的绝对路径，存放.jks或.keystore文件。

    
    
    "apklab.keystorePath": "/home/oozer/downloads/debug.keystore"

apklab.keystorePassword：存储密钥库的密码。

apklab.keyAlias：存储密钥库中所使用密钥的别名。

apklab.keyPassword：存储密钥库中所使用密钥的密码。

## 工具使用

### 打开APK和Apktool项目

打开Command Palette (Ctrl+Shift+P) ➜ APKLab：打开一个APK：

![](https://image.3001.net/images/20210110/1610290169_5ffb13f92a904ef238eb1.gif)

或者，直接打开一个现有的Apktool项目目录。

### 应用MitM补丁

右键点击apktool.yml文件 ➜ APKLab：准备HTTPS流量检测：

![](https://image.3001.net/images/20210110/1610290148_5ffb13e403aa572af295a.gif)

### APK重构与签名

右键点击apktool.yml文件 ➜ APKLab：APK重构：

![](https://image.3001.net/images/20210110/1610290195_5ffb14131ab96269eb1cd.gif!small)

### 将APK安装至设备

右键点击dist目录下的.apk文件➜ APKLab：安装APK：

![](https://image.3001.net/images/20210110/1610290273_5ffb1461168136e53dd80.gif!small)

### 清理ApkTool框架目录

打开Command Palette (Ctrl+Shift+P) ➜ APKLab：清空ApkTool框架目录。

## 项目地址

APKLab：【[ _GitHub传送门_](https://github.com/Surendrajat/APKLab)】

