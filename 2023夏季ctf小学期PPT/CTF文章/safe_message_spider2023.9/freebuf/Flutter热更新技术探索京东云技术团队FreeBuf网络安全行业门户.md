## **一，需求背景：**

APP 发布到市场后，难免会遇到严重的 BUG 阻碍用户使用，因此有在不发布新版本 APP 的情况下使用热更新技术立即修复 BUG 需求。原生
APP（例如：Android & IOS）的热更新需求已经比较成熟，但 Flutter 技术栈目前还缺少类似的技术方案，因此 Flutter
研发团队，也需要类似的热更新技术。

##  **二，Flutter 热更新技术方向分析：**

经过分析目前可能有三种可行的方案： 1）类似 RN 框架； 2）页面动态组件框架； 3）Dart 虚拟机定制方案；

方案名称| 原理| 优点| 缺点| 开源方案  
---|---|---|---|---  
类似 RN 的方案| 用 JS 以 Flutter 语法写 dart，然后用 JavaScript 把 XML DSL 转为 Flutter 的原子
widget 组件，然后再让 Flutter 来渲染| 由于 ios 系统内置支持 js，ios 上完全可以实现更新| 1)
由于跨语言执行，对于性能有影响；学习成本高 2) Android 端需要额外引入 JS 库| 手 Q 的 MXFlutter，58 同城的 Fair  
页面动态组件方案| 编译期时插桩 / 预埋好 DynamicWidget 到代码中，然后动态下发 Json 数据，通过协定好的语义匹配到 JSON
内的数据，动态替换 Widget 内容来实现更新| 能支持 Android/iOS 两端的更新| 1）UI 更新相对较容易，业务逻辑动态化较麻烦；
2）语义解析器开发成本相对较大，且不易维护 3）需要一整套前后端服务和工具| 天猫的 Tangram，淘宝的 DinamicX 等  
Dart 虚拟机定制方案| 通过分析 Dart 虚拟机的原理，修改 Flutter Engine 层 Java/C++ 代码实现热更新的目标；|
性能影响小，动态性很高，技术上可以替换所有 Flutter 页面（包括 UI，逻辑，资源文件）| 由于使用的是定制引擎，需要维护不同版本的 Flutter
引擎代码；| 未开源  
  
 **因为其他方式都有开源的示例，本案将重点以第三种 “Dart 虚拟机定制方案” 为目标，做方案的研究讲解。**

##  **三，预备知识**

 **在开始了解技术方案之前，需要提前了解一些相应的技术概念：**

###  **3.1 Flutter 编译模式**

 **Flutter 开发语言是 Dart，它的编译模式来自 Dart 的编译模式，主要有 JIT (Just In Time) 和 AOT (Ahead
Of Time)。**

编译模式名称| 特点| 优点| 缺点  
---|---|---|---  
JIT| 即时编译，典型例子 V8，它可以即时编译运行 JS，只需要输入源代码字符串，就可以编译运行代码| 可以动态下发和执行代码，不用管 CPU
架构，可以提供动态化内容| 1, 大量字符串代码让 JIT 编译器花费时间和内存； 2, 性能不好；  
AOT| 预先编译，典型例子 C/C++，通过 GCC 编译成二进制代码，然后安装取得权限后才可以加载执行| 事先编译好的，加载和执行速度快| 1,
编译时区分 CPU 架构；2, 生成的二进制代码包比较大；3, 二进制代码需要取得权限才可以执行，无法在 ios 系统上动态更新  
  
 **Flutter 编译模式有：Debug，Release，Profile；**

Flutter 编译模式| 特点  
---|---  
Debug| 对应 JIT 模式，支持设备和模拟器； 打开了断言，支持快速开发，支持 HotReload； 并未对包大小，执行速度做优化；  
Release| 对应 AOT 模式，支持真机，不支持模拟器； 禁止了所有断言调试信息； 对包大小，启动和执行速度进行了优化；  
Profile| 类似 Release 模式，保留了一些调试功能，帮助性能分析；  
  
###  **3.2 Flutter 编译产物分析**

Flutter 下的 iOS/Android 工程本质上是一个标准的 iOS/Android 的工程； **IOS 平台：** Flutter 通过在
BuildPhase 中添加 shell (xcode_backend.sh) 来生成和嵌入 App.framework 和
Flutter.framework 到 ios; **Android 平台：** Flutter 通过 gradle 来添加 flutter.jar
和编译完的二进制文件添加到 Android;

 **3.2.1 引擎层结构分析：**

