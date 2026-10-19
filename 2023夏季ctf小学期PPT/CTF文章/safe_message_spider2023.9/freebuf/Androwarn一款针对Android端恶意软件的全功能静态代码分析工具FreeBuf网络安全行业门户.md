![Androwarn](https://image.3001.net/images/20190328/1553733893_5c9c190552751.jpg!small)  

## Androwarn介绍

 **Androwarn是一款专为Android端应用程序设计的安全分析工具，该功能的主要功能是检测并提醒用户Android应用程序中潜在的恶意行为。**

在androguard库的帮助下，Androwarn可以通过对目标应用程序的Dalvik字节码和Smali代码进行静态分析，来判断目标应用程序中潜在的恶意行为。分析完成之后，工具会自动生成分析报告，报告中的技术细节划分，取决于用户的设置参数。

## 功能介绍

1、 针对不同类型恶意行为的字节码和数据流结构进行分析：

> a) 电话标识符提取：IMEI, IMSI, MCC, MNC, LAC和CID等等；
>
> b) 设备设置提取：软件版本、使用统计、系统设置和操作日志等等；
>
> c) 地理位置信息：GPS/WiFi地理定位数据；
>
> d) 连接接口信息提取：WiFi凭证、蓝牙MAC地址等；
>
> e) 电话服务滥用：SMS短信发送、电话呼叫；
>
> f) 音频/视频流拦截：电话录音、视频捕捉；
>
> g) 远程连接建立：打开套接字会话、蓝牙配对、APN设置编辑；
>
> h) PIM数据包提取：通讯录、日历、SMS短信、电子邮件和剪贴板等；
>
> i) 外部内存操作：访问SD卡文件；
>
> j) 任意代码执行：执行JNI、UNIX等原生代码，实现提权；
>
> k) 拒绝服务：事件通知、文件删除、进程终止、禁用虚拟键盘、关机/重启；

2、 根据技术细节等级生成分析报告：

> a) 新手建议使用：(-v 1)
>
> b) 高级：(-v 2)
>
> c) 专家：(-v 3)

3、 根据用户设置的格式生成分析报告：

> a) 明文格式txt
>
> b) 基于Bootstrap模板的HTML格式
>
> c) JSON

## 工具使用

### 选项参数

    
    
    $ usage:androwarn [-h] -i INPUT [-o OUTPUT] [-v {1,2,3}] [-r {txt,html,json}]
                     [-d]
                     [-L{debug,info,warn,error,critical,DEBUG,INFO,WARN,ERROR,CRITICAL}]
                     [-w]
     
    version:1.4
     
    optionalarguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            APK file to analyze
      -o OUTPUT, --output OUTPUT
                            Output report file(default
                           "./<apk_package_name>_<timestamp>.<report_type>")
      -v {1,2,3}, --verbose {1,2,3}
                            Verbosity level(ESSENTIAL 1, ADVANCED 2, EXPERT 3)
                            (default 1)
      -r {txt,html,json}, --report {txt,html,json}
                            Report type (default"html")
      -d, --display-report  Display analysis results to stdout
      -L {debug,info,warn,error,critical,DEBUG,INFO,WARN,ERROR,CRITICAL},--log-level {debug,info,warn,error,critical,DEBUG,INFO,WARN,ERROR,CRITICAL}
                            Log level (default"ERROR")
      -w, --with-playstore-lookup
                            Enable online lookupson Google Play

### 使用样例

    
    
    $python androwarn.py -i my_application_to_be_analyzed.apk -r html -v 3

默认配置下，工具会在命令行的当前目录下生成分析报告。如果用户选择的是HTML格式的报告，工具会生成一份单独的HTML文件，并自动潜入CSS/JS资源。

### 参考样本

项目目录中还给广大用户提供了一份用于分析参考的恶意软件样本，该样本中整合了多种恶意行为。APK文件位于_SampleApplication/bin/目录下，HTML报告可从_SampleReports目录下获取。

## 工具安装与依赖组件

1、 Python 2.7 + androguard + jinja2+ play_scraper + argparse

2、 最简单的工具安装与环境配置方法：

    
    
    $ pip install androwarn

然后直接使用”$ androwarn”命令。

3、 或者你也可以使用git命令把项目代码克隆到本地：

    
    
    $ git clone git://github.com/maaaaz/androwarn.git

然后运行下列命令完成依赖组建的安装：

    
    
    $ pip install -r requirements.txt

## 许可证协议

本项目遵循[GNU](http://www.gnu.org/licenses/)许可证协议。

 ***
参考来源：[maaaaz](https://github.com/maaaaz/androwarn)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

