## 一 . 埋头分析踩坑路

从系统的角度去寻找hook点，而不是为了抓包而抓包。

### 1.okhttp调用流程

    
    
    public static final MediaType JSON  
    = MediaType.get("application/json; charset=utf-8");  
    ​  
    OkHttpClient client = new OkHttpClient();  
    ​  
    String post(String url, String json) throws IOException {  
    RequestBody body = RequestBody.create(json, JSON);  
    Request request = new Request.Builder()  
    .url(url)  
    .post(body)  
    .build();  
    try (Response response = client.newCall(request).execute()) {  
    return response.body().string();  
    }  
    }

上面是okhttp官网的一个demo，关键代码就在client.newCall。从此处接口调用开始，终会调用至okhttp框架,
okhttp本是sdk，后来aosp已经集成至系统，所以可以归类至框架层。

框架层不详述，主要就是这几个java类:

    
    
    com.android.okhttp.internal.huc.HttpURLConnectionImpl  
    com.android.okhttp.internal.http.HttpEngine  
    com.android.okhttp.internal.http.RetryableSink  
    com.android.okhttp.internal.http.CacheStrategy$Factory

其实client.newCall终会通过URL获取一个connection

    
    
    HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();

这里的urlConnection其实就是HttpURLConnectionImpl的实例，该类有getInputStream
getOutputStream方法，内部分别会调用HttpEngine的getBufferedRequestBody，getResponse。刚开始我尝试hook过这两个接口，比如hook
getResponse后，可以将response打印出来.

之后我发现Request只能打印header，并不能打印body。所以又埋头继续分析，getBufferedRequestBody这个函数刚好可以入手，获取一个sink，最后以RetryableSink为突破点，比如hook
其write函数就可以将body打印出来。write函数对应于app层面的urlConnection.getOutputStream().write。

后来发现一个Request,调用getBufferedReuqestBody函数可能不止一次，所以会有数据重复的问题，后来我又寻找到了CacheStrategy$Factory.get点进行Hook，发现还是有数据重复。发现以上hook均有弊端

  * 数据重复

  * 非okhttp调用无法抓取

接着又继续从native层的send,sendmsg,write,recv,read打印调用栈。最后折腾了三天，决定放弃治疗，还是采取工具吧。

    
    
    okhttp流程：sdk接口->okhttp框架->native(libc)

### 2.分析过程中frida踩到的坑(重点都在注释中)

  1. android.util.Log不打印
    
        var Logd = function Logd(tag, msg) {  
    Java.use("android.util.Log").d(tag, msg);  
    };  
      
      
    Logd('http-body-', '11111111111111');//该log不打印  
    Logd('http-body', '11111111111111');//该log打印

  2. 匿名内部类获取成员需要反射
    
        var printRequest = function(request) {  
    var Buffer = Java.use("com.android.okhttp.okio.Buffer");  
    var bodyField = request.getClass().getDeclaredField('body');  
    bodyField.setAccessible(true);  
    ​  
    if (request == null) return;  
    Logd('http', 'printRequest: request' + request);  
    //var requestBody = request.body();//gadget直接报错  
    var requestBody = bodyField.get(request);  
    ​  
    var requestBodyClass = requestBody.getClass();  
    var ClassInstanceArray = Java.array('java.lang.Class', []);  
    ​  
    //var contentLengthMethod = requestBodyClass.getMethod("contentLength");//gadget直接报错  
    var contentLengthMethod = requestBodyClass.getMethod("contentLength", ClassInstanceArray);  
      
    contentLengthMethod.setAccessible(true);  
    var ObjectInstanceArray = Java.array('java.lang.Object', []);  
    var contentLength = requestBody ? contentLengthMethod.invoke(requestBody, ObjectInstanceArray) : 0;  
    //if (contentLength == 0) contentLength = contentLen;  
    Logd('http', 'printRequest contentLength: ' + contentLength);  
    if (contentLength > 0) {  
    var BufferObj = Buffer.$new();  
    requestBody.writeTo(BufferObj);  
    Logd(TAG, "\nrequest body :\n" + BufferObj.readString() + "\n");  
    }  
    };

  3. android.os.Bundle打印，需要将Bundle unparcel
    
        var printIntentAndExtras = function printIntentAndExtras(intentObj) {  
    if (intentObj == null) return;  
    var Intent = Java.use("android.content.Intent");  
    var Bundle = Java.use("android.os.Bundle");  
    var bundleObj = Intent.getExtras.call(intentObj);  
      
    if (bundleObj != null) {  
    Bundle.getSize.call(bundleObj, null);//调用getSize即可反序列化  
    }  
      
    Logd(TAG, ‘printIntentAndExtras ’ + bundleObj);  
    };

