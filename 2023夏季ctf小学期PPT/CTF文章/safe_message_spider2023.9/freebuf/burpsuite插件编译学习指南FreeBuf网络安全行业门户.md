原创 AgeloVito 合天智汇

简介：本文讲解如何编译github上相关burp插件作者开发的基于maven构建的java项目，让初学者也能自己动手编译自己需要的burp插件，以及更方便的阅读和学习开发者的代码。

一、为什么要自己搭建burp extender编译环境 1、Bapp Store中提供的插件 和 相应github 作者发布版本不对应，更新速度慢
2、从Bapp Store安装插件的方式 burp会把插件保存以下目录

C:\Users\administrator \AppData\Roaming\BurpSuite\bapps

我相信很多windows用户都不喜欢C盘空间被强奸的感觉

示例如图所示：

![v2-9beeac17a750101c66a06aecc6d2fb4b_hd.j](https://pic4.zhimg.com/80/v2-9beeac17a750101c66a06aecc6d2fb4b_hd.jpg)

![v2-56ec2a3acfaf4943a2e5e6f88ceba68e_hd.j](https://pic3.zhimg.com/80/v2-56ec2a3acfaf4943a2e5e6f88ceba68e_hd.jpg)

![v2-37da08283c585cbf210bfa43934bff97_hd.j](https://pic1.zhimg.com/80/v2-37da08283c585cbf210bfa43934bff97_hd.jpg)

3、有时需要修改插件的某些bug或者完善插件某些功能，异或学习插件开发。

二、环境准备 1、准备jdk1.8.0_231

<https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html>

2、准备jdk1.7.0_80

<https://www.oracle.com/technetwork/java/javase/downloads/java-archive-downloads-javase7-521261.html>

>
> Tips：2.1、jdk1.7.0_80是jdk1.7系列最终版本，jdk1.8.0_231是jdk1.8系列迄今的最终版本2.2、为什么要准备两个版本的jdk为了兼容性，避免不必要的麻烦，有些coder喜欢jdk1.7，有些喜欢jdk1.8，以及maven
> tomcat等各种java生态圈的东西你用起来的时候也需要考虑兼容性。  
>

3、设置java环境变量

![v2-dd748ee135ad6a39701af90a69af2dfd_hd.j](https://pic3.zhimg.com/80/v2-dd748ee135ad6a39701af90a69af2dfd_hd.jpg)

![v2-07f9143b76ba263117675ea162963f80_hd.j](https://pic4.zhimg.com/80/v2-07f9143b76ba263117675ea162963f80_hd.jpg)

![v2-0d52ba0f289d43c93acb2acb104e1af3_hd.j](https://pic1.zhimg.com/80/v2-0d52ba0f289d43c93acb2acb104e1af3_hd.jpg)

4、搭建eclipse开发环境Eclipse版本：Eclipse IDE 2019-06

https://www.eclipse.org/downloads/download.php?file=/technology/epp/downloads/release/2019-06/R/eclipse-jee-2019-06-R-win32-x86_64.zip建议使用压缩包版本，不用使用installereclipse各版本的区别https://www.eclipse.org/downloads/packages/release

![v2-b6e65d92067a26f4ad6bb6c9cedccd1a_hd.j](https://pic3.zhimg.com/80/v2-b6e65d92067a26f4ad6bb6c9cedccd1a_hd.jpg)

每个版本的具体介绍本文不展开，想了解的同学可以根据上面的链接查看相应版本的名字，然后根据名字搜索就会有相应的介绍文章。总得来说就是对jdk版本的支持程度以及自带的功能插件不同，插件都是可以后期从Eclipse
Marketplace按需扩充的，不建议用最新版本，避免臃肿。

![v2-305b03d9ebaea18882f0971691729b89_hd.j](https://pic4.zhimg.com/80/v2-305b03d9ebaea18882f0971691729b89_hd.jpg)

![v2-b7bbea15ad043dbd49acbdb827789e2a_hd.j](https://pic3.zhimg.com/80/v2-b7bbea15ad043dbd49acbdb827789e2a_hd.jpg)

Tips：为什么要使用eclipse

1、用户习惯使然

2、eclipse很多东西可以自定义，C盘空间不会被强奸

3、免费，不用去破解

在eclipse中配置多版本jdk环境，如图所示：

![v2-1463913411afafdf09914e4a6b564792_hd.j](https://pic2.zhimg.com/80/v2-1463913411afafdf09914e4a6b564792_hd.jpg)

![v2-77b8bd20f087f831f3a605616af2d5e0_hd.j](https://pic1.zhimg.com/80/v2-77b8bd20f087f831f3a605616af2d5e0_hd.jpg)

![v2-67a024544cf7e6faa283ba982b27af89_hd.j](https://pic4.zhimg.com/80/v2-67a024544cf7e6faa283ba982b27af89_hd.jpg)

按照以上步骤将jdk1.7和jdk1.8配置都加入eclipse，当我们使用时就可以在jdk1.7和jdk1.8之间来回切换了。

![v2-3e9aba3acca4d39da2fe2c2f24c7813e_hd.j](https://pic2.zhimg.com/80/v2-3e9aba3acca4d39da2fe2c2f24c7813e_hd.jpg)

5、搭建maven环境

> 5.1
> maven是什么Maven是基于Java平台的自动化构建工具。其中包括：清理、编译、测试、报告、打包、安装、部署，对于我们而言主要用于管理jar包5.2
> 为什么要使用maven最主要的是因为很多burp插件开发者就是用maven来管理jar
> 包，而各种依赖的jar包如果我们要手动去下载并且导入进项目的话很麻烦。5.3
> 下载maven官网下载地址：https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-3/3.6.3/binaries/apache-> maven-3.6.3-bin.zip5.4 配置maven5.4.1 配置如图所示环境变量  
>

![v2-8733e98e9961576883a6e94be1cee259_hd.j](https://pic2.zhimg.com/80/v2-8733e98e9961576883a6e94be1cee259_hd.jpg)

![v2-2c5406b31b9b13016c3a030ad2f24ed4_hd.j](https://pic2.zhimg.com/80/v2-2c5406b31b9b13016c3a030ad2f24ed4_hd.jpg)

![v2-69799857fb5abeffd9e701855c782278_hd.j](https://pic4.zhimg.com/80/v2-69799857fb5abeffd9e701855c782278_hd.jpg)

如下图所示，maven环境搭建好了

![v2-36e5ff61134eee3b0b420ebfbff2e7d9_hd.j](https://pic4.zhimg.com/80/v2-36e5ff61134eee3b0b420ebfbff2e7d9_hd.jpg)

> 5.4.2
> maven添加阿里云镜像仓库Tips：为什么要添加阿里中央厂库现在我们大多数java项目都使用maven来管理我们的依赖包，默认情况我们会从国外的maven中心仓库下载依赖，这样就造成下载速度较慢的问题。我们可以通过添加阿里云镜像提高maven下载依赖包的速度修改conf目录下settings.xml文件，增加如下内容:  
>

![v2-9579a0acf4ff9893faf69a6f9ad09743_hd.j](https://pic4.zhimg.com/80/v2-9579a0acf4ff9893faf69a6f9ad09743_hd.jpg)

>
> 5.4.3自定义maven的本地仓库位置Tips：为什么要自定义本地仓库位置（为了C盘空间不被强奸）修改conf目录下settings.xml文件，增加如下内容:  
>

![v2-76f7024f36b05d3e2c161414f2e51d5e_hd.j](https://pic1.zhimg.com/80/v2-76f7024f36b05d3e2c161414f2e51d5e_hd.jpg)

> 5.5 在eclipse中配置maven  
>

![v2-a9f7733629f3deab2feb0fb5a29b345a_hd.j](https://pic3.zhimg.com/80/v2-a9f7733629f3deab2feb0fb5a29b345a_hd.jpg)

三、编译基于maven构建的burpsuite插件项目源码

Tips：以昨晚更新的J2EEScan举例说明，下载地址：

<https://codeload.github.com/ilmila/J2EEScan/zip/v2.0.0beta>

![v2-06dd903b6ec5a17a7fdb0aa4ee980ecd_hd.j](https://pic4.zhimg.com/80/v2-06dd903b6ec5a17a7fdb0aa4ee980ecd_hd.jpg)

按照如图所示步骤操作：

![v2-84a965dbdbb0cd3eea4765f7ffa78289_hd.j](https://pic2.zhimg.com/80/v2-84a965dbdbb0cd3eea4765f7ffa78289_hd.jpg)

![v2-303a7c4df7304babeed72dd9bd6b1ba4_hd.j](https://pic4.zhimg.com/80/v2-303a7c4df7304babeed72dd9bd6b1ba4_hd.jpg)

![v2-047d0c82b3999ca06077a34da0be16ec_hd.j](https://pic2.zhimg.com/80/v2-047d0c82b3999ca06077a34da0be16ec_hd.jpg)

![v2-8f706ad9dc98503671a3e9e232e05007_hd.j](https://pic1.zhimg.com/80/v2-8f706ad9dc98503671a3e9e232e05007_hd.jpg)

导入成功后如图所示

![v2-ae05257a2000cfa5f33d80fee8d40a35_hd.j](https://pic3.zhimg.com/80/v2-ae05257a2000cfa5f33d80fee8d40a35_hd.jpg)

如果你windos上的jdk环境配置的是jdk1.8，那么需要修改J2EEScan项目jdk环境为1.8，这是为了保持编译环境和运行环境的一致性，避免坑。因为作者使用的开发环境是jdk1.7，如果你本机也是jdk1.7的运行环境就不用修改了。

![v2-ee12da87b14289a5a8790fe29acdf877_hd.j](https://pic2.zhimg.com/80/v2-ee12da87b14289a5a8790fe29acdf877_hd.jpg)

![v2-f6526b7e49894b54cf7db409d6bb0426_hd.j](https://pic2.zhimg.com/80/v2-f6526b7e49894b54cf7db409d6bb0426_hd.jpg)

![v2-92a563433c247e8b0f88d52968514332_hd.j](https://pic2.zhimg.com/80/v2-92a563433c247e8b0f88d52968514332_hd.jpg)

四、编译基于maven构建的java项目

按照如图所示步骤操作：

![v2-ad89181ed8fb446bf7793fa8e23c4026_hd.j](https://pic3.zhimg.com/80/v2-ad89181ed8fb446bf7793fa8e23c4026_hd.jpg)

![v2-879f9c630535d87d5d393d003cf3ac47_hd.j](https://pic2.zhimg.com/80/v2-879f9c630535d87d5d393d003cf3ac47_hd.jpg)

![v2-2b4a3f96e2f440a16b60c1c39e3baa57_hd.j](https://pic2.zhimg.com/80/v2-2b4a3f96e2f440a16b60c1c39e3baa57_hd.jpg)

最后：此文为科普文，如果大家喜欢我这种结构的文章，我将继续输出。也可以使用mvn自带的命令编译项目，或者使用intellij idea，看个人取舍而已。

> 个人愚见：什么是好的技术类文章，判断标准：它回答了以下7个问题。7个问题1、A 是什么2、A 的发展史3、A 解决了什么问题4、A
> 的应用领域5、怎么使用A6、使用时应注意的点7、使用A的思路及其发散  
>

在学习没接触过的知识时，希望大家运用这种方法论，我写文章时也会遵循该模式。

编译jar包下载地址：

<https://pan.baidu.com/s/1e7Ef9FZg439h4nvDcCkyKA>

复制下方链接做实验：

Burpsuite简介：

[实验:Burpsuite简介(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID9d6c0ca797abec2017042513331200001)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关!

  

