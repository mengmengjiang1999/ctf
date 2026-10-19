# 参数介绍

    
    
    ❯ frida-skeleton -h
    usage: frida-skeleton.py [-h] [-i] [-p PORT] [-s] [-v] [regexps [regexps ...]]
    
    a tool that helps you hook the program you want to hook according to regular
    expressions, more details see: https://github.com/Margular/frida-skeleton
    
    positional arguments:
      regexps               regular expressions that specifies the application
                            names you want to hook, for example "^com\.baidu\.",
                            if it is empty, hook all programs starting with com.
    
    optional arguments:
      -h, --help            show this help message and exit
      -i, --install         install frida server to /data/local/tmp automatically
      -p PORT, --port PORT  reverse tcp port, if specified, manipulate iptables
                            automatically, data flow: mobile | all tcp streams ->
                            mobile | random tcp port -> your pc/laptop | tcp PORT,
                            done by iptables and adb reverse
      -s, --spawn           spawn mode on, attach mode off, same as native frida
      -v, --verbose         verbose output

## -i

自动从github安装对应版本和架构的frida-server，安装是在插入USB后进行的，不会提前安装，frida-server会下载到assets目录下，支持断点续传，并且不会重复下载；下载完之后会自动通过adb
push到/data/local/tmp目录下并自动添加执行权限以及在后台运行

## -p PORT

如-p 8080，会自动利用iptables将所有的TCP流量重定向到安卓的8080端口，并且还会通过adb
reverse将安卓上的8080映射到本机的8080，这样就可以在本机用Burp Suite监听8080端口来抓包了（是不是很方便呢）

## -s

激活spawn模式，默认是attach模式，开启此选项会导致目标进程自动重启，请提前保存重要内容，在此处指定spawn模式将会忽略后续项目的spawn选项配置，使得所有的项目都开启spawn模式，请谨慎使用该选项，优先通过项目配置文件修改

## -v

debug模式，会输出更多的信息

## regexps [regexps …]

frida-skeleton会根据你指定的正则表达式去匹配包名hook对应的程序，支持多个正则表达式

# 教程

接下来介绍frida-skeleton典型的几种用法，根据需要选择自己需要的场景，示例用到的apk可以到这里下载：<https://github.com/Margular/frida-skeleton/releases/download/v2.0.0/Margular.apk>

## 配合BurpSuite抓包，自动绕过证书绑定校验(SSL pinning)

以下几种方式都可以:

    
    
    # 针对io.github.margular进行抓包
    frida-skeleton -vip 8080 io.github.margular
    # 部分匹配也可
    frida-skeleton -vip 8080 margular
    # 精准匹配
    frida-skeleton -vip 8080 ^io\.github\.margular$
    # 支持多个参数，以下会hook所有包名里面有margular或者google的app
    frida-skeleton -vip 8080 margular google  
    

  

需要开启BurpSuite的透明代理模式，且端口要和-p指定的一致:

![burpsuite_invisible_proxy.png](https://image.3001.net/images/20201121/1605929536_5fb88a4031c64592c57d5.png!small)

## 利用内置函数对APK进行模糊hook

  1. 创建工程项目

新版本有了工程项目的概念，首先你需要在projects目录下新建一个目录，目录名随意，然后目录里面放至少一个js文件(例如main.js)和一个配置文件config.yaml，参考default项目，你可以将default项目拷贝为另一个名字省去创建目录的麻烦

  2. 配置config.yaml

可配置项参考[https://wiki.margular.com/frida-skeleton/config](https://wiki.margular.com/zh/frida-skeleton/config)

  3. 编写hook脚本

    
    
    // hook所有类名里面包含io.github.margular的类中的所有函数
    Trace.javaClassByRegex(/io.github.margular.MainActivity/);

  

输出如下，输出太多多的部分我用…省略了，如此会打印出hook到的类的时候的所有方法和所有成员的值

    
    
    [2020-06-16 21:30:48] [INFO] [FridaThread|emulator-5554|io.github.margular] {"tracing":"io.github.margular.MainActivity.getBestLanguage","overloaded":1}
    [2020-06-16 21:30:48] [INFO] [FridaThread|emulator-5554|io.github.margular] {"tracing":"io.github.margular.MainActivity.onClick","overloaded":1}
    [2020-06-16 21:30:48] [INFO] [FridaThread|emulator-5554|io.github.margular] {"tracing":"io.github.margular.MainActivity.onCreate","overloaded":1}
    [2020-06-16 21:30:48] [INFO] [FridaThread|emulator-5554|io.github.margular] {"class":"io.github.margular.MainActivity","methodCount":3,"overloadCount":3}
    [2020-06-16 21:30:48] [INFO] [FridaThread|emulator-5554|io.github.margular] {"regexp":"/io.github.margular.MainActivity/","classCount":1,"methodCount":3,"overloadCount":3}
    [2020-06-16 21:31:02] [INFO] [FridaThread|emulator-5554|io.github.margular] io.github.margular.MainActivity.onClick(android.support.v7.widget.AppCompatButton{9028f9d VFED..C.. ...P.... 341,1348-737,1474 #7f070022 app:id/btnSpeak}|{"class":"android.view.View","methods":["int hashCode()", ... ,"int SCROLL_AXIS_VERTICAL = 2"]})
    [2020-06-16 21:31:02] [INFO] [FridaThread|emulator-5554|io.github.margular] io.github.margular.MainActivity.getBestLanguage(Python)
    [2020-06-16 21:31:02] [INFO] [FridaThread|emulator-5554|io.github.margular] io.github.margular.MainActivity.getBestLanguage(Python) => Python
    [2020-06-16 21:31:02] [INFO] [FridaThread|emulator-5554|io.github.margular] io.github.margular.MainActivity.onClick(android.support.v7.widget.AppCompatButton{9028f9d VFED..C.. ...P.... 341,1348-737,1474 #7f070022 app:id/btnSpeak}|{"class":"android.view.View","methods":["int hashCode()", ... ,"int SCROLL_AXIS_VERTICAL = 2"]}) => undefined

  

## 利用内置函数对APK的函数进行精准hook，适合需要修改函数执行逻辑的场景

    
    
    var MainActivity = Java.use('io.github.margular.MainActivity');
    
    Common.impl(MainActivity.getBestLanguage, function (lang) {
        // 此处可以进行代码修改，这里我直接返回了一个自定义的值
        return '我不知道，反正不是PHP';
    });

  

输出如下，同时函数的执行结果会被修改为我指定的值，Common.impl对frida的implementation实现进行了封装，可以自动打印log，非常方便：

    
    
    [2020-06-16 21:40:23] [INFO] [FridaThread|emulator-5554|io.github.margular] {"tracing":"io.github.margular.MainActivity.getBestLanguage","overloaded":1}
    [2020-06-16 21:40:25] [INFO] [FridaThread|emulator-5554|io.github.margular] io.github.margular.MainActivity.getBestLanguage(Python)
    [2020-06-16 21:40:25] [INFO] [FridaThread|emulator-5554|io.github.margular] io.github.margular.MainActivity.getBestLanguage(Python) => 我不知道，反正不是PHP

  

更多函数请看：[https://wiki.margular.com/frida-skeleton/javascript-api](https://wiki.margular.com/zh/frida-skeleton/javascript-api)

