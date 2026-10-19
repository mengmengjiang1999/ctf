**今天给大家介绍的是一款名叫Xori的自动化反编译与静态分析工具，广大研究人员可以利用该工具来对PE32、32+和Shellcode进行审计分析。**

![a.png](https://image.3001.net/images/20190331/1554015342_5ca0646ec32b8.png!small)

### 支持架构

    
    
    i386
    
    x86-64

### 文件格式

    
    
    PE,PE+
    
    明文shellcode

## 工具功能

1、 管理栈内存；

2、 轻量级模拟：枚举全部路径（寄存器、栈和某些指令）；

3、 完整模拟：仅跟踪代码路径（性能慢）；

4、 模拟TEB&PEB结构；

5、 显示引用内存地址的字符串；

6、 使用FLIRT风格签名；

7、 识别偏移量地址中的函数引用。

## 工具依赖组件

    
    
    rustc 1.27.0

### rust安装-macOS & Linux发行版

    
    
    curl https://sh.rustup.rs -sSf | sh

### rust安装-Windows

rust工具集下载地址：【[rustup.exe](https://www.rust-lang.org/en-US/other-installers.html#other-ways-to-install-rustup)】

![b.png](https://image.3001.net/images/20190331/1554015385_5ca06499758ea.png!small)  

该工具将会安装rust的编译器-rustc，rust包管理器-cargo，以及其他用于rut环境下的实用工具。

### 安装rust依赖组件

如果大家遇到了下图所示的情况，是因为没有安装Build Tools for Visual
Studio【[解决方案](https://github.com/endgameinc/xori#install-rust-toolchain)】：

![c.png](https://image.3001.net/images/20190331/1554015400_5ca064a8e52e5.png!small)  

1、 按照提示要求，点击上述链接，或直接点击【[这里](https://aka.ms/buildtools)】；

2、 取消rustup-init.exe；

3、 回到浏览器，往下滑，点开“Tools forVisual Studio 2017”标签页，下载“Build Tools for Visual
Studio2017”；

![d.png](https://image.3001.net/images/20190331/1554015408_5ca064b0abf4d.png!small)  

4、 运行下载好的可执行文件；

选择“Visual C++ build tools”并点击安装，安装完成后关闭安装程序：

![e.png](https://image.3001.net/images/20190331/1554015414_5ca064b6dd898.png!small)  

### 安装rust工具链

运行rustup.exe，你将会看到如下所示的输出：

![f.png](https://image.3001.net/images/20190331/1554015428_5ca064c4a437d.png!small)  

成功安装后，你将会看到rust编译器-rustc、rust包管理器-cargo和其他实用工具已经全部安装完成了。路径分别为“C:\Users\%username%\\.cargo“和”C:\Users\%username%\\.rustu”。

![g.png](https://image.3001.net/images/20190331/1554015435_5ca064cbd3125.png!small)  

## Xori安装与配置

下载和构建Xori代码：

    
    
    git clone <https://github.com/endgameinc/xori.git>
    
    cd xori
    
    cargo build --release

创建xori.json配置文件：

    
    
    cpxori.json.example xori.json
    
    [editif desired]

构建符号文件（可选项）：

如果你想要创建自己的符号文件，你需要设置dll目录。

    
    
    "function_symbol32":"./src/analysis/symbols/generated_user_syswow64.json",
    
    "function_symbol64":"./src/analysis/symbols/generated_user_system32.json",
    
    "symbol_server":{
    
           "dll_folder32":"./dlls/32bit",
    
           "dll_folder64":"./dlls/64bit"

运行pesymbols覆盖function_symbol文件：

    
    
    ./target/release/pesymbols

## 工具运行

    
    
    ./target/release/xori-f test.exe

### 运行所有测试

    
    
    cargo test

## 浏览器GUI

![h.png](https://image.3001.net/images/20190331/1554015521_5ca06521d1dfe.png!small)  

### 工具要求

    
    
    Nodejs
    
    Yarn

### 构建

    
    
    cd gui
    
    npm install

## 运行

在一个终端下：

    
    
    cd gui
    
    node src/server.js

在另一个终端下：

    
    
    cd gui
    
    npm start

浏览器默认地址为<http://localhost:3000/>，后端API监听地址为<http://localhost:5000/>。

## 项目地址

Xori：【[GitHub传送门](https://github.com/endgameinc/xori)】

***参考来源：[gildasio](https://github.com/gildasio/h2t)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

