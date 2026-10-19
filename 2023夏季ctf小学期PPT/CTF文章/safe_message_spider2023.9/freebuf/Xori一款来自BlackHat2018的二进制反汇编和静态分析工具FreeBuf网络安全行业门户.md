**Xori是一个自动化的反汇编和静态分析库，它使用shellcode或PE二进制文件并提供分类分析数据。**

## 体系结构：

> I386 X86-64

## 文件格式

> PE，PE + 普通的shellcode

## 目前的特点

> 1.输出json格式结果
>
> 2.反汇编函数
>
> 3.支持导入。

> 管理图像和堆栈内存。
>
> Light仿真 - 用于枚举所有路径（寄存器，堆栈，某些指令）。
>
> 完全仿真 - 仅遵循代码的路径（性能缓慢）。
>
> 模拟TEB和PEB结构。
>
> 评估基于DLL导出的函数。
>
> 根据引用的内存位置显示字符串。
>
> 使用FLIRT样式签名（快速库识别和识别技术）。
>
> 允许使用模拟PEB。
>
> 在不返回的调用后检测填充。
>
> 尝试从偏移中识别函数引用。  
>

## 它还一些的不足：

> 引擎是互动的。
>
> 不能转储字符串。
>
> 不处理非可执行的部分。
>
> 对非pe文件不启用TEB和PEB。
>
> 只模拟了一部分的x86指令。
>
> 修补和组装。
>
> 没有其他插件或第三方脚本。

## Requirements

`rustc 1.27.0`

### 为OSX和Linux Distros安装rust

`curl <https://sh.rustup.rs> -sSf | sh`

### 为Windows安装防rust

<https://www.rust-lang.org/en-US/other-installers.html>

选择：

    
    
    x86_64-pc-windows-gnu
    x86_64-pc-windows-msvc（需要Visual Studio构建工具）
    

## 安装

### 1.Build Xori

此命令还将创建其他二进制文件，例如 pesymbols 和 peinfo。

    
    
    git clone https://github.com/endgameinc/xori.git
    cd xori
    cargo build --release
    

### 2.创建xori.json配置文件

    
    
    cp xori.json.example xori.json
    [edit if desired]
    

### 3.（可选）构建symbols文件

如果要创建自己的symbols文件，则需要将dll文件夹设置为存储Windows dll的位置。

    
    
    "function_symbol32": "./src/analysis/symbols/generated_user_syswow64.json",
    "function_symbol64": "./src/analysis/symbols/generated_user_system32.json",
    "symbol_server": {
        "dll_folder32": "./dlls/32bit",
        "dll_folder64": "./dlls/64bit"
    

运行pesymbols来覆盖function_symbol json`./target/release/pesymbols`

## 运行

`./target/release/xori -f test.exe`

### 运行所有测试

`cargo test`

### 浏览器GUI

| Chrome | Firefox | Safari | IE |Opera|| :------| ------: | :------: |
:------: | :------: || Latest ✔ | Latest ✔ | Latest ✔ | x | Latest ✔ |

### 要求

`nodejs yarn（UI dev可选）`

### Build

    
    
    cd gui
    npm install
    

### 运行

在一个终端输入

    
    
    cd gui
    node src/server.js
    

在另一个终端输入

    
    
    cd gui
    npm start
    

它将打开您的默认浏览器到<http://localhost:3000/>。后端API正在侦听localhost：5000。

 ***参考来源：[GitHub](https://github.com/endgameinc/xori)，周大涛编译，转载请注明来自
FreeBuf.COM**

