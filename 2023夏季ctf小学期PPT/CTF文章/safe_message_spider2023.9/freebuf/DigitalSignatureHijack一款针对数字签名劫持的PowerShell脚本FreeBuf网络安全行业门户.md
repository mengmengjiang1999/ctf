![1592996866_5ef33402f004d.jpg!small](https://image.3001.net/images/20200624/1592996866_5ef33402f004d.jpg!small)

## Digital-Signature-Hijack

 **Digital-Signature-Hijack是一款针对数字签名劫持攻击的PowerShell脚本。**

在现代Windows操作系统中，代码签名技术用于帮助用户识别来自不可信源的可信二进制文件。二进制文件通过使用数字证书进行签名，数字证书包含有关发布者，嵌入的私钥和公钥的信息。

该脚本专为安全研究人员设计，开发人员通常会对其代码进行签名，以便向用户保证他们的软件是可信的，而且没有被恶意修改。 这都通过使用数字签名来完成的。
因此，签名代码是一种验证文件的真实性和完整性的方法。

## 功能介绍

> 1、以微软身份对目标主机中所有的可执行文件进行数字签名；
>
> 2、以微软身份对目标主机中所有的PowerShell脚本文件进行数字签名；
>
> 3、验证所有可移植可执行文件的数字签名；
>
> 4、验证所有PowerShell脚本文件的数字签名

Digital-Signature-Hijack通过劫持注册表并添加必要的值，以及利用Matt Graeber开发的自定义SIP
DLL文件来实现其功能。因此，用户需要将MySIP.dll文件的路径修改为对应的本地路径：

> [_MySIP.dll_](https://github.com/netbiosX/Digital-Signature-> Hijack/raw/master/Hijack-Certificates/MySIP.dll)-[
> _https://github.com/mattifestation/PoCSubjectInterfacePackage_](https://github.com/mattifestation/PoCSubjectInterfacePackage)

## 工具下载

广大研究人员可以使用下列命令将该项目文件克隆至本地：

    
    
    git clone https://github.com/netbiosX/Digital-Signature-Hijack.git

## 工具演示

对可执行文件进行签名：

    
    
    SignExe

![1.png](https://image.3001.net/images/20200624/1592996888_5ef3341891cfe.png!small)

验证签名有效性：

    
    
    ValidateSignaturePE

![2.png](https://image.3001.net/images/20200624/1592996898_5ef33422365f3.png!small)

对PowerShell脚本文件进行签名：

    
    
    SignPS

![3.png](https://image.3001.net/images/20200624/1592996909_5ef3342d52ade.png!small)

验证签名有效性：

    
    
    ValidateSignaturePS

![1592996947_5ef33453c110a.png!small](https://image.3001.net/images/20200624/1592996947_5ef33453c110a.png!small)

## 项目地址

> Digital-Signature-Hijack：【[
> _GitHub传送门_](https://github.com/netbiosX/Digital-Signature-Hijack)】

## 参考资料

> 1、[ _https://pentestlab.blog/2017/11/06/hijacking-digital-> signatures/_](https://pentestlab.blog/2017/11/06/hijacking-digital-> signatures/)
>
> 2、[ _http://www.exploit-monday.com/2017/08/application-of-authenticode-> signatures.html_](http://www.exploit-monday.com/2017/08/application-of-> authenticode-signatures.html)
>
> 3、[
> _https://specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf_](https://specterops.io/assets/resources/SpecterOps_Subverting_Trust_in_Windows.pdf)
>
> 4、 _https://www.*******.com/watch?v=wxmxxgL6Nz8_
>
> 5、[ _https://blog.conscioushacker.io/index.php/2017/09/27/borrowing-> microsoft-code-signing-> certificates/_](https://blog.conscioushacker.io/index.php/2017/09/27/borrowing-> microsoft-code-signing-certificates/)

## 参考来源

> [_thelinuxchoice_](https://github.com/thelinuxchoice/evildll)

