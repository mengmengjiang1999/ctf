## 1.前言

在日常渗透过程中我们经常会遇到瓶颈无处下手，这个时候如果攻击者从公众号或者APP进行突破，往往会有很多惊喜。但是目前市场上的APP都会为防止别人恶意盗取和恶意篡改进行一些保护措施，比如`模拟器检测、root检测、APK加固、代码混淆、代码反调试、反脱壳、签名校验`等等对抗机制。

而测试人员对APP进行渗透的首步操作通常就是上burp或者Charles这类抓包工具进行抓包，查看请求记录里的域名及链接地址是否可以进一步利用，但是如果遇到一些APP出现证书报错或者抓不到包的情况该怎么办，读过本篇文章之后，相信你会拥有一些新的解决方案和思考。

## 2.数字证书

我们都知道http协议传输的是明文信息，是可以直接捕获的，从而造成了数据泄露。为了防止中间人的拦截，出现了HTTPS加密机制。在HTTPS中，使用了`证书+数字签名`解决了这个问题。

这部分加密机制的知识可以阅读这篇文章[HTTPS整套加密机制是如何实现的？](https://www.cnblogs.com/TF511/articles/10791460.html)，里面写的非常详细。此篇的重点在于如何应对APP的抓包对抗。

我总结的HTTPS加密机制如下：

  *  **数字签名** 是发送方的明文经历了两次加密得到的两个东西组成，一个是hash ，一个是经过私钥加密。
  *  **数字证书** 就是明文+数字签名。但是数字证书中的内容远不止这俩，还包括了权威机构的信息，服务器的域名，最重要的是有签名的计算方法，不然用公钥进行解密之后的hash，如何与加密明文进行对比呢，还有证书中还包括公钥，公钥用于发放给请求证书的客户端。
  * HTTPS就是使用SSL/TLS协议进行加密传输，让客户端拿到服务器的公钥，然后客户端随机生成一个对称加密的秘钥，使用公钥加密，传输给服务端，后续的所有信息都通过该对称秘钥进行加密解密，完成整个HTTPS的流程。

## 3.https抓包

### 导入用户证书

在第一次使用burp时，都会有这么一步，将burp的证书导出，添加进浏览器
【受信任的根证书颁发机构】中去，这样就会信任burp发来的请求包，也就可以请求数据进行修改。我们对APP抓包，也同样要将burp证书安装到系统证书中去，一般从【SD卡安装】的证书会存放在用户信任的凭据下

![image-20220307180246534](https://image.3001.net/images/20221024/1666596096_63563d00a4536c6e85054.png!small)

![image-20211228140857040](https://image.3001.net/images/20221024/1666596097_63563d0124289fae2739c.png!small)

> 但是，在Android 7.0以前，应用默认会信任系统证书和用户证书，Android 7.0开始，默认只信任系统证书。
>
> 所以如果你的手机是处于Android7.0以上版本的话，并且在没有绑定SSL证书的情况下，也会抓不到包，从安卓开发的角度可以很清楚的看到这一点。

下图是我将burp证书安装到Android7.1.2的用户证书下，使用okhttp对<https://ttt.com>进行请求的结果。由于ttt.com的SSL证书是自签名证书，而自签名证书是不被系统默认信任的，所以需要先将ttt.com的自签名证书添加到系统证书中才可以访问。

![Image](https://image.3001.net/images/20221024/1666596097_63563d019c19111dc4811.png!small)

自签名证书的生成如下图所示：

![image-20220321214737368](https://image.3001.net/images/20221024/1666596098_63563d023b43c44276a2a.png!small)

  * 系统证书路径：`/system/etc/security/cacerts/`
  * 用户证书路径：`/data/misc/user/0/cacerts-added/`

移动到系统根证书路径的方法：

1、导出burp.der

2、使用openssl更改证书格式,先将burp证书的der格式转成pem,再获取证书的hash

    
    
    openssl x509 -inform DER -in burp.der -out burp.pem
    openssl x509 -inform PEM -subject_hash_old -in burp.pem 
    

![image-20220323223407377](https://image.3001.net/images/20221024/1666596103_63563d070e87824d1738c.png!small)

3.移动到系统根证书目录路径下

Android根证书目录都是以pem证书的hash值+.0格式，所以要将刚才生成的pem改名为xxxx.0

    
    
    mv burp.pem a5ba575.0
    

由于系统读写权限问题，不一定能直接上传到system目录

    
    
    adb push 9a5ba575.0 /sdcard
    
    adb shell 
    mount -o remount,rw /system
    cp /sdcard/9a5ba575.0 /system/etc/security/cacerts/
    chmod 644 /system/etc/security/cacerts/9a5ba575.0
    

移动完成之后，再打开【设置】-【安全】-【信任的凭据】验证一下

![image-20220307181611032](https://image.3001.net/images/20221024/1666596122_63563d1a5c4e7d1890c24.png!small)

这时可以在Android7.0以上版本正常访问<https://ttt.com>了，其他抓包工具同理即可。

### 证书有效期过长

还有一种情况是，导入到系统证书仍抓不到包，并且浏览器会报 **NET::ERR_CERT_VALIDITY_TOO_LONG** 错误。

原因是chrome从2018年开始只信任有效期少于825天（27个月）的证书，而burp证书有效期过长。

解决方案是自己做一个低于27个月的root证书导入burp，再通过burp重新导出证书并放入到系统证书路径下。

    
    
    openssl genrsa -out key.pem 3072 -nodes
    openssl req -new -x509 -key key.pem -sha256 -config openssl.cnf -out cert.pem -days 730 -subj "/C=JP/ST=/L=/O=m4bln/CN=MY CA"
    openssl pkcs12 -export -inkey key.pem -in cert.pem -out cert_and_key.pfx
    把cert_and_key.pfx导入burp
    

目前还没遇到过这种情况，但是如果遇到了这种问题要知道怎么解决。

>
> 以上两种方法都是仅依靠了系统校验证书的方式进行抓包，APP在整个请求HTTPS的请求过程时还并未进行证书校验，和在普通的浏览器中访问并无区别，只是要将想要被信任的证书放入系统证书路径内。

## 4.SSLPinning

对于像ttt.com这种自签名的免费证书，不需要CA权威认证的证书，大多数APP开发商都会使用。那么如果在安卓开发的过程中，将证书的验证逻辑放在APP内部，与系统和浏览器毫无相关，这时再想将burp证书导入系统受信任路径下也于事无补了。

APP自己校验证书，分为两种，一种是将验证逻辑也在代码中，一种是写在安卓7.0之后才有的network-security-config中。

验证是方式也有两种，一种是验证证书公钥的hash值，一种是直接验证证书的公钥文件。

这种通过APP自身的验证方式就叫做证书绑定(也叫Certificate Pinning或SSL Pinning)。

那么如何去判断一个APP是否使用了证书绑定呢？首先拿到apk文件，用apktool工具进行反编译，查看敏感文件

    
    
    apktool d -s <file.apk> -o <outdir>
    

开发人员经常会将网络配置的相关文件保存到指定位置，如下图就指定在了xml目录下。

![image-20220321222952210](https://image.3001.net/images/20221024/1666596122_63563d1ae3a2827e00b70.png!small)

所以在反编译后的res/xml目录下会有一个network_security_config.xml文件，打开看到<domain-config>标签，说明使用了证书绑定机制。

![image-20220321222356576](https://image.3001.net/images/20221024/1666596123_63563d1b6fa152182d12c.png!small)

### 在配置文件中检验的两种方法

    
    
    <network-security-config xmlns:tools="http://schemas.android.com/tools">
        <!--允许http访问-->
        <base-config cleartextTrafficPermitted="true"
            tools:ignore="InsecureBaseConfiguration" />
      
        <!--证书校验-->
        <domain-config>
            <domain includeSubdomains="true">www.ttt.com</domain>
            <trust-anchors>
                <certificates src="@raw/ttt"/>
            </trust-anchors>
        </domain-config>
      
        <!--公钥校验-->
        <domain-config cleartextTrafficPermitted="true">
            <domain includeSubdomains="true">ttt.com</domain>
            <!--利用xml校验证书公钥的hash值-->
            <pin-set expiration="2099-01-01"
                tools:ignore="MissingBackupPin">
                <pin digest="SHA-256">7VMdvZE3PGbxb0Pgf1PlCp+MI8KZ2ZC5psM8TIylNDA=</pin>
            </pin-set>
            <!--利用xml校验证书的公钥文件-->
            <trust-anchors>
                <certificates src="@raw/ttt"/>
            </trust-anchors>
        </domain-config>
      
    </network-security-config>
    

这两种校验机制出现一种即可，从代码中可以看出，ttt.com就是安卓自己要校验绑定的域名。

如果只是在这个文件进行校验，有两种解决方案：一是直接将文件中校验的部分<trust-anchors>或<pin-set>注释掉，再重新打包和签名即可，但是这过程又有些麻烦，并不是上上策，如果遇到了不能重打包的apk就尴尬了。。。二是最常用的也是最好用的frida来hook关键函数进行绕过，后面会讲解。当然有些人会直接在真机或者模拟器上安装xposed模块，但是我个人觉得每次使用都要软重启，可能还会造成卡机，所以感觉还是使用frida最方便。

### 在代码中检验的两种方法

1.利用代码校验证书的公钥hash

    
    
    String hostname = "www.ttt.com";
    CertificatePinner certificatePinner = new CertificatePinner.Builder()
        .add(hostname, "sha256/7VMdvZE3PGbxb0Pgf1PlCp+MI8KZ2ZC5psM8TIylNDA=")
        .build();
    OkHttpClient client = new OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .hostnameVerifier(new HostnameVerifier() {
            @Override
            public boolean verify(String hostname, SSLSession session) {
                return true;
            }
        }).build();
    

2.利用代码校验证书的公钥证书文件

    
    
    // 获取证书输入流
    InputStream openRawResource = getApplicationContext().getResources().openRawResource(R.raw.ttt); 
    Certificate ca = CertificateFactory.getInstance("X.509").generateCertificate(openRawResource);
    // 创建 Keystore 包含我们的证书
    KeyStore keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
    keyStore.load(null, null);
    keyStore.setCertificateEntry("ca", ca);
    // 创建一个 TrustManager 仅把 Keystore 中的证书 作为信任的锚点
    TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm()); // 建议不要使用自己实现的X509TrustManager，而是使用默认的X509TrustManager
    trustManagerFactory.init(keyStore);
    // 用 TrustManager 初始化一个 SSLContext
    sslContext = SSLContext.getInstance("TLS");  //定义：public static SSLContext sslContext = null;
    sslContext.init(null, trustManagerFactory.getTrustManagers(), new SecureRandom());
    
    OkHttpClient client = new OkHttpClient.Builder()
        .sslSocketFactory(sslContext.getSocketFactory(),
                          (X509TrustManager) trustManagerFactory.getTrustManagers()[0] )
        .hostnameVerifier(new HostnameVerifier() {
            @Override
            public boolean verify(String hostname, SSLSession session) {
                return true;
            }
        }).build();
    

通过frida进行hook，这种绕过的脚本也很多，比较熟悉的有JustTrustMe和
[DroidSSLUnpinning](https://github.com/WooyunDota/DroidSSLUnpinning)，他们的底层原理都是一样的，通过hook关键的验证函数，进行逻辑绕过。

frida的安装过程就不详细讲解了，网上很多教程。这里我使用的是`frida 12.8.0 + frida-tools=5.3.0`

这里我使用的hook.js的脚本如下：

    
    
    /*  Android ssl certificate pinning bypass script for various methods
    by Maurizio Siddu modify by Ch3nYe
    
    Run with:
    frida -U -f [APP_ID] -l frida_multiple_unpinning.js --no-pause
    */
    setTimeout(function() {
    Java.perform(function () {
    console.log('');
    console.log('======');
    console.log('[#] Android Bypass for various Certificate Pinning methods [#]');
    console.log('======');
    
    
    var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    
    
    // TrustManager (Android < 7) //
    ////////////////////////////////
    var TrustManager = Java.registerClass({
    // Implement a custom TrustManager
    name: 'dev.asd.test.TrustManager',
    implements: [X509TrustManager],
    methods: {
    checkClientTrusted: function (chain, authType) {},
    checkServerTrusted: function (chain, authType) {},
    getAcceptedIssuers: function () {return []; }
    }
    });
    // Prepare the TrustManager array to pass to SSLContext.init()
    var TrustManagers = [TrustManager.$new()];
    // Get a handle on the init() on the SSLContext class
    var SSLContext_init = SSLContext.init.overload(
    '[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom');
    try {
    // Override the init method, specifying the custom TrustManager
    SSLContext_init.implementation = function(keyManager, trustManager, secureRandom) {
    console.log('[+] Bypassing Trustmanager (Android < 7) request');
    SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
    };
    } catch (err) {
    console.log('[-] TrustManager (Android < 7) pinner not found');
    //console.log(err);
    }
    
    
    
    // OkHTTPv3 (quadruple bypass) //
    /////////////////////////////////
    try {
    // Bypass OkHTTPv3 {1}
    var okhttp3_Activity_1 = Java.use('okhttp3.CertificatePinner');
    okhttp3_Activity_1.check.overload('java.lang.String', 'java.util.List').implementation = function (a, b) {
    console.log('[+] Bypassing OkHTTPv3 {1}: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] OkHTTPv3 {1} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass OkHTTPv3 {2}
    // This method of CertificatePinner.check could be found in some old Android app
    var okhttp3_Activity_2 = Java.use('okhttp3.CertificatePinner');
    okhttp3_Activity_2.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function (a, b) {
    console.log('[+] Bypassing OkHTTPv3 {2}: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] OkHTTPv3 {2} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass OkHTTPv3 {3}
    var okhttp3_Activity_3 = Java.use('okhttp3.CertificatePinner');
    okhttp3_Activity_3.check.overload('java.lang.String', '[Ljava.security.cert.Certificate;').implementation = function (a, b) {
    console.log('[+] Bypassing OkHTTPv3 {3}: ' + a);
    return true;
    };
    } catch(err) {
    console.log('[-] OkHTTPv3 {3} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass OkHTTPv3 {4}
    var okhttp3_Activity_4 = Java.use('okhttp3.CertificatePinner');
    okhttp3_Activity_4[''].implementation = function (a, b) {
    console.log('[+] Bypassing OkHTTPv3 {4}: ' + a);
    };
    } catch(err) {
    console.log('[-] OkHTTPv3 {4} pinner not found');
    //console.log(err);
    }
    
    
    
    // Trustkit (triple bypass) //
    //////////////////////////////
    try {
    // Bypass Trustkit {1}
    var trustkit_Activity_1 = Java.use('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
    trustkit_Activity_1.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (a, b) {
    console.log('[+] Bypassing Trustkit {1}: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] Trustkit {1} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass Trustkit {2}
    var trustkit_Activity_2 = Java.use('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
    trustkit_Activity_2.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (a, b) {
    console.log('[+] Bypassing Trustkit {2}: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] Trustkit {2} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass Trustkit {3}
    var trustkit_PinningTrustManager = Java.use('com.datatheorem.android.trustkit.pinning.PinningTrustManager');
    trustkit_PinningTrustManager.checkServerTrusted.implementation = function () {
    console.log('[+] Bypassing Trustkit {3}');
    };
    } catch (err) {
    console.log('[-] Trustkit {3} pinner not found');
    //console.log(err);
    }
    
    
    
    
    // TrustManagerImpl (Android > 7) //
    ////////////////////////////////////
    try {
    var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
    TrustManagerImpl.verifyChain.implementation = function (untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
    console.log('[+] Bypassing TrustManagerImpl (Android > 7): ' + host);
    return untrustedChain;
    };
    } catch (err) {
    console.log('[-] TrustManagerImpl (Android > 7) pinner not found');
    //console.log(err);
    }
    
    
    
    // Appcelerator Titanium //
    ///////////////////////////
    try {
    var appcelerator_PinningTrustManager = Java.use('appcelerator.https.PinningTrustManager');
    appcelerator_PinningTrustManager.checkServerTrusted.implementation = function () {
    console.log('[+] Bypassing Appcelerator PinningTrustManager');
    };
    } catch (err) {
    console.log('[-] Appcelerator PinningTrustManager pinner not found');
    //console.log(err);
    }
    
    
    
    // OpenSSLSocketImpl Conscrypt //
    /////////////////////////////////
    try {
    var OpenSSLSocketImpl = Java.use('com.android.org.conscrypt.OpenSSLSocketImpl');
    OpenSSLSocketImpl.verifyCertificateChain.implementation = function (certRefs, JavaObject, authMethod) {
    console.log('[+] Bypassing OpenSSLSocketImpl Conscrypt');
    };
    } catch (err) {
    console.log('[-] OpenSSLSocketImpl Conscrypt pinner not found');
    //console.log(err);
    }
    
    
    
    // OpenSSLEngineSocketImpl Conscrypt //
    ///////////////////////////////////////
    try {
    var OpenSSLEngineSocketImpl_Activity = Java.use('com.android.org.conscrypt.OpenSSLEngineSocketImpl');
    OpenSSLSocketImpl_Activity.verifyCertificateChain.overload('[Ljava.lang.Long;', 'java.lang.String').implementation = function (a, b) {
    console.log('[+] Bypassing OpenSSLEngineSocketImpl Conscrypt: ' + b);
    };
    } catch (err) {
    console.log('[-] OpenSSLEngineSocketImpl Conscrypt pinner not found');
    //console.log(err);
    }
    
    
    
    // OpenSSLSocketImpl Apache Harmony //
    //////////////////////////////////////
    try {
    var OpenSSLSocketImpl_Harmony = Java.use('org.apache.harmony.xnet.provider.jsse.OpenSSLSocketImpl');
    OpenSSLSocketImpl_Harmony.verifyCertificateChain.implementation = function (asn1DerEncodedCertificateChain, authMethod) {
    console.log('[+] Bypassing OpenSSLSocketImpl Apache Harmony');
    };
    } catch (err) {
    console.log('[-] OpenSSLSocketImpl Apache Harmony pinner not found');
    //console.log(err);
    }
    
    
    
    // PhoneGap sslCertificateChecker (https://github.com/EddyVerbruggen/SSLCertificateChecker-PhoneGap-Plugin) //
    //////////////////////////////////////////////////////////////////////////////////////////////////////////////
    try {
    var phonegap_Activity = Java.use('nl.xservices.plugins.sslCertificateChecker');
    phonegap_Activity.execute.overload('java.lang.String', 'org.json.JSONArray', 'org.apache.cordova.CallbackContext').implementation = function (a, b, c) {
    console.log('[+] Bypassing PhoneGap sslCertificateChecker: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] PhoneGap sslCertificateChecker pinner not found');
    //console.log(err);
    }
    
    
    
    // IBM MobileFirst pinTrustedCertificatePublicKey (double bypass) //
    ////////////////////////////////////////////////////////////////////
    try {
    // Bypass IBM MobileFirst {1}
    var WLClient_Activity_1 = Java.use('com.worklight.wlclient.api.WLClient');
    WLClient_Activity_1.getInstance().pinTrustedCertificatePublicKey.overload('java.lang.String').implementation = function (cert) {
    console.log('[+] Bypassing IBM MobileFirst pinTrustedCertificatePublicKey {1}: ' + cert);
    return;
    };
    } catch (err) {
    console.log('[-] IBM MobileFirst pinTrustedCertificatePublicKey {1} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass IBM MobileFirst {2}
    var WLClient_Activity_2 = Java.use('com.worklight.wlclient.api.WLClient');
    WLClient_Activity_2.getInstance().pinTrustedCertificatePublicKey.overload('[Ljava.lang.String;').implementation = function (cert) {
    console.log('[+] Bypassing IBM MobileFirst pinTrustedCertificatePublicKey {2}: ' + cert);
    return;
    };
    } catch (err) {
    console.log('[-] IBM MobileFirst pinTrustedCertificatePublicKey {2} pinner not found');
    //console.log(err);
    }
    
    
    
    // IBM WorkLight (ancestor of MobileFirst) HostNameVerifierWithCertificatePinning (quadruple bypass) //
    ///////////////////////////////////////////////////////////////////////////////////////////////////////
    try {
    // Bypass IBM WorkLight {1}
    var worklight_Activity_1 = Java.use('com.worklight.wlclient.certificatepinning.HostNameVerifierWithCertificatePinning');
    worklight_Activity_1.verify.overload('java.lang.String', 'javax.net.ssl.SSLSocket').implementation = function (a, b) {
    console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {1}: ' + a);
    return;
    };
    } catch (err) {
    console.log('[-] IBM WorkLight HostNameVerifierWithCertificatePinning {1} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass IBM WorkLight {2}
    var worklight_Activity_2 = Java.use('com.worklight.wlclient.certificatepinning.HostNameVerifierWithCertificatePinning');
    worklight_Activity_2.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (a, b) {
    console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {2}: ' + a);
    return;
    };
    } catch (err) {
    console.log('[-] IBM WorkLight HostNameVerifierWithCertificatePinning {2} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass IBM WorkLight {3}
    var worklight_Activity_3 = Java.use('com.worklight.wlclient.certificatepinning.HostNameVerifierWithCertificatePinning');
    worklight_Activity_3.verify.overload('java.lang.String', '[Ljava.lang.String;', '[Ljava.lang.String;').implementation = function (a, b) {
    console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {3}: ' + a);
    return;
    };
    } catch (err) {
    console.log('[-] IBM WorkLight HostNameVerifierWithCertificatePinning {3} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass IBM WorkLight {4}
    var worklight_Activity_4 = Java.use('com.worklight.wlclient.certificatepinning.HostNameVerifierWithCertificatePinning');
    worklight_Activity_4.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (a, b) {
    console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {4}: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] IBM WorkLight HostNameVerifierWithCertificatePinning {4} pinner not found');
    //console.log(err);
    }
    
    
    
    // Conscrypt CertPinManager //
    //////////////////////////////
    try {
    var conscrypt_CertPinManager_Activity = Java.use('com.android.org.conscrypt.CertPinManager');
    conscrypt_CertPinManager_Activity.isChainValid.overload('java.lang.String', 'java.util.List').implementation = function (a, b) {
    console.log('[+] Bypassing Conscrypt CertPinManager: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] Conscrypt CertPinManager pinner not found');
    //console.log(err);
    }
    
    
    
    // CWAC-Netsecurity (unofficial back-port pinner for Android<4.2) CertPinManager //
    ///////////////////////////////////////////////////////////////////////////////////
    try {
    var cwac_CertPinManager_Activity = Java.use('com.commonsware.cwac.netsecurity.conscrypt.CertPinManager');
    cwac_CertPinManager_Activity.isChainValid.overload('java.lang.String', 'java.util.List').implementation = function (a, b) {
    console.log('[+] Bypassing CWAC-Netsecurity CertPinManager: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] CWAC-Netsecurity CertPinManager pinner not found');
    //console.log(err);
    }
    
    
    
    // Worklight Androidgap WLCertificatePinningPlugin //
    /////////////////////////////////////////////////////
    try {
    var androidgap_WLCertificatePinningPlugin_Activity = Java.use('com.worklight.androidgap.plugin.WLCertificatePinningPlugin');
    androidgap_WLCertificatePinningPlugin_Activity.execute.overload('java.lang.String', 'org.json.JSONArray', 'org.apache.cordova.CallbackContext').implementation = function (a, b, c) {
    console.log('[+] Bypassing Worklight Androidgap WLCertificatePinningPlugin: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] Worklight Androidgap WLCertificatePinningPlugin pinner not found');
    //console.log(err);
    }
    
    
    
    // Netty FingerprintTrustManagerFactory //
    //////////////////////////////////////////
    try {
    var netty_FingerprintTrustManagerFactory = Java.use('io.netty.handler.ssl.util.FingerprintTrustManagerFactory');
    //NOTE: sometimes this below implementation could be useful
    //var netty_FingerprintTrustManagerFactory = Java.use('org.jboss.netty.handler.ssl.util.FingerprintTrustManagerFactory');
    netty_FingerprintTrustManagerFactory.checkTrusted.implementation = function (type, chain) {
    console.log('[+] Bypassing Netty FingerprintTrustManagerFactory');
    };
    } catch (err) {
    console.log('[-] Netty FingerprintTrustManagerFactory pinner not found');
    //console.log(err);
    }
    
    
    
    // Squareup CertificatePinner [OkHTTP<v3] (double bypass) //
    ////////////////////////////////////////////////////////////
    try {
    // Bypass Squareup CertificatePinner  {1}
    var Squareup_CertificatePinner_Activity_1 = Java.use('com.squareup.okhttp.CertificatePinner');
    Squareup_CertificatePinner_Activity_1.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function (a, b) {
    console.log('[+] Bypassing Squareup CertificatePinner {1}: ' + a);
    return;
    };
    } catch (err) {
    console.log('[-] Squareup CertificatePinner {1} pinner not found');
    //console.log(err);
    }
    try {
    // Bypass Squareup CertificatePinner {2}
    var Squareup_CertificatePinner_Activity_2 = Java.use('com.squareup.okhttp.CertificatePinner');
    Squareup_CertificatePinner_Activity_2.check.overload('java.lang.String', 'java.util.List').implementation = function (a, b) {
    console.log('[+] Bypassing Squareup CertificatePinner {2}: ' + a);
    return;
    };
    } catch (err) {
    console.log('[-] Squareup CertificatePinner {2} pinner not found');
    //console.log(err);
    }
    
    
    
    // Squareup OkHostnameVerifier [OkHTTP v3] (double bypass) //
    /////////////////////////////////////////////////////////////
    try {
    // Bypass Squareup OkHostnameVerifier {1}
    var Squareup_OkHostnameVerifier_Activity_1 = Java.use('com.squareup.okhttp.internal.tls.OkHostnameVerifier');
    Squareup_OkHostnameVerifier_Activity_1.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (a, b) {
    console.log('[+] Bypassing Squareup OkHostnameVerifier {1}: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] Squareup OkHostnameVerifier pinner not found');
    //console.log(err);
    }
    try {
    // Bypass Squareup OkHostnameVerifier {2}
    var Squareup_OkHostnameVerifier_Activity_2 = Java.use('com.squareup.okhttp.internal.tls.OkHostnameVerifier');
    Squareup_OkHostnameVerifier_Activity_2.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (a, b) {
    console.log('[+] Bypassing Squareup OkHostnameVerifier {2}: ' + a);
    return true;
    };
    } catch (err) {
    console.log('[-] Squareup OkHostnameVerifier pinner not found');
    //console.log(err);
    }
    
    
    
    // Android WebViewClient (double bypass) //
    ///////////////////////////////////////////
    try {
    // Bypass WebViewClient {1} (deprecated from Android 6)
    var AndroidWebViewClient_Activity_1 = Java.use('android.webkit.WebViewClient');
    AndroidWebViewClient_Activity_1.onReceivedSslError.overload('android.webkit.WebView', 'android.webkit.SslErrorHandler', 'android.net.http.SslError').implementation = function (obj1, obj2, obj3) {
    console.log('[+] Bypassing Android WebViewClient {1}');
    };
    } catch (err) {
    console.log('[-] Android WebViewClient {1} pinner not found');
    //console.log(err)
    }
    try {
    // Bypass WebViewClient {2}
    var AndroidWebViewClient_Activity_2 = Java.use('android.webkit.WebViewClient');
    AndroidWebViewClient_Activity_2.onReceivedSslError.overload('android.webkit.WebView', 'android.webkit.WebResourceRequest', 'android.webkit.WebResourceError').implementation = function (obj1, obj2, obj3) {
    console.log('[+] Bypassing Android WebViewClient {2}');
    };
    } catch (err) {
    console.log('[-] Android WebViewClient {2} pinner not found');
    //console.log(err)
    }
    
    
    
    // Apache Cordova WebViewClient //
    //////////////////////////////////
    try {
    var CordovaWebViewClient_Activity = Java.use('org.apache.cordova.CordovaWebViewClient');
    CordovaWebViewClient_Activity.onReceivedSslError.overload('android.webkit.WebView', 'android.webkit.SslErrorHandler', 'android.net.http.SslError').implementation = function (obj1, obj2, obj3) {
    console.log('[+] Bypassing Apache Cordova WebViewClient');
    obj3.proceed();
    };
    } catch (err) {
    console.log('[-] Apache Cordova WebViewClient pinner not found');
    //console.log(err);
    }
    
    
    
    // Boye AbstractVerifier //
    ///////////////////////////
    try {
    var boye_AbstractVerifier = Java.use('ch.boye.httpclientandroidlib.conn.ssl.AbstractVerifier');
    boye_AbstractVerifier.verify.implementation = function (host, ssl) {
    console.log('[+] Bypassing Boye AbstractVerifier: ' + host);
    };
    } catch (err) {
    console.log('[-] Boye AbstractVerifier pinner not found');
    //console.log(err);
    }
    
    
    });
    
    }, 0);
    

启动frida进行hook指定APP的包名

    
    
    frida -U -f com.example.safehttps -l hook.js --no-pause
    

![Image](https://image.3001.net/images/20221024/1666596123_63563d1be5caf2dc0bd4d.png!small)

可以看到开启burp抓包成功。

## 5.开启双向校验

双向校验顾名思义也就是服务器也要对客户端进行证书校验，在刚才客户端校验服务端的基础上添加一直被校验的逻辑在里面。

首先ttt.com所在的nginx服务器要开启双向认证

![Image](https://image.3001.net/images/20221024/1666596124_63563d1c7cb6e9ef953cf.png!small)

开启客户端的校验后，在浏览器进行访问，会发现返回400，没有被请求的SSL证书发送，是因为浏览器正常请求不会携带证书信息去请求ttt.com

![Image](https://image.3001.net/images/20221024/1666596124_63563d1cecddd5739c7bd.png!small)

那么如何携带客户端的证书，就要利用burp来操作，将ttt.com的证书添加到TLS客户证书

![Image](https://image.3001.net/images/20221024/1666596125_63563d1d6911326d4ba7a.png!small)

这时再访问

![Image](https://image.3001.net/images/20221024/1666596125_63563d1ded00d6a7dc4ec.png!small)

在APP中进行绑定客户端的证书文件，一般是p12格式文件，会放在assets目录下或者raw目录下，client.p12会有一个密钥内置在代码中，需要找到才能添加进burp中。

![image-20220307190429062](https://image.3001.net/images/20221024/1666596126_63563d1e56316a7423249.png!small)

这个在反编译后的目录下也能找到，通常在assets或者res/raw目录下查找，但是再导入burp这一步是需要证书密码的，比如上图能明显看到密码是123456，但是找不到证书密码怎么办，可以看一下目录下是否存在lib文件夹，如果存在的话极大可能是将密码写进so层了，这就需要你会IDA反汇编获取证书密钥了，这部分在此不详细阐述，感兴趣的朋友可以先去研究一下。

![image-20220321232207166](https://image.3001.net/images/20221024/1666596126_63563d1ec5f9e97c54b96.png!small)

### APP双向校验验证

服务器校验客户端的证书ClientSSLSocketFactory，服务端将客户端的证书进行绑定。

    
    
    TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
    trustManagerFactory.init((KeyStore) null);
    TrustManager[] trustManagers = trustManagerFactory.getTrustManagers();
    if (trustManagers.length != 1 || !(trustManagers[0] instanceof X509TrustManager)) {
        throw new IllegalStateException("Unexpected default trust managers:" + Arrays.toString(trustManagers));
    }
    trustManager = (X509TrustManager) trustManagers[0];
    
    OkHttpClient client = new OkHttpClient.Builder()
            .sslSocketFactory(Objects.requireNonNull(ClientSSLSocketFactory.getSocketFactory(getApplicationContext())), Objects.requireNonNull(trustManager))
            .hostnameVerifier(new HostnameVerifier() {
                @Override
                public boolean verify(String hostname, SSLSession session) {
                    //强行返回true 即验证成功
                    return true;
                }
    }).build();
    
    
    
    public class ClientSSLSocketFactory  {
        private static final String KEY_STORE_PASSWORD = "123456"; // 证书密码
        private static InputStream client_input;
    
        public static SSLSocketFactory getSocketFactory(Context context) {
            try {
                //客户端证书
                client_input = context.getResources().getAssets().open("client.p12");
                SSLContext sslContext = SSLContext.getInstance("TLS");
                KeyStore keyStore = KeyStore.getInstance("PKCS12");
                keyStore.load(client_input, KEY_STORE_PASSWORD.toCharArray());
                KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
                keyManagerFactory.init(keyStore, KEY_STORE_PASSWORD.toCharArray());
                sslContext.init(keyManagerFactory.getKeyManagers(), null, new SecureRandom());
                return sslContext.getSocketFactory();
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                try {
                    client_input.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            return null;
        }
    }
    

双向校验时，要将SSLPinning与服务器校验客户端证书的模块同时开启。

对其就行绕过，需要先启动Frida进行hook，然后勾选上客户端证书，才可以请求成功。如下图所示：

![Image](https://image.3001.net/images/20221024/1666596127_63563d1f2dbbbb947ad3e.png!small)

没勾选就会请求失败，出现400 Bad Request，和浏览器无代理时请求的结果一样，如下图：

![Image](https://image.3001.net/images/20221024/1666596127_63563d1fab62c5d490665.png!small)

此时burp代理日志显示如下，SSL请求失败

![Image](https://image.3001.net/images/20221024/1666596128_63563d203b921f11b9908.png!small)

### WebView证书校验

webview也是一种请求方式，相当于页面的跳转或嵌入，请求的结果会显示在主屏幕上。

对于webview证书校验，有些可以找到的脚本不一定有绕过，所以在使用的过程中要查看是否含有webview的关键信息

这里我使用的是[DroidSSLUnpinning](https://github.com/WooyunDota/DroidSSLUnpinning)

使用效果如下：

![Image](https://image.3001.net/images/20221024/1666596128_63563d20b91e5c354d741.png!small)

![Image](https://image.3001.net/images/20221024/1666596129_63563d21427fcfc1198f3.png!small)

此时的APP绑定场景为：OKhttp请求为双向校验，webview为SSLPinning校验。所以在图中的上面一行是okhttp的请求结果，下面的是webview的请求结果，此脚本双向校验仍然可以绕过。

如果说webview再添加了客户端校验，那么在反编译apk后，需要找到webview访问域名的证书密钥，再安装进burp中即可。

## 6.ssl_logger通杀

至此，我们可以绕过证书绑定，抓APP发出的https包了，然而上述的证书解绑hook工具仅仅是通过hook了几种绑定证书的API，不适用于新出现或者非主流的证书绑定技术。这时，就需要神器
**ssl_logger**

[ssl_logger](https://github.com/5alt/ssl_logger)是用来解密SSL流量的工具，也是一款基于frida的hook工具，通过hook
libssl库中的SSL_read、SSL_write等函数来实现流量解密，由于底层的实现会调用这几个函数来封装，所以可以直接解出流量数据。

![image-20220307185359590](https://image.3001.net/images/20221024/1666596129_63563d21cc07ec869c084.png!small)

[r0capture](https://github.com/r0ysue/r0capture)是r0ysue大佬在其基础上进行改进的一款工具。

![image-20220307185253814](https://image.3001.net/images/20221024/1666596130_63563d224bd6cf8cbf191.png!small)

由于ssl_logger是适用于MAC和linux操作系统，所以我选择在kali上进行hook实现双向校验的app

![Image](https://image.3001.net/images/20221024/1666596130_63563d22c7ded95b695dd.png!small)

打开抓到的1.pcap包

![Image](https://image.3001.net/images/20221024/1666596131_63563d239a5a512d70cbd.png!small)

![Image](https://image.3001.net/images/20221024/1666596132_63563d2433b204576d5d0.png!small)

从图中可以看出成功的获取到了信息，是不是感觉这个工具特别神，但是看pcap的包总归不如看burp的一目了然，这个工具就这一点不太友好。所以用哪个看你心情啦~~

## 7.eBPF hook 免CA证书

[ecapture](https://github.com/ehids/ecapture)：eBPF HOOK
uprobe实现的各种用户态进程的数据捕获，无需改动原程序。这个工具也是通过hook了`libssl`库中`SSL_write`、`SSL_read`这两个关键的SSL加密函数的返回值，拿到明文信息，通过ebpf
map传递给用户进程。在APP中，如果遇到场景是burp抓包时出现证书报错，我觉得可以尝试一下用这个工具直接curl访问进行抓包。eBPF
hook也是最近才发现的hook方法，值得我们去深入探索。

我这里用的是作者v0.1.3版本发布的工具，使用效果如下：

![image-20220322204531014](https://image.3001.net/images/20221024/1666596132_63563d24a0372263049e0.png!small)

## 8.总结

在依靠系统或默认浏览器校验证书的情况下，导入burp证书为用户证书是可以抓https包的

当app支持的最小API为24（Android 7.0）或以上时，默认情况下app只信任系统级别的证书，需要把burp变为系统证书

自签名证书作为系统证书时，有效期最长不超过825天，用户证书则没有限制

开启证书校验的APP在使用burp抓包时会报certtificate_unknown等错误

使用frida hook绕过双向证书校验时，必须要将客户端的p12文件导入burp中

一些脚本仍绕不过可以使用ssl_logger或者逆向代码进行分析验证逻辑，再有针对性的绕过

p12文件的密钥如果在so层，需要会用IDA进行静态分析lib下的so文件获取关键密钥

看完本篇文章之后，相信你再面对抓不到包的APP或者是https请求也不会手足无措了。

## 9.参考文章

[Android HTTPS认证的N种方式和对抗方法总结](https://ch3nye.top/Android-HTTPS%E8%AE%A4%E8%AF%81%E7%9A%84N%E7%A7%8D%E6%96%B9%E5%BC%8F%E5%92%8C%E5%AF%B9%E6%8A%97%E6%96%B9%E6%B3%95%E6%80%BB%E7%BB%93/)

参考了此文章的项目按照自己的想法进行了些许改进的项目地址 :
[Safehttps](https://github.com/dummersoul/SafeHttpsTest)

[Android
Https抓包实践](https://mabin004.github.io/2018/03/05/https%E4%B8%AD%E9%97%B4%E4%BA%BA%E6%94%BB%E5%87%BB%E5%8E%9F%E7%90%86/)

