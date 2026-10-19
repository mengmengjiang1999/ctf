# 工具环境准备

JDK：因为Android应用都包含Java外壳，所以Java环境是必要的。没有Java，就没有apktool、Eclipse、jarsigner。

ADT：ADT中除了神器adb（AndroidDebug
Bridge）和Monitor，还包含了Emulator虚拟机和Eclipse开发环境；另有较为新锐的替代品Android Studio。

GDB：作为大名鼎鼎的跨平台调试工具，GDB在实际测试中主要用于DUMP内存，从而发现敏感信息、解密数据、脱壳等等。

NDK：NDK可以在Windows上编译Android(arm)使用的Native层可执行文件（C/C++），各项Native层测试工具都可用NDK制作。

安卓设备：已root的真实手机/Emulator，不推荐x86虚拟机)VirtualBox/Genymotion)。x86虽然运行快，但是兼容性不佳，尤其客户APP涉及Native层时有时会出现莫名其妙的异常;

# 流量处理工具

BurpSuite/Fiddler：针对HTTP进行各种操作的利器。

Wireshark：偶尔遇到不走HTTP的APP时，定位代码用。

# 文件处理工具

ApkTool：功能众多，主要用来解包和打包Apk文件。

SignApk：对Apk文件进行签名，否则无法安装运行。

# Dalvik反编译工具

Dex2Jar：将Dex文件转换为Jar文件，便于反编译Java。

Smali2Java：直接从APK中反编译Java。

# 逆向分析工具

JD-GUI/Luyten：可以反编译Class/Jar文件，在Dex2Jar之后使用。

IDA：当APP存在Native层代码时，用于进行逆向分析。

# Xposed框架

XposedBridge：JAR文件，Xposed开发所必需的接口库。

XposedInstaller：APK文件，Xposed运行环境，注意5.0前后版本不同。

