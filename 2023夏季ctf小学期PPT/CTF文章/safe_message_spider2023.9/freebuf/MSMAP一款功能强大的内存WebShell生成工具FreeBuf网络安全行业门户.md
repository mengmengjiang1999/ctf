![](https://image.3001.net/images/20221129/1669727683_638605c32cdb6174be249.jpg!small)

## 关于MSMAP

MSMAP是一款功能强大的内存WebShell生成工具，该工具提供了各种容器、组件、编码器、WebShell、代理和管理客户端等工具，可以帮助广大研究人员更好地生成、管理和使用WebShell。

## 工具功能

> 1、动态菜单
>
> 2、自动补全
>
> 3、脚本生成
>
> 4、轻量级模式
>
> 5、图形化接口

### 容器

> Java：Tomcat7、Tomcat8、Tomcat9、Tomcat10、Resin4、Sping*、JVM*； .NET：IIS； PHP
> Python

### WebShell/代理

    
    
    CMD / SH、AntSword、JSPJS、Behinder、Godzilla

### 解码器/解密器/哈希工具

> 解码器：Base64；
>
> 解密器：XOR、RC4、AES128、AES256；
>
> 哈希工具：MD5、SHA128、SHA256；

## 工具下载&运行

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hosch3n/msmap.git

然后切换到项目目录下，运行下列命令即可使用MSMAP：

    
    
    cd msmap
    
    python generator.py

注意：必须设置一个独立密码，并且参数选项是大小写敏感的。

## 高级使用

编辑config/environment.py：

    
    
    # 自动补全
    
    auto_build = True 
    
    # Base64编码类文件
    
    b64_class = True
    
    # 生成脚本文件
    
    generate_script = True
    
    # 编译器绝对路径
    
    java_compiler_path = r"~/jdk1.6.0_04/bin/javac"
    
    dotnet_compiler_path = r"C:\Windows\Microsoft.NET\Framework\v2.0.50727\csc.exe"

编辑gist/java/container/tomcat/servlet.py：

    
    
    // Servlet路径模式
    
    private static String pattern = "*.xml";

如果在WsFilter中使用了加密编码器，则密码必须设置为和路径相同，比如说/passwd。

下列命令可以自动拷贝剪切板内容：

    
    
    pip3 install pyperclip

## 工具使用样例

### CMD/SH

系统命令搭配Base64编码器 | 注入Tomcat Valve：

    
    
    python generator.py Java Tomcat Valve Base64 CMD passwd

### AntSword

JSP类型搭配默认编码器 | 注入Tomcat Valve：

    
    
    python generator.py Java Tomcat Valve RAW AntSword passwd

JSP类型搭配aes_128_ecb_pkcs7_padding_md5 编码器 | 注入Tomcat Listener：

    
    
    python generator.py Java Tomcat Listener AES128 AntSword passwd

JSP类型搭配rc_4_sha256 编码器 | 注入Tomcat Servlet：

    
    
    python generator.py Java Tomcat Servlet RC4 AntSword passwd

JSP类型搭配xor_md5 编码器 | AgentFiless注入HttpServlet：

    
    
    python generator.py Java JDK JavaX XOR AntSword passwd

JSPJS类型搭配aes_128_ecb_pkcs7_padding_md5 编码器 | 注入Tomcat WsFilter：

    
    
    python generator.py Java Tomcat WsFilter AES128 JSPJS passwd

JSPJS类型搭配xor_md5 编码器 | 注入Spring Handler：

    
    
    python generator.py Java Spring Handler XOR JSPJS passwd

### Behinder

default_aes类型 | 注入Tomcat Valve：

    
    
    python generator.py Java Tomcat Valve AES128 Behinder rebeyond

default_xor_base64类型 | 注入Spring Interceptor：

    
    
    python generator.py Java Spring Interceptor XOR Behinder rebeyond

### Godzilla

JAVA_AES_BASE64类型 | 注入Tomcat Valve：

    
    
    python generator.py Java Tomcat Valve AES128 Godzilla superidol

JAVA_AES_BASE64类型 | AgentFiless注入HttpServlet：

    
    
    python generator.py Java JDK JavaX AES128 Godzilla superidol

JAVA_AES_BASE64类型 | 注入Spring Handler：

    
    
    python generator.py Java Spring Handler AES128 Godzilla superidol

## 工具使用演示

![](https://image.3001.net/images/20221129/1669727855_6386066f1699a529b2afa.png!small)

![](https://image.3001.net/images/20221129/1669727861_63860675a8e2fc507e1a3.png!small)

![](https://image.3001.net/images/20221129/1669727868_6386067c2098bddb3b1c1.png!small)

## 项目地址

 **MSMAP** ：【[ _GitHub传送门_](https://github.com/hosch3n/msmap)】

## 参考资料

> [
> _https://github.com/BeichenDream/GodzillaMemoryShellProject_](https://github.com/BeichenDream/GodzillaMemoryShellProject)
>
> [ _https://github.com/AntSwordProject/AntSword-JSP-> Template_](https://github.com/AntSwordProject/AntSword-JSP-Template)
>
> [ _https://github.com/yzddmr6/As-> Exploits/tree/master/core/memshell_manage_](https://github.com/yzddmr6/As-> Exploits/tree/master/core/memshell_manage)
>
> [
> _https://github.com/rebeyond/Behinder_](https://github.com/rebeyond/Behinder)
>
> [ _https://github.com/veo/wsMemShell_](https://github.com/veo/wsMemShell)
>
> [ _https://github.com/wh1t3p1g/ysomap_](https://github.com/wh1t3p1g/ysomap)

