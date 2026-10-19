## 一、前言

 **过年在家无聊，原本打算装个抢红包插件发笔小横财，却掉进了很多坑，折腾损失了不少(时间和精力)红包。顺便学习了下猴神`MonkeyDev`的使用。**

## 二、MonkeyDev介绍

`iOSOpenDev`的升级版，非越狱插件开发集成神器。

> 1.可以使用`Xcode`开发`CaptainHook Tweak`，`Logos
> Tweak`和命令行工具，在越狱机器开发插件，这是原来的`iOSOpenDev`功能的迁移和改进。
>
> 2.只需拖入一个砸壳应用，即可自动集成`class-dump`，`restore-> symbol`，`Reveal`，`Cycript`和注入的动态库并重签名安装到非越狱机器。
>
> 3.支持调试自己编写的动态库和第三方`App`
>
> 4.支持通过`CocoaPods`第三方应用集成`SDK`以及非越狱插件，简单来说就是通过`CocoaPods`建造了一个非越狱插件商店。

 **相关链接**`monkeydev`文档说明：<https://monkeydev.org/>

## 三、MonkeyDev插件的安装

这里给出官方环境要求和安装步骤： **环境要求**

1、 安装最新的[theos](https://github.com/theos/theos/wiki/Installation)

    
    
    sudo git clone --recursive https://github.com/theos/theos.git /opt/theos
    

2、 安装`ldid`（如安装theos过程安装了ldid，跳过）

    
    
    brew install ldid
    

3、 配置免密码登录越狱设备（如果没有越狱设备，跳过）

    
    
    ssh-keygen -t rsa -P ''
    ssh-copy-id -i /Users/username/.ssh/id_rsa root@ip
    

或者安装`sshpass`自己的设置密码：

    
    
    brew install https://raw.githubusercontent.com/kadwanev/bigboybrew/master/Library/Formula/sshpass.rb
    

  * 注：`Mac`环境`git clone`提速
  * 修改`https`方式`git clone`配置 (需根据`ss`代理端口号而定)

    
    
    vim ~/.gitconfig
    
    [http]
        postBuffer = 524288000
        proxy = socks5://127.0.0.1:1086
    [https]
        proxy = socks5://127.0.0.1:1086
    

  * 或者用命令行修改配置

    
    
    git config --global http.proxy 'socks5://127.0.0.1:1086'
    git config --global https.proxy 'socks5://127.0.0.1:1086'
    

**安装** 1、 通过以下命令选择指定的`Xcode`进行安装：

    
    
    sudo xcode-select -s /Applications/Xcode-beta.app
    

2、 默认安装的`Xcode`为:

    
    
    xcode-select -p
    

3、 执行安装命令：

    
    
    sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/AloneMonkey/MonkeyDev/master/bin/md-install)"
    

4、 卸载:

    
    
    sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/AloneMonkey/MonkeyDev/master/bin/md-uninstall)"
    

5、 如果没有发布特殊说明，使用如下命令更新即可：

    
    
    sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/AloneMonkey/MonkeyDev/master/bin/md-update)"
    

安装/更新之后重启下`Xcode`再新建项目。

## 四、MonkeyApp的使用

主要介绍`MonkeyDev`的一步集成`非越狱`调试。

 **创建项目**

安装完成之后，打开`Xcode`，单击`File` \- `New` \-`Project`...，选择`iOS`滑动到最下方可以看到`MonkeyDev`提供的模块如下图，选择相应的项目类型，就可以创建对应的项目。

