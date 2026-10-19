# 1\. 应用密码安全定义

应用密码包含：数据库密码、redis密码、通讯密码、pin密钥等。

本文的目标是确保上述密码在应用中不以明文形式， **而是以加密形式存在，并且加密机制要相对安全，不易破解。**

# 2\. 本文关注范围

由于pin密钥之类的是通过硬件加密机实现的，不在本文论述范围内， **本文重点关注应用侧配置文件中的数据库密码、** **redis** **密码、**
**FTP/FTPS** **密码等。**

# 3\. 现状描述

1、很多系统并没有对密码安全足够重视，密码依然以明文状态为主。

例如：（以下配图均为测试环境的模拟举例）

数据库密码明文写在配置文件中：

![1605712803_5fb53ba3167dc0e712f29.png!small?1605712803781](https://image.3001.net/images/20201118/1605712803_5fb53ba3167dc0e712f29.png!small?1605712803781)

redis密码明文写在配置文件中：

![1605712815_5fb53baf5d8f45d8a0f1f.png!small?1605712816014](https://image.3001.net/images/20201118/1605712815_5fb53baf5d8f45d8a0f1f.png!small?1605712816014)

2、即便采用了加密，也多是采用较为容易破解的算法，例如Base64。

3、FTP/FTPS密码明文写在Shell脚本中。

![1605712827_5fb53bbbc37508bb8dd81.png!small?1605712828336](https://image.3001.net/images/20201118/1605712827_5fb53bbbc37508bb8dd81.png!small?1605712828336)

# 4\. 保护应用密码的意义

即使服务器已经被getshell，但是加密的密码可以避免黑客直接拖库获取业务数据，或者是入侵关联的系统，造成更大的危害。并且能为我们的防御争取时间。

# 5\. 使用jasypt框架保护配置文件中的密码

### 5.1 组件介绍

[github地址] <https://github.com/ulisesbocchio/jasypt-spring-boot>

![1605712848_5fb53bd0b2943767bacf5.png!small?1605712849977](https://image.3001.net/images/20201118/1605712848_5fb53bd0b2943767bacf5.png!small?1605712849977)

特别说明1：本次提供的工具passwdtools-1.1.1.jar包提供了PBEWithHMACSM3AndSM4 | SM4 |
PBEWithHMACSHA512AndAES_256 | PBEWithMD5AndDES
一共4种加密算法，前两者基于国密SM3/SM4算法，两个带HMAC的算法因为加入了随机salt的关系，每次加密出来的密文是不同的。

特别说明2：本教程基于SpringBoot/SpringCloud应用进行说明(普通java应用类似)，且推荐使用IDEA-IDE和Maven工具。

## 5.2 快速上手

 **step1** **：jdk** **环境增加依赖包**

    
    
    # 拷贝依赖包bcprov-jdk15to18-1.66.jar(Maven仓库可下载，附件有提供)到jdk环境目录下
    
    [Mac-jdk路径]
    
    /Library/Java/JavaVirtualMachines/jdk1.8.0_231.jdk/Contents/Home/jre/lib/ext/
    
    [Linux-jdk路径]
    
    /usr/java/jdk1.8.0_231-amd64/jre/lib/ext/
    
    [windows-jdk路径]
    
    C:\Program Files\Java\jre1.8.0_261\lib\ext\

 **step2** **：应用引入依赖** **(pom.xml** **设置** **)**

将封装好的passwdtools-1.1.1.jar拷贝到{project_home}/ src/main/resources/lib/下。

修改pom.xml文件

    
    
    <dependency>
    
    <groupId>com.github.ulisesbocchio</groupId>
    
    <artifactId>jasypt-spring-boot-starter</artifactId>
    
    <version>3.0.3</version>
    
    </dependency>
    
    <!-- 引入自定义jar包 -->
    
    <dependency>
    
    <groupId>passwdtools</groupId>
    
    <artifactId>passwdtools</artifactId>
    
    <version>1.1.1</version>
    
    <scope>system</scope>
    
    <systemPath>${project.basedir}/src/main/resources/lib/passwdtools-1.1.1.jar</systemPath>
    
    </dependency>

在IDEA中点击File-Project Structure-Libraries，点击+添加上一步lib目录下的jar包。

![1605712886_5fb53bf67f142e02cc2d2.png!small?1605712888502](https://image.3001.net/images/20201118/1605712886_5fb53bf67f142e02cc2d2.png!small?1605712888502)

特别说明：建议使用最新的3.0.3版本，3.0.0之前版本默认加密方法为PBEWithMD5AndDES，算法安全程度不足。

修改pom.xml，设置maven打包规则将自定义jar包一并打入：  
![1605712898_5fb53c02732f490092d3f.png!small?1605712899150](https://image.3001.net/images/20201118/1605712898_5fb53c02732f490092d3f.png!small?1605712899150)

 **step3** **：计算密文**

可以直接使用我已经打包好的jar包计算密文，useage如下：

    
    
    java -jar passwdtools-1.1.1.jar {Algorithm} "{加密密码}" "{明文}"
    
    [Algorithm]
    
    1-PBEWithHMACSM3AndSM4(推荐)
    
    2-SM4
    
    3-PBEWithHMACSHA512AndAES_256
    
    4-PBEWithMD5AndDES
    
    eg：
    
    java -jar passwdtools-1.1.1.jar 1 "dabaicai" "1qaz2wsx@dbc"

![1605712917_5fb53c1584a52e10b1d01.png!small?1605712917959](https://image.3001.net/images/20201118/1605712917_5fb53c1584a52e10b1d01.png!small?1605712917959)

 **step4** **：增加自定义解密类** **CustomStringEncryptor(** **附件** **zip** **包中会提供**
**)**

    
    
    import com.dbc.passwdtools.PBEWithHMACSM3AndSM4StringEncryptor;
    
    import org.jasypt.encryption.StringEncryptor;
    
    import org.slf4j.Logger;
    
    import org.slf4j.LoggerFactory;
    
    import org.springframework.beans.factory.annotation.Value;
    
    import org.springframework.context.annotation.Configuration;
    
    
    
    
    /**
    
    * 自定义解密类
    
    * @author dabaicai
    
    */
    
    @Configuration("CustomStringEncryptor")
    
    public class CustomStringEncryptor implements StringEncryptor {
    
    
    
    
    private static final Logger logger = LoggerFactory.getLogger(CustomStringEncryptor.class);
    
    
    
    
    @Value("${jasypt.encryptor.password}")
    
    private String enpassword;
    
    
    
    
    @Override
    
    public String encrypt(String s) {
    
    return null;
    
    }
    
    
    
    
    @Override
    
    public String decrypt(String s) {
    
    PBEWithHMACSM3AndSM4StringEncryptor pbeWithHMACSM3AndSM4StringEncryptor = new PBEWithHMACSM3AndSM4StringEncryptor();
    
    pbeWithHMACSM3AndSM4StringEncryptor.initialize(this.enpassword);
    
    return pbeWithHMACSM3AndSM4StringEncryptor.decrypt(s);
    
    }
    
    }

说明：如果要使用其他算法，修改蓝色部分字体即可，passwdtools-1.1.1.jar中还封装了SM4等其他工具类。

 **step5** **：** **application** **配置文件中配置密文**

    
    
    # 数据库密码(密文处填入step2计算得出的密码)
    
    spring.core.password=ENC({密文})
    
    # 设置使用自定义解密Bean
    
    jasypt:
    
    encryptor:
    
    bean: CustomStringEncryptor
    
    # 设置加密密钥(这里是临时配置但并不安全，正确配置请参考5.4进阶配置)
    
    jasypt.encryptor.password=dabaicai

例如：

![1605712950_5fb53c36c6a346c76df7c.png!small?1605712951389](https://image.3001.net/images/20201118/1605712950_5fb53c36c6a346c76df7c.png!small?1605712951389)

## 5.3 加密密码配置问题

目前已经广泛使用这一框架，但是对于加密密钥jasypt.encryptor.password的配置用法普遍存在安全问题。

 **配置在配置文件中**

很容易通过查看你的pom.xml文件或者是引入的jar包推测应用使用的jasypt版本，从而推测出算法，再使用jasypt工具根据密码即可解密明文。解密代码如下（如果采用了PBEWithHMACSHA512AndAES_256）：

    
    
    AES256TextEncryptor aes256TextEncryptor = new AES256TextEncryptor();
    
    aes256TextEncryptor.setPassword("dabaicai");
    
    String enc_password = "Xe1mGmfgEcIlU/zWfqrx2T+q+t5+O7qvvM+JDNnhkgZlrny6pjVHV+U/wfVp8jA+";
    
    String password = aes256TextEncryptor.decrypt(enc_password);
    
    System.out.println("de password: " + password);

 **配置在Apollo等配置中心**

配置中心在应用本地是有缓存文件的，通过缓存文件同样可以查看配置的密码。

![1605712964_5fb53c44ae88e58c79432.png!small?1605712965839](https://image.3001.net/images/20201118/1605712964_5fb53c44ae88e58c79432.png!small?1605712965839)

 **通过命令参数启动**

    
    
    java -jar -Djasypt.encryptor.password=dabaicai {xxx.jar}

无法隐藏进程信息：

![1605712987_5fb53c5b8bda194c013d9.png!small?1605712987952](https://image.3001.net/images/20201118/1605712987_5fb53c5b8bda194c013d9.png!small?1605712987952)

## 5.4 进阶配置

综上所述，需要采用其他方式来隐藏加密密码配置项jasypt.encryptor.password。目前推荐采用的方式是在应用启动脚本中，读取用户输入的加密密码，存放到临时文件中，然后应用程序启动时读取该临时文件的内容设置jasypt.encryptor.password，最后在启动脚本中删除该临时文件。这样加密密码仅保存在内存中，较难被直接读取。

相关启动脚本参考代码如下：

    
    
    #!/bin/bash
    
    echo "please input the encryption password: "
    
    read encryption
    
    echo "${encryption}" > /tmp/startEnv.properties
    
    # start the application
    
    nohup java -jar mintleaf-fast.jar >/dev/null 2>&1 &
    
    sleep 10
    
    rm -rf /tmp/startEnv.properties

应用程序启动时代码（这里以SpringBoot/SprintCloud程序为例）：

    
    
    private static final String START_ENV_PROFILE_PATH = "/tmp/startEnv.properties";
    
    
    
    
    private static final String JASYPT_ENCRYPTOR_PASSWORD = "jasypt.encryptor.password";
    
    
    
    
    public static void main(String[] args) throws Exception {
    
    SpringApplication app = new SpringApplication(MintLeafApplication.class);
    
    // 读取临时文件
    
    Map<String, Object> map = new HashMap<>();
    
    String jasEncPassword = FileUtil.readLine(new RandomAccessFile(new File(START_ENV_PROFILE_PATH), "r"), Charset.defaultCharset());
    
    map.put(JASYPT_ENCRYPTOR_PASSWORD, jasEncPassword);
    
    app.setDefaultProperties(map);
    
    app.run(args);
    
    //SpringApplication.run(MintLeafApplication.class, args);
    
    }

参考执行结果：

![1605713008_5fb53c703de467aac1f34.png!small?1605713008691](https://image.3001.net/images/20201118/1605713008_5fb53c703de467aac1f34.png!small?1605713008691)

查看History和ps -ef均无泄漏：

![1605713023_5fb53c7f68a2cdd8ce5a8.png!small?1605713024252](https://image.3001.net/images/20201118/1605713023_5fb53c7f68a2cdd8ce5a8.png!small?1605713024252)

## 5.5 使用总结

> jdk环境增加依赖包 —— 应用引入maven/jar包依赖 —— 计算密文 —— 增加自定义解密类CustomStringEncryptor ——
> application配置ENC({密文})和自定义解密Bean —— 在应用启动脚本中读取用户输入的密码，写入特定临时文件 ——
> 应用程序启动时读取特定临时文件设置jasypt.encryptor.password —— 启动脚本删除临时文件。
>
> 尽量使用最新版本的jasypt框架。本次提供的工具passwdtools-1.1.1.jar包提供了PBEWithHMACSM3AndSM4 | SM4
> | PBEWithHMACSHA512AndAES_256 | PBEWithMD5AndDES
> 一共4种加密算法，前两者基于国密SM3/SM4算法，两个带HMAC的算法因为加入了随机salt的关系，每次加密出来的密文是不同的，推荐使用PBEWithHMACSM3AndSM4算法。
>
> 该框架同样支持配置在Apollo等分布式配置中心的密码。

![1605713037_5fb53c8df318d2c001e76.png!small?1605713038998](https://image.3001.net/images/20201118/1605713037_5fb53c8df318d2c001e76.png!small?1605713038998)

其他jasypt框架的详细使用方法可以查看github页面的readme.md文档中的相关说明。

# 6\. 使用Shc加密Shell脚本

### 6.1 Shc简介

SHC是一个脚本编译程序，使用RC-4加密代码加密shell， 并把shell转换为二进制可执行文件（支持动态链接和静态链接）。

下载地址：<http://www.datsi.fi.upm.es/~frosal/sources/>

### 6.2 安装

linux下使用如下方式安装：

    
    
    # 下载对应版本
    
    wget http://www.datsi.fi.upm.es/~frosal/sources/shc-3.8.9b.tgz
    
    # 解压
    
    tar vxf shc-3.8.9b.tgz
    
    # make安装（可能会出现一些编译错误，请忽略）
    
    cd shc-3.8.9b
    
    make test
    
    make strings
    
    make install
    
    # 如果出现如下编译错误请忽略（只是会缺少一些帮助文档）

![1605713052_5fb53c9c5383ad75bc37e.png!small?1605713052878](https://image.3001.net/images/20201118/1605713052_5fb53c9c5383ad75bc37e.png!small?1605713052878)

    
    
    apt-get install shc

## 6.3 快速上手

 **useage:**

    
    
    CFLAGS=-static shc -v -f {shell脚本}

参数说明：

    
    
    -e date (指定过期时间)
    
    -m message  （指定过期提示的信息）
    
    -f script_name （指定要编译的shell路径）
    
    -r relax security  （在其他服务器执行/在不同操作系统执行，但是安全性会降低）
    
    -v Verbose compilation （输出编译的详细情况）
    
    CFLAGS=-static (采用静态编译，关联的静态库会被引入到可执行文件中，否则最终执行服务器上也需要安装对应的静态库)

 **测试示例：**

如下是一个典型的FTP访问脚本ftp_test.sh：

    
    
    #!/bin/bash
    
    ftp_username=nfsnobody
    
    ftp_password=1qaz2wsx@dbc
    
    
    
    
    function ftp_upload() {
    
    lftp -u ${ftp_username},${ftp_password} sftp://10.211.55.5:20002 << EOF
    
    cd reportcase
    
    put $1
    
    bye
    
    EOF
    
    }
    
    
    
    
    ftp_upload $1

使用shc加密：

    
    
    CFLAGS=-static shc -v -f ftp_test.sh

加密后会生成可执行二进制文件ftp_test.sh.x和ftp_test.sh.x.c。

![1605713087_5fb53cbf122e7c292d9e9.png!small?1605713087627](https://image.3001.net/images/20201118/1605713087_5fb53cbf122e7c292d9e9.png!small?1605713087627)

后者是从来生成可执行程序ftp_test.sh.x的C语言原文件，该原文件包含了不少可以用于识别的信息，所以建议删除避免被识别：

![1605713112_5fb53cd869f60e9b835c3.png!small?1605713113435](https://image.3001.net/images/20201118/1605713112_5fb53cd869f60e9b835c3.png!small?1605713113435)

加密后的可执行文件ftp_test.sh.x也建议重命名成其他名字，例如ftp_test，.sh.x的后缀使用shc加密的特征过于明显，另外可以看到，内容已经被编译成不可识别的可执行文件了：

![1605713159_5fb53d079a94990bd3026.png!small?1605713160755](https://image.3001.net/images/20201118/1605713159_5fb53d079a94990bd3026.png!small?1605713160755)

执行加密后的程序，可以正常上传：

![1605713149_5fb53cfd42efe12e9851c.png!small?1605713149648](https://image.3001.net/images/20201118/1605713149_5fb53cfd42efe12e9851c.png!small?1605713149648)

## 6.4 使用总结

> 在部署服务器上安装shc工具。
>
> 使用CFLAGS=-static shc -v -f {shell}加密你的脚本。
>
> 删除生成的.c文件并重命名.sh.x文件。
>
>
> 特别注意1：加密后的可执行文件不再可以通过shell脚本的source指令被引入，所以涉及到多个脚本调用的，需要把密码整合到主脚本，然后将主脚本加密，被加密的脚本中是可以包含source指令的。
>
> 特别注意2：如果要在研发环境加密脚本后部署到生产环境（跨服务器），需要在加密的时候增加-r参数：CFLAGS=-static shc -r -v -f
> {shell}