![1685071701_64702755c22f816ecfcb2.png!small?1685071702586](https://image.3001.net/images/20230526/1685071701_64702755c22f816ecfcb2.png!small?1685071702586)

 **3.2.2 Android 编译产物的分析**

![1685071709_6470275deecaa473b0d23.png!small?1685071710787](https://image.3001.net/images/20230526/1685071709_6470275deecaa473b0d23.png!small?1685071710787)

![1685071718_647027664d7490a5e0f12.png!small?1685071718852](https://image.3001.net/images/20230526/1685071718_647027664d7490a5e0f12.png!small?1685071718852)

 **3.2.3 IOS 编译产物的分析**

![1685071726_6470276e76f5d32de6659.png!small?1685071726983](https://image.3001.net/images/20230526/1685071726_6470276e76f5d32de6659.png!small?1685071726983)

![1685071736_647027786c3844f2de511.png!small?1685071737396](https://image.3001.net/images/20230526/1685071736_647027786c3844f2de511.png!small?1685071737396)

##  **四，热更新技术方案分析**

###  **4.1 业务代码分析**

根据 “3.3.1” ～“3.3.2” 的分析可以确定无论是 IOS 还是 Android APP
业务代码都是由四个段组成：kDartVmSnapshotData、kDartVmSnapshotInstructions、kDartIsolateSnapshotData、kDartIsolateSnapshotInstructions；
**理论上只要能动态替换加载的代码段 & 数据段代码即可实现目标。**

名称| 注释| 作用| 注释  
---|---|---|---  
kDartIsolateSnapshotData| Dart isolate 数据段| 类信息，全局变量，函数指针等| 允许动态下发  
kDartIsolateSnapshotInstructions| Dart isolate 指令段| 包含由 Dart isolate 执行的 AOT
代码| IOS 不允许动态下发  
kDartVmSnapshotData| vm isolate 数据段| isolate 之间共享的 Dart 堆 (heap) 的初始状态| 允许动态下发  
kDartVmSnapshotInstructions| vm isolate 指令段| 包含 VM 中所有 Dart isolate 之间共享的通用程序的
AOT 指令| IOS 不允许动态下发  
  
注释： isolate, snapshot, vm isolate 含义解释如下：

名称| 含义  
---|---  
isolate| Dart 是单线程，isolate 跟线程差不多，可以理解为 Dart 中的线程。 isolate
与线程的区别：线程与线程之间是共享内存的，而 isolate 和 isolate 之间是内存不共享的。 不存在锁竞争问题，两个 Isolate
完全是两条独立的执行线，且每个 Isolate 都有自己的事件循环，它们之间只能通过发送消息通信，所以它的资源开销低于线程。  
snapshot| 将类信息、全局变量、函数指令直接以序列化的方式存在磁盘中，称为 Snapshot（快照）。  
vm isolate| 同一个进程里可以有很多 isolate，但两个 isolate 的堆区是不能共享的，所以官方设计了 VM isolate，也就是
kDartVmSnapshot，用来多个 isolate 之间的交互。  
  
![1685071772_6470279c9c1dd772eae43.png!small?1685071773404](https://image.3001.net/images/20230526/1685071772_6470279c9c1dd772eae43.png!small?1685071773404)

###  **4.2 业务代码的加载分析（运行时）**

按照 4.1 的分析思路，我们首先需要了解 Flutter 运行时代码加载的完整流程，经过梳理分析流程如下：

 **1 ）Android- APP 业务代码的加载流程：**

![1685071781_647027a50575be47dc8e9.png!small?1685071781683](https://image.3001.net/images/20230526/1685071781_647027a50575be47dc8e9.png!small?1685071781683)

 **2）IOS- APP 业务代码的加载流程：**

![1685071791_647027af27ee24ef3ba66.png!small?1685071791907](https://image.3001.net/images/20230526/1685071791_647027af27ee24ef3ba66.png!small?1685071791907)

###  **4.3 业务代码的编译生成（编译时）**

根据以上的分析，我们知道了 Flutter
业务代码的数据结构，也知道了在运行时如何加载，因此我们只需要在编译时做更改，产生自己需要的代码段，和数据段文件。在运行时加载自己的构建产物即可达到目标。

 **1）在此以 IOS 构建自己的业务代码流程做详细分析：**

![1685071804_647027bc6c9922f3983fe.png!small?1685071805230](https://image.3001.net/images/20230526/1685071804_647027bc6c9922f3983fe.png!small?1685071805230)

有完成构建流程可以分析，基本流程是 “Dart Code（业务代码）” -> (通过 Dart 编译器 gen_snapshot.cc) 生成
snapshot_assemble.S 的汇编文件 -> (通过 xcrun 工具) 生成 snapshot_assemble.o 的 obj 文件 ->
(通过 xcun clang 工具链) 生成了 App.Framework。

 **2）Android 的产物构建流程和 IOS 类似。由于 Android 有其他更简单的方案， 因此省略详细的构建流程分析，大致如下：**

![1685071813_647027c5ccc3525404ca1.png!small?1685071814510](https://image.3001.net/images/20230526/1685071813_647027c5ccc3525404ca1.png!small?1685071814510)

###  **4.4 实现热更新的方案探索**

根据上面的技术分析结果，已经可以独立生成自己的代码段，数据段文件。通过需改虚拟机底层代码的方式，也可以动态的加载运行。但由于 IOS
系统目前底层的系统还不能动态加载可读写的代码段数据到内存中，所以还有技术难点需要突破。但 Android 端有更简单的路径可以解决，因此下面以
Android 端为例重点分析思路，大致如下图所示：

![1685071823_647027cf4fe0c5108dfe1.png!small?1685071823833](https://image.3001.net/images/20230526/1685071823_647027cf4fe0c5108dfe1.png!small?1685071823833)

由上图可以得知，Android 端 热修复核心步骤如下：

1， 修改 Flutter Engine 代码，加载指定路径的 libapp.so 和 flutter_aasets，比如私有目录
(data/data/files)；

2， 编译 APK 时，利用 Gradle Transform 插件，根据 Flutter SDK 的 engine version 动态替换官方的
Flutter engine，最终写入修改后的 engine 到 APK；

3， 生成补丁包：利用 BSdiff 算法比较新旧 APK 文件，生成 patch 补丁包

4， APP 启动时访问后端接口，根据参数（app 的版本号，补丁包版本号，md5，flutter SDK 版本号，Engine 版本号）拉取补丁包；

5， 合成补丁包：校验 md5，app 版本号，补丁版本号，安装时间；

6， 自定义 Flutter Engine 加载指定路径的 libapp.so 和 flutter_assets 资源文件；

  

> 作者：京东科技 刘振中、周智
>
> 内容来源：京东云开发者社区

