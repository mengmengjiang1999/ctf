## **情报背景**

近期，connectwise发现了一个利用Excel默认密码的攻击事件，在该事件中，攻击者使用了Excel的默认密码加密，借此改进钓鱼和进行防御规避，本文将对相关技术内容进行分析。

 **组织名称**

|

未知  
  
---|---  
  
 **相关工具**

|

Remcos  
  
 **战术标签**

|

防御规避 初始访问  
  
 **技术标签**

|

静态检测规避 钓鱼  
  
 **情报来源**

|

https://www.connectwise.com/resources/formbook-remcos-rat  
  
##  **01** 攻击技术分析

攻击过程如下：

1.发送钓鱼的PDF邮件，在邮件中包含加密和压缩的Excel文档

2.经过解密和解压缩，还原Excel文档

3.诱骗受害者点击并执行宏代码

4.从宏代码中下载文件vbc.exe（实际是Remcos 后门）并执行，释放恶意Periodicity.dll

5.同时，vbc.exe将自身复制到%AppData%\Roaming中,重命名为iys.exe,使用vbs脚本执行上线iys.exe

6.vbc.exe 进行自删除并持久化，完成整个攻击流程

 **亮点：利用excel默认密码改善钓鱼手段和静态检测规避**

在Excel中，可以使用保护功能对Excel加密，达到保证Excel完整性和保密性等作用。

![1661851448_630dd7380d31b33d2cb26.png!small?1661851448886](https://image.3001.net/images/20220830/1661851448_630dd7380d31b33d2cb26.png!small?1661851448886)![1661851457_630dd741d0eed0424a4f5.png!small?1661851458609](https://image.3001.net/images/20220830/1661851457_630dd741d0eed0424a4f5.png!small?1661851458609)

1\. 静态免杀效果

在本次攻击中，攻击者利用Excel的默认密码 VelvetSweatshop 对其进行加密，达到静态免杀的效果。

复现如下：

使用CS中生成的原生macro制作宏样本，某杀软扫描结果如下：

![1661851540_630dd7940dec0243b885a.png!small?1661851540860](https://image.3001.net/images/20220830/1661851540_630dd7940dec0243b885a.png!small?1661851540860)

然后，使用默认密码VelvetSweatshop对其进行加密，再次扫描，没有报毒：

![1661851553_630dd7a130f5ad3232d96.png!small?1661851553963](https://image.3001.net/images/20220830/1661851553_630dd7a130f5ad3232d96.png!small?1661851553963)

  

经过测试，使用Excel 2019时，经过加密后的宏会被禁用，微软在该版本下对其有更多的安全限制，更加安全。

![1661851566_630dd7aeccdc57015d964.png!small?1661851567597](https://image.3001.net/images/20220830/1661851566_630dd7aeccdc57015d964.png!small?1661851567597)

  

具体警告内容如下：

![1661851578_630dd7ba81a2dc639ad4f.png!small?1661851579262](https://image.3001.net/images/20220830/1661851578_630dd7ba81a2dc639ad4f.png!small?1661851579262)

2\. 减少钓鱼诱导操作

在以往的钓鱼Excel中，如果对文档进行加密，需要受害者点开后输入密码。

![1661851617_630dd7e17770e003a29c1.png!small?1661851618268](https://image.3001.net/images/20220830/1661851617_630dd7e17770e003a29c1.png!small?1661851618268)

但使用默认密码时，是不需要输入密码的。Excel会首先尝试使用嵌入的默认密码VelvetSweatshop
来解密和打开文件，如果设置的密码是默认密码，则不会有密码保护的弹窗。

![1661851625_630dd7e9bc33f09568a1b.png!small?1661851626633](https://image.3001.net/images/20220830/1661851625_630dd7e9bc33f09568a1b.png!small?1661851626633)

##  **02 总结**

该攻击手法主要在Remcos后门为主导的恶意软件中使用。对宏的shellcode而言，该加密方式有较好的静态免杀效果，并可以减少钓鱼过程中的步骤，但同时对Excel的版本有一定的要求。

