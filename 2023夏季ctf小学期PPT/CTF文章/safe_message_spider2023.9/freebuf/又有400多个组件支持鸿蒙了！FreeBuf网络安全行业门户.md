HarmonyOS目前提供了16000多个API，而在API之外HarmonyOS还提供一系列 ** **组件库****
供开发者使用，这些库明显降低了应用开发者的开发难度，从而提升开发效率，让应用开发更简单高效。

HarmonyOS组件库在OpenHarmony开源社区上可以直接获取，华为也还在不断扩增当中。如此好用的HarmonyOS组件库到底是什么？我们可以从以下五个方面来理解。

##  **一、HarmonyOS组件库介绍**

2021年，HarmonyOS将陆续推出1000+组件，包含UI、动画图形、框架、安全、工具、网络、文件数据、多媒体、图片缓存和基础功能，共10类（具体类别可参见下图），具有多设备形态可用、多端部署、性能优化三大特点。

![](https://image.3001.net/images/20210427/1619505193_6087b0297f24e194689a8.png!small)

##  **二、HarmonyOS组件Project目录结构**

HarmonyOS组件的项目工程目录结构与Java工程类似，分为build编译目录、libs依赖库目录、src源码目录和构建脚本，结构清晰易懂。

![](https://image.3001.net/images/20210427/1619505208_6087b038d18864a0a1fbe.png!small)

开发者可以通过HarmonyOS的IDE工具DevEco Studio直接使用组件来进行项目开发，只需打开指定模板，相关目录结构就会自动导入到工程文件中。

  * DevEco Studio下载链接： _https://developer.harmonyos.com/cn/develop/deveco-studio#download_

![](https://image.3001.net/images/20210427/1619505228_6087b04cdd269046f2de7.png!small)

##  **三** **、组件的引用方式**

### 常用组件的引用方式有以下三种：

 **1.Har包引用(build.gradle)**

二进制目录的引用简单直接，开发者只需把组件库都放进libs目录即可。做原型时非常方便，是初学者或者测试时常用的方式。

dependencies {

implementation project(":mylibrary")

}

 **2.源文件引用(build.gradle)**

开发者对使用的组件有优化需求的时候，可以进行源文件引用，把源码下载下来后同步修改。优化之后，还可以把源码贡献到开源仓中。

dependencies {

implementation fileTree(dir: 'libs', include: ['*.jar', '*.har'])

}

 **3.Maven仓引用(build.gradle)**

Maven仓引用适合大规模团队开发或者商业应用开发，开发者直接在中央仓下载即可。

步骤一：

    
    
    allprojects{
    
    repositories {
    
    maven {
    
    url ‘file://D:/01.localMaven/’  //本地或远程Maven仓
    
    }
    
    }
    
    }

步骤二：

    
    
    dependencies {
    
    implementation 'com.huawei.har:mylibrary:1.0.1'
    
    }

##  **四、组件库如何获取**

开发者通过OpenHarmony Gitee开源地址下载源码，或在HarmonyOS官网组件库文档当中，即可获取相关组件。

 **1.组件库源码获取路径**

  * Gitee开源链接：[ _https://gitee.com/openharmony-tpc_](https://gitee.com/openharmony-tpc)

![](https://image.3001.net/images/20210427/1619505256_6087b0685836d516bc37f.png!small)

 **2.组件库文档获取路径**

HarmonyOS组件库统一管理平台，可以方便快捷地查询文档。

  * 链接地址：[ _https://hpm.harmonyos.com/hapm/_](https://hpm.harmonyos.com/hapm/)

![](https://image.3001.net/images/20210427/1619505271_6087b077d1dbf11a83b2d.png!small)

##  **五** **、部分组件Demo效果展示**

 **1.BezierMaker：简单的贝塞尔曲线绘制方法**

  * 源码下载地址：[ _https://gitee.com/openharmony-tpc/BezierMaker_](https://gitee.com/openharmony-tpc/BezierMaker)

![](https://image.3001.net/images/20210427/1619505285_6087b08590637efe825cf.gif!small)

![](https://image.3001.net/images/20210427/1619505301_6087b095f05a2d83dd9cb.gif!small)

 **2.Cardslib：卡片式布局库**

  * 源码下载地址：[ _https://gitee.com/openharmony-tpc/cardslib_](https://gitee.com/openharmony-tpc/cardslib)

![](https://image.3001.net/images/20210427/1619505454_6087b12e132ecb7e8fbbd.gif!small)![](https://image.3001.net/images/20210427/1619505504_6087b1608926c94b9db93.gif!small)

 **3.confetti模仿雪花飘落的动画**

  * 源码下载地址：[ _https://gitee.com/openharmony-tpc/confetti_](https://gitee.com/openharmony-tpc/confetti)

![](https://image.3001.net/images/20210427/1619505520_6087b170295745297c752.gif!small)

![](https://image.3001.net/images/20210427/1619505536_6087b180dcfbea85afb75.gif!small)

 **4.FileDownloader：文件下载库**

  * 源码下载地址：[ _https://gitee.com/openharmony-tpc/FileDownloader_](https://gitee.com/openharmony-tpc/FileDownloader)

![](https://image.3001.net/images/20210427/1619505594_6087b1bac01a160b99221.gif!small)

通过以上的介绍和描述，相信各位对HarmonyOS组件库如何使用应该有了一些基础的概念与认知。HarmonyOS组件库可以帮助开发者更加高效地开发应用，与此同时，它的良性发展也需要开发者们在使用时不断反馈、补充和完善。HarmonyOS生态的壮大繁荣，需要更多开发者的力量加入。

