![](https://image.3001.net/images/20221115/1668480025_6372fc1964099698c5350.jpg!small)

## 关于jscythe

jscythe是一款功能强大的Node.js环境安全测试工具，在该工具的帮助下，广大研究人员可以利用Node.js所提供的[
_Inspector机制_](https://nodejs.org/en/docs/guides/debugging-getting-started/)来强制性让基于Node.js/Electron/v8实现的进程去执行任意JavaScript代码。值得一提的是，即使是在目标进程的调试功能被禁用的情况下，jscythe也能做到这一点。

当前版本的jscythe1⃣️在Visual Studio Code、Discord和任意Node.js应用程序上进行过完整测试，请广大研究人员放心使用。

## Node.js的Inspector机制是什么？

Node.js 提供的 Inspector 非常强大，不仅可以用来调试 Node.js 代码，还可以实时收集 Node.js 进程的内存、 CPU
Profile 和堆栈内存快照等数据，同时支持静态、动态开启，是一种调试和诊断 Node.js 进程非常好的方式。

通过它可以收集 Node.js 进程的堆快照分析是否有内存泄漏，可以收集 CPU Profile
分析代码的性能瓶颈，从而帮助提高服务的可用性和性能。另外，它支持动态开启，降低了安全风险，同时支持对子线程进行调试，是一个非常强大的工具。

## 工具运行机制

> 1、定位到目标进程；
>
> 2、向目标进程发送SIGUSR1信号，此时将会打开一个端口并开启调试器；
>
> 3、通过在发送SIGUSR1信号之前和之后比较打开的端口来确定调试端口；
>
> 4、从http://localhost:<port>/json获取WebSocket调试URL和会话ID；
>
> 5、使用提供的代码发送一个Runtime. evaluate请求；
>
> 6、搞定！

## 工具下载

该工具基于Rust语言开发，因此我们首先需要在本地设备上安装并配置好Rust环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/evilsocket/jscythe.git

### 项目构建

切换到项目目录下，然后通过cargo命令完成项目代码构建：

    
    
    cd /jscythe
    cargo build --release

## 工具运行

指定一个目标进程，并执行一个基础表达式语句：

    
    
    ./target/debug/jscythe --pid 666 --code "5 - 3 + 2"

从一个文件执行代码：

    
    
    ./target/debug/jscythe --pid 666 --script example_script.js

example_script.js文件中的代码可以require任何代码模块并执行任意代码，例如：

    
    
    require('child_process').spawnSync('/System/Applications/Calculator.app/Contents/MacOS/Calculator', { encoding : 'utf8' }).stdout

通过表达式语句搜索进程信息：

    
    
    ./target/debug/jscythe --search extensionHost --script example_script.js

查看工具帮助信息：

    
    
    jscythe --help

## 工具运行截图

![](https://image.3001.net/images/20221115/1668480135_6372fc8728a2549a8b450.jpeg!small)

## 许可证协议

本项目的开发与发布遵循[ _GPLv_
_3_](https://github.com/evilsocket/jscythe/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **jscythe** ：【[ _GitHub传送门_](https://github.com/evilsocket/jscythe)】

## 参考资料

    
    
    https://nodejs.org/en/docs/guides/debugging-getting-started/

