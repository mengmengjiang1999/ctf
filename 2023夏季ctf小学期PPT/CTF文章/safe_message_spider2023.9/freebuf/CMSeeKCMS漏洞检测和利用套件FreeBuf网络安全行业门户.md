**![68747470733a2f2f692e696d6775722e636f6d2f6e3255366e56482e706e67.png](https://image.3001.net/images/20180704/15306593566542.png!small)**

**CMSeeK是一个CMS的漏洞检测和利用套件。**

 **已发布版本**

    
    
    - Version 1.0.1 [19-06-2018]
    - Version 1.0.0 [15-06-2018]

[Changelog文件](https://github.com/Tuhinshubhra/CMSeeK/blob/master/CHANGELOG)

## 特性

  * 支持20多种CMS的基本CMS检测
  * 高级Wordpress扫描 
    * 版本检测
    * 用户检测（3种检测方法）
    * 查找版本漏洞等！
  * 模块化爆破系统   

    * 你可以根据需求选择自带爆破模块或自己创建模块并与之集成

## **安装要求及兼容性：**

CMSeeK是由 **python3** 编写的，因此你需要安装 **python3**
的运行环境。此外，CMSeeK当前仅支持基于unix的系统，对于Windows系统的支持在后续会陆续添加。CMSeeK依赖git进行自动更新，因此请确保你已安装了git。

## 安装使用

CMSeeK的安装使用非常简单，你只需确保你安装了python3和git（仅用于克隆repo）并使用以下命令：

    
    
    git clone https://github.com/Tuhinshubhra/CMSeeK
    cd CMSeeK
    python3 cmseek.py

## 检查更新

你可以从主菜单中检查更新，或使用python3 cmseek.py --update命令检查更新及应用自动更新。

P.S：请确保你已安装了git，CMSeeK将使用git来进行自动更新。

## 检测方法

CMSeek检测主要通过以下两项：

> HTTP头
>
> 网页源代码

## 支持的CMS

CMSeeK目前支持检测的CMS有22个，你可以在cmseekdb目录中的cmss.py文件中找到该列表。所有cms的存储格式如下：

    
    
    cmsID = {
       'name':'Name Of CMS',
       'url':'Official URL of the CMS',
       'vd':'Version Detection (0 for no, 1 for yes)',
       'deeps':'Deep Scan (0 for no 1 for yes)'
     }

## 扫描结果

所有扫描结果都被存储在名为cms.json的json文件中，你可以在Result\<Target
Site>目录中找到日志，爆破结果同样也被存储在站点结果目录下的txt文件中。

以下是json报告日志的示例：

![68747470733a2f2f692e696d6775722e636f6d2f356441396a51672e706e67.png](https://image.3001.net/images/20180704/15306594745984.png!small)

## 爆破模块

CMSeek具有模块化的bruteforce系统，这意味着你可以添加定制的bruteforce模块与cmseek配合使用。不久后我们将会撰写一个模块创建的说明文档，但是如果你已经知道如何创建，那你需要的做的是：

>   1. 添加注释 # <Name Of The CMS> Bruteforce module。这将帮助CMSeeK知道CMS所使用正则表达式的名称
>   2. 添加注释 ### cmseekbruteforcemodule，让CMSeeK知道这是一个模块
>   3. 将模块复制并粘贴到CMSeeK目录下的brutecms目录中
>   4. 使在第一个菜单中使用U作为输入，打开CMSeeK并重建Cache
>   5. 如果一切正常，你将看到截图所示内容，下次打开CMSeeK时，你的模块将在bruteforce菜单中列出。
>

![68747470733a2f2f692e696d6775722e636f6d2f3242726c37706c2e706e67.png](https://image.3001.net/images/20180704/15306593897067.png!small)

## 相关截图

![68747470733a2f2f692e696d6775722e636f6d2f77714f4f7778302e706e67.png](https://image.3001.net/images/20180704/15306594118778.png!small)

![68747470733a2f2f692e696d6775722e636f6d2f4338534b5131442e706e67.png](https://image.3001.net/images/20180704/15306594351994.png!small)![68747470733a2f2f692e696d6775722e636f6d2f367857553757312e706e67.png](https://image.3001.net/images/20180704/15306594457433.png!small)

 **免责声明：** 在使用CMSeeK进行渗透测试时，请先取得授权，并遵守当地的法律法规。作者对本程序造成的任何误用或损害概不负责。

 ** *参考来源：[GitHub](https://github.com/Tuhinshubhra/CMSeeK)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

