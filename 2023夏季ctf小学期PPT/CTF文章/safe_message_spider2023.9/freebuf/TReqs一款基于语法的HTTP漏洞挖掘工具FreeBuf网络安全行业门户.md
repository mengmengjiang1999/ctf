## 关于T-Reqs

T-Reqs全称为Two
Requests，T-Reqs是一款基于语法的HTTP模糊测试漏洞挖掘工具，该工具可以通过发送版本为1.1或更早版本的变异HTTP请求来对目标HTTP服务器进行模糊测试以及漏洞挖掘。该工具主要通过下列三大步骤实现其功能：（1）生成输入；（2）对生成的输入进行变异处理；（3）将变异后的数据发送至目标服务器；

## 生成输入

工具会使用输入的CFG（上下文无关文法）语法来生成HTTP请求。由于下面所示的示例语法是为请求行模糊处理而定制的，因此每个请求行组件及其可能的值都已经明确指定了。此时，我们将能够使用各种形式的请求行生成有效的请求，并从变异的角度将每个请求行组件视为一个单独的单元。

    
    
    '<start>':
    
         ['<request>'],
    
     '<request>':
    
         ['<request-line><base><the-rest>'],
    
     '<request-line>':
    
         ['<method-name><space><uri><space><protocol><separator><version><newline>'],
    
     '<method-name>':
    
         ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'],
    
     '<space>':
    
         [' '],
    
     '<uri>':
    
         ['/_URI_'],
    
     '<protocol>':
    
         ['HTTP'],
    
     '<separator>':
    
         ['/'],
    
     '<version>':
    
         ['0.9', '1.0', '1.1'],
    
     '<newline>':
    
         ['\r\n'],
    
     '<base>':
    
         ['Host: _HOST_\r\nConnection:close\r\nX-Request-ID: _REQUEST_ID_\r\n'],
    
     '<the-rest>':
    
         ['Content-Length: 5\r\n\r\nBBBBBBBBBB'],

## 输入变异

每个组件都可以用两种方式进行标记：字符串变异和树变异（具体参见[
_示例配置_](https://github.com/bahruzjabiyev/T-Reqs-HTTP-Fuzzer/blob/main/config)）。如果组件为字符串变异，那么我们就可以删除、替换或在随机位置插入随机字符。

在下面的示例（左侧）中，删除了协议版本（1）中的最后一个字符，用R替换方法名称中的第三个字母（S），并在URI的开头插入正斜杠。然而，如果一个组件是树变异，那么我们就可以随机、替换或插入到该组件下的一个随机位置。

下面的示例（右侧）显示了应用于请求行组件的三个树变异：（1）方法被协议替换；（2）在当前URI之后插入一个额外的URI；（3）删除现有的proto。

![](https://image.3001.net/images/20220210/1644498748_62050f3c6ffe83aba0fb7.png!small)

## 工具下载&安装&配置

该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

### 源码获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/bahruzjabiyev/T-Reqs-HTTP-Fuzzer.git

## 工具使用

### 工具配置

测试工具应该了解用户对输入的生成和变异的偏好。更具体地说，应该在配置文件中指定输入语法、突变组件和突变首选项等（具体参见[
_示例配置_](https://github.com/bahruzjabiyev/T-Reqs-HTTP-Fuzzer/blob/main/config)）。

### 运行模式

为了能够复现在每次迭代中生成和变异的输入，工具使用了一个种子编号。实际上，在输入的生成和变异的过程中，这个种子编号会作为一个随机的变异种子来使用。根据这些种子提供给工具的方式，它将以下列两种模式中的其中一种运行：单独模式和集体模式。

在单独模式下，工具将根据用户指定的种子来生成和变异输入。在下面的命令中，指定了一个种子（即505）。或者，也可以使用-f选项指定种子列表。

    
    
    python3 main.py -i -c config -s 505

在集体模式（默认）下，工具将从零开始作为种子值，并在每次迭代中递增，直到结束，其中种子的开始和结束编号是可以自定义配置的。

    
    
    python3 main.py -c config

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/bahruzjabiyev/T-Reqs-HTTP-Fuzzer/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **T-Reqs：** 【[ _GitHub传送门_](https://github.com/bahruzjabiyev/T-Reqs-HTTP-Fuzzer)】

## 参考资料

> [
> _https://bahruz.me/papers/ccs2021treqs.pdf_](https://bahruz.me/papers/ccs2021treqs.pdf)
>
> [ _https://www.sigsac.org/ccs/CCS2021/accepted-> papers.html_](https://www.sigsac.org/ccs/CCS2021/accepted-papers.html)
>
> [ _https://github.com/bahruzjabiyev/T-Reqs-HTTP-> Fuzzer/blob/main/config_](https://github.com/bahruzjabiyev/T-Reqs-HTTP-> Fuzzer/blob/main/config)
>
> [ _https://github.com/bahruzjabiyev/T-Reqs-HTTP-> Fuzzer/blob/main/code/feedback-> server.py_](https://github.com/bahruzjabiyev/T-Reqs-HTTP-> Fuzzer/blob/main/code/feedback-server.py)

