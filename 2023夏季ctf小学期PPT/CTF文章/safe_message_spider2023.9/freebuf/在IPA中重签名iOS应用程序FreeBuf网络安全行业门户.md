![](https://image.3001.net/images/20200215/1581747990_5e478f1618c31.jpg!small)

**当我们在对iOS应用程序执行黑盒安全测试时，我们一般只能从AppStore来访问和获取iOS应用程序。但是在大多数情况下，客户都会给我们提供一个IPA文件。在黑盒测试过程中，我们无法访问目标应用的源代码，因此通过Xcode将其部署到设备并进行测试，几乎是不可能的。但是有一种可行的解决方案，即使用我们手头上的配置文件来重新启动应用程序，并将其部署到我们的测试设备上。**

在这篇文章中，我们将演示如何重新对一个iOS应用程序签名，并生成一个IPA文件，然后将其部署到我们的测试设备上。

##  代码签名

代码签名作为一种安全保护措施，苹果要求所有在其设备上运行的代码都必须由他们信任的开发人员进行数字签名，而数字（代码）签名的签名的工作方式与SSL证书在网站上的工作方式类似。

###  苹果-iOS应用程序唯一有效的签发商

> 苹果的代码签名支持站点：【[传送门](https://developer.apple.com/support/code-signing/)】
>
>
> iOS代码签名指南：【[传送门](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Introduction/Introduction.html)】

##  从IPA中提取应用程序Bundle

首先，我们手上需要有一个.ipa文件。你可以选择使用[frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump)或其他工具，这个看你个人喜欢，但最终我们得有一个可以使用得IPA文件。我们这里选择使用的是[OWASP iGoat-Swift](https://github.com/owasp/igoat-swift)。你可以直接点击【[这里](https://github.com/OWASP/iGoat-Swift/blob/master/iGoat-Swift_v1.0.ipa)】下载iGoat-Swift_v1.0.ipa，并完成IPA文件的“提取”。

接下来，我们使用[ios-deploy](https://github.com/ios-control/ios-deploy)来将应用程序加载到我们的测试设备上。但你如果现在尝试侧加载IPA文件的话，可能会失败，因为此时提供的配置文件不会将我们的设备作为App运行的有效设备，因此我们才需要对目标App进行重签名。

我们可以把IPA文件当作ZIP文件来进行解压，不用去在意文件的扩展名，因为我们可以直接修改扩展名。

    
    
    $ mv iGoat-Swift_v1.0.ipa iGoat-Swift_v1.0.zip
    
        $ unzip iGoat-Swift_v1.0.zip -d iGoat-Swift
    
        # this should create a directory iGoat-Swift with Payload inside

这里，我们需要弄清楚这个IPA文件需要哪些权限，因此我们需要先提取出这部分内容。

##  提取授权内容

安装在一台苹果设备上的每一个应用程序都需要一个配置描述文件，这些配置文件需要在苹果的开发者门户网站上创建。我们假设已经有了这样一个文件了，那我们就要用我们的配置文件来替换掉当前IPA中的配置文件，但是现在我们需要查看当前的配置文件，并了解配置文件的要求，以此来创建我们的配置文件。

首先，我们需要从embedded.mobileprovision中提取出一个plist，我们的工作目录为iGoat-Swift目录：

> iGoat-Swift
>
> └── Payload
>
> └── iGoat-Swift.app

然后再从应用程序Bundle中获取到embedded.mobileprovision：

    
    
    $ cd iGoat-Swift
    
        $ security cms -D -i Payload/iGoat-Swift.app/embedded.mobileprovision > provision.plist

我们可以用常用的文本编辑器打开plist文件，或者直接使用PlistBuddy来将plist中的所有授权域提取出来：

    
    
    $ /usr/libexec/PlistBuddy -x -c 'Print :Entitlements' provision.plist | tee entitlements.plist
    
        $ /usr/libexec/PlistBuddy -x -c 'Print :Entitlements' provision.plist > entitlements.plist
    
        $ cat entitlements.plist

接下来，我们将看到下列信息：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "<http://www.apple.com/DTDs/PropertyList-1.0.dtd>">
    
        <plist version="1.0">
    
        <dict>
    
                <key>application-identifier</key>
    
                <string>6J6AZQ7T23.*</string>
    
                <key>com.apple.developer.team-identifier</key>
    
                <string>6J6AZQ7T23</string>
    
                <key>get-task-allow</key>
    
                <true/>
    
                <key>keychain-access-groups</key>
    
                <array>
    
                        <string>6J6AZQ7T23.*</string>
    
                </array>
    
        </dict>
    
        </plist>

此时，我们已经知道了需要创建的授权内容了，其中：

> get-task-allow：允许我们以调试模式运行App，当我们从Xcode中运行App时将会添加授权。
>
> keychain-access-groups：允许我们App组之间共享钥匙链对象。

当我们在Xcode中为keychain-access-groups选择授予的权限时，application-identifier和com.apple.developer.team-identifier将会自动生成。

##  创建一个“空白”的应用程序

现在，创建一个空的Xcode项目，这个App的授权应该跟我们需要重签名的App的授权内容相同。重签名后的结果就是，我们将得到两个功能相同但签名不同的应用程序。

经过刚才的分析，我们已经知道了iGoat-Swift需要“keychain-access-groups”这个权限，然后需要在项目信息中的授权部分搜索并添加该权限。

接下来，构建并运行我们的空项目，在测试设备上运行了该App之后，你将会拿到一个包含了测试设备ID的有效配置描述文件。

现在，我们就可以将这个空的App从测试设备上删除了，我们只需要用Xcode来创建正确的配置描述文件，然后用它来对iGoat-Swift App进行重签名。

##  获取正确的配置文件

在Xcode的文件导航栏中，选择“Product”，点击目标App。然后检查Xcode
Inspector区域（在Xocde界面的右侧面板），找到应用程序Bundle的路径。

在应用程序Bundle中，我们将会看到“embedded.mobileprovision”，然后把配置描述文件拷贝到当前的工作目录中：

    
    
    $ cp PATH_YOU_GOT_FROM_XCODE/embedded.mobileprovision new_embedded.mobileprovision

我们可以根据这个配置描述文件来获取到目标App所需的权限：

    
    
    $ security cms -D -i new_embedded.mobileprovision > new_provision.plist
    
        $ /usr/libexec/PlistBuddy -x -c 'Print :Entitlements' new_provision.plist | tee new_entitlements.plist

现在，我们可以移除之前的代码签名了：

    
    
    $ rm -r Payload/iGoat-Swift.app/_CodeSignature

接下来，使用下列命令来访问我们的配置描述文件（在钥匙链Keychain中）：

    
    
    $ security find-identity -v -p codesigning

在获取到所需信息之后，我们就可以对应用程序进行重签名了：

    
    
    $ codesign -f -s "Your Provisioning Profile (AAAAAA)" --entitlements new_entitlements.plist Payload/iGoat-Swift.app/
    
        $ codesign -f -s "Your Provisioning Profile (AAAAA)" --entitlements new_entitlements.plist Payload/iGoat-Swift.app/Frameworks/*
    
        $ codesign -f -s "Your Provisioning Profile (AAAA)" --entitlements new_entitlements.plist Payload/iGoat-Swift.app/iGoat-Swift

现在，我们使用重签名的应用程序Bundle来生成一个新的IPA文件了：

    
    
    $ zip -qr iGoat-Swift_v1.0.ipa  Payload/

接下来，使用ios-deploy来将新生成的iOS应用程序部署到我们的测试设备上：

    
    
    $ ios-deploy -b iGoat-Swift_v1.0.ipa

##  参考资料

> 1、<https://developer.apple.com/support/code-signing/>
>
>
> 2、<https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Introduction/Introduction.html>
>
> 3、<https://github.com/owasp/igoat-swift>
>
> 4、<https://github.com/OWASP/owasp-mstg>

 *** 参考来源：[rderik](https://rderik.com/blog/resigning-ios-apps-from-an-ipa-for-mobile-security-research/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

