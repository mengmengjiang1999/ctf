**随着Nougat（Android 7）的发布 ，一个名为“Network Security
Configuration”的新安全功能也随之而来。这个新功能的目标是允许开发人员在不修改应用程序代码的情况下自定义他们的网络安全设置。SSL/TLS的连接的默认配置中还包含了其他修改；如果应用程序的SDK高于或等于24，则只有系统证书才会被信任。**

以上所有都会影响Android移动应用程序评估的执行方式。如果需要拦截HTTPS流量，则必须安装代理证书，但其会安装在'用户证书'的container中，默认情况下不受信任。在这里，我们将着重解释新机制如何工作，以及如何通过重新编译应用程序以及在运行时hook一些机制来修改默认行为。这些步骤对拦截应用程序与服务器之间的HTTPS流量至关重要。

## 如何作为开发者使用该功能

要修改默认配置，必须在resources目录中创建一个指定自定义配置的XML文件。
下面的代码片段显示了一个配置文件示例，该配置文件指定用户证书来管理应用程序生成的所有HTTPS连接。

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <network-security-config>
        <base-config>
            <trust-anchors>
                <certificates src="system"/>
                <certificates src="user"/>
            </trust-anchors>
        </base-config>
    </network-security-config>  
    

![Screen-Shot-2018-03-12-at-19.27.18-1024x491.png](https://image.3001.net/images/20180318/15213723816051.png!small)  

此外，该文件必须从Android Manifest文件中引用，其在应用标签上引入了android:networkSecurityConfig，如下所示：

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <manifest ... >
        <application android:networkSecurityConfig="@xml/network_security_config"
                        ... >
            ...
        </application>
    </manifest>  
    

## 如何作为渗透测试者绕过该功能

### 重新编译

如果要评估的应用程序在Android 7或更高版本上执行，并且targetSdkVersion键被配置为24（Android
7）或更高版本，则应用程序可能使用默认配置。因此，应用程序不会信任用户证书（即代理CA证书）。修改默认配置的常用方法是在插入XML后重新编译应用程序，这将激活证书container的使用。一旦我们有了APK，这个过程就可以通过使用apktool来实现，它允许应用程序被修改。

首先使用apktool反编译应用程序，完成该过程后，resources目录中必须创建一个XML文件，AndroidManifest.xml文件也必须被修改以指向Network
Security Configuration文件。完成后，我们可以使用apktool重新编译应用程序，并使用Java
JDK提供的jarsigner工具对生成的APK文件进行签名。

当使用任意证书重新签名APK时，可以使用adb（Android Debug Bridge）将其安装在手机中。 如果移动端被配置为通过中间代理（如Burp
Suite）发送流量，那么只要CA证书安装在系统上，就可以拦截HTTPS流量。

### 运行时hook

值得注意的是，在某些情况下，上述场景可能无法实现的。例如，如果应用程序使用sharedId共享另一个应用程序的相同ID并因此直接访问其数据，那么Android会将我们的场景限制为仅由相同证书签名的应用程序。此时将应用程序重新编译并重新签名是无法完成的，因为无法使用应用程序开发人员使用的原始证书对已修改的APK进行签名。

对于这种场景，动态检测会有点用，因为它允许修改运行时的应用程序行为，而不修改应用程序本身。要实施此过程，我们要创建一个Frida脚本，用于适应目标SDK版本的应用程序上的Network
Security Configuration默认行为。

android.security.net.config包实现了网络安全配置模块，而主类ManifestConfigSource加载XML文件中指定的自定义配置或默认配置时（在资源文件不存在的情况下）。
你可以看到下面的内容：

    
    
    package android.security.net.config;
    public class ManifestConfigSource implements ConfigSource {
    . . .
        private ConfigSource getConfigSource() {
            synchronized (mLock) {
    . . .
                if (mConfigResourceId != 0) {
    . . .
     
                   source = new XmlConfigSource(mContext, mConfigResourceId,
     debugBuild, mTargetSdkVersion, mTargetSandboxVesrsion);
                } else {
                    . . . 
                    source = new DefaultConfigSource(usesCleartextTraffic, mTargetSdkVersion, mTargetSandboxVesrsion);
                }
                mConfigSource = source;
                return mConfigSource;
            }
        }
    . . .
    }  
    

DefaultConfigSource类（在ManifestConfigSource类中定义为私有类）是在未使用XML文件修改配置时使用的类。

    
    
    package android.security.net.config;
    public class ManifestConfigSource implements ConfigSource {
     ...
        private static final class DefaultConfigSource implements ConfigSource {
            private final NetworkSecurityConfig mDefaultConfig;
            public DefaultConfigSource(boolean usesCleartextTraffic, int targetSdkVersion,
                    int targetSandboxVesrsion) {
                mDefaultConfig = NetworkSecurityConfig.getDefaultBuilder(targetSdkVersion,
                        targetSandboxVesrsion)
                        .setCleartextTrafficPermitted(usesCleartextTraffic)
                        .build();
            }
            @Override
            public NetworkSecurityConfig getDefaultConfig() {
                return mDefaultConfig;
            }
            @Override
            public Set<Pair<Domain, NetworkSecurityConfig>> getPerDomainConfigs() {
                return null;
            }
     }
    }  
    

从构造函数中可以看出，它接收三个参数，其中一个针对应用程序的SDK版本。该值用于使用getDefaultBuilder()方法构建NetworkSecurityConfig类，方法显示在下一段代码中。可以看出，如果targetSdkVersion小于或等于SDK版本23（Android
Marshmallow即Android 6.0），那么最后一段代码将加载用户证书。

    
    
    package android.security.net.config;
    public final class NetworkSecurityConfig {
    ...
       public static final Builder getDefaultBuilder(int targetSdkVersion, int targetSandboxVesrsion) {
                  Builder builder = new Builder()
                          .setHstsEnforced(DEFAULT_HSTS_ENFORCED)
                          // System certificate store, does not bypass static pins.
                          .addCertificatesEntryRef(
                                  new CertificatesEntryRef(SystemCertificateSource.getInstance(), false));
                  final boolean cleartextTrafficPermitted = targetSandboxVesrsion < 2;
                  builder.setCleartextTrafficPermitted(cleartextTrafficPermitted);
                  // Applications targeting N and above must opt in into trusting the user added certificate
                  // store.
                  if (targetSdkVersion <= Build.VERSION_CODES.M) {
                      // User certificate store, does not bypass static pins.
                      builder.addCertificatesEntryRef(
                              new CertificatesEntryRef(UserCertificateSource.getInstance(), false));
                  }
                  return builder;
       }
    ...  
    

考虑到这一点，我们可以创建一个Frida脚本来hook
DefaultConfigSource类的构造函数并更改targetSdkVersion变量的值。此外，即使一些代码将来会更改此构造函数，该脚本也会hook到getDefaultBuilder()方法以确保该值被修改。

    
    
    Java.perform(function(){
          var ANDROID_VERSION_M = 23;
          var DefaultConfigSource = Java.use("android.security.net.config.ManifestConfigSource$DefaultConfigSource");
          var NetworkSecurityConfig = Java.use("android.security.net.config.NetworkSecurityConfig");
          DefaultConfigSource.$init.overload("boolean", "int").implementation = function(usesCleartextTraffic, targetSdkVersion){
                 console.log("[+] Modifying DefaultConfigSource constructor");
                 return this.$init.overload("boolean", "int").call(this, usesCleartextTraffic, ANDROID_VERSION_M);
          };
     
         DefaultConfigSource.$init.overload("boolean", "int", 
    "int").implementation = function(usesCleartextTraffic, targetSdkVersion,
     targetSandboxVersion){
                 console.log("[+] Modifying DefaultConfigSource constructor");
     
                return this.$init.overload("boolean", "int", 
    "int").call(this, usesCleartextTraffic, ANDROID_VERSION_M, 
    targetSandboxVersion);
          };
          NetworkSecurityConfig.getDefaultBuilder.overload("int").implementation = function(targetSdkVersion){
                 console.log("[+] getDefaultBuilder original targetSdkVersion => " + targetSdkVersion.toString());
                 return this.getDefaultBuilder.overload("int").call(this, ANDROID_VERSION_M);
          };
     
     
         NetworkSecurityConfig.getDefaultBuilder.overload("int", 
    "int").implementation = function(targetSdkVersion, 
    targetSandboxVersion){
                 console.log("[+] getDefaultBuilder original targetSdkVersion => " + targetSdkVersion.toString());
                 return this.getDefaultBuilder.overload("int", "int").call(this, ANDROID_VERSION_M, targetSandboxVersion);
          };
    });  
    

此时，通过使用Frida加载上述脚本，可以生成面向SDK 24或更高版本的Android应用程序，然后可以使用HTTP代理（例如Burp
Suite）拦截流量。

    
    
    $ frida -U -l ntc.js -f <package_name> --no-pause

 ***参考来源：[nccgroup](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2017/november/bypassing-androids-network-security-configuration/)，[ibotpeaches](https://ibotpeaches.github.io/Apktool/)，Covfefe编译，转载请注明来自FreeBuf.COM**

