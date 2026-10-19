作者：[金刚@TSRC](https://security.tencent.com/index.php/blog/msg/122?from=timeline&isappinstalled=0
"金刚@TSRC")

#### 一 漏洞概述

Apktool是Android开发人员常用的工具，可用于反编译、重打包Apk。

近日，国外安全人员披露了早期版本的Apktool存在的两个漏洞细节，一个是XXE漏洞，可造成对用户电脑/系统任意文件的访问；另一个是路径穿越漏洞，可释放、覆盖用户电脑/系统文件、代码执行等危害。

#### 二 漏洞实例

###### 1\. XML外部实体 (XXE) 漏洞

原理：Apktool在解析AndroidManifest.xml文件时，不会禁用外部实体引用，导致存在XML外部实体注入攻击(XXE)漏洞。

利用方式：恶意攻击者通过构造Android应用中的恶意XML文件，用户使用Apktool对该应用进行重打包时，触发XXE漏洞，导致对用户电脑上文件的访问。

以下是利用过程：

先构造恶意AndroidManifest.xml，在其中插入一段访问远程服务器的代码，如下所示：

![](https://images.seebug.org/content/images/2017/12/20b36827-11d0-48fb-a54c-31f0ba9bacb7.png-w331s)

当用户使用Apktool对这个目录进行重打包生成Apk时，从远程服务器日志可以看出，用户电脑已经静默访问该网站。

![](https://images.seebug.org/content/images/2017/12/4000c9ba-5bf5-43b1-a949-f2abf1f17edb.png-w331s)
![](https://images.seebug.org/content/images/2017/12/b938a5bd-61c4-41e3-ab97-30ec2b2b5f04.png-w331s)

研究人员也提供了读取/etc/目录下的文件并将内容回传给远程服务器的PoC代码，如下图所示：
![](https://images.seebug.org/content/images/2017/12/67127ef9-903f-40bc-9b45-deb2f52b0d3d.png-w331s)

关于XXE漏洞攻击和防护手段，可以访问TSRC的[这篇博客](https://security.tencent.com/index.php/blog/msg/69
"这篇博客")了解详情。

###### 2\. 路径穿越漏洞

原理：Apktool在解析apktool.yml文件中的unknownFiles字段时，没有对”../“字符串进行过滤，导路径穿越漏洞。

利用方式：恶意攻击者通过构造恶意apktool.yml文件，在unknownFiles字段中使用包含”
../“的路径，用户使用Apktool对该应用进行反编译时，造成释放、替换用户电脑对应路径下文件，甚至可造成代码执行的危害。

以下是利用过程：

先看一个正常apk反编译后的apktool.yml文件，

![](https://images.seebug.org/content/images/2017/12/7c7a7d1c-e546-424c-8e9e-fc4ee71a4a98.png-w331s)

接着我们对其中的unknownFiles字段进行修改，添加一个能在apktool解压时穿越到apache服务器路径下的变量，如下图所示，

![](https://images.seebug.org/content/images/2017/12/7b66cc1d-f9e4-4d43-b4ae-7eeeae245337.png-w331s)

然后使用apktool对这个修改后的文件夹进行重打包，生成的apk效果如下：

![](https://images.seebug.org/content/images/2017/12/dd73b1f4-59e9-4f7e-9581-774b9f15b919.png-w331s)

当用户下载这个apk，使用apktool对其进行反编译时，
shell.php文件会被释放到/var/www/html路径下，同理，也可以替换用户其他路径下的文件。

![](https://images.seebug.org/content/images/2017/12/46134b19-697d-4eb7-b21c-4bba3101555a.png-w331s)
![](https://images.seebug.org/content/images/2017/12/de53843e-4a4e-45bd-a41b-809cca733209.png-w331s)

#### 三 修复建议

Apktool在`1.5.2-2.2.4`之间的版本受上述漏洞影响，Apktool作者已经在新版本修复漏洞，建议升级至最新版。

Apktool下载链接： <https://bitbucket.org/iBotPeaches/apktool/downloads>

#### 四 结语

这个漏洞向我们展示了一个新的新攻击面，通过对常用开发者工具的漏洞利用，达到窃取用户/公司/系统敏感文件、代码执行的目的。建议大家不仅要对系统进行日常更新，也要关注常用软件的更新。

#### 五 参考文章

  * [ParseDroid: Targeting The Android Development & Research Community](https://research.checkpoint.com/parsedroid-targeting-android-development-research-community/ "ParseDroid: Targeting The Android Development & Research Community")
  * [Apktool v2.2.4 Released](https://connortumbleson.com/2017/07/29/apktool-v2-2-4-released/ "Apktool v2.2.4 Released")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/475/>

