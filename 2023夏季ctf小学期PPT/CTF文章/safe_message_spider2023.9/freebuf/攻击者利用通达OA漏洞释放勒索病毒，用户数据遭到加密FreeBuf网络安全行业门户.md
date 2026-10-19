**近日，通达OA官方论坛发布了一则安全更新，披露了近期出现攻击者利用通达OA文件上传和文件包含漏洞释放勒索病毒的攻击事件，攻击者通过漏洞上传webshell伪装OA插件的下载提示页面，诱导用户点击下载运行勒索病毒，官方紧急发布了各版本的安全加固补丁。**

![](https://image.3001.net/images/20200319/1584600492_5e7315ac73bdf.png!small)

从官方发布的补丁分析，通达OA V11以下版本仅存在未授权任意文件上传漏洞；通达OA
V11版本则存在未授权任意文件上传以及任意文件包含两个漏洞，攻击者可在通达OA V11版本利用两个漏洞构造组合利用链，最终在目标服务器上执行任意代码。

## 漏洞复现

搭建通达OA V11版本漏洞环境，通过构造文件上传绕过，实现PHP文件成功上传到目标服务器。效果如下图：

![](https://image.3001.net/images/20200319/1584600614_5e73162626828.png!small)

通过文件包含漏洞，构造攻击数据，成功访问到目标服务器的nginx服务器日志。效果如下图：

![](https://image.3001.net/images/20200319/1584600621_5e73162db2e9c.png!small)

通过组合利用两个漏洞，最终实现代码执行操作：

![](https://image.3001.net/images/20200319/1584600636_5e73163c5a005.png!small)

![](https://image.3001.net/images/20200319/1584600647_5e731647d82f6.png!small)

## 事件分析

据深信服安全团队分析，此次利用漏洞进行攻击的是一款GO语言编写的勒索病毒，使用RSA+AES算法加密，暂时没有公开的解密工具。勒索病毒进行加密后会在每个目录下释放勒索信息文件readme_readme_readme.txt，向用户勒索0.3比特币，具体内容如下：

![](https://image.3001.net/images/20200319/1584600792_5e7316d83259c.png!small)

并且加密后会并没有修改特定的后缀，而是在原有的文件后缀的最后加上一个“1”：

![](https://image.3001.net/images/20200319/1584600803_5e7316e3d3413.png!small)

### 恶意文件详细分析

该勒索病毒使用GO语言编写，没有加壳或去符号化，功能较为简单，从main中可以看到大致的执行流程：

![](https://image.3001.net/images/20200319/1584600828_5e7316fce2dbb.png!small)

进行加密的文件类型包括：

>
> ".doc,.docx,.xls,.xlsx,.ppt,.pptx,.pst,.ost,.msg,.eml,.vsd,.vsdx,.txt,.log,.csv,.rtf,.123,.wks,.wk1,.pdf,.dwg,.onetoc2,.snt,.jpeg,.jpg,.docb,.docm,.dot,.dotm,.dotx,.xlsm,.xlsb,.xlw,.xlt,.xlm,.xlc,.xltx,.xltm,.pptm,.pot,.pps,.ppsm,.ppsx,.ppam,.potx,.potm,.edb,.hwp,.602,.sxi,.sti,.sldx,.sldm,.vdi,.vmdk,.vmx,.gpg,.aes,.ARC,.PAQ,.bz2,.tbk,.bak,.tar,.tgz,.gz,.7z,.rar,.zip,.backup,.iso,.vcd,.bmp,.png,.gif,.raw,.cgm,.tif,.tiff,.nef,.psd,.ai,.svg,.djvu,.m4u,.m3u,.mid,.wma,.flv,.3g2,.mkv,.3gp,.mp4,.mov,.avi,.asf,.mpeg,.vob,.mpg,.wmv,.fla,.swf,.wav,.mp3,.sh,.class,.jar,.java,.rb,.asp,.php,.jsp,.brd,.sch,.dch,.dip,.pl,.py,.vb,.vbs,.ps1,.bat,.cmd,.js,.asm,.h,.pas,.cpp,.c,.cs,.suo,.sln,.ldf,.mdf,.ibd,.myi,.myd,.frm,.odb,.dbf,.db,.mdb,.accdb,.sql,.sqlitedb,.sqlite3,.asc,.lay6,.lay,.mml,.sxm,.otg,.odg,.uop,.std,.sxd,.otp,.odp,.wb2,.slk,.dif,.stc,.sxc,.ots,.ods,.3dm,.max,.3ds,.uot,.stw,.sxw,.ott,.odt,.pem,.p12,.csr,.crt,.key,.pfx,.der"

执行cmd命令停止mysql，解除文件占用：

![](https://image.3001.net/images/20200319/1584600846_5e73170ec5c12.png!small)

使用base64解码RSA加密随机生成的AES算法的公钥，并用公钥加密AES秘钥：

![](https://image.3001.net/images/20200319/1584600858_5e73171a8a4d2.png!small)

将加密后的秘钥拼接到勒索信息中，随后遍历目录释放勒索信息文件：

![](https://image.3001.net/images/20200319/1584600864_5e731720491ec.png!small)

使用AES算法加密文件：

![](https://image.3001.net/images/20200319/1584600894_5e73173ec899b.png!small)

### 补丁分析

在通达OA所发布的补丁包中，共修复了通达OA
2003版、2013增强版、2015版、2016版、2017版和V11版。所有版本均修复了ispirit/im/upload.php文件，下图所示即为upload.php修复前后的代码（左边为修复前代码，右边为修复后的代码）：

![](https://image.3001.net/images/20200319/1584600913_5e731751d5a4b.png!small)

从修复的地方看出，通过取消‘include_once
"./auth.php";’的else判定条件，将之前的选择性验证改变为强制验证，使得用户在上传文件前都要执行认auth.php验证操作，确定是否为登录状态。

在修复前的upload.php文件的代码中，如果url参数中包含了P参数，就可以绕过此验证操作。通过构造带有参数P的请求包，即可直接进行文件上传。

在通达OA
V11版本中，官方还额外修复了ispirit/interface/gateway.php文件，下图所示即为gateway.php修复前后的代码（左边为修复前代码，右边为修复后的代码）：

![](https://image.3001.net/images/20200319/1584600927_5e73175fd29c8.png!small)

从上述代码中，可以看到该接口未包含auth.php文件进行认证，所以该操作不需要登录认证，且在文件最后，执行了文件包含操作“include_once
$url;”而且执行该语句的条件也很简单，即为路径中存在general、ispirit、module其中一个路径即可。且$url为外部可控参数，$url参数来源于url的json参数。从这里可以看出，攻击者可以通过构造请求，实现任意文件包含。

从以上的补丁分析可以看出，在通达OA V11以下各版本均存在未授权任意文件上传漏洞；而在通达OA
V11版本中，存在未授权任意文件上传以及任意文件包含漏洞。攻击者可以在通达OA V11版本中，通过两个漏洞的组合利用，完成远程代码执行操作。

## 影响范围

目前受影响的通达OA版本：

### 1.任意文件上传漏洞影响：

> 通达OA V11
>
> 通达OA 2017
>
> 通达OA 2016
>
> 通达OA 2015
>
> 通达OA 2013增强版
>
> 通达OA 2013

### 2.任意文件包含漏洞影响：

> 通达OA V11

## 修复建议

还未出现勒索现象的通达OA用户尽可能的将服务器断开互联网，并立即备份数据，且做好异地备份，如出现上文提到的下载OA插件提示页面请一定不要点击下载，并尽快通过下列官方链接下载通达OA官方公布的补丁程序进行防护：

> <http://tongda2000.com/news/673.php?spm=a2c4g.11174386.n2.3.3d3d1051dif5d9>

## 参考链接

> <http://www.tongda2000.com/news/673.php>

***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

