## **01** 键盘布局简介

键盘布局是按键在键盘上的分布模式，决定了键位顺序。键盘布局在发展过程中，由于使用习惯的不同，各国间使用的键盘布局存在细微差别，因此在Windows系统上以国家为单位区分不同的键盘布局方案。我们最熟悉的布局模式当属美式键盘。键盘布局以动态链接库的形式存在System路径下，在系统启动时加载。本文将通过探究键盘布局文件的加载方式得到其潜在的利用方法。

![1659428137_62e8dd29daabdb65dbb71.png!small?1659428138879](https://image.3001.net/images/20220802/1659428137_62e8dd29daabdb65dbb71.png!small?1659428138879)

##  **02** 键盘布局方案加载过程

键盘布局文件的加载由winlogon.exe完成。Windows Logon Process(即winlogon.exe)，是Windows NT
用户登录程序，用于管理用户登录和退出，且以 SYSTEM
用户运行。在入口WinMain中，调用了函数UpdatePerUserSystemParameters：

![1659428159_62e8dd3f1fd2134c4971f.png!small?1659428159786](https://image.3001.net/images/20220802/1659428159_62e8dd3f1fd2134c4971f.png!small?1659428159786)

该函数位于user*32.dll中：

![1659428172_62e8dd4cc6666291d34b5.png!small?1659428173642](https://image.3001.net/images/20220802/1659428172_62e8dd4cc6666291d34b5.png!small?1659428173642)

在函数UpdatePerUserSystemParameters中，首先调用GetActiveKeyboardName，通过查询注册表项：

计算机\HKEY_CURRENT_USER\Keyboard Layout\Preload

获取默认加载的键盘布局文件：

![1659428210_62e8dd7254765cb47ca23.png!small?1659428210998](https://image.3001.net/images/20220802/1659428210_62e8dd7254765cb47ca23.png!small?1659428210998)

在对应注册表下，保存着默认加载的键盘布局编号：

![1659428236_62e8dd8c2e7c2aad6329e.png!small?1659428236853](https://image.3001.net/images/20220802/1659428236_62e8dd8c2e7c2aad6329e.png!small?1659428236853)

该编号指向注册表

计算机\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Keyboard
Layouts\00000804

![1659428273_62e8ddb13f30e24aebadc.png!small?1659428273891](https://image.3001.net/images/20220802/1659428273_62e8ddb13f30e24aebadc.png!small?1659428273891)

可以看到，当前默认启用的键盘布局文件是中文简体环境下的键盘布局，即美式键盘布局。在获取到当前启用的键盘布局文件名后，以此为参数调用LoadKeyboardLayoutWorker：

![1659428310_62e8ddd6add81c72488d9.png!small?1659428311496](https://image.3001.net/images/20220802/1659428310_62e8ddd6add81c72488d9.png!small?1659428311496)

在OpenKeyboardLayoutFile中，先调用GetKeyboardDllName判断当前语言环境，主要是为了区分出日、韩两种特殊键盘布局。各语言环境下的键盘布局可能略有差别，但是日韩因其文字的特殊性有其特定的键盘标准。接着OpenKeyboardLayoutFileWorker加载对应的DLL：

![1659428341_62e8ddf5286d2330f43f7.png!small?1659428341823](https://image.3001.net/images/20220802/1659428341_62e8ddf5286d2330f43f7.png!small?1659428341823)

OpenKeyboardLayoutFileWorker进一步调用LoadLibraryExW加载对应DLL：

![1659428359_62e8de0701ffffccd0afb.png!small?1659428359684](https://image.3001.net/images/20220802/1659428359_62e8de0701ffffccd0afb.png!small?1659428359684)

在加载前没有进行文件合法性相关的校验，这为恶意利用留下了空间。

##  **03** 键盘布局文件利用

 **1.键盘布局文件的构建**

Windows支持自定义键盘布局，利用微软官方的键盘布局生成器Keyboard Layout
Creator(MSKLC.exe)可以生成键盘布局文件对应的源码文件。首先加载已有键盘布局：

![1659428402_62e8de32080eaac52fbb7.png!small?1659428402671](https://image.3001.net/images/20220802/1659428402_62e8de32080eaac52fbb7.png!small?1659428402671)

选择当前语言地区的布局：

![1659428413_62e8de3d97792379cb64d.png!small?1659428414294](https://image.3001.net/images/20220802/1659428413_62e8de3d97792379cb64d.png!small?1659428414294)

保存源码文件：

![1659428766_62e8df9e783fcbe59e282.png!small?1659428767157](https://image.3001.net/images/20220802/1659428766_62e8df9e783fcbe59e282.png!small?1659428767157)

保存的结果是一个.klc文件：

![1659428777_62e8dfa956bba7788908a.png!small?1659428778081](https://image.3001.net/images/20220802/1659428777_62e8dfa956bba7788908a.png!small?1659428778081)

需要使用kbdutool.exe将.klc解析为键盘布局源码文件：

kbdutool.exe-u -i -s out.klc

生成的源码文件如下：

![1659428814_62e8dfce80580fb7b5282.png!small?1659428815174](https://image.3001.net/images/20220802/1659428814_62e8dfce80580fb7b5282.png!small?1659428815174)

在Layout01.C末尾添加DllMain函数：

![1659428833_62e8dfe1959d8e09d69e4.png!small?1659428834407](https://image.3001.net/images/20220802/1659428833_62e8dfe1959d8e09d69e4.png!small?1659428834407)

利用源码文件创建工程，在安装了WDK的环境下编译成对应系统架构的DLL，即可生成自定义布局文件。

 **2.键盘布局文件的安装**

键盘布局的安装方式有两种：

a)由上面的分析可知，在键盘布局加载时，会直接加载Preload注册表项下保存的默认键盘布局，可以通过劫持或替换默认键盘布局DLL等方式实现安装；

b)利用input.dll导出函数InstallLayoutOrTip进行安装。

第一种安装方式简单粗暴，通过修改Preload注册表改变默认加载的键盘布局文件。下面重点看第二种安装方式：

根据MSDN的InstallLayoutOrTip调用示例，可以通过在键盘布局注册表项

计算机\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Keyboard Layouts

下新增一个新编号，并添加相关字段信息：

![1659428886_62e8e016616d17c3daab4.png!small?1659428887078](https://image.3001.net/images/20220802/1659428886_62e8e016616d17c3daab4.png!small?1659428887078)

创建后，将恶意的键盘布局文件部署在system目录下，调用InstallLayoutOrTip启用目标键盘布局文件。函数第一个参数构造如下：

语言标识符(LangID):键盘布局ID(KLID)

![1659428906_62e8e02a00b438308996b.png!small?1659428906578](https://image.3001.net/images/20220802/1659428906_62e8e02a00b438308996b.png!small?1659428906578)

第二个参数默认为0，调用InstallLayoutOrTip启用指定布局文件，利用过程如下：

![1659428932_62e8e044770818a1ee843.png!small?1659428933269](https://image.3001.net/images/20220802/1659428932_62e8e044770818a1ee843.png!small?1659428933269)

安装结果：

![1659428950_62e8e056298588702440a.png!small?1659428950934](https://image.3001.net/images/20220802/1659428950_62e8e056298588702440a.png!small?1659428950934)

重启靶机后，恶意键盘布局文件被成功加载，弹出管理员权限cmd：

![1659429000_62e8e0880fed382257f6b.png!small?1659429000907](https://image.3001.net/images/20220802/1659429000_62e8e0880fed382257f6b.png!small?1659429000907)

安装过程需要管理员权限，且需要对相关注册表项进行更改，在防护措施不足的终端上容易被利用实现权限维持与持久化。

##  **04** 总结

键盘布局作为Windows下的特殊系统机制，其键盘布局DLL的生成与安装都有相应的工具与API，利用成本很低，是较好的权限维持方式。但是，键盘布局的利用方式同样存在其弊端，除了持久化的DLL需要放置在System目录下以外，还需要管理员权限实现安装，且行为容易被拦截。如果没有终端防护设备，通过这种方式实现的持久化与维*权还是能够达到很好的效果。

 **参考**

> 自定义键盘布局持久化：
>
> https://github.com/NtQuerySystemInformation/CustomKeyboardLayoutPersistence
>
> InstallLayoutOrTip调用示例：
>
> https://docs.microsoft.com/zh-cn/windows/win32/tsf/installlayoutortip

