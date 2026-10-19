![](https://image.3001.net/images/20190914/1568462143_5d7cd53fbe9b8.png!small)

##  Truegaze

**Truegaze是一款专门针对Android和iOS应用程序的静态分析工具，该工具主要针对的是应用程序源代码之外的资源安全问题，例如字符串、第三方库和配置文件等等。广大研究人员可以利用Truegaze来对目标移动端应用程序进行安全检测与分析。**

##  工具要求

该工具的正常运行需要Python 3环境，我们可以直接在requirements.txt文件中找到所有的依赖模块。该工具目前只在Python
3.7环境下进行了测试，但理论上可以在所有的Python 3.x版本上运行，目前该工具还不支持Python 2.x环境。

##  工具安装

我们可以使用下列命令并通过pip来安装Truegaze：

> pip install truegaze
>
> truegaze

大家还可以手动下载并运行Truegaze：

> git clone <https://github.com/nightwatchcybersecurity/truegaze.git>
>
> cd truegaze
>
> pip -r requirements.txt
>
> python -m truegaze.cli

##  工具使用

###  枚举功能模块：

> truegaze list

###  扫描目标应用程序：

> truegaze scan test.apk
>
> truegaze scan test.ipa

###  扫描多个应用程序：

> truegaze scan *.apk
>
> truegaze scan *.ipa

##  工具样本输出

###  功能模块枚举：

![](https://image.3001.net/images/20190914/1568462184_5d7cd568aa5bd.png!small)

###  扫描目标应用程序：

    
    
    user@localhost:~/$ truegaze scan ~/test.ipa
    
        Identified as an iOS application via a manifest located at: Payload/IPAPatch-DummyApp.app/Info.plist
    
        Scanning using the "AdobeMobileSdk" plugin
    
        -- Found 1 configuration file(s)
    
        -- Scanning "Payload/IPAPatch-DummyApp.app/Base.lproj/ADBMobileConfig.json'
    
        ---- FOUND: The ["analytics"]["ssl"] setting is missing or false - SSL is not being used
    
        ---- FOUND: The ["remotes"]["analytics.poi"] URL doesn't use SSL: <http://assets.example.com/c234243g4g4rg.json>
    
        ---- FOUND: The ["remotes"]["messages"] URL doesn't use SSL: <http://assets.example.com/b34343443egerg.json>
    
        ---- FOUND: A "templateurl" in ["messages"]["payload"] doesn't use SSL: <http://my.server.com/?user=>{user.name}&zip={user.zip}&c16={%sdkver%}&c27=cln,{a.PrevSessionLength}
    
        ---- FOUND: A "templateurl" in ["messages"]["payload"] doesn't use SSL: <http://my.43434server.com/?user=>{user.name}&zip={user.zip}&c16={%sdkver%}&c27=cln,{a.PrevSessionLength}
    
        Done!

###  显示已安装的工具版本：

> user@localhost:~/$ truegaze version
>
> Current version: v0.2

##  工具架构

Truegaze是一款命令行工具，该工具由多个能够检测安全漏洞的功能模块组成，其中的每一个模块都可以执行单独的扫描任务，所有的扫描结果都可以直接打印输出在命令行工具中。

##  项目地址

> Truegaze：【[GitHub传送门](https://github.com/nightwatchcybersecurity/truegaze)】

 ***
参考来源：[nightwatchcybersecurity](https://github.com/nightwatchcybersecurity/truegaze)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

