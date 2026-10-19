  

## 一、开源背景

随着移动互联网的高速发展，人们的生产生活也逐渐从PC电脑端转移到手机等移动端，各类移动App也如雨后春笋般产生。受限于代码的开发质量等原因，App中或多或少的会存在安全漏洞或因开发设计不谨慎引入的违规收集个人信息等合规风险，带漏洞运行的App将严重威胁着网络及用户安全，合规问题则可能受到监管通报甚至存在下架处罚风险。

因此，企业也在加大人力进行漏洞及合规风险挖掘并推进修复等相关工作，目前行业内普遍采用人工审计加自动化检测工具去发现风险。不过随着数量越来越庞大的漏洞，以及App隐私合规等问题的出现，安全人员面临的挑战逐渐升级，故一个有效的漏洞及合规风险自动化检测工具将为安全人员的人工挖掘提供良好补充，也节省了大量时间和人力。

在字节跳动，面对数量众多的App产品，无恒实验室需要在产品上线前发现隐私合规风险，挖掘出安全漏洞，保护用户的数据与隐私安全。无恒实验室对业内自动化App漏洞检测工具进行了充分调研，最终发现这些工具或因为漏报、误报率太高导致需要消耗大量人力对扫描结果进行确认，或因为不开放源码导致无法根据特定的扫描需求进行定制化开发。为了能更好的实现高质量漏洞及隐私合规检测，无恒实验室自主研发了appshark引擎，用于漏洞及隐私合规风险的自动化检测。无恒实验室选择将这个引擎开源，成为一个公共的工具，希望吸引更多业界专家参与打磨，为企业及白帽子做App风险检测提供便利。

  

## 二、全面了解appshark

### 1、appshark的介绍

appshark除了实现行业普遍应用的数据流分析，还将指针分析与数据流分析融合，因而漏洞建模上更精准，规则更灵活，在误报率和漏报率方面有了比较大的改进。

### 2、appshark可以解决什么问题

Appshark可以作为公司内部的Android
App的自动化检测工具，辅助企业发现App的安全漏洞及隐私合规风险，也可以作为白帽子日常App漏洞挖掘的助手，提高漏洞挖掘的效率及产出。

### 3、appshark在字节跳动的表现如何

appshark加载全部规则集时，对于抖音、今日头条等超大规模App，可以在1小时内完成所有分析并输出结果。同时，如前所述，由于appshark引擎中加入了指针分析和数据流分析，可以实现在此基础上进行更加灵活精准的规则设计，在字节跳动内部使用时，大部分规则的误报率和漏报率均已经降至5%以下。

  

## 三、如何使用appshark

> git开源项目地址：http://github.com/bytedance/appshark

接下来以一个常见漏洞案例来展示如何使用appshark：

### 1、ContentProvider漏洞为例

ContentProvider作为安卓中最通用的组件，不少有经验的程序员也经常会写出越权漏洞，如下就是一个非常明显的有越权问题的示例。

  

    
    
    <provider android:name=".VulProvider1"  android:authorities="slipme1" android:exported="true" />

  

    
    
    public class VulProvider1 extends ContentProvider {
    
        @Override
        public ParcelFileDescriptor openFile(@NonNull Uri uri, @NonNull String mode) throws FileNotFoundException {
            File root = getContext().getExternalFilesDir("sandbox");
            String path = uri.getQueryParameter("path");
            return ParcelFileDescriptor.open(new File(root, path), ParcelFileDescriptor.MODE_READ_ONLY);
        }
    }

  

### 2、编写扫描规则

appshark有非常灵活的规则来指定source以及sink，
详细的介绍文档可以参考<https://github.com/bytedance/appshark/blob/main/doc/zh/how_to_write_rules.md>。撰写规则最重要的就是确定source以及sink，一般把外部用户可直接或间接控制的变量视为source，明显openFile的参数0也就是uri是用户可控制的，而sink点比较合适的一个地方是`ParcelFileDescriptor.open`的参数0，因为如果source能够控制`ParcelFileDescriptor.open`参数0，那么基本上就可以读取任何文件了。

因此我们的规则ContentProviderPathTraversal.json如下：

  

    
    
    {
      "ContentProviderPathTraversal": {
        "SliceMode": true,
        "traceDepth": 14,
        "desc": {
          "name": "ContentProviderPathTraversal",
          "category": "",
          "wiki": "",
          "detail": "如果Content Provider重写了openFile，但是没有对Uri进行路径合法性校验，那么攻击者可能通过在uri中插入../的方式访问预期外的文件",
          "possibility": "",
          "model": ""
        },
        "source": {
          "Param": {
            "<*: android.os.ParcelFileDescriptor openFile(*)>": [
              "p0"
            ]
          }
        },
        "sink": {
          "<android.os.ParcelFileDescriptor: android.os.ParcelFileDescriptor open(java.io.File,int)>": {
            "TaintCheck": [
              "p0"
            ]
          }
        }
      }
    }

  

### 3、通过github下载config文件夹

    
    
    git clone https://github.com/bytedance/appshark

  

### 4\. 修改config文件

  1. 将apkPath修改为你想要扫描的apk绝对路径。为了方便，可以在这里下载参考： <https://github.com/nkbai/BypassPathTraversal/blob/main/apk/app-debug.apk>

  3. 指明你要使用的规则，也就是ContentProviderPathTraversal.json文件，这个文件应该放在config/rules目录下，因为appshark是通过这个路径来查找这些规则的。

  4. 指定输出结果保存的目录，默认是当前目录下的out文件，你可以指定一个其他目录。

### 5\. 启动appshark

先下载：<https://github.com/bytedance/appshark/releases/download/0.1/AppShark-0.1-all.jar>，然后启动。

    
    
    java -jar AppShark-0.1-all.jar config/config.json5

  

### 6\. 查看结果

结果在当前目录的out/results.json文件中，里面给出了所有的漏洞列表。关于结果的详细解释请查看https://github.com/bytedance/appshark/blob/main/doc/zh/result.md。
如果对某个具体的漏洞有疑问，可以查看url字段指明的HTML文件。

针对这个漏洞，你应该可以在results.json中看到，存在漏洞的函数（postion），漏洞传播的数据流（target）:

  

    
    
    {
        "details": {
            "Sink": [
                "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>->$r5"
            ],
            "position": "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>",
            "entryMethod": "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>",
            "Source": [
                "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>->@parameter0"
            ],
            "url": "out/vulnerability/6-ContentProviderPathTraversal.html",
            "target": [
                "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>->@parameter0",
                "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>->$r1",
                "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>->$r2_1",
                "<com.security.bypasspathtraversal.VulProvider1: android.os.ParcelFileDescriptor openFile(android.net.Uri,java.lang.String)>->$r5"
            ]
        },
        "hash": "186d1273a64ac711c703e259ce0329fa8a25cf37",
        "possibility": ""
    }

  

## 四、后续计划

appshark会长期维护，欢迎大家使用，欢迎交流提建议以及贡献代码。

