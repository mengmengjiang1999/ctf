![](https://image.3001.net/images/20220507/1651929298_627670d2a8eac399c5724.png!small)

## 关于IOSSecuritySuite

IOSSecuritySuite是一款针对iOS平台的安全防篡改保护工具，该工具功能强大且易于使用，基于纯Swift开发。如果你正在开发iOS应用程序，并且想根据OWASP
MASVS标准来保护你的iOS应用程序安全，那么IOSSecuritySuite绝对会成为你的得力助手。

## 功能介绍

> 1、检测系统是否越狱（支持iOS 11+）;
>
> 2、检测是否附带调试器；
>
> 3、判断应用程序是否在模拟器中运行；
>
> 4、检测设备中运行的常见逆向工程工具；

## 工具安装

首先，广大研究人员需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/securing/IOSSecuritySuite.git

我们提供了四种方法来帮助广大研究人员运行和使用IOSSecuritySuite。

 **1、添加源代码**

直接将“IOSSecuritySuite/*.swift”文件添加到你的项目中。

 **2、使用CocoaPods配置**

    
    
    pod 'IOSSecuritySuite'

 **3、使用Carthage配置**

    
    
    github "securing/IOSSecuritySuite"

 **4、使用Swift包管理工具配置**

    
    
    .package(url: "https://github.com/securing/IOSSecuritySuite.git", from: "1.5.0")

## 更新Info.plist

将IOSSecuritySuite添加到你的项目中之后，我们还需要更新主Info.plist文件。其中包含了越狱检测模式的检测代码，该功能使用了“canOpenURL(_:)”方法，并且需要指定查询的URL地址：

    
    
    <key>LSApplicationQueriesSchemes</key>
    
    <array>
    
        <string>cydia</string>
    
        <string>undecimus</string>
    
        <string>sileo</string>
    
        <string>zbra</string>
    
        <string>filza</string>
    
        <string>activator</string>
    
    </array>

## 工具使用

### 越狱检测模块

下列方法将判断设备是否越狱，并返回True或False值：

    
    
    if IOSSecuritySuite.amIJailbroken() {
    
    print("This device is jailbroken")
    
    } else {
    
    print("This device is not jailbroken")
    
    }

Verbose模式：

    
    
    let jailbreakStatus = IOSSecuritySuite.amIJailbrokenWithFailMessage()
    
    if jailbreakStatus.jailbroken {
    
    print("This device is jailbroken")
    
    print("Because: \(jailbreakStatus.failMessage)")
    
    } else {
    
    print("This device is not jailbroken")
    
    }

其中的“failMessage”是一个字符串，包含了由逗号分隔的指示符：

> Cydia URL scheme detected, Suspicious file exists:
> /Library/MobileSubstrate/MobileSubstrate.dylib, Fork was able to create a
> new process

Verbose & 数据过滤：

    
    
    let jailbreakStatus = IOSSecuritySuite.amIJailbrokenWithFailedChecks()
    
    if jailbreakStatus.jailbroken {
    
       if (jailbreakStatus.failedChecks.contains { $0.check == .existenceOfSuspiciousFiles }) && (jailbreakStatus.failedChecks.contains { $0.check == .suspiciousFilesCanBeOpened }) {
    
             print("This is real jailbroken device")
    
       }
    
    }

### 调试器检测模块

    
    
    let amIDebugged: Bool = IOSSecuritySuite.amIDebugged()

### 禁用调试器

    
    
    IOSSecuritySuite.denyDebugger()

### 模拟器检测模块

    
    
    let runInEmulator: Bool = IOSSecuritySuite.amIRunInEmulator()

### 逆向工程工具检测模块

    
    
    let amIReverseEngineered: Bool = IOSSecuritySuite.amIReverseEngineered()

### 系统代理检测模块

    
    
    let amIProxied: Bool = IOSSecuritySuite.amIProxied()

### 运行时钩子检测模块

    
    
    let amIRuntimeHooked: Bool = amIRuntimeHook(dyldWhiteList: dylds, detectionClass: SomeClass.self, selector: #selector(SomeClass.someFunction), isClassMethod: false)

### 禁用符号钩子模块

    
    
    denySymbolHook("$s10Foundation5NSLogyySS_s7CVarArg_pdtF")   // denying hooking for the NSLog function
    
    NSLog("Hello Symbol Hook")
    
         
    
    denySymbolHook("abort")
    
    abort()

### MSHook检测模块

    
    
    // Function declaration
    
    func someFunction(takes: Int) -> Bool {
    
    return false
    
    }
    
     
    
    // Defining FunctionType : @convention(thin) indicates a “thin” function reference, which uses the Swift calling convention with no special “self” or “context” parameters.
    
    typealias FunctionType = @convention(thin) (Int) -> (Bool)
    
     
    
    // Getting pointer address of function we want to verify
    
    func getSwiftFunctionAddr(_ function: @escaping FunctionType) -> UnsafeMutableRawPointer {
    
    return unsafeBitCast(function, to: UnsafeMutableRawPointer.self)
    
    }
    
     
    
    let funcAddr = getSwiftFunctionAddr(someFunction)
    
    let amIMSHooked = IOSSecuritySuite.amIMSHooked(funcAddr)

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-2-Clause_](https://github.com/securing/IOSSecuritySuite/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **IOSSecuritySuite：** 【[
_GitHub传送门_](https://github.com/securing/IOSSecuritySuite)】

## 参考资料

> [ _https://github.com/OWASP/owasp-masvs_](https://github.com/OWASP/owasp-> masvs)
>
> [ _https://www.securing.biz/_](https://www.securing.biz/)
>
> [
> _https://developer.apple.com/documentation/uikit/uiapplication/1622952-canopenurl_](https://developer.apple.com/documentation/uikit/uiapplication/1622952-canopenurl)
>
> [ _https://www.securing.biz/en/mobile-application-security-best-> practices/index.html_](https://www.securing.biz/en/mobile-application-> security-best-practices/index.html)
>
> [
> _https://github.com/rockbruno/swiftshield_](https://github.com/rockbruno/swiftshield)
>
> [ _https://github.com/TheSwiftyCoder/JailBreak-> Detection_](https://github.com/TheSwiftyCoder/JailBreak-Detection)
>
> [
> _https://github.com/abhinashjain/jailbreakdetection_](https://github.com/abhinashjain/jailbreakdetection)
>
> [
> _https://gist.github.com/ddrccw/8412847_](https://gist.github.com/ddrccw/8412847)

