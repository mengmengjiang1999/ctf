![](https://image.3001.net/images/20210507/1620394333_6095415d5b0759bb9db0c.png!small)

## 关于LibAFL

LibAFL是一款高级模糊测试工具，该工具基于Rust开发，并且扩展性和适用性都很强，可以针对Windows、Android、Linux和macOS等系统平台使用。

目前，LibAFL项目由[ _Andrea Fioraldi_](andreafioraldi@gmail.com)和D[ _ominik
Maier_](mail@dmnk.co)负责开发和维护。

LibAFL是一款现成可直接使用的模糊测试工具，该工具支持研究人员进行完全定制化的开发，其中包括以下几个突出功能：

> 运行速度快：我们在编译时尽我们所能，保持运行时开销最小。在frida模式下，手机运行速度可以达到120k次用例执行/秒（使用所有核心）。
>
> 可扩展性强：支持LibAFL线性扩展，并通过TCP扩展到多台设备。
>
>
> 适用性强：你可以随意替换LibAFL的各个模块。比如说，BytesInput只是一个可用的表单输入模块，我们还可以随意添加一个基于AST的输入来进行结构化模糊测试等等。
>
>
> 跨平台使用：LibAFL支持在Windows、macOS、Linux和Android等平台上使用（x86_64和Arch64），LibAFL还可以内置no_std对嵌入式设备和虚拟机监控程序进行模糊测试。

## 工具使用

首先，我们需要在本地设备上安装好Rust语言开发环境。我们强烈建议不要使用Linux发行版包，因为已经过期了。我们建议大家直接安装Rust【[
_文档_](https://www.rust-lang.org/tools/install)】。

接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/AFLplusplus/LibAFL

如果你想要获取最新版并体验尝鲜功能的话，可以运行下列命令：

    
    
    git checkout dev

然后使用下列命令构建代码库：

    
    
    cargo build --release

完成后，需要使用下列命令构建API文档：

    
    
    cargo doc

现在，我们就可以使用下列命令查看LibAFL的参考手册了（需要[ _mdbook_](https://github.com/rust-lang/mdBook)）：

    
    
    cd docs && mdbook serve

我们在项目的./fuzzers目录下提供了大量模糊测试样例，请确保在使用前详细阅读参考文档。

目前功能最完成的模糊测试器为./fuzzers/libfuzzer_libpng，它是一个多核心类libfuzzer的模糊测试器。

## 项目地址

LibAFL：【[ _GitHub传送门_](https://github.com/AFLplusplus/LibAFL)】

## 参考资料

[
_https://github.com/AFLplusplus/LibAFL/blob/main/docs/src/getting_started/setup.md_](https://github.com/AFLplusplus/LibAFL/blob/main/docs/src/getting_started/setup.md)

[ _https://docs.rs/libafl/_](https://docs.rs/libafl/)

[ _https://github.com/rust-lang/mdBook﻿_](https://github.com/rust-lang/mdBook)

