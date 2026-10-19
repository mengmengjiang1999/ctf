**前言** ： 要问我Goby怎么样，我会坚定回答你“ **最强实时网络空间测绘，没有之一** ”
。初次发现Goby还是来自于同事@hq404的推荐，看完第一反应，真漂亮，我馋了，我要xxxxxx。其Logo和UI做的相当棒，当然不仅拥有华丽的外表，更让我深爱又离不开的即最强实时网络空间测绘，如官方定位一样快速、专业、深入、全面，导致我现在每个项目或是测试工作都是先来Goby跑一波。但是正如上述所说Goby目前着重于资产测绘，而漏洞扫描相关的PoC数量还处于堆砌阶段，又看到Goby的插件市场越来越完善，故打算把Vulmap也以插件形式加入，以互补Goby的PoC，便于发现更多漏洞。

## 0x001 插件效果

### 1.1 插件使用

这里为插件0.1.0版本的演示效果，后续不同版本显示效果可能不同。![](https://image.3001.net/images/20210303/1614763839_603f573fb740e1532fc58.gif!small)

## 0x002 插件开发

### 2.1 编写前序

 **2.1.1 Vulmap工具介绍**

Vulmap 是一款 Web 漏洞扫描和验证工具, 可对 WebApps 进行漏洞扫描, 并且具备漏洞利用功能, 目前支持的 WebApps 包括
ActiveMQ, Flink, Shiro, Solr, Struts2, Tomcat, Unomi, Drupal, Elasticsearch,
Fastjson, Jenkins, Laravel, Nexus, Weblogic, Jboss, Spring, ThinkPHP等。

 **2.1.2 Goby开发版**

写Goby务必安装Goby就是了，Goby分别有不同版本，官方文档中推荐使用Goby开发版。

Goby开发版下载：<https://cn.gobies.org/docs.html>

且里边有一个HelloWorld的例子可以很直观的展示Goby插件的效果和接口位置等。这里的Goby插件主要都是靠JS，我在尝试编写之前是完全没有过编写JS经验的，纯白，自己只是个Python手，凭借着Python的一点经验花了一天半最终实现了这个插件，期间的官方文档起到了很大的帮助，这里要给编写doc的表哥（也可能是表姐）们打call，也找@go0p师傅问了不少问题特此感谢（所以插件开发问题尽管找他233）。

### 2.2 插件目录结构

搬自https://cn.gobies.org/docs.html的插件目录结构。

    
    
    ├── .gitignore          // 忽略构建输出和node_modules文件
    ├── README.md           // 插件介绍文档
    ├── CHANGELOG.md        // 插件更新日志文档
    ├── src
    │   └── extension.js    // 插件源代码
    ├── package.json        // 插件配置清单

主要代码分别package.json和extension.js，前者为插件的配置清单，后者为插件主要代码。

### 2.3 设定插件配置选项

这里就需要编写package.json，Vulmap的内容如下

    
    
    "configuration": {
      "vulmap.py 位置": {
        "type": "string",
        "default": "",
        "description": "请输入vulmap.py的位置(示例:/home/zhzy/vulmap.py)",
        "fromDialog": true
      },
      "python3 命令或位置": {
        "type": "string",
        "default": "python3",
        "description": "请输入在当前环境下的Python3的命令或位置，也可以是绝对路径(示例:python3 or /usr/bin/python3)"
      }
    },

这里主要设定了两个键值，一个是vulmap.py位置用于设定Vulmap扫描器的位置路径，之后需要调用Vulmap进行扫描时使用，没有默认值，因为大家的目录习惯都不同所以需要手动指定。

再就是python3命令或位置需要用户指定python3命令的全称或绝对路径同样用于之后扫描时调用Vulmap，至于填写python、python3、python3.8等等就要看具体自己系统里的名称了，还是一样因为每个人的配置习惯和环境变量不同。

这里有个坑点，我在使用的电脑为Debian
testing(Linux系统)，使用的Goby也是Linux版本的，且平时使用zhzy（uid:1001）的用户，但是由于Goby需要root权限启动我每次都是sudo
./Goby来启动，这就导致Goby识别的环境变量和我当前的环境变量不同，例如我在zhzy用户设置alias python =
‘/xxx/python3.9’但是以sudo运行的Goby会识别python为Linux默认的python2，就导致版本不对应，所以还是建议写入python的绝对路径。

对应效果：

###
![](https://image.3001.net/images/20210303/1614765347_603f5d23621e4d5553826.png!small)2.4
设定入口点

为显示有Vulmap按钮的地方，此时需要编写extension.js文件，内容如下

    
    
    let identical = {
        "web": true,
        "http": true,
        "https": true
    };

然后自定义一个注册命令用于检测是否显示Vulmap按钮

    
    
    Goby.registerCommand('vulmapCheck', function (content) {
        if (identical[content.protocol]) return true;
        return false;
    });

分别会在Goby界面中能够识别到http、https、Web协议的地方显示按钮，这里的按钮位置参考了Packer
Fuzzer插件及Xray插件，因为都是进行Web扫描，故入口点也一样。

对应的效果：![](https://image.3001.net/images/20210303/1614764814_603f5b0eb3a61d8812376.png!small)

###
![](https://image.3001.net/images/20210303/1614764823_603f5b175d796a52688d7.png!small)2.5
扫描的调用及结果

调用Vulmap进行扫描主要为以下内容：

    
    
    function runScanner(targetUrl,taskResult){
        var cp = require('child_process');
        var command  = config["python3 命令或位置"]["default"] + " " + config["vulmap.py 位置"]["default"] + " -u " + targetUrl + " > " + taskResult;
        // Goby.showInformationMessage(command);
        cp.exec(command, (error, stdout, stderr) => {
            console.log(`stdout: ${stdout}`);
            console.log(`stderr: ${stderr}`);
            if (error) {
                console.error(`扫描命令错误: ${error}`);
                Goby.showErrorMessage(`扫描命令错误: ${error}`);
                return;
            } else {
                console.log(command)
                Goby.showInformationMessage(`任务创建成功: ${taskID},请稍等片刻再次点击查看结果`);
            }
        })
    }

调用扫描主要还是靠var
command拼接的系统命令，因为Goby目前无法滚动实时显示执行结果，故目前将扫描结果重定向到文本文件中，在Vulmap扫描中，会在插件目录result中创建对应任务ID的结果文件，再次点击按钮后会判断文件存在并展开文件内容，判断代码如下：

    
    
    if (fs.existsSync(taskResult)) {
        const lines = fs.readFileSync(taskResult).toString()
        if (lines.includes("Scan completed and ended")) {
            if (lines.includes("[+]")) {
                Goby.showSuccessMessage(`vulmap 扫描完成并发现漏洞 !`);
            } else if (lines.includes("[?]")){
                Goby.showSuccessMessage(`vulmap 扫描完成并发现疑似漏洞 ?`);
            } else if (lines.includes("install -r requirements.txt")){
                Goby.showWarningMessage(`vulmap 的依赖还有问题,要先解决 ~`);
            } else {
                Goby.showSuccessMessage(`vulmap 扫描完成，但是没有发现漏洞 ~`);
            }
            Goby.showIframeDia(taskResult, "vulmap scan result", "900", "520");
        } else if (lines.includes("Survival check failed")){
            if (lines.includes("[+]")) {
                Goby.showSuccessMessage(`vulmap 扫描完成并发现漏洞 !`);
            } else if (lines.includes("[?]")){
                Goby.showSuccessMessage(`vulmap 扫描完成并发现疑似漏洞 ?`);
            } else if (lines.includes("install -r requirements.txt")){
                Goby.showWarningMessage(`vulmap 的依赖还有问题,要先解决 ~`);
            } else {
                Goby.showSuccessMessage(`vulmap 扫描完成，但是没有发现漏洞 ~`);
            }
            Goby.showIframeDia(taskResult, "vulmap scan result", "900", "520");
        } else {
            Goby.showWarningMessage(`正在扫描: ${targetUrl} 还没扫完, 请稍等再打开~`);
            Goby.showIframeDia(taskResult, "vulmap scan result", "900", "520");
        }
    } else {
        Goby.showInformationMessage(`运行 vulmap 扫描目标: ${targetUrl}`);
        // 此时开启vulmap扫描
        runScanner(targetUrl,taskResult);
    }

按钮不同阶段的判断效果。![](https://image.3001.net/images/20210303/1614764919_603f5b77209c46b3080e0.png!small)

![](https://image.3001.net/images/20210303/1614764927_603f5b7f2302aa036ef8d.png!small)

![](https://image.3001.net/images/20210303/1614764937_603f5b8961dbc23b70f29.png!small)

当最终判断扫描完成后即可得到完整的扫描结果。

![](https://image.3001.net/images/20210303/1614764986_603f5bba4d048ec1a1a9e.png!small)  
至此Goby中调用第三方扫描器的扫描效果便完成了。

## 0x003 小结

完全是想要编写Goby插件才第一次接触编写JS，因为对JS完全不熟悉很多地方一直在参考现有的其他插件照猫画虎做出来的，主要参考了@go0p师傅的Goby
Xray插件和@Poc Sir师傅的Packer
Fuzzer插件，虽然目前代码简单粗暴但是能实现想象中的扫描效果了，一天半的产物目前可用还是达到预期的效果了。

Vulmap 后续版本中会引入html格式报告，之后也会将插件扫描结果改为html格式，更直观方便大家查看结果。

插件开发文档及Goby开发版下载：  
https://gobies.org/docs.html

关于插件开发在B站都有详细的教学，欢迎大家到弹幕区合影~  
https://www.bilibili.com/video/BV1u54y147PF/

> 作者：zhzyker

