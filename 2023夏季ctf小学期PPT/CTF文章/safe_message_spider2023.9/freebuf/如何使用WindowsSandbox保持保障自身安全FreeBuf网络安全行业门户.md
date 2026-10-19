![](https://image.3001.net/images/20190712/1562867191_5d2775f70f1ab.jpg!small)

**Windows10（版本1903）中最有趣的一项功能，就是Windows沙盒了。Windows沙盒相当于一个Windows
10虚拟机，它可以快速启动，并帮助我们测试下载下来的软件、浏览器扩展以及可疑网站，而且不会让恶意软件感染我们正常的Windows操作系统。**

对于那些安全意识非常强，但又不想安装专用虚拟机软件（例如VirtualBox、Hyper-V或VMWare等）的用户来说，Windows沙盒就是一个非常理想的替代方案了。

在安装Windows沙盒之前，需要提醒大家，启用沙盒之后同时也会启用Hyper-V，这将导致VMWare和VirtualBox无法在主机上正常运行。

## 安装Windows沙盒

首先，我们要确保我们的设备系统满足下列要求：

1、 Windows 10专业版或企业版，版本号为1903或更高版本。虽然Windows
10家庭版也有办法安装Windows沙盒，但需要很多额外操作，本文不做赘述。

2、 AMD64架构。

3、 在BIOS中启用虚拟化功能。

4、 至少4GB RAM（推荐8GB）。

5、 至少1GB磁盘空间（建议SSD）。

6、 至少双核CPU（建议4核心超线程CPU）。

Windows沙盒安装步骤如下：

1、 确保使用Windows 10专业版或企业版，版本号为1903或更高版本。

2、 确保BIOS中启用[了CPU的虚拟化功能](https://www.bleepingcomputer.com/tutorials/how-to-enable-cpu-virtualization-in-your-computer-bios/)。

3、 点击“开始”菜单，搜索“Windows功能”。在搜索结果中，点击“开启或关闭Windows功能”。

![](https://image.3001.net/images/20190712/1562867202_5d27760243447.jpg!small)

4、 打开Windows功能面板之后，往下滑，找到Windows Sandbox，勾选后点击OK按钮。

![](https://image.3001.net/images/20190712/1562867208_5d2776087ecc8.jpg!small)

5、 安装完成后重启设备，Windows会自动完成安装操作。

## 使用Windows沙盒

点击开始菜单，搜索Windows Sandbox（Windows沙盒），点击搜索结果，启动程序。

Windows沙盒首次加载时，可能时间会久一点，因为它需要生成Windows10镜像并用于虚拟机中。加载成功后，我们就会看到一个基于Windows
10的完整版Windows虚拟机操作系统了。

![](https://image.3001.net/images/20190712/1562867215_5d27760fb487d.jpg!small)

Windows沙盒运行后，我们可以直接传输文件，或复制粘贴主机剪贴板的内容。

![](https://image.3001.net/images/20190712/1562867220_5d27761415bce.jpg!small)

所有的复制粘贴操作跟直接在主机系统中的复制粘贴操作是一样的，用户不会感觉到任何差异。

为了演示Windows沙盒的使用方式，我访问了一个需要安装Adobe Flash
Player的网站。因为我不喜欢在主机上使用这些东西，所以我打算在Windows沙盒中进行测试。大家可以看到，原来这个文件绑定了恶意广告插件，如果这些东西安装在主机系统中，很可能还会感染勒索软件、挖矿软件或木马后门等等。

![](https://image.3001.net/images/20190712/1562867226_5d27761a9d7c0.jpg!small)

好消息就是，Windows沙盒中的任何操作都不会影响主机系统，我们可以随意下载、安装和测试各种恶意软件。当你再次打开Windows沙盒时，它会自动恢复到初始状态，使用起来非常方便。

## Windows沙盒还可以更好

首先，我个人是非常喜欢Windows沙盒这个功能的，它易于使用，允许用户快速启动和运行Windows
10虚拟机，而且所有权限级别的用户都可以直接访问和使用，这使得我们测试网站或浏览器扩展插件会变得非常容易。

但是，Windows沙盒只包含了基本的操作系统以及实用工具，没有安装其他的应用程序，因此我们无法在Windows沙盒中测试Word和Excel等恶意Office文档。

另一个问题，由于Windows沙盒可以直接读取主机系统的剪切板内容，如果用户在剪切板中保存了凭证或密码等敏感信息的话，沙盒中运行的任何内容都可以访问到这些数据。

 ***
参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/microsoft/using-the-windows-sandbox-to-stay-safe-online/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

