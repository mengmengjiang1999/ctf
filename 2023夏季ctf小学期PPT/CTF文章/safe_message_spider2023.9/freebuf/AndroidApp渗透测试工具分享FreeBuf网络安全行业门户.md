> 自己在网上搜集了一些App安全学习教程及工具，项目地址：<https://github.com/Brucetg/App_Security>

**这段时间因为某些原因接触了Android App渗透测试，发现了几个不错的App渗透测试工具（虽然这些工具早就出来了
2333），搭建测试环境的过程中遇到了一些问题，特地总结一下，希望能给大家带来帮助。**

##  一. drozer简介

drozer（以前称为Mercury）是一款Android安全测试框架。

drozer允许您通过承担应用程序的角色并与Dalvik VM，其他应用程序的IPC端点和底层操作系统进行交互来搜索应用程序和设备中的安全漏洞。

drozer提供工具来帮助您使用，共享和理解公共Android漏洞。它可以帮助您通过开发或社会工程将drozer
Agent部署到设备。使用weasel（MWR的高级开发负载）drozer能够通过安装完整代理，将有限代理注入正在运行的进程或连接反向shell以充当远程访问工具（RAT）来最大化其可用权限。

项目地址：<https://github.com/mwrlabs/drozer>

##  Mac 安装drozer

1\. 安装Python 2.7（系统自带）

2\. 安装Protobuf 2.6 or greater

    
    
    sudo pip install protobuf

3\. 安装Pyopenssl 16.2 or greater

    
    
    sudo pip install pyopenssl

4\. 安装Twisted 10.2 or greater

    
    
    sudo pip install twisted

5\. 安装JDK 1.7

这里我安装的是JDK 1.8，最后也安装成功了。

