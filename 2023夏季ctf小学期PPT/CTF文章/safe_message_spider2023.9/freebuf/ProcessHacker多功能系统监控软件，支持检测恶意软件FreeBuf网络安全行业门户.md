**今天给大家介绍的是一款免费且强大的多功能工具，广大研究人员可以利用该工具来监控自己的系统资源，调试软件或检测恶意软件。**

![aaaaaaaaaaaaaa.png](https://image.3001.net/images/20190227/1551258853_5c7654e56a3bb.png!small)

##  Process Hacker项目地址

> 官方网站：<https://processhacker.sourceforge.io/>
>
> GitHub：<https://github.com/processhacker/processhacker>

###  系统要求

Windows7及以上版本，支持32位或64位。

##  功能介绍

> -提供详细的系统活动信息概览，支持高亮显示；
>
> -提供图标数据和统计数据，可帮助我们快速追踪目标资源和进程；
>
> -不能编辑或删除文件？追踪正在使用目标文件的进程；
>
> -活动网络连接诊断，可直接关闭连接；
>
> -获取实时磁盘访问信息；
>
> -以内核模式查看栈内存数据，支持WOW64和.NET；
>
> -越过services.msc：创建、编辑和控制服务；
>
> -体积小，可移动，无需安装；
>
> -100%[免费软件](http://www.gnu.org/philosophy/free-sw.en.html)（遵循[GPL
> v3](http://www.gnu.org/licenses/gpl-3.0.en.html)许可证协议）

##  项目构建

要求Visual Studio（2017及更高版本）

执行build目录下的build_release.cmd文件来编译项目代码，如果你想使用Visual
Studio来构建项目，你可以加载ProcessHacker.sln和Plugins.sln解决方案。

你可以从【[这里](https://www.visualstudio.com/vs/community/)】下载免费版本的Visual
Studio社区版来构建、运行或开发Process Hacker。

###  其他信息

不可以在64位操作系统上运行32位版本的ProcessHacker。

##  工具设置

如果你直接从U盘运行Process Hacker，你同样需要保存Process Hacker的设置。这里，你需要在Process
Hacker.exe所在的目录中创建一个名叫"ProcessHacker.exe.settings.xml"的空文件。

##  插件支持

点击Hacker->Plugins配置工具插件。

如果你遇到由插件所导致的程序崩溃，请确保插件和Process Hacker均为最新版本。

ExtendedTools插件所提供的磁盘和网络信息仅可在Process Hacker以管理员权限运行的环境下使用。

###  KProcessHacker

ProcessHacker使用了内核模式驱动器和KProcessHacker来辅助特定功能，其中包括：

> -捕捉内核模式栈数据；
>
> -提升进程处理枚举效率；
>
> -获取文件信息；
>
> -获取EtwRegistration对象名称；
>
> -设置Handle属性；

请注意，默认配置下KprocessHacker仅允许有管理员权限的进程建立连接。进行下列操作可允许ProcessHacker查看所有进程（无管理员权限）：

>
> 1.在注册表编辑器中，找到HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\KProcessHacker3；
>
> 2.在这个键下，创建一个名叫Parameters的键；
>
> 3.创建一个名为SecurityLevel的DWORD值，设置为2；如果你使用的不是官方版本，你需要将其设置为0；
>
> 4.最后，重启KprocessHacker3服务（sc stop KProcessHacker3,sc start KProcessHacker3）；

***参考来源：[processhacker](https://github.com/processhacker/processhacker)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

