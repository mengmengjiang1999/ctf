## 关于Fennec

Fennec是一个针对类Unix操作系统的多功能事件应急响应工具箱，Fennec基于Rust开发，可以帮助广大研究人员在类Unix操作系统上实现网络安全事件应急响应。除此之外，Fennec还支持广大研究人员自行开发相关的配置文件，并增加工具箱中的实用工具。

## 功能介绍

> 1、单独的静态编译的二进制文件；
>
> 2、可以执行任何osquery SQL查询；
>
> 3、支持执行系统命令；
>
> 4、使用正则表达式解析任何文本文件；
>
> 5、支持收集系统日志和文件；
>
> 6、以结构化格式返回数据；
>
> 7、支持多种输出格式（JSONL、CSV和KJSON）；
>
> 8、灵活的配置文件；
>
> 9、数据结果直接写入ZIP文件以节省空间；
>
> 10、运行速度非常快；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/AbdulRhmanAlfaifi/Fennec.git

## 依赖组件

Fennec的正常工作需要依赖于osquery，首先我们需要修改“deps/<TARGET_OS>/config.yaml”配置文件。

接下来，使用下列命令构建代码：

 **动态链接：**

    
    
    cargo build --release

 **静态链接（编译所有组件）：**

    
    
    RUSTFLAGS="-C target-feature=+crt-static" cargo build --release --target x86_64-unknown-linux-gnu

除此之外，我们还可以直接访问该项目的【[
_Releases页面_](https://github.com/AbdulRhmanAlfaifi/Fennec/releases/tag/v0.2.1)】下载工具预编译代码。

## 工具使用

    
    
    fennec 0.1.0
    
    AbdulRhman Alfaifi <aalfaifi@u0041.co>
    
    Aritfact collection tool for *nix systems
    
     
    
    USAGE:
    
        fennec_x86_64-unknown-linux-gnu [OPTIONS]
    
     
    
    OPTIONS:
    
        -c, --config <FILE>             设置自定义配置文件
    
        -f, --log-file <FILE>             设置日志文件名称，默认为fennec.log
    
        -h, --help                      打印工具帮助信息
    
        -l, --log-level <LEVEL>   设置日志等级，默认为info，可选trace、debug、info、error
    
        -o, --output <FILE>            设置输出文件名，默认为ABDULRHMAN-PC.zip
    
        --osquery-path <PATH>       设置osquery路径，默认为./osqueryd
    
        --output-format <FORMAT> 设置输出格式，默认为JSON，可选JSONL、CSV、KJSON
    
        -q, --quiet                     不将日志输出至STDOUT
    
        --show-config                 显示嵌入的配置文件
    
    -V, --version                   打印工具版本信息

## 工具使用样例

### 默认配置

下面给出的使用样例，测试平台为Ubuntu 20，工具配置为默认配置：

![](https://image.3001.net/images/20220501/1651402171_626e65bb7732924053b6c.gif)

### 结合Kuiper使用

我们需要使用下列参数选项来运行Fennec，输出的数据才是Kuiper支持的格式：

    
    
    sudo ./fennec --output-format kjson

或者，我们也可以直接在配置文件中添加“args”字段：

    
    
    args:
    
      - "--output-format"
    
      - "kjson"

重新编译后再次执行Fennec：

    
    
    sudo ./fennec

然后将输出结果ZIP文件上传至Kuiper即可：

![](https://image.3001.net/images/20220501/1651402093_626e656d7988c60d514f6.gif)

## 测试平台

> Ubuntu 20.04.3 LTS（x86_64）
>
> Ubuntu 19.04（x86_64）
>
> Ubuntu 18.04.6 LTS（x86_64）
>
> Ubuntu 17.04（x86_64）
>
> Ubuntu 16.04.7 LTS（x86_64）
>
> Ubuntu 15.10（x86_64）
>
> Ubuntu 14.04.6 LTS（x86_64）
>
> Ubuntu 13.04（x86_64）
>
> Ubuntu 12.04.5 LTS（x86_64）
>
> CentOS 8.4.2105（x86_64）
>
> CentOS 7.9.2009（x86_64）
>
> CentOS 6.10（x86_64）
>
> Ubuntu 20.04（aarch64）
>
> MacOS Monterey v12.0.1（x86_64）

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/AbdulRhmanAlfaifi/Fennec/blob/master/LICENSE-APACHE)开源许可证协议。

## 项目地址

 **Fennec：** 【[ _GitHub传送门_](https://github.com/AbdulRhmanAlfaifi/Fennec)】

## 参考资料

> [
> _https://github.com/DFIRKuiper/Kuiper﻿_](https://github.com/DFIRKuiper/Kuiper)