踩到的坑其实不只上面的，刚开始也百度过一些frida网络拦截的方案，还仔细的研究了okhttp的Interceptor方案，最后发现app也是用了拦截器，所以就发生冲突，导致无法使用该方案。

也纯粹的分析过app的smali，寻找调用栈以及网络请求，最后，只有几个比较小的收获，可能对读者没有用处，不过记录一下，方便自己以后回忆。

  1. java.net.URL拦截
    
        var URLHook = function() {  
    var URL = Java.use('java.net.URL');  
    URL.openConnection.overload().implementation = function() {  
    var retval = this.openConnection();  
    Logd('URL', openConnection' + retval);  
    return retval;  
    };  
    };//URL.openConnection调用概率比较大，但是不一定对网络进行请求

  2. 拦截app调用http请求前使用json的地方，这只是其中之一
    
        var jsonHook = function() {  
    var xx = Java.use('e.h.a.a');//app smali  
    var xxa_method = xx.a.overload('org.json.JSONObject', 'java.lang.String', 'java.lang.String');  
    xxa_method.implementation = function(jsonObj, str1, str2) {  
    Logd("json", jsonObj + " str1: " + str1 + " str2" + str2);  
    xxa_method.call(this, jsonObj, str1, str2);  
    }  
    }

  3. trace http相关class
    
        var traceAllHttpClass = function() {  
    Java.perform(function() {  
    Java.enumerateLoadedClasses({  
    onMatch: function(name, handle) {  
    /*"e.h.a.a$a",起初也拦截过app的该混淆类*/  
    if (name.indexOf("com.android.okhttp.Http") != -1 || name.indexOf("com.android.okhttp.Request") != -1  
    || name.indexOf("com.android.okhttp.internal") != -1) {  
    traceClass(name);//对这三个class进行trace  
    }  
    },  
    onComplete: function() {  
    }  
    });  
    });  
    };

  4. Request$Builder拦截
    
        var BuilderClass = Java.use('com.android.okhttp.Request$Builder')  
    ​  
    BuilderClass.build.implementation = function () {  
    //LOG('com.android.okhttp.HttpUrl$Builder.build overload', { c: Color.Light.Cyan });  
    //printBacktrace();  
    var retval = this.build();  
    Logd(TAG, "retval:" + retval);  
    printRequest(retval);  
    return retval;  
    }

  5. property_get拦截
    
        var nativePropertyGetAddr = Module.findExportByName(null, '__system_property_get');  
    Interceptor.attach(nativePropertyGetAddr, {  
    onEnter: function onEnter(args) {  
    this._name = args[0].readCString();  
    this._value = args[1];  
    },  
    onLeave: function onLeave(retval) {  
    if (this._name.indexOf("ro.build.id") != -1) {  
    var virtualDevice = getVirtualDevice();  
    if (DEBUG_PROP) Logd(TAG, "__system_property_get fake " + this._name + "=>to " + virtualDevice.build_id);  
      
    this._value.writeUtf8String(virtualDevice.build_id);  
    }  
      
    var strFilter = /^ro\./g;  
    if (DEBUG_PROP && this._name.match(strFilter) != null) Logd(TAG, "__system_property_get " + this._name);  
    }  
    });

## 二 . 设备android_id导致用户过期的处理

    
    
    var DEBUG_PROP = false;  
    var DEVICE_CONFIG = "/sdcard/.device";  
    ​  
    function getVirtualDevice() {  
    var nativeOpen = new NativeFunction(Module.findExportByName(‘libc.so’, 'open'), 'int', ['pointer', 'int']);  
    var nativeRead = new NativeFunction(Module.findExportByName('libc.so', 'read'), 'int', ['int', 'pointer', 'int']);  
    var fd = nativeOpen(Memory.allocUtf8String(DEVICE_CONFIG), 0);  
    var mem = Memory.alloc(1024);  
    var readLen = nativeRead(fd, mem, 1024);  
    var json = JSON.parse(mem.readCString(readLen));  
    return json;  
    }  
    ​  
    Secure.getString.implementation = function () {  
    var retval = this.getString(arguments[0], arguments[1]);  
    if (DEBUG_PROP) Logd(TAG, "Settings.Secure get " + arguments[1] + " val " + retval);  
      
    if (arguments[1].indexOf("android_id") != -1) {  
    var virtualDevice = getVirtualDevice();  
    return virtualDevice.android_id;  
    }  
      
    return retval;  
    };

## 三 . 使用抓包工具fiddle抓包脱坑

### 1.fiddle代理设置OK，app却无法登陆

分析adb log,进程有
java.security.cert.CertPathValidatorException的打印，之前也看过一些frida拦截抓包绕过证书的帖子。先试一把暴力搜索：

    
    
    Java.perform(function(){  
    const groups = Java.enumerateMethods('*!verify/u');  
    var classes = null;  
    for(var i in groups){  
    var classes = groups[i]['classes'];  
      
    for(var i in classes){  
    Java.use(classes[i]['name'])  
    .verify  
    .overload('java.lang.String', 'javax.net.ssl.SSLSession')  
    .implementation = function() {  
    printBacktrace();  
    LOG("[+] invoke verify", { c: Color.Red });  
    return true;  
    }  
    }  
    }  
    });

调用verify直接暴力返回true，依然无法登陆，报错是同样的ssl问题。百度搜索后找到了答案。apktool解包，然后修改

    
    
    res/xml/network_security_config.xml  
    <?xml version="1.0" encoding="utf-8"?>  
    <network-security-config>  
    <base-config cleartextTrafficPermitted="true">  
    <trust-anchors>  
    <certificates src="system" />  
    <!--添加fiddle证书可信任  
    <certificates src="user" />  
    -->  
    </trust-anchors>  
    </base-config>  
    </network-security-config>

重打包签名后运行一把，fiddle抓到了包，app也能正常登陆了，这次也是运气好吧，app的ssl校验只有单向app校验，服务器并没有进行校验。

## 四.结束

从周二下午一直折腾到周五，最后从系统层面的HttpEngine寻找hook点并不是很好的方法，弊端也已明了。所以趁着周日的时间，再试一下各种百度到的方法
----抓包工具，然后一步步将遇到的问题pass掉。

下面是抓到的两个包：

    
    
    HTTP/1.1 200 OK  
    Date: Sun, 16 Aug 2020 06:27:34 GMT  
    Content-Type: application/json  
    Content-Length: 101  
    Connection: keep-alive  
    Grpc-Metadata-Content-Type: application/grpc  
    Vary: Origin  
    Vary: Accept-Encoding  
    ​  
    {"result":{"errno":"OK","errmsg":"成功"},"data":{"version":"xxxxxxxx-351e-40cf-aaa9-3177d6df9b7f"}}  
    -----------------------------------  
    HTTP/1.1 200 OK  
    Date: Sun, 16 Aug 2020 06:27:34 GMT  
    Content-Type: application/json  
    Content-Length: 99  
    Connection: keep-alive  
    Grpc-Metadata-Content-Type: application/grpc  
    Vary: Origin  
    Vary: Accept-Encoding  
    ​  
    {"result":{"errno":"OK","errmsg":"成功"},"data":{"nodeToken":"xxxxxxxc24d79f55c0b07beaf50cb566"}}
    
    
    POST https://tap-xxxxxxx.xxxxxx.com/api/v2/Android/analytics/basic HTTP/1.1  
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cjbcjdsabcjvbXVCJ9.eyJ1aWQiOjE4ODMzMDEsInNlY3JldCI6IjAzNzE0M2Y3LTExMTUtNGY2Yi1iNzQxLWUyMjc5ZDM3MGY3MCIsImV4cCI6MTU5NzgxNjQ0MiwiaXNzIjoiZ3Vlc3QgbG9naW4ifQ.W3SiO0-afbhxPITjRinnhyWhZLy1bzZhYexm5VCWklI  
    X-Device-ID: 9xxxxxxx84d4542e  
    X-Loc: ["China","Shanghai","Shanghai","","ChinaUnicom","31.224349","121.4767528","Asia/Shanghai","UTC+8","310000","86","CN","AP","xxx.166.xxx.xxx"]  
    X-App-Version: 2.2.0  
    Content-Type: application/json; charset=utf-8  
    Content-Length: 208  
    Host: xx-xxxx.xxxxxx.com  
    Connection: Keep-Alive  
    Accept-Encoding: gzip  
    User-Agent: okhttp/4.7.2  
    ​  
    {"deviceID":"9xxxxxxx84d4542e","model":"V1813BA","systemVersion":"9","version":"2.2.0","location":{"latitude":xx.x99x990990991,"longitude":xxx.26689769073256},"network":{"g2":0,"g3":0,"g4":4,"g5":0,"wifi":4}}  
    ​  
    -----------------------------------  
    HTTP/1.1 200 OK  
    Date: Sun, 16 Aug 2020 06:27:35 GMT  
    Content-Type: application/json  
    Content-Length: 43  
    Connection: keep-alive  
    Grpc-Metadata-Content-Type: application/grpc  
    Vary: Origin  
    Vary: Accept-Encoding  
    ​  
    {"result":{"errno":"OK","errmsg":"成功"}}

