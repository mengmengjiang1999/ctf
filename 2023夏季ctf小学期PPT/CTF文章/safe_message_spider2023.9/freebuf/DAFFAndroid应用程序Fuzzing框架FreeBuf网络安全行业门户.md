****

[](https://youtu.be/ug5ZuezbD3c)

****

**Droid应用程序Fuzz框架（DAFF）可以帮助你在android设备中，对Android浏览器和PDF阅读器进行模糊测试，以发现其中可能存在的内存损坏漏洞。你可以使用它内置的fuzzers或导入你自定义的fuzz文件。DAFF由内置的fuzzers和crash
monitor（系统崩溃监视器）组成。目前它支持对以下应用的fuzzing测试：**

##  **浏览器**

  * [Google Chrome - com.android.chrome](https://play.google.com/store/apps/details?id=com.android.chrome)
  * [Mozilla Firefox - org.mozilla.firefox](https://play.google.com/store/apps/details?id=org.mozilla.firefox)
  * [Opera - com.opera.browser](https://play.google.com/store/apps/details?id=com.opera.browser)
  * [UC Browser - com.UCMobile.intl](https://play.google.com/store/apps/details?id=com.UCMobile.intl)

##  **PDF 查看器/阅读器**

  * [Adobe Acrobat Reader - com.adobe.reader](https://play.google.com/store/apps/details?id=com.adobe.reader)
  * [Foxit PDF Reader - com.foxit.mobile.pdf.lite](https://play.google.com/store/apps/details?id=com.foxit.mobile.pdf.lite)
  * [Google PDF Viewer - com.google.android.apps.pdfviewer](https://play.google.com/store/apps/details?id=com.google.android.apps.pdfviewer)
  * [WPS Office + PDF - cn.wps.moffice_eng](https://play.google.com/store/apps/details?id=cn.wps.moffice_eng)
  * [Polaris Office - com.infraware.office.link (WIP)](https://play.google.com/store/apps/details?id=com.infraware.office.link)

## Fuzz 生成器

DAFF有三种fuzzer模式：

  1. **Google Domato** \- 使用稍作修改的[Google Domato](https://github.com/google/domato)生成fuzzer文件。
  2. **Dumb Fuzzer** \- 顾名思义，愚蠢的fuzzer。（仅限PDF）
  3. **预生成文件（第三方fuzzer）-** 使用你私人或自定义的fuzzer生成文件。将html和pdf样本分别放置在generators/html/htmls和generators/pdf/pdfs中。

## 傻瓜式安装及使用

 **Android 设备**

  * 在Android设备中安装支持的浏览器和PDF阅读器。
  * 在Android设备中启用USB调试。
  * 将Android设备的网络连接到计算机的同一WiFi网络中。
  * 使用数据线将Android设备连接到计算机，并始终允许计算机进行USB调试。

 **计算机**

  * Install Python 2.7
  * git clone <https://github.com/ajinabraham/Droid-Application-Fuzz-Framework.git>
  * pip install -r requirements.txt
  * 在settings.py中，将DEVICE_ID设置为Android设备ID。 你可以用adb devices命令查看ID。
  * 同时将FUZZ_IP设置为电脑的本地IP地址。使用ifconfig/ipconfig命令查看当前的IP地址。
  * 如果adb不在你的PATH中，请在ADB_BINARY中将路径设置为adb binary。
  * 运行Web GUI python daff_server.py
  * 访问<http://0.0.0.0:1337>上的Fuzzer Web界面
  * 选择应用程序，选择fuzz生成器并启动fuzzing！

## DAFF视频演示

 **注意：** 在Android设备上安装应用后，至少要使用一次，并允许弹出窗口等。

## 结语

该项目是我的私人项目，开放它是为了对社区做出我的一点贡献。平时我并没太多的时间维护这个项目。因此，如果大家发现该项目存在的问题，请积极帮助修复并发送pull
requests。而我也会尽我所能，为大家提供更简单清晰的技术文档。如果在使用过程中遇到问题，希望大家学会利用Google或Stack
Overflow这类的网站来解决问题。

 ***参考来源：[github](https://github.com/ajinabraham/Droid-Application-Fuzz-Framework)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

