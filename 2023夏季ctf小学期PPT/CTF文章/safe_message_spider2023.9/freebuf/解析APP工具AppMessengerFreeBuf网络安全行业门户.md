## 0x00 介绍

下载链接：<https://github.com/sulab999/AppMessenger>

一款适用于以APP病毒分析、APP漏洞挖掘、APP开发、攻防行动/红队/渗透测试团队为场景的移动端(Android、iOS)辅助分析工具，可以帮助APP开发工程师、病毒分析师、漏洞/安全研究员提高工作效率，帮助渗透测试工程师、攻击队成员/红队成员快速收集到移动端中关键的资产信息并提供基本的信息输出,如：包名（packageName）、版本(versionName\versionCode)、应用签名(Signature)、文件MD5、SDK、URL、APP漏洞等信息。

## 0x01 使用

1、如有java环境，可双击apkmsg.jar，即可启动，直接将APP拖入即可自动识别2、如果无法打开或显示有乱码，可下载配套的jdk11，运行里面写好的脚本，即可一键启动3、MAC和Linux系统需要对运行脚本和JAVA_HOME里的文件授予可执行权限，命令如下chmod
777 运行mac/运行linux.shchmod -R 777
JAVA_HOMEjdk11：<https://github.com/sulab999/AppMessenger/releases/download/v4.6.2/jdk11.zip>

![](https://image.3001.net/images/20221114/1668393503_6371aa1f237df1074e68a.png!small)

拖进去就能查看到信息，

  * [√] 支持任意文件MD5识别
  * [√] 支持DEX、APK、IPA文件的信息收集
  * [√] 支持Android壳识别（识别准确率99%，业界一流）
  * [√] 支持基础检测：文件路径、包名、版本名、文件MD5、文件SHA1、DEX MD5、文件大小、allowbackup、debuggable、打包时间
  * [√] 支持解析APP权限信息、签名信息、支持系统版本等其他信息
  * [√] 支持敏感信息检测，如：url、ip等
  * [√] 支持Windows系统、MacOS系统、*nux系列的系统
  * [×] 一键对APK文件重打包
  * [×] APP漏洞挖掘

详细信息参考：https://github.com/sulab999/AppMessenger

