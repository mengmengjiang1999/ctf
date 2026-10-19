![aaaaa.jpg](https://image.3001.net/images/20190617/1560735553_5d06ef415812a.jpg!small)

## Versionscan

**Versionscan是一款可以帮助安全研究人员评估PHP项目安全性的漏洞扫描及安全报告工具，它可以检测已知的CVE漏洞，并报告目标站点的潜在安全问题。**

目前该工具仍在适配不同的Linux发行版。

## 工具安装

### 使用Composer

    
    
    {
    
        "require": {
    
            "psecio/versionscan":"dev-master"
    
        }
    
    }

该工具当前的依赖组件只有Symfony控制台。

## 工具使用

如果你需要直接对当前项目的PHP版本进行安全检查，可以直接运行下列命令：

    
    
    bin/versionscan

脚本将会检测当前实例的PHP_VERSION信息，并自动生成扫描结果（是否通过安全检测）。输出的扫描结果格式大致如下：

![微信截图_20190617172757.png](https://image.3001.net/images/20190617/15607636873001.png!small)

工具生成的扫描结果会以彩色的形式对“通过”和“未通过”进行高亮标注。

### PHP版本检测

如果你想要给工具指定扫描的PHP版本号，你可以使用php-version参数：

    
    
    bin/versionscanscan --php-version=4.3.2

### 仅报告“未通过”项目

当然了，你也可以命令versionscan只报告未通过安全检测的项目实例：

    
    
    bin/versionscanscan --fail-only

### 扫描结果排序

你还可以使用sort参数来对扫描结果进行排序，排序基于漏洞CVE ID的威胁评级：

    
    
    bin/versionscanscan --sort=risk

### 输出格式

Versionscan的默认会直接将扫描结果以人类可读的形式输出至控制台，不过我们还可以定义其他的输出格式来帮助我们更好地使用这些扫描结果，比如说JSON格式。我们可以使用
--format参数来修改输出格式：

    
    
    vendor/bin/versionscanscan --php-version=5.5 --format=json

目前，该工具支持的输出格式有console、json、xml和html。

HTML输出格式需要使用--output参数来指定文件输出路径：

    
    
    vendor/bin/versionscanscan --php-version=5.5 --format=html --output=/var/www/output

工具会将输出结果写入至一个文件名类似“versionscan-output-20150808.html”的文件中。

## 项目地址

Versionscan：【[GitHub传送门](https://github.com/psecio/versionscan)】

 ***
参考来源：[psecio](https://github.com/psecio/versionscan)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

