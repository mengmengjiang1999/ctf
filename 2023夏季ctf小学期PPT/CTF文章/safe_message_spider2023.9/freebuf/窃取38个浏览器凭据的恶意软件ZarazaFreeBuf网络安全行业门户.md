研究人员发现了一种新的凭据窃取恶意软件，名为 Zaraza。该恶意软件使用 Telegram 作为 C&C 的信道，且 Zaraza 是俄语“感染”的意思。

Zaraza 以大量浏览器为攻击目标，并且在俄语 Telegram 频道中积极宣传。一旦 Zaraza 入侵成功，就会检索失陷主机上的敏感数据并将其通过
Telegram 发送给攻击者。

Zaraza 能够通过 38 个浏览器中窃取用户凭据，包括 Google Chrome、Microsoft Edge、Opera、AVG
Browser、Brave 和 Yandex
等。攻击目标包括网上银行、加密货币钱包、电子邮件与其他高价值网站，攻击者会将窃取的凭据用于身份盗用、金融欺诈以及未授权访问等恶意目的。

## 感染链

Zaraza 会从网络浏览器中提取登录凭据并将其保存在文本文件中。此外，Zaraza 还会以 JPG
格式捕获失陷主机的活动窗口截图。所有被窃数据都会被回传给攻击者，供攻击者选择使用。

![image.png-143.6kB](https://image.3001.net/images/20230424/1682348576_64469a20210649dfb8af1.png!small)Zaraza
感染链

## 技术分析

Zaraza 是使用 C# 开发的 64 位二进制文件，并且在代码中包含许多俄语。攻击者还将程序的入口点设置为 NULL，很难在调试时停在断点。

![image.png-405.2kB](https://image.3001.net/images/20230424/1682348577_64469a2100d9a4915de38.png!small)Zaraza
样本文件

执行后 Zaraza 会获取失陷主机的用户名，并在 Temp 目录中使用该名称创建子文件夹。

![image.png-65.3kB](https://image.3001.net/images/20230424/1682348578_64469a221244b0cdf76cb.png!small)文件创建代码

接下来，样本会在子文件夹中创建名为 output.txt 文件。

    
    
    C:\Users\<用户名>\AppData\Local\Temp\<PC名>\<用户名>\output.txt

Zaraza 会逐一扫描如下 38 个浏览器，提取所有相关的凭据。

![image.png-59.8kB](https://image.3001.net/images/20230424/1682348578_64469a22b359632a1cd36.png!small)浏览器列表

如下为样本中各个浏览器的用户数据文件夹路径：

![image.png-593.7kB](https://image.3001.net/images/20230424/1682348579_64469a239195e9f7bbe0c.png!small)浏览器用户数据文件夹路径

浏览器使用的 SQLite 数据库中包含各种网站的登录信息，字段如下所示：

  * origin_url：网站的主要链接
  * action_url：站点的登录链接
  * username_element：网站上的用户名字段
  * username_value：用于登录的用户名
  * password_element：网站上的密码字段
  * password_value：用于登录的加密密码
  * date_created：数据存储日期
  * times_used：密码被使用的次数
  * blacklisted_by_user：如果永远不应存储密码，则设置为 1

攻击者主要获取 origin_url、username_value 与 password_value。由于密码以加密方式存储，两种不同的加密方法如下所示：

  * 较新版本的浏览器使用 v80 加密算法。首先利用主密钥加密存储用户的 Web 登录密钥，再使用 Windows DPAPI CryptProtectData 进行二次加密。为了识别加密密钥，在字符串的开头插入 DPAPI 再使用 base64 对加密密钥进行编码，保存在用户数据文件夹中。
  * 较旧版本的浏览器使用 Windows DPAPI CryptProtectData 进行加密，加密后的密码存储在数据文件中。

![image.png-54.2kB](https://image.3001.net/images/20230424/1682348580_64469a24c6232dc265c37.png!small)找回密码

从浏览器中成功提取加密密钥后，攻击者将此数据保存到 output.txt 文件中。

使用 CopyFromScreen() 获取失陷主机的屏幕截图，并将其保存到与 output.txt 相同的文件位置 Screen.jpg。

    
    
    C:\Users\<用户名>\AppData\Local\Temp\<PC名>\<用户名>\Screen.jpg

攻击者通过 Telegram 频道来传递窃取数据：

![image.png-437.1kB](https://image.3001.net/images/20230424/1682348581_64469a2575ce3ad761d4c.png!small)Telegram
通信

## 网络分析

样本文件回传数据至俄语 Telegram 私人频道，如下所示：

![image.png-129.5kB](https://image.3001.net/images/20230424/1682348582_64469a26c5dc35a5b3acc.png!small)信道详细信息

## Zaraza 样本文件

Zaraza 似乎是商业化的，攻击者在对外销售失陷主机的访问权限。分析 Telegram 频道的过程中，发现样本文件可用选项如下所示：

  * Restart (if keyboard is missing)
  * Help and support
  * Change a language/LANGUAGE
  * Pay by Subscription
  * Create a post
  * Edit post
  * Content plan
  * Reports and statistics
  * Settings
  * Creatives
  * Get a personalized sticker pack

如下为研究人员试图在频道中配置选项，但访问被拒绝。

![image.png-220.5kB](https://image.3001.net/images/20230424/1682348583_64469a27902794e8a8d7a.png!small)Telegram
样本文件

通过分析 HTTPS 流量，发现 Zaraza 回传了包含俄语用户名和账户信息的数据。攻击目标或者攻击者本身，一定与俄语存在某种关联。

![image.png-315.2kB](https://image.3001.net/images/20230424/1682348584_64469a28e4d0dfdf28228.png!small)HTTPS
流量

## Yara

    
    
    {meta:malware_name = "Zarazabot"description = "Zarazabot is a credential stealer that is capable of stealing login credentials from web browsers."author = "Uptycs Inc"version = "1"strings:$string_1 = "\\Ya Passman Data" ascii wide$string_2 = "\\Google\\Chrome\\User Data" ascii wide$string_3 = "Microsoft\\Edge\\User Data" ascii wide$string_4 = "BraveSoftware\\Brave-Browser\\User Data" ascii wide$string_5 = "encrypted_key" ascii wide$string_6 = "FromBase64String" ascii wide$string_7 = "<UploadToTelegram>" ascii wide$string_8 = "DownloadString" ascii wide$string_9 = "CopyFromScreen" ascii wide$string_10 = "\\output.txt" ascii wide$string_11 = "Passwords.txt" ascii wide$string_12 = "\\Screen.jpg" ascii widecondition:all of them}

## IOC

> 41D5FDA21CF991734793DF190FF078BA  
> https[:]//t[.]me/zarazaA_bot  
> 149.154.167[.]220

## 参考来源

> [Uptycs](https://www.uptycs.com/blog/zaraza-bot-credential-password-stealer)

