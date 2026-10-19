## 关于Whispers

Whispers是一款功能强大的静态代码分析工具，该工具可以帮助广大研究人员解析各种常见的数据格式，并搜索硬编码凭证和危险函数。Whispers支持在命令行终端中运行，或者也可以将其集成到CI/CD管道中。

## 检测功能

> 密码
>
> API令牌
>
> AWS密钥
>
> 私钥
>
> 凭证哈希
>
> 身份认证令牌
>
> 危险函数
>
> 敏感文件

## 支持的格式

Whispers本质上来说是一款结构化的问版本解析工具，而不是一个代码分析工具。

下面列出的是当前版本Whispers支持的数据格式：

> YAML
>
> JSON
>
> XML
>
> .npmrc
>
> .pypirc
>
> .htpasswd
>
> .properties
>
> pip.conf
>
> conf / ini
>
> Dockerfile
>
> Dockercfg
>
> Shell scripts
>
> Python3

Python3文件会以AST进行解析，因为这是原生语言支持。

## 声明和赋值格式

该工具可以将下列语言文件解析为文本，并检测常见的变量声明和赋值模式：

> JavaScript
>
> Java
>
> Go
>
> PHP

## 特殊格式支持

> AWS凭证文件
>
> JDBC连接字符串
>
> Jenkins配置文件
>
> SpringFramework配置文件
>
> Java属性文件
>
> Dockercfg注册认证文件
>
> GitHub令牌

## 工具安装

### 通过PyPI安装

    
    
    pip3 install whispers

### GitHub安装

    
    
    git clone https://github.com/Skyscanner/whispers
    
    cd whispers
    
    make install

## 工具使用

### 命令行接口

    
    
    whispers --help
    
    whispers --info
    
    whispers source/code/fileOrDir
    
    whispers --config config.yml source/code/fileOrDir
    
    whispers --output /tmp/secrets.yml source/code/fileOrDir
    
    whispers --rules aws-id,aws-secret source/code/fileOrDir
    
    whispers --severity BLOCKER,CRITICAL source/code/fileOrDir
    
    whispers --exitcode 7 source/code/fileOrDir

### Python

    
    
    from whispers.cli import parse_args
    
    from whispers.core import run
    
     
    
    src = "tests/fixtures"
    
    configfile = "whispers/config.yml"
    
    args = parse_args(["-c", configfile, src])
    
    for secret in run(args):
    
      print(secret)

## 工具配置

Whispers工具支持多种配置选项，我们可以根据需要来配置是否在结果中互殴文件路径、密钥或其他值等。config.yml的参考格式如下：

    
    
    include:
    
      files:
    
        - "**/*.yml"
    
     
    
    exclude:
    
      files:
    
        - "**/test/**/*"
    
        - "**/tests/**/*"
    
      keys:
    
        - ^foo
    
      values:
    
        - bar$
    
     
    
    rules:
    
      starks:
    
        message: Whispers from the North
    
        severity: CRITICAL
    
        value:
    
          regex: (Aria|Ned) Stark
    
          ignorecase: True

最快的配置方法就是将config.yml文件拷贝至一个新的文件中，然后直接将其以参数形式传递给Whispers：

    
    
    whispers --config config.yml --rules starks src/file/or/dir

## 自定义规则

我们可以通过下列方式，在[
_whispers/rules_](https://github.com/Skyscanner/whispers/blob/master/whispers/rules)文件中添加和编辑自己的自定义规则：

    
    
    rule-id:  # unique rule name
    
      description: Values formatted like AWS Session Token
    
      message: AWS Session Token  # report will show this message
    
      severity: BLOCKER           # one of BLOCKER, CRITICAL, MAJOR, MINOR, INFO
    
     
    
      key:        # specify key format
    
        regex: (aws.?session.?token)?
    
        ignorecase: True   # case-insensitive matching
    
     
    
      value:      # specify value format
    
        regex: ^(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9\+\/]{270,450}$
    
        ignorecase: False  # case-sensitive matching
    
        minlen: 270        # value is at least this long
    
        isBase64: True     # value is base64-encoded
    
        isAscii: False     # value is binary data when decoded
    
        isUri: False       # value is not formatted like a URI
    
     
    
      similar: 0.35        # maximum allowed similarity between key and value
    
                           # (1.0 being exactly the same)

## 插件

Whispers中所有的解析功能都是通过插件实现的，每一个插件都会使用pairs()方法实现一个类，并返回匹配规则的键值对：

    
    
    class PluginName:
    
        def pairs(self, file):
    
            yield "key", "value"

## 项目地址

 **Whispers：** 【[ _GitHub传送门_](https://github.com/Skyscanner/whispers)】

## 参考资料

> [
> _https://github.com/Skyscanner/whispers/blob/master/whispers/config.yml_](https://github.com/Skyscanner/whispers/blob/master/whispers/config.yml)
>
> [
> _https://github.com/Skyscanner/whispers/blob/master/whispers/rules﻿_](https://github.com/Skyscanner/whispers/blob/master/whispers/rules)

