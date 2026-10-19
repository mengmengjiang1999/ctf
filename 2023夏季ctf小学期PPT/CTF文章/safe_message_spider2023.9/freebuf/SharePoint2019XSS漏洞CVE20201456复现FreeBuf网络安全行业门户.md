![](https://image.3001.net/images/20210121/1611244007_6009a1e77ebddc1f364a5.png!small)

## 写在前面的话

在这篇文章中，我们将分析SharePoint 2019中的一个安全漏洞。虽然这个漏洞不是一个典型的JavaScript
XSS，但微软还是把这个漏洞定性为了XSS漏洞。

内部部署的SharePoint
2019服务器支持实现的用户配置选项将允许经过身份验证的用户上传图片，而用户配置文件中上传的图像路径可以在保存对话框请求中进行更改。在这里，我们就可以向其中插入任意链接，这将允许我们攻击任何访问嵌入了用户个人资料图片页面的用户。由于SharePoint中用户个人资料图片的出现率很高，因此可能会导致多种攻击场景出现，比如说DoS、用户跟踪和攻击中继等等。目前，该漏洞被归类为了跨站脚本漏洞（XSS），分配的漏洞编号为[
_CVE-2020-1456_](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1456)。

## 环境配置

### Windows Server

> [ _Windows Server 2019 Evaluation_](https://www.microsoft.com/en-> us/evalcenter/evaluate-windows-server-2019)
>
> 版本: 1809
>
> OS build: 17763.379
>
> Windows更新：09/09/2019 12:13PM
>
> 添加活动目录域服务

### SQL Server

> 安装[ _MS SQL Server 2017 Evaluation Edition_](https://www.microsoft.com/en-> us/evalcenter/evaluate-sql-server-2017-rtm)
>
> 安装类型: 基础安装
>
> 安装器版本: 14.1805.40.72.1
>
> 数据库版本: 14.0.1000.169
>
> 安装Microsoft SQL Server Management Studio Release 18.2

### SharePoint 2019

> [ _SharePoint Server 2019 (_ _安装版本_
> _16.0.10337.12109)_](https://www.microsoft.com/de-de/evalcenter/evaluate-> sharepoint-server-2019)
>
> 使用Passmark OSFMount (v3.0.1005.0)将IMG文件存储为ISO
>
> 以Single-Server模式安装SharePoint
>
> 添加User Profile Service应用程序

## 漏洞评级

> 漏洞类别：没有对用户提供的输入数据进行正确有效的过滤。
>
> CVSS 2：评分6.5（中危）
>
> CVSS 3.1：评分6.5（中危）

## 漏洞复现详细说明

在测试SharePoint应用程序的过程中，我还部分测试了SharePoint本身。在启用了用户配置文件的SharePoint设置中，每个用户都可以上传用户个人图片。上传图片后，可以在用户配置文件中查看，然后最终接受图片并永久保存更改，包括所有其他条目。

![](https://image.3001.net/images/20210121/1611244029_6009a1fd0f4868b154b54.png!small)

保存所有更改之后，SharePoint会执行一个POST请求，并给用户显示更改情况：

    
    
    http://192.168.0.151/_layouts/15/EditProfile.aspx?UserSettingsProvider=234bf0ed-70db-4158-a332-4dfd683b4148&ReturnUrl=http%3a%2f%2f192.168.0.151%2fPerson.aspx%3faccountname%3d%3C span%20style=%22background-color:%20#fcbd00%22%3Epoint%3C/span%3E%255C%3Cspan%20style=%22background-color:%20#fcbd00%22%3Eshareuser%3C/span%3E&changephoto=1

![](https://image.3001.net/images/20210121/1611244038_6009a206842ded355fc3e.png!small)

该请求还会包含下列参数：

    
    
    ctl00$PlaceHolderMain$ProfileEditorEditPictureURL

该参数会存储上传的用户资料图片的路径，并对URL进行编码：

![](https://image.3001.net/images/20210121/1611244047_6009a20fd8740fb9092cd.png!small)

URL编码的参数和值如下所示：

    
    
    ctl00%24PlaceHolderMain%24ProfileEditorEditPictureURL=http%3A%2F %2F192.168.0.151%3A80%2FUser%2520Photos%2FProfilbilder%2Fpoint_shareuser_Mthumb.jpg

明文参数和值如下：

    
    
    ctl00$PlaceHolderMain$ProfileEditorEditPictureURL= http://192.168.0.151:80/User%20Photos/Profilbilder/point_shareuser_Mthumb.jpg

我们可以拦截这个POST请求，然后将参数值修改为“http://123.itsec.de/random.png”。因为服务器接受了用户提供的输入，我们就可以在本地存储的图片中嵌入自定义的URL。

修改后的参数值如下：

    
    
    ctl00$PlaceHolderMain$ProfileEditorEditPictureURL=http://123.itsec.de/random.png

插入的URL已经嵌入其中，此时，这个链接提供的是一个大小为1GB的“图片文件”。我们可以看到，浏览器会请求我们的“图片文件”。

![](https://image.3001.net/images/20210121/1611244064_6009a220eb21531b8997a.png!small)

通过分析HTML中-img标签的src参数，我们可以直接在网页的源代码中识别嵌入的链接。

![](https://image.3001.net/images/20210121/1611244071_6009a227c4d8e25292a93.png!small)

## 总结

每当用户访问了这些嵌入了链接的包含用户图像的用户个人配置页面时，浏览器都会在后台打开嵌入的链接。这将允许攻击者跟踪目标用户，并在网络中产生大量的流量，或诱使目标设备执行攻击者所想要的攻击。

## 参考资料

> [ _https://portal.msrc.microsoft.com/en-US/security-> guidance/advisory/CVE-2020-1456_](https://portal.msrc.microsoft.com/en-> US/security-guidance/advisory/CVE-2020-1456)
>
> [ _https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2020-1456_](https://cve.mitre.org/cgi-> bin/cvename.cgi?name=CVE-2020-1456)
>
> [ _https://it-sec.de/ger/Aktuelles-Termine/it.sec-blog/it.sec-Research-Team-> findet-unbekannte-Schwachstelle-in-Microsoft-Office-SharePoint_](https://it-> sec.de/ger/Aktuelles-Termine/it.sec-blog/it.sec-Research-Team-findet-> unbekannte-Schwachstelle-in-Microsoft-Office-SharePoint)

