![](https://image.3001.net/images/20200813/1597325948.png!small)

## SharpChromium

SharpChromium是一个针对浏览器数据的.NET 4.0
CLR项目，在SharpChromium的帮助下，广大研究人员可以轻松提取浏览器中类似Cookie、浏览历史和存储凭证之类的数据。

值得一提的是，SharpChromium目前支持Google Chrome、Microsoft Edge以及Microsoft Edge
Beta版本浏览器，并且能够提取下列类型的数据：

  * Cookie（JSON格式）；
  * 历史记录，以及跟每一条历史记录相关的Cookie；
  * 存储的用户凭证；

注意：该工具返回的全部Cookie都是以JSON格式呈现的，如果你安装了[ _Cookie
Editor_](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)之类的插件，你还可以直接将这些数据拷贝到浏览器插件中的“Import”视图中并直接提取和查看会话信息。

## 工具优势

跟之前的工具相比，当前版本的SharpChromium有以下几个优势，其中包括：

  * 不需要设计类型编译或反射；
  * Cookie数据以JSON格式显示，便于导入Cookie Editor；
  * 不需要从远程资源下载SQLite程序集；
  * 支持Chromium浏览器，也可扩展至其他浏览器；

## 工具下载

广大研究及人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/djhohnstein/SharpChromium.git

## 工具使用

    
    
    Usage:
    
        .\SharpChromium.exe arg0 [arg1 arg2 ...]
    
     
    
    Arguments:
    
        all       - 获取所有的Chromium Cookie,、历史记录和用户凭证.
    
        full      - 该参数功能跟“all”参数相同
    
        logins    - 获取所有的存储凭证
    
        history   - 获取用户的历史记录，以及相关的Cookie
    
        cookies [domain1.com domain2.com] - 获取用户JSON格式的Cookie，如果传递了域名参数，则会返回根域名相匹配的Cookie。否则，所有的Cookie都将存储在一个临时文件中，格式如下：“%TEMP%\$browser-cookies.json”

## 工具使用样例

### 获取跟Google Docs以及GitHub相关的Cookie：

    
    
    .\SharpChromium.exe cookies docs.google.com github.com

![](https://image.3001.net/images/20200813/1597326008.png!small)

### 获取历史记录条目以及相关的Cookie：

    
    
    .\SharpChromium.exe history

![](https://image.3001.net/images/20200813/1597326002.png!small)

### 获取浏览器中存储的全部用户登录凭证（仅显示非空密码）：

    
    
    .\SharpChromium.exe logins

![](https://image.3001.net/images/20200813/1597325995.png!small)

## 项目地址

SharpChromium：【[ _GitHub传送门_](https://github.com/djhohnstein/SharpChromium)】

