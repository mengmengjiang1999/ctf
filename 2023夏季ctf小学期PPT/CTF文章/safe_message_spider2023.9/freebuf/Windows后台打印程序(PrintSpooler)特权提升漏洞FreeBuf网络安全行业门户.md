## 前言提要

2021年6月9日，微软修复`Windows Print Spooler`（CVE-2021-1675）权限提升漏洞。

2021年6月29日，有安全研究员在GitHub公布打印机漏洞利用exp，但是令人意想不到得是，该漏洞利用exp针对得漏洞是一个与CVE-2021-1675类似但不完全相同得漏洞，且微软并没有更新补丁，所以意味着这是一个0day漏洞，这个0day漏洞被称为`PrintNightmare`（CVE-2021-34527）。

2022年2月8日，`Windows Print
Spooler`（CVE-2022-2199）提权漏洞再次爆出，该漏洞是PrintNightmare的续集！

## 程序介绍

Spooler（打印后台处理服务）的进程名是spoolsv.exe，WinXP Home/PRO默认安装的启动类型是自动，依赖于Remote
Procedure
Call。Spooler是为了提高文件打印效率，将多个请求打印的文档统一进行保存和管理，先将要打印的文件拷贝到内存，待打印机空闲后，再将数据送往打印机处理。这样处理速度更快些。建议将其设置为手动，有打印任务时再打开。

打印机程序无论是个人机还是服务器都是默认启动！！！（该漏洞利用应在所有Windows桌面版本上工作）

## 影响版本

发行版：2022/02/08

参考链接：<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-21999>

![image-20220318115522526](https://image.3001.net/images/20220319/1647675923_62358a131cfb550b88d28.png!small)

![image-20220318115534493](https://image.3001.net/images/20220319/1647675927_62358a17923fc461b1e82.png!small)

## 漏洞复现

下载并解压exp压缩包：

<https://github.com/ly4k/SpoolFool>

以下 PoC 使用创建新本地管理员的 DLL`admin / Passw0rd!`. DLL (`AddUser.dll`)
并且源代码可以在这个存储库中找到。

    
    
    SpoolFool.exe-dllAddUser.dll  
    #Win10成功执行DLL，添加本地管理员admin的用户  
    #admin/ Passw0rd!  
    ​  
    netuseradmin

![image-20220318113117532](https://image.3001.net/images/20220319/1647675931_62358a1b7f62811dbf880.png!small)

![image-20220318113211964](https://image.3001.net/images/20220319/1647675935_62358a1f01b5a7070d690.png!small)

### 执行漏洞利用后，将留下以下工件以供以后清理

    
    
    1、创建的打印机驱动程序目录不会被删除  
    2、有效负载 DLL 被复制到打印机驱动程序目录中，并且不会被删除  
    3、任何创建的打印机都不会被删除  
    4、目标打印机的SpoolDirectory值未恢复

## 服务禁用

这个服务是windows中的后台打印处理服务，当然作为server的操作系统中，这个服务是一定要禁止掉的了。

  1. 开始菜单-管理工具-服务，打开服务界面

![image-20220318132357592](https://image.3001.net/images/20220319/1647675940_62358a24576f921d1c935.png!small)

  2. 找到`Print Splooler`服务，双击该服务

![image-20220318132425802](https://image.3001.net/images/20220319/1647675945_62358a29d891b1c2bfdda.png!small)

从上图可以看到，该服务的当前启动状态为：自动。另外，大家可以注意下启动类型，共包括如下的类型：自动(延迟启动)、自动、手动、禁用

 **下面给大家分别解释下：**

  * 自动：自动是指电脑启动时同时加载该服务项，以便支持其他在此服务基础上运行的程序。

  * 自动(延时启动)：是Windows7及windows server 2008 R2中非常人性化的一个设计。采用这种方式启动，可以在系统启动一段时间后延迟启动该服务项，可以很好地解决一些低配置电脑因为加载服务项过多导致电脑启动缓慢或启动后响应慢的问题。

  * 手动：该进程虽然关闭，但依然可以在特定情况下被激活。

  * 禁用：除非用户手动修改属性，否则服务将无法运行。

## 漏洞修复

<https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-21999>

下载安全更新程序！！！！

  

漏洞参考：

<https://blog.csdn.net/Trouble_99/article/details/122880780>