![](https://image.3001.net/images/20180827/1535368657_5b83ddd15d21c.png!small)

6\. 安装Python的service_identity模块（不安装的话后面运行drozer时总会显示警告）

    
    
    sudo pip install service_identity

7\. 安装 adb（Android Debug Bridge）

可以去 <https://developer.android.com/studio/releases/platform-tools>下载相应平台上的安装包，解压后配置下环境变量即可，这里仅演示Mac下的安装方式：

 **安装homebrew（已安装的话可跳过）**

ruby -e "$(curl -fsSL
<https://raw.githubusercontent.com/Homebrew/install/master/install>)"

安装adb

    
    
    brew install android-platform-tools

测试是否安装成功

    
    
    adb devices

如果不报错就说明安装成功啦。

8\. 安装drozer

到 <https://labs.mwrinfosecurity.com/tools/drozer/> 下载相应平台的安装包：

![](https://image.3001.net/images/20180827/1535368688_5b83ddf038432.png!small)

这里我下载的是drozer（Python .whl）

然后进入文件所在目录，执行以下命令：

    
    
    sudo pip install drozer-2.x.x-py2-none-any.whl

注意：这里的2.x.x要替换成自己下载的版本，比如这里下载的是2.4.4，就替换成2.4.4

安装成功后，执行drozer命令后输出如下：

![](https://image.3001.net/images/20180827/1535368703_5b83ddff87aa1.png!small)

Windows和Linux平台上的安装大体上类似，就不一一测试了。

##  客户端安装

同样到：<https://labs.mwrinfosecurity.com/tools/drozer/> 下载客户端，也就是drozer（Agent
.apk only）,然后安装到手机或者模拟器上就好。

##  使用

###  使用Android模拟器：

如果使用Android模拟器，则需要设置合适的端口，以便PC可以连接到模拟器内部或设备上的代理打开的TCP套接字。默认情况下，drozer使用端口31415:

列出所有设备：

    
    
    adb devices

![](https://image.3001.net/images/20180827/1535368720_5b83de1013547.png!small)

启动drozer服务端：

    
    
    drozer server start

接着执行：

    
    
    adb connect 192.168.56.101:5555      #连接到模拟器
    adb forward tcp:31415 tcp:31415      #进行端口转发

启动移动设备中的drozer agent，将右下角的关闭置为打开状态：

![](https://image.3001.net/images/20180827/1535368744_5b83de28b5607.png!small)

然后，使用drozer控制台进行连接，在PC终端中执行以下命令：

    
    
    drozer console connect --server 192.168.56.101

如果连接成功，PC终端效果如下：

![](https://image.3001.net/images/20180827/1535368762_5b83de3ac7ce4.png!small)

此时，Android客户端状态如下：

![](https://image.3001.net/images/20180827/1535368780_5b83de4c82275.png!small)

###  常用命令：

    
    
    run app.package.list               #列出设备中安装的包
    run app.package.list -f app名称     #不一定非得是完整的包名
    run app.package.info               #获取安装的包的信息
    run app.package.info -a com.android.browser   #列举指定包的信息
    run app.package.info -p android.permission.INTERNET  #列出具有相应权限的包

![](https://image.3001.net/images/20180827/1535368807_5b83de67d7da4.png!small)

    
    
    run app.activity.info         #列举设备上所有的activity
    run app.activity.info -f 包名    #搜索包的activity

![](https://image.3001.net/images/20180827/1535368832_5b83de80a02a5.png!small)

    
    
    run app.provider.info          #列举设备上所有的provider
    run app.service.info          #列举设备上所有的service
    run app.broadcast.info         #列举设备上所有的广播
    run app.package.attacksurface com.android.browser     #查看设备上某包的受攻击面
    run app.activity.info -a 包名       #列出包的所有Activity

![](https://image.3001.net/images/20180827/1535368852_5b83de94ca1b8.png!small)

    
    
    #运行activity
    run app.activity.start --action 【activity 设置的intent filter的action属性】 --category 【activity 设置的intent filter的category 属性】--component 【package 名字】 【component 属性】
    例如：
    run app.activity.start --action android.intent.action.MAIN --category android.intent.category.LAUNCHER --component com.android.browser com.android.browser.BrowserActivity
    
    
    #根据指定的intent action和intent category来查看activity
    run app.activity.forintent --action 【intent action】 --category 【intent category】
    run app.activity.forintent --action android.intent.action.VIEW --category android.intent.category.DEFAULT

其他用法如下：

Dex是Android系统中可以在Dalvik虚拟机上直接运行的文件格式。java源代码经过ADT的复杂编译后转换成Dex文件，这是一个逐步优化的过程。Dex文件的指令码就是Dalvik虚拟机专有的一套指令集，专门为嵌入式系统优化过，相比标准java的.class文件，它体积小，运行效率高。  

    
    
    $ run app.activity.forintent                   // Find activities that can handle the given intent                               
    $ run app.activity.info                        // Gets information about exported activities.                                   
    $ run app.activity.start                       // Start an Activity                                                             
    $ run app.broadcast.info                       // Get information about broadcast receivers                                     
    $ run app.broadcast.send                       // Send broadcast using an intent                                                 
    $ run app.broadcast.sniff                      // Register a broadcast receiver that can sniff particular intents               
    $ run app.package.attacksurface                // Get attack surface of package                                                 
    $ run app.package.backup                       // Lists packages that use the backup API (returns true on FLAG_ALLOW_BACKUP)     
    $ run app.package.debuggable                   // Find debuggable packages                                                       
    $ run app.package.info                         // Get information about installed packages                                       
    $ run app.package.launchintent                 // Get launch intent of package                                                   
    $ run app.package.list                         // List Packages                                                                 
    $ run app.package.manifest                     // Get AndroidManifest.xml of package                                             
    $ run app.package.native                       // Find Native libraries embedded in the application.                             
    $ run app.package.shareduid                    // Look for packages with shared UIDs                                             
    $ run app.provider.columns                     // List columns in content provider                                               
    $ run app.provider.delete                      // Delete from a content provider                                                 
    $ run app.provider.download                    // Download a file from a content provider that supports files                   
    $ run app.provider.finduri                     // Find referenced content URIs in a package                                     
    $ run app.provider.info                        // Get information about exported content providers                               
    $ run app.provider.insert                      // Insert into a Content Provider                                                 
    $ run app.provider.query                       // Query a content provider                                                       
    $ run app.provider.read                        // Read from a content provider that supports files                               
    $ run app.provider.update                      // Update a record in a content provider                                         
    $ run app.service.info                         // Get information about exported services                                       
    $ run app.service.send                         // Send a Message to a service, and display the reply                             
    $ run app.service.start                        // Start Service                                                                 
    $ run app.service.stop                         // Stop Service                                                                   
    $ run auxiliary.webcontentresolver             // Start a web service interface to content providers.                           
    $ run exploit.jdwp.check                       // Open @jdwp-control and see which apps connect                                 
    $ run exploit.pilfer.general.apnprovider       // Reads APN content provider                                                     
    $ run exploit.pilfer.general.settingsprovider  // Reads Settings content provider                                               
    $ run information.datetime                     // Print Date/Time                                                               
    $ run information.deviceinfo                   // Get verbose device information                                                 
    $ run information.permissions                  // Get a list of all permissions used by packages on the device                   
    $ run scanner.activity.browsable               // Get all BROWSABLE activities that can be invoked from the web browser         
    $ run scanner.misc.native                      // Find native components included in packages                                   
    $ run scanner.misc.readablefiles               // Find world-readable files in the given folder                                 
    $ run scanner.misc.secretcodes                 // Search for secret codes that can be used from the dialer                       
    $ run scanner.misc.sflagbinaries               // Find suid/sgid binaries in the given folder (default is /system).             
    $ run scanner.misc.writablefiles               // Find world-writable files in the given folder                                 
    $ run scanner.provider.finduris                // Search for content providers that can be queried from our context.             
    $ run scanner.provider.injection               // Test content providers for SQL injection vulnerabilities.                     
    $ run scanner.provider.sqltables               // Find tables accessible through SQL injection vulnerabilities.                 
    $ run scanner.provider.traversal               // Test content providers for basic directory traversal vulnerabilities.         
    $ run shell.exec                               // Execute a single Linux command.                                               
    $ run shell.send                               // Send an ASH shell to a remote listener.                                       
    $ run shell.start                              // Enter into an interactive Linux shell.                                         
    $ run tools.file.download                      // Download a File                                                               
    $ run tools.file.md5sum                        // Get md5 Checksum of file                                                       
    $ run tools.file.size                          // Get size of file                                                               
    $ run tools.file.upload                        // Upload a File                                                                 
    $ run tools.setup.busybox                      // Install Busybox.                                                               
    $ run tools.setup.minimalsu                    // Prepare 'minimal-su' binary installation on the device.

##  二. Androguard

###  Androguard简介：

Androguard是一款使用Python编写的跨平台的Android逆向工具，它可以在
Linux/Windows/OSX上运行。使用它可以反编译android应用，也可以用来做android app的静态分析（static
analysis）。

###  安装Androguard：

    
    
    sudo pip install -U androguard

###  Androguard的使用：

主要文件：

    
    
    androarsc.py          
    androauto.py            
    androaxml.py            
    androdd.py           
    androgui.py            
    androlyze.py          
    androsign.py        
    androcg.py             
    androdis.py
    
    
    1. androarsc.py            #直接从给定文件或APK中解码resources.arsc

![](https://image.3001.net/images/20180827/1535368875_5b83deab1aef5.png!small)

    
    
    2. androauto.py                    #使用该文件可进入自动模式

使用方法：

![](https://image.3001.net/images/20180827/1535368893_5b83debd39316.png!small)

    
    
    3. androaxml.py            #从指定的APK中解析或直接解析AndroidManifest.xml并以XML格式打印出来或者保     存到文件中，这个程序也可用于处理任何AXML编码的文件，比如来自布局目录中的文件。

使用方法：

![](https://image.3001.net/images/20180827/1535368924_5b83dedc1a85e.png!small)

    
    
    4. androdd.py             #反编译APK并创建控制流图

使用方法：

![](https://image.3001.net/images/20180827/1535368962_5b83df0280100.png!small)

    
    
    5. androgui.py            #androguard的图形化界面文件，需要安装PyQT5

使用方法：

![](https://image.3001.net/images/20180827/1535368984_5b83df188d005.png!small)

    
    
    6. androlyze.py           #打开一个IPython终端并开始逆向工程

使用方法：

![](https://image.3001.net/images/20180827/1535369010_5b83df3267c2d.png!small)

    
    
    7. androsign.py           #返回APK中所有证书的指纹

使用方法：

![](https://image.3001.net/images/20180827/1535369031_5b83df4723b39.png!small)

    
    
    8. androcg.py             #基于数据分析创建调用图并将其导出为图形格式

使用方法：

![](https://image.3001.net/images/20180827/1535369059_5b83df6307799.jpg!small)

    
    
    9. androdis.py                  #该文件是DEX文件的反汇编程序

使用方法：

![](https://image.3001.net/images/20180827/1535369079_5b83df771d69e.jpg!small)

实例：

    
    
    androarsc.py -i crackme0502.apk -o crackme0502.arsc

![](https://image.3001.net/images/20180827/1535369103_5b83df8fe8c71.jpg!small)

    
    
    androdd.py -i crackme0502.apk -o crackme0502

执行完该命令后，所有输出均在crackme0502中

    
    
    androsign.py --hash SHA1 -a -s crackme0502.apk

![](https://image.3001.net/images/20180827/1535369122_5b83dfa2defc3.jpg!small)

    
    
    androcg.py -s crackme0502.apk

如果上述执行上述命令后报错：AttributeError: 'DiGraph' object has no attribute 'edge'

只需要安装networkx低版本即可（最新版2.2），改为1.9后程序正常运行：

    
    
    sudo pip install networkx==1.9

![](https://image.3001.net/images/20180827/1535369145_5b83dfb999c73.jpg!small)

更详细的使用方法请参考：
<https://media.readthedocs.org/pdf/androguard/latest/androguard.pdf>

常用的Android 渗透测试框架除了文章中提到的，还有好几个，不过这里限于篇幅原因就先写这么多吧！

参考文章：<http://blog.orleven.com/2017/06/22/android-base/>

 ***本文作者：Brucetg，转载请注明来自FreeBuf.COM**