![-w500](https://image.3001.net/images/20200207/1581049183_5e3ce55f870df.jpg!small)点击创建`MonkeyAPP`，然后会自动生成相关文件如下图：![-w500](https://image.3001.net/images/20200207/1581049206_5e3ce57661d5b.jpg!small)

项目结构包含以下部分：

`put ipa or app here`:将需要分析的解密后的`App`或者`ipa`文件放到该目录下面。

`WeChatDemoDylib`这个是将被注入目标`App`的动态库，需要hook的代码可以在`WeChatDemoDylib.m`文件里面写，支持`OC
runtime`的`HOOK`，C函数的`fishhook`。

`WeChatDemoDylib.xm`:支持用Logos语法编写`hook`代码。

`WeChatDemoDylib.m`:可以在该文件中编写注人的`hook`代码。

`AntiAntiDebug`:里面是反反调试的代码.

`fishhook`:自动集成的`fishhook`模块。

### 常用的logos语法

官方介绍<http://iphonedevwiki.net/index.php/Logos>

1、`%hook`指定需要`hook`的类名

    
    
    %hook SBApplicationController
    -(void)uninstallApplication:(SBApplication *)application {
        NSLog(@"Hey, we're hooking uninstallApplication:!");
        %orig; // Call the original implementation of this method
        return;
    }
    %end
    

2、`%new`该指令用来给指定的class添加一个新的函数

    
    
    %new
    -(void)newMethod:(NSString*) output{
        NSLog(@"This is a new method : %@", output);
    }
    

3、`％orig`调用原始的挂钩方法。

    
    
    ％orig 
    ％orig （arg1 ， … ）
    

4、`%group`用于条件初始化或`%hook`分组

    
    
    %group iOS8
    %hook IOS8_SPECIFIC_CLASS
        // your code here
    %end // end hook
    %end // end group ios8
    
    %group iOS9
    %hook IOS9_SPECIFIC_CLASS
        // your code here
    %end // end hook
    %end // end group ios9
    
    %ctor {
        if (kCFCoreFoundationVersionNumber > 1200) {
            %init(iOS9);
        } else {
            %init(iOS8);
        }
    }
    

## 五、查找定位微信登录按钮

将`pp助手`下载的解密后的`ipa`放入`targetapp`文件中，通过`monkey`工程的图层调试发现（`Debug` > `View
Debugging` > `Capture View Hierarchy`）为灰色无法选择。

![-w555](https://image.3001.net/images/20200207/1581049711_5e3ce76f129bd.jpg!small)

故使用`FLEXLoader`定位`APP`登录按钮：

`FLEXLoader`下载及使用相关链接：<https://github.com/buginux/FLEXLoader>

![-w277](https://image.3001.net/images/20200207/1581049754_5e3ce79ae699d.jpg!small)选择登录按钮后，查看`views`，点击查看方法详情。![-w277](https://image.3001.net/images/20200207/1581049782_5e3ce7b63a0a9.jpg!small)

然后定位到了登录按钮的方法`onFirstViewLogin`和该方法所在的类`WCAccountLoginControlLogic`

编写相关代码监听登录按钮：

![-w277](https://image.3001.net/images/20200207/1581049874_5e3ce812670b2.jpg!small)

## 六、修改微信步数

通过搜索发现使用`MonkeyDev`插件修改微信步数的代码如下：

    
    
    #import <UIKit/UIKit.h>
    
    %hook WCDeviceStepObject
    - (int)m7StepCount {
        return 88888;
    }
    %end
    

![-w215](https://image.3001.net/images/20200207/1581049925_5e3ce8453f19a.jpg!small)

## 七、微信抢红包插件

找了两款自动抢红包插件，分别是`yahibo`的源码和`清水师傅`打包好的`dylib`，测试发现在最新版`微信`(7.0.8)都可以正常使用。
![-w277](https://image.3001.net/images/20200207/1581049965_5e3ce86d22374.jpg!small)
清水师傅的功能较多，并且使用和安装方便快捷。
![-w291](https://image.3001.net/images/20200207/1581049987_5e3ce8838b960.jpg!small)

### 注入重打包ipa文件

以清水师傅打包好的dylib为例，在非越狱手机下的安装方法如下。

相关链接：<https://qiita.com/shimizukawasaki/items/d8d01e30a8f67da68ea1>

1、使用PP助手下载`越狱应用`里的VX（该区的ipa均为砸壳后的文件）
![-w500](https://image.3001.net/images/20200207/1581050035_5e3ce8b3a8377.jpg!small)

2、下载一键注入工具：
![-w500](https://image.3001.net/images/20200207/1581050061_5e3ce8cd28fe9.jpg!small)选好对应路径，将下载的砸壳后的`ipa`文件和`dylib`文件进行重打包。

下载地址：<http://www.iosre.com/t/ipa-ipa/15494>

### 将ipa安装到非越狱手机

先说下踩过的2个坑吧

 **使用Impactor安装**

 **坑一：** 将`ipa`文件拖入`Impactor`，输入`APPLE
ID`帐号与密码后出现了各种报错提示，关闭了苹果双重认证，重新申请了`apple id`，换`win`系统等等，最后一直没安装成功，放弃了。

![-w452](https://image.3001.net/images/20200207/1581050114_5e3ce90208aa8.jpg!small)

 **相关链接**

<http://www.cydiaimpactor.com/>

<https://www.52pojie.cn/thread-946944-1-1.html>

 **使用AltDeploy安装**

**坑二：**`google`发现有说`AltDeploy`简单快捷完全取代了`Impactor`，然后下载使用发现最后出现应用名错误，找到`issues`发现不少人遇到此问题，解决方法说更换1.0版本，最后发现`AltDeploy`在安装`ipa`过程中莫名崩溃，也放弃了。

![-w477](https://image.3001.net/images/20200207/1581050169_5e3ce93972808.jpg!small)

 **相关链接**

<https://mrmad.com.tw/altdeploy>

<https://github.com/pixelomer/AltDeploy>

 **使用MonkeyDev安装**

最后还是使用`MonkeyDev`来安装注入好的`ipa`文件。1、打开`Xcode`，单击`File` \- `New` \-`Project`...，选择`iOS`滑动到最下方可以看到`MonkeyDev`点击创建`MonkeyAPP`，将注入好的ipa文件放入`TargetApp`目录内。

![-w1000](https://image.3001.net/images/20200207/1581050234_5e3ce97a9245e.jpg!small)

2、在`Signing&Capabilities`内设置登录自己的`APPLE ID`

![-w1000](https://image.3001.net/images/20200207/1581050269_5e3ce99d81604.jpg!small)3、将`非越狱`手机连接`mac`，选择需要安装的手机设备，然后按运行。

![-w500](https://image.3001.net/images/20200207/1581050305_5e3ce9c14c00d.jpg!small)4、点击`手机设置`-`通用`-`描述文件与设备管理`，将开发者应用`Apple
Development：your AppleID`设置为`信任`。

![-w210](https://image.3001.net/images/20200207/1581050335_5e3ce9df859de.jpg!small)5、打开`微信`-`设置`-`清水必杀技`即可启用`抢红包`、`防撤回`和修改`微信步数`等功能。

![-w210](https://image.3001.net/images/20200207/1581050367_5e3ce9ff1d295.jpg!small)6、可以使用`ida`来修改字符串达到个人DIY设置

![-w1000](https://image.3001.net/images/20200207/1581050440_5e3cea48e456b.jpg!small)

## 八、总结

通过学习和实践发现`MonkeyDev`不但可以在非越狱的手机上进行逆向分析，还能自动完成各种准备工作，并且能联动`Xcode`自身的调试功能。1、源码及DYLIB下载地址：链接:<https://pan.baidu.com/s/1pohumAKmfxt72bBJMBOUNQ>
密码:zhte2、猴神的私有`CocoaPods`仓库 <https://github.com/AloneMonkey/MonkeyDevSpecs>
有一些网友上传的插件，也可以学习和使用。

## 九、参考链接

> <https://github.com/AloneMonkey/MonkeyDev/wiki/>
>
> <https://juejin.im/post/5da82cf1e51d4524e207fc39#heading-14>
>
> <https://mp.weixin.qq.com/s/XArk877Av3RvYhrwfhzKsA>
>
> <https://juejin.im/post/5e1aa4d951882520a167d8ee#heading-3>
>
> <https://qiita.com/shimizukawasaki/items/d8d01e30a8f67da68ea1>
>
> <https://github.com/zhengmin1989/MyArticles>

 ***本文原创作者：tales，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

