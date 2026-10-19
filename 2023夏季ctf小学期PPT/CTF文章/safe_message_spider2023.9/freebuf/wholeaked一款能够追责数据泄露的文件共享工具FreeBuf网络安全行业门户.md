![](https://image.3001.net/images/20220423/1650704179_6263bf33582440aa13381.png!small)

## 关于wholeaked

wholeaked是一款功能强大的文件共享工具，该工具基于go语言开发，可以帮助广大系统管理员和安全研究人员在组织发生数据泄露的时候，迅速找出数据泄露的“始作俑者”。

wholeaked可以获取被共享的文件信息以及接收人列表，并且会为每一个接收人创建一个唯一的签名，然后将其嵌入到共享的文件中。接下来，wholeaked将能够使用Sendgrid、AWS
SES或SMTP集成方案来将文件自动发送到相应的接收人手中。当然了，如果你不想通过电子邮件来发送共享文件的话，我们也可以手动共享文件。

值得一提的是，wholeaked适用于所有文件类型。

## 文件共享流程

![](https://image.3001.net/images/20220423/1650704190_6263bf3e6ad8e8653090e.png!small)

## 签名验证

如果想要弄清楚是谁泄漏了文档的话，我们只需要将泄漏的文件提供给wholeaked，然后wholeaked将会通过比对数据库中的签名来判断到底是谁泄漏了我们的文件：

![](https://image.3001.net/images/20220423/1650704198_6263bf4622c7b51b3c716.png!small)

## 文件类型和检测模式

wholeaked可以将唯一签名添加到文件的不同部分，可用的检测模式如下：

> 文件哈希：检测文件的SHA256哈希，支持所有文件类型；
>
> 二进制：直接将签名添加到文件的二进制数据中，支持所有文件类型；
>
> 元数据：将签名添加到文件的元数据中，支持的文件类型包括：PDF、DOCX、XLSX、PPTX、MOV、JPG、PNG、GIF、EPS、AI、PSD；
>
> 水印：在文件的文本中插入一个不可见的签名，仅支持PDF文件；

## 工具安装

### 源码安装

广大研究人员可以访问该项目的【[
_Releases页面_](https://github.com/utkusen/wholeaked/releases/latest)】下载预构建的工具代码，并直接运行：

    
    
    unzip wholeaked_0.1.0_macOS_amd64.zip
    
    ./wholeaked --help

### GitHub安装

除此之外，我们也可以在本地设备安装并配置好Go环境后，使用下列命令将该项目源码克隆至本地：

    
    
    go install github.com/utkusen/wholeaked@latest

## 依赖组件

wholeaked需要使用exiftool来将签名添加到文件的元数据中，如果你不使用该功能，就可以不用安装exiftool。

exiftool的安装步骤如下：

 **# 基于Debian的Linux系统**

    
    
    apt install exiftool

 **# macOS**

    
    
    brew install exiftool

 **# Windows**

    
    
    从https://exiftool.org/下载exiftool，然后将exiftool.exe放到wholeaked目录下。

wholeaked还需要使用pdftotext来验证PDF文件中的水印如果你不使用该功能，就可以不用安装pdftotext。

pdftotext的安装步骤如下：

> 1、Linux系统需要下载“Xpdf”命令行工具，下载地址：https://www.xpdfreader.com/download.html；
>
> 2、提取压缩包，并切换到“bin64”目录；
>
> 3、将pdftotext（或pdftotext.exe）拷贝到wholeaked目录下即可；
>
> 4、基于Debian的Linux系统可以运行下列命令直接安装pdftotext：
    
    
    apt install libfontconfig

## 工具使用

### 基础使用

wholeaked需要使用“-n”参数指定项目名称，“-f”参数指定需要添加签名的文件路径，“-t”参数指定目标接收人列表：

    
    
    ./wholeaked -n test_project -f secret.pdf -t targets.txt

其中的targets.txt需要包含接收人名称和电子邮件地址：

    
    
    Utku Sen,utku@utkusen.com
    
    Bill Gates,bill@microsoft.com

执行完成后，工具将会生成下列文件：

    
    
    test_project/files/Utku_Sen/secret.pdf
    
    test_project/files/Bill_Gates/secret.pdf

默认配置下，wholeaked会讲签名添加到所有可用的文件位置，我们也可以使用下列命令指定需要添加文件签名的位置：

    
    
    ./wholeaked -n test_project -f secret.pdf -t targets.txt -binary=false -metadata=false -watermark=false

### 发送电子邮件

如果你想通过电子邮件来共享文件的话，需要在CONFIG文件中进行相应的配置。

### 验证泄漏的文件

我们可以使用“-validate”选项来验证泄漏文件的人：

    
    
    ./wholeaked -n test_project -f secret.pdf -validate

## 工具使用演示

 **视频地址：**[
_https://www.you*tube.com/watch?v=EEDtXp9ngHw_](https://www.youtube.com/watch?v=EEDtXp9ngHw)

## 许可证协议

本项目的开发与发布遵循BSD-3-Clause开源许可证协议。

## 项目地址

 **wholeaked：** 【[ _GitHub传送门_](https://github.com/utkusen/wholeaked)】

## 参考资料

> [ _https://exiftool.org/_](https://exiftool.org/)
>
> [
> _https://www.xpdfreader.com/download.html_](https://www.xpdfreader.com/download.html)
>
> [
> _https://github.com/utkusen/wholeaked/releases/latest_](https://github.com/utkusen/wholeaked/releases/latest)

