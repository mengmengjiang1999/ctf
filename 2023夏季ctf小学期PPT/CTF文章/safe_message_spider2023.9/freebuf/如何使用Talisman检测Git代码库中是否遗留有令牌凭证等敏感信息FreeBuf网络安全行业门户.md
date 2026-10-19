![](https://image.3001.net/images/20220402/1648871578_6247c89a1175adcfcf1a3.png!small)

## 关于Talisman

Talisman是一款功能强大的敏感数据检测工具，可以通过在目标代码库中设置钩子，来确保代码库中没有开发人员遗留的潜在凭证数据或敏感信息。

在该工具的帮助下，广大开发人员可以验证潜在的SSH密钥、授权令牌和私钥等。

## 工具下载

广大开发人员可以使用下列命令将该工具源码克隆至本地：

    
    
    git clone https://github.com/thoughtworks/talisman.git

## 工具安装

Talisman支持macOS、Linux和Windows操作系统平台，并且能够以下列方式进行安装：

> 1、将Git钩子以全局Git钩子模版和CLI实用工具方式安装；
>
> 2、将Git钩子设置在单个Git库中使用；

### 以全局钩子模版安装

我们建议广大开发人员以Git钩子模版的形式安装和使用Talisman，因为这种方式不仅可以将Talisman安装在现有的Git代码库中，而且还可以安装在我们初始化或克隆的任何新代码库中。

首先，打开终端并运行下列命令，然后下载并安装代码库：

    
    
    curl --silent  https://raw.githubusercontent.com/thoughtworks/talisman/master/global_install_scripts/install.bash > /tmp/install_talisman.bash && /bin/bash /tmp/install_talisman.bash

或

    
    
    curl --silent  https://raw.githubusercontent.com/thoughtworks/talisman/master/global_install_scripts/install.bash > /tmp/install_talisman.bash && /bin/bash /tmp/install_talisman.bash pre-push

接下来，如果你没有在“$PATH”中设置“TALISMAN_HOME”的话，工具将提醒你进行配置。

最后，选择一个Talisman需要扫描的代码库，并设置一个Git钩子为符号连接。这里可以将“SEARCH_ROOT”环境变量设置为目标代码库的路径。

 **处理已有钩子**

在全局范围内安装Talisman不会影响代码库中已有的钩子。如果工具的安装脚本找到了已有钩子，则会显示在控制台中。

### 安装在单个项目中

首先，使用下列命令下载Talisman的安装脚本：

    
    
    curl https://thoughtworks.github.io/talisman/install.sh > ~/install-talisman.sh
    
    chmod +x ~/install-talisman.sh

接下来，将钩子安装进单独的项目中：

    
    
    cd my-git-project
    
    ~/install-talisman.sh

或

    
    
    cd my-git-project
    
    ~/install-talisman.sh pre-commit

 **处理已有钩子**

Talisman需要通过设置来跟现有的Git钩子链接，将下列代码添加进“.pre-commit-config.yaml”即可：

    
    
    -   repo: https://github.com/thoughtworks/talisman
    
        rev: ''  # Update me!
    
        hooks:
    
        # either `commit` or `push` support
    
        -   id: talisman-commit
    
    # -   id: talisman-push

## 工具使用

工具安装完成之后，Talisman将会自动运行并检测代码库中潜在的敏感信息。一旦检测到敏感数据或潜在的安全数据泄露，Talisman便会立刻显示相关的详细信息：

![](https://image.3001.net/images/20220402/1648871661_6247c8edcd857494cd1d4.png!small)

## 以CLI工具使用

如果我们在命令行工具中执行Talisman，将会看到该工具所支持的全部选项参数：

    
    
    -c, --checksum string          校验和计算，建议.talismanrc格式
    
      -d, --debug                   启用调试模式
    
      -g, --githook string             以pre-push或pre-commit方式设置钩子
    
          --ignoreHistory            以当前线程扫描所有文件
    
      -i, --interactive                交互式更新Talisman
    
      -p, --pattern string            扫描文件模式
    
      -r, --reportdirectory string      存储扫描报告的路径
    
      -s, --scan                    扫描Git提交历史
    
      -w, --scanWithHtml            生成HTML报告
    
      -v, --version                 显示Talisman当前版本

## 生成HTML报告

下列命令可以生成HTML格式报告：

    
    
    talisman --scanWithHtml

上述命令将在目标代码库中创建一个名为“talisman_html_report”的目录。此时，我们需要在该代码库中启动一个HTTP服务器，以访问报告内容：

    
    
    python -m SimpleHTTPServer <port> (eg: 8000)

接下来，打开浏览器并输入下列地址，即可获取HTML版本的扫描报告：

    
    
    http://localhost:8000

## 工具使用截图

### 欢迎界面

![](https://image.3001.net/images/20220402/1648871754_6247c94a2e6c565d55cb1.png!small)

### 概述界面

![](https://image.3001.net/images/20220402/1648871761_6247c951e85511e3b0748.png!small)

### 详细报告

![](https://image.3001.net/images/20220402/1648871772_6247c95c659349bcfe698.png!small)

### 错误报告

![](https://image.3001.net/images/20220402/1648871783_6247c967b0acb251e53e7.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/thoughtworks/talisman/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Talisman：** 【[ _GitHub传送门_](https://github.com/thoughtworks/talisman)】

## 参考资料

> [ _https://git-scm.com/docs/git-init#_template_directory_](https://git-> scm.com/docs/git-init#_template_directory)
>
> [ _https://github.com/thoughtworks/talisman#handling-existing-> hooks_](https://github.com/thoughtworks/talisman#handling-existing-hooks)
>
> [ _https://pre-commit.com/_](https://pre-commit.com/)
>
> [
> _https://github.com/typicode/husky/blob/master/DOCS.md_](https://github.com/typicode/husky/blob/master/DOCS.md)

