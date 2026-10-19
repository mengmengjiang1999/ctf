**![stealing-2fa-tokens.jpg](https://image.3001.net/images/20180831/1535682900_5b88a954e0ffa.jpg!small)**

## **前言**

 **面对日趋严峻的网络安全形式，企业也不断的变换着他们的安全防护方案。越来越多的企业开始对GSuite和OWA等外部服务，推出强制性的2FA验证。**
**这一举措为外部边界创造了更高级别的安全性，但同时也促进了攻击者对捕获2FA令牌技术的不断创新。**

**近些年，网上也出现了许多有关窃取2FA令牌的技术手段。在某些情况下，攻击者会尝试欺骗移动电话上的GSM，或是尝试通过查找禁用双因素的旧门户来绕过2AF。近期，我们还发现了有攻击者通过社工手段在帐户上伪造密码重置来欺骗用户，以窃取发送至他们短信的令牌。**

本文主要讨论如何使用CredSniper来窃取2AF令牌 。

## CredSniper 简介

凭证钓鱼也算是个老生常谈的话题了。为此，大多数企业也开始在正常的入职流程中推出安全意识培训。但据我所知，大多数企业所谓的培训就是例如如何在Email中找到flags这类的问题，而不是灌输真正的网络安全意识。因此，如果我能克隆一个完美且他们熟悉的认证门户再结合一些社工技巧，那么我相信，大多数人都会乖乖的交出他们的凭据和2AF令牌。

### HTTPS是强制性的

如果你要克隆GSuite门户网站，则必须执行此操作，否则Google
Chrome浏览器会向目标提醒该网站为恶意网站。想要解决这个问题也很容易，只需将其切换为HTTPS即可，因为Google并不会拦截访问者和服务器之间的请求和响应payload。在安装过程中，CredSniper将为你的主机从Let’s
Encrypt请求一个新的SSL证书。唯一你要做的就是，将你使用的主机名指向托管克隆门户的服务器IP地址。

### 模块化认证门户

虽然CredSniper附带了用于GSuite的模块，但我们可以以最小的开销来创建新模块。在未来这将更加简化，使用户能够在5-10分钟内完成新门户模块的创建。该模块定义了模板和路由之间的映射。例如，某人访问/登录，则模块将智能识别该认证过程阶段并加载相应的模板。CredSniper希望目标用户首先使用真正的门户进行身份验证，而后当2FA
SMS token被发送给目标用户后，CredSniper就会提示用户输入它。

模板是真正门户网站的HTML副本，但带有必要的模板标签。CredSniper使用的模板语言是Jinja2，它提供了一种使用用户提供的数据个性化网络钓鱼页面的无缝方式。例如，像GSuite这样的一些身份验证门户，它们首先会要求用户提供电子邮件地址，然后将其发送到密码页再发送到2FA页面。在密码页中，GSuite会在其电子邮件地址旁显示用户个人资料。由于CredSniper在网络钓鱼的第一阶段已经捕获了电子邮件地址，因此在后续页面中使用它只需在HTML模板中放置标记（例如{{username}}）即可。在渲染模板时，Jinja2会自动将标记替换为值。此外，我们可以在模块内配置任意数量的路由，以应对身份验证过程中所有不同的情况。

### API集成

CredSniper还附带了轻量级API，因此用户可以将捕获的凭据集成到其他应用程序中。由于2FA令牌时效性较短，因此API提供了一种快速使用凭据来自动执行身份验证任务的方法。在运行CredSniper时，屏幕上将生成一个API令牌，你可以使用该令牌查看凭据、标记凭据以及更新配置。

### 查看凭据（GET）

    
    
    https://<phish site>/creds/view?api_token=<api token>

### 标记凭据（GET）

    
    
    https://<phish site>/creds/seen/<cred_id>?api_token=<api token>

### 更新配置（POST）

    
    
    https://<phish site>/config
    
    {
    
       'enable_2fa': true,
    
       'module': 'gmail',
    
       'api_token': 'some-random-string'
    
    }

### 安装

CredSniper要求你为计划使用的主机名配置DNS。Let's
Encrypt需要能够在颁发SSL证书之前验证主机名，因此需要将主机名分配给托管CredSniper的主机的IP地址。之前有人报告说，安装脚本在Ubuntu
16.04之外的发行版上会抛出错误。虽然该脚本支持在其他Linux版本或发行版上安装运行，但这里我强烈建议大家使用Ubuntu
16.04，避免可因此带来的不必要麻烦。

首先，我们从GitHub repo克隆该项目，这将为我们获取所有必要文件。 克隆完成后，切换目录并运行install.sh脚本。

    
    
    $ git clone https://github.com/ustayready/CredSniper
    $ cd CredSniper
    ~/CredSniper$ ./install.sh

安装过程中，脚本将会向你询问一些基本配置信息。

> **Module to deploy (ex: gmail)：** 将要运行的CredSniper模块。有关列表，请参阅modules/目录。
>
> **Final redirect URL：** 钓鱼后目标浏览器最终重定向到的URL。
>
> **Enable SSL? [Y/n]：** 是否启用SSL进行网络钓鱼。
>
> **Enable two-factor phishing? [Y/n]：** 是否启用双因素钓鱼。
>
> **Enter hostname for certificates (ex: app.example.com)：** Let's
> Encrypt将使用该主机名来检索CredSniper的SSL证书。为了使该主机名能够访问CredSniper，在运行install.sh之前，主机名的DNS必须指向主机名的IP地址。
>
> **Port to listen on (default: 80/443)：**
> 默认情况下，如果CredSniper在HTTP模式下运行，则分配端口为80。如果在HTTPS模式下运行，则分配端口为443。

如果以下尚未安装，则该脚本也会为你安装：

> Let’s Encrypt Apt Repository
>
> Python3
>
> VirtualEnv
>
> GnuPG
>
> CertBot
>
> Python3 模块：Flask, mechanicalsoup, pyopenssl

使用Python3为你创建一个虚拟环境并安装一些必要的Python3模块。紧接着，将会为你启用Python的端口绑定，你将可以从userland侦听端口80/443。最后，SSL证书的证书和私钥将被复制到certs/文件夹中。

安装完成后，将会运行CredSniper！之后想要运行CredSniper，只需简单的键入 python credsniper.py -help 即可。

如果你想退出主机并希望在之后运行CredSniper，请确保你在运行credsniper.py之前已激活了Python虚拟环境：

    
    
    ~/$ cd CredSniper
    ~/CredSniper$ source bin/activate
    (CredSniper) ~/CredSniper$ python credsniper.py –help

## 使用

CredSniper具有较强的使用灵活性，可在多种不同的可配置模式下运行。

    
    
    usage: credsniper.py [-h] --module MODULE [--twofactor] [--port PORT] [--ssl] [--verbose] --final FINAL --hostname HOSTNAME
    
    optional arguments:
    -h, --help                           显示帮助信息并退出
    --module MODULE                      钓鱼模块名称 - 例如, "gmail"
    --twofactor                          启用双因素钓鱼
    --port PORT                          侦听端口 (默认: 80/443)
    --ssl                                通过Let's Encrypt使用SSL
    --verbose                            启用详细输出
    --final FINAL                        钓鱼完成后用户重定向到的最终URL
    --hostname HOSTNAME                  SSL主机名

如果你选择在不使用内置API的情况下监控网络钓鱼凭据，则应该熟悉以下两个文件：

### 临时缓存凭据

.cache：缓存文件主要用于在启用双因素凭据的临时存储，以防止在目标未完成双因素步骤的情况下丢失凭据。

### sniped文件

.sniped：sniped文件提供捕获凭据的平面文件(Flat
File)存储以及双因素信息，IP地址和地理位置等信息。在某些情况下，如果你在一个从未登录的位置进行身份验证，Gmail将可能要求你提供经过身份验证的最后位置信息。通过抓取钓鱼目标的IP地址，并快速对其进行地理定位，可以为你提供准确可靠的答案。

页面克隆

虽然唯一公开的内置模块是Gmail，但modules/目录中还有一个示例模块可帮助你快速创建新模块。为了快速的克隆一个页面，我倾向于使用名为“[Save
Page WE](https://addons.mozilla.org/en-US/firefox/addon/save-page-we/)”的FireFox插件，该插件可以为你在一个HTML页面内嵌入外部资源。这样可以避免加载克隆网站托管的嵌入资源，希望删除CredSniper可能意外发生的任何回调。请务必遵循示例模块HTML模板，以包含正确的模板参数。有关更多内容，你可以关注后续我们关于CredSniper克隆页面的文章，或是观看我们发布在YouTube上的Tradecraft
Security
Weekly视频“[使用CredSniper钓取2FA令牌](https://www.youtube.com/watch?v=TeSt9nEpWTs)”。

对于Gmail等网站，会有多个页面。身份验证过程的生命周期大致如下：

 **用户提供电子邮件地址，Google会验证该帐户**

> 如果无效，则告知用户电子邮件无效；
>
> 如果有效，则继续。

 **Google要求提供用户密码**

> 如果无效，则告知用户密码无效；
>
> 如果有效且2FA未激活，则重定向到GSuite；
>
> 如果有效且2FA已激活，则继续。

 **Google请求2FA令牌**

> 如果是SMS，则使用代码向用户触发文本消息；
>
> 如果是Authenticator，则提示输入OTP代码；
>
> 如果是Yubikey，则提示插入并激活U2F设备；
>
> 如果是触摸提示，则提示用户触摸手机；
>
> 如果user-agent反映未知浏览器，则提示短信；
>
> 如果令牌有效，则重定向到GSuite；
>
> 如果令牌有效但仍存可疑，则提示用户输入其他信息。

CredSniper的处理方式也很简单：

 **提示用户发送电子邮件**

> 使用谷歌的Picaso服务在后台使用电子邮件加载配置文件

 **提示用户输入密码**

> 使用电子邮件和密码在后台进行认证，然后确认是否启用了2FA；
>
> 如果启用了2FA，则捕获其他信息（即SMS的最后几位数字，OTP应用程序名称（Duo/Authenticator/etc），IP地址，地理位置）；
>
> 如果禁用2FA，则重定向到CredSniper中配置的最终目标URL。

 **提示用户输入2FA令牌**

> 重定向到最终目标URL

 **结语**

CredSniper在Black
Hills受到了用户的广泛好评。除了CredSniper，在这里我还想为大家推荐另一款功能强大的工具[Evilginx2](https://github.com/kgretzky/evilginx2)。Evilginx2是一个可绕过双因素验证的高级钓鱼框架，用于远程捕获任何Web服务的凭证和会话cookie。因此，如果CredSniper不是你想要的，那么我强烈建议你尝试使用evilginx2。最后，感谢大家的阅读！

***参考来源：[blackhillsinfosec](https://www.blackhillsinfosec.com/stealing-2fa-tokens-on-red-teams-with-credsniper/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

