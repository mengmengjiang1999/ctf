***本文原创作者：xiaoguazh，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 一、前言

 **此文的主要目的是回顾多年前破解JUDE Pro(以及用友财务)软件的一些经历，总结怎样更好的保护应用软件的License。**

首先在此由衷表达自己对JUDE 开发团队的尊敬，非常感谢开发出这么精简,强大,实用的软件！  

JUDE (Java & UML Development Environment)
是日本一个团队开发的Java应用软件，整合了UML建模，代码生成，反向工程，数据库ER建模，脑图，流程图，非常小巧(~30Mb)，界面特别友好，使用方便，非常适合日常开发人员的UML建模，脑图分析等等。JUDE原网址：<http://jude.change-vision.com>

ASTAH是JUDE的继任者，它提供更加丰富的功能，感兴趣的朋友，推荐一试，<http://astah.net>  

特注：

(1) JUDE Pro在2009年已经终止，并且被新产品取代，此贴中涉及到部分反编译的JUDE代码，不再构成侵权；

(2) 之前破解的JUDE也仅限自己使用，并没有广泛传播，也常自责这样是非常不道德的事情，对ASTAH没有再做破解尝试。

## 二、破解JUDE Pro(专业版)

其实所有应用软件的破解的方法都非常类似，比如直接反汇编或者反编译。

本文主要使用Java反编译的方法：反编译->根据关键信息分析和定位License检测代码->修改代码->编译->替换原JAR文件。

### 2.1 需要的工具和环境

JAD, Linux, JDK

### 2.2 分析关键信息提示

(1)分析JUDE Pro的license文件 (JUDE_License_User_Professional.xml)中的关键信息提示：  

![image.png](https://image.3001.net/images/20181209/1544285803_5c0bee6bbfd7d.png!small)

(2)分析界面操作中的关键信息提示

License Selection提示：  

![image.png](https://image.3001.net/images/20181209/1544285842_5c0bee92268d6.png!small)License
File 过期提示：

![image.png](https://image.3001.net/images/20181209/1544285869_5c0beead414e4.png!small)![image.png](https://image.3001.net/images/20181209/1544285878_5c0beeb6df2c1.png!small)

总结关键信息如下：

    
    
    String/prompt from UI
    "License Management", "Set License Key…", "License Information", "No License", "purse a license or set another license key" 
    
    String/text from resources
    "no_product_license', "incorrect_product_license", "choose_license", "no_user_license", "incorrect_user_license"  
    

### 2.3 简单破解尝试

(1)更新系统时间：破解失败，NTP会导致系统时间自动同步，一旦License首次验证失败，就会被标记成永久失效；

(2)直接修改License文件：破解失败，文件的完整性由公私钥机制做Hash校验，任何内容改动都会导致License失效。

### 2.4 反编译

使用JAD在Linux环境下反编译jude-pro.jar代码，搜索关键信息：

    
    
    grep incorrect_user_license *.java
    grep DSA *.java
    grep X509EncodedKeySpec *.java
    grep USER_SIGNATURE *.java
    grep JUDE_License_User_Professional *.java
    grep System.exit\(0\) *.java
    

### 2.5 定位License检查逻辑入口

例如，经过分析最终得出结论iR.class 为License检测的主要逻辑实现，修改代码绕过License检查和判断。

(1)绕过License选择提示(直接return true)

![image.png](https://image.3001.net/images/20181209/1544286293_5c0bf0550f3ca.png!small)

![image.png](https://image.3001.net/images/20181209/1544286331_5c0bf07b2481f.png!small)(2)绕过警告提示(直接return
true)

![image.png](https://image.3001.net/images/20181209/1544286413_5c0bf0cd97b78.png!small)(3)绕过License检查

![image.png](https://image.3001.net/images/20181209/1544286472_5c0bf1089acb5.png!small)![image.png](https://image.3001.net/images/20181209/1544286484_5c0bf114ca3d0.png!small)
![image.png](https://image.3001.net/images/20181209/1544286503_5c0bf127292d2.png!small)![image.png](https://image.3001.net/images/20181209/1544286516_5c0bf1349cf28.png!small)

### 2.6 重新编译iR.java，更新"jude-pro.jar"

    
    
    javac -classpath jude-pro.jar iR.java
    jar uvf jude-pro.jar iR.class
    

### 2.7 测试

启动Jude，成功进入界面，所有专业版菜单和功能全部开启，检查版本信息：

###
![image.png](https://image.3001.net/images/20181209/1544286687_5c0bf1dfa8c88.png!small)

### 2.8 破解总结

代码逻辑并不严谨，事实上有多处License检测的代码都可以被简单绕过：

(1)太多Boolean的检查方法，非常容易被快速定位核心逻辑，并且使用return true直接绕过；

(2)甚至可以构造自己的公钥和私钥来生成License文件的Hash签名，只需替换代码中的公钥字符串即可，自己就可以随意签发License文件。

## 三、应用软件保护的思考

下面是一些关于应用软件保护的一些方法总结：  

分类 | 保护方法 | 备注  
---|---|---  
线索隐藏 | (1)隐藏或者加密关键信息和提示  
(2)核心检测代码加密关键字，避免使用和License文件或者界面提示信息同样的明文，例如：
"incorrect_user_license"，"PRODUCT_KIND"，"USER_KIND" ...  
(3)移除或者尽量减少"不必要"的和License相关的信息和提示 | 减少给破解者提供更多线索  
软件包保护 | (1)采用JAR包签名  
(2)采用例如ProGuard等扰码手段，在编译器对class，成员变量，方法等做扰码，例如："oOooo0O"，"1l11lll1"...  
(3)增加package完整性的检测逻辑，例如size，change time，MD5 ...  
(4)使用自己修改过的/专有的JDK |  
  
License的检查 | (1)避免集中式的一次性的License检查实现，避免使用全局的License标记  
(2)除登录是的License检查之外，考虑在代码里随机的增加检查点(或者我们称之为暗桩)  
(3)避免使用boolean方法和简单If-else逻辑比较来实现License 检测  
(4)开发多套License检查逻辑，随机使用  
(5)避免在代码里直接嵌入公钥或私钥  
(6)一旦License检查失败，应该永久标记此license为失效状态  
(7)采用C/S模式，远程校验 (但也会增加新的复杂度，还有通信安全等问题也需要一并考虑)  
(8)延迟提示错误，一旦发现程序被尝试破解，延迟报错,，比如几小时或者几天后在提示  
(9)使用误导提示把尝试破解的人引向其他方向，增加其破解的难度，例如如果实际需要的密码为10位字符，则提示请输入8位字符的密码...  
(10)分散License检测逻辑到多个不同class，并且使用一些假的校验实现来干扰破解者(混淆视听)  
(11)增大破坏，比如发现被破解或者尝试，执行系统重启，删除本地文件，格式化等等 (不推荐) | 推荐多种方法结合使用  
License文件保护 | (1)强化代码逻辑检查License文件的恶意篡改  
(2)使用二进制的License文件，避免使用纯文本  
(3)使用随机的，动态的算法 |  
  
  
|  
|  
  
  
## 四、结束语

从应用软件的角度，也许确实没有办法来防止软件被最终破解，因为一旦软件发布，所有的防卫方法也就都固定了下来，可是攻击和破解的方式却是无穷的，破解只是时间问题。

我们真正能做的，就是尽量增加软件被破解的难度和包括破解的时间成本。当然也包括平衡我们自己要保护的软件本身的价值，来采取合适的保护措施。  

 ***本文原创作者：xiaoguazh，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

