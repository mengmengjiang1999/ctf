Adobe发布了一则安全更新，修复Adobe Flash
Player中的一个严重远程执行代码漏洞（CVE-2020-9746），攻击者可通过诱使受害者访问网站利用该漏洞。

在不知情的用户访问网站时，攻击者只要在HTTP响应中插入恶意字符串就可利用该漏洞。

Adobe在安全公告中表示，“Adobe已经为用于Windows，macOS，Linux和Chrome OS的Adobe Flash
Player发布了安全更新。这些更新修复了Flash
Player中的一个严重漏洞。”成功利用该漏洞，攻击者可导致崩溃，从而在当前用户的上下文中执行任意代码。

要利用CVE-2020-9746，攻击者需要在默认通过TLS/SSL发送的HTTP响应中插入恶意字符串。

远程攻击者可利用该漏洞造成崩溃，从而在访客的设备上执行命令。这些命令会在当前用户的安全上下文中执行，并且不需要管理员权限。

该漏洞影响Adobe Flash Player Desktop Runtime 32.0.0.433及之前版本，Adobe Flash Player for
Google Chrome 32.0.0.433及之前版本，Adobe Flash Player for Microsoft Edge and
Internet Explorer 11 32.0.0.387及之前版本。

厂商已在Adobe Flash Player Desktop Runtime 32.0.0.445版本，Adobe Flash Player for
Google Chrome 32.0.0.445版本和Adobe Flash Player for Microsoft Edge and Internet
Explorer 11 32.0.0.445版本中修复了该漏洞。

值得注意的是，从2020年12月31日起，Adobe将不再为其Flash Player分发或提供更新。

专家认为此举将会降低通过用户的浏览器发动的web攻击。多年来，Flash Player中的多个漏洞遭到了攻击者的利用。

