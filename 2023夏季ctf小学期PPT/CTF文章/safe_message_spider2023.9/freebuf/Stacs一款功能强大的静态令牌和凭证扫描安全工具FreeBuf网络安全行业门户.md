![](https://image.3001.net/images/20211224/1640326534_61c56586a7f6d6c36c953.png!small)

## 关于Stacs

Stacs一款功能强大的静态令牌和凭证扫描工具，本质上来说，Stacs是一个基于YARA的静态凭证扫描工具，该工具支持二进制文件格式、嵌套文档分析、可组合规则集和忽略列表以及SARIF报告。

当前版本的Stacs支持tarballs、gzip、bzips、zips、7z、iso、rpm和xz文件的递归解包。由于Stacs处理的是它所检测到的文件类型，而不是文件名，因此该工具将自动支持基于这些类型的适当文件格式，例如Docker镜像、Android
APK和Java JAR文件。

## Stacs的适用人群

Stacs可以为任何需要涉及到二进制文件的安全团队提供帮助，因为Stacs可以为开发人员提供自动检查目标代码版本中是否意外包含静态凭据和敏感数据的能力。

然而，这并不意味着Stacs不适用于Saas应用层序、企业软件或者产品源代码。比如说，我们可以使用Stacs在上传到公共或私有容器的Docker镜像中寻找静态凭证。除此之外，我们还可以通过Stacs搜索意外编译到可执行文件、移动设备软件包和“企业文档”（如Java应用程序服务器使用的文档）中的凭据。

## 工具使用

使用Stacs最简单的方法就是通过Docker
Hub中发布的Docker镜像了。不过，Stacs也可以直接通过Python的PyPI来安装，或者你也可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/stacscan/stacs.git

### Docker使用

使用发布的Docker镜像，Stacs将该能够直接帮助我们完成组件扫描。我们可以直接在扫描容器中加载大量文件，并交给Stacs的Docker镜像进行扫描。

比如说，我们可以使用下列命令直接扫描当前目录中的所有内容：

    
    
    docker run \
    
        --rm \
    
        --mount type=bind,source=$(pwd),target=/mnt/stacs/input \
    
    stacscan/stacs:latest

默认配置下，Stacs会直接将所有的发现以SARIF格式直接输出至STDOUT，并确保一切数据按顺序排列，所有的信息都会被记录并发送至STDERR。

### PyPI安装

我们也可以通过Python的PyPi来安装Stacs。此时我们可以通过“stacs”命令直接在本地开发环境中执行项目扫描。

我们可以使用下列命令直接通过PyPI安装Stacs：

    
    
    pip install stacs

## 微软SARIF报告查看

当前版本的Stacs数据输出格式仅支持SARIF v2.1.0，下图显示的是我们利用Stacs在一个Docker镜像中发现的结果：

![](https://image.3001.net/images/20211224/1640326590_61c565be7b8f662cdc27d.png!small)

## 项目地址

Stacs：【[ _GitHub传送门_](https://github.com/stacscan/stacs)】

## 参考资料

  * [ _https://virustotal.github.io/yara/_](https://virustotal.github.io/yara/)
  * [ _https://github.com/stacscan/stacs-rules_](https://github.com/stacscan/stacs-rules)
  * [ _https://microsoft.github.io/sarif-web-component/_](https://microsoft.github.io/sarif-web-component/)
  * [ _https://github.com/docker/for-mac/issues/3677_](https://github.com/docker/for-mac/issues/3677)

