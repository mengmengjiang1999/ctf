![](https://image.3001.net/images/20211127/1637993577_61a1cc696bcf5b0d2b1dc.png!small)

## 关于Bopscrk

Bopscrk是一款功能强大的字典生成工具，在该工具的帮助下，广大研究人员可以轻松生成强大的智能字典。当前版本的Bopscrk已经引入了[
_BlackArch Linux_](https://blackarch.org/)渗透测试发行版系统中。

## 工具特性

  * 目标明确的字典创建：支持引入根目标用户相关的个人信息，并进行单词组合，将结果转换为所有可能的密码。其中的lyricpass模块将允许我们搜索跟艺术家相关的歌词等信息，并导入至字典中。
  * 可定制的大小写转换：通过一个简单的配置文件创建自定义的字符集和转换模式。
  * 字典列表排除：从另一个字典列表中排除指定密码（以避免重复使用已经测试过的密码）。
  * 支持交互模式和单行命令。

## 工具要求

  * Python 3
  * 使用lyricpass模块（可选）：

    
    
    pip install requirements.txt

## 工具下载

由于该工具基于Python 3开发，因此先在本地设备上安装并配置好Python 3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/r3nt0n/bopscrk.git

## 工具使用

    
    
    -h, --help         显示帮助信息并退出
    
      -i, --interactive     交互模式，脚本需要提供关于目标的信息
    
      -w               单词组合，以逗号分隔（非交互模式）
    
      --min             生成字典密码的最小长度 (默认: 4)
    
      --max             生成字典密码的最大长度 (默认: 32)
    
      -c, --case          启用大小写转换
    
      -l, --leet           启用leet转换
    
      -n                每次字典密码组合的最大数量 (默认: 2)
    
      -a , --artists        搜索歌词信息的艺术家名称，以逗号分隔
    
      -x , --exclude       从其他字典获取需要排除的所有字典密码，多个字典文件以逗号分隔
    
      -o , --output       输出文件存储至字典列表中 (默认: tmp.txt)
    
      -C , --config        指定需要使用的配置文件 (默认: ./bopscrk.cfg)

## 工作机制

  * 必须提供一些基础单词作为字典种子；
  * lyricpass功能允许介绍艺术家。该工具将下载他所有歌曲的歌词，每一行都将被添加为一个新的字典密码。默认情况下，还会添加艺术家姓名和每个词语上单词首字母构成的单词；
  * 该工具将使用上述信息生成所有可能的字典密码组合；
  * 为了生成更多的组合，它将添加一些常用的分隔符（例如“-”、“_“、”）、数字和密码中常用的特殊字符；
  * 可以使用leet和大小写转换来丰富密码字典；
  * 可以提供已经针对目标测试过的单词列表，以便从结果单词列表（-x）中排除所有这些单词；

## Lyricpass模块

该功能基于initstring开发的[
_lyricpass项目_](https://github.com/initstring/lyricpass)实现，并做了额外的修改以将输入和输出工具与Bopscrk集成在一起。

该功能可以从用户提供的属于艺术家的所有歌曲中检索所有歌词。默认情况下，它将存储每个艺术家、使用空格替换找到的每个词语、找到的每个词语的首字母缩写（如果已激活leet和大小写转换，则稍后会将转换这些首字母缩写）。

![](https://image.3001.net/images/20211127/1637993618_61a1cc920b69de5bf8ce6.png!small)

## 工具使用演示

![](https://image.3001.net/images/20211127/1637993641_61a1cca9edb53a0caf73e.gif)

![](https://image.3001.net/images/20211127/1637993666_61a1ccc2b8df694415695.gif!small)

## 项目地址

 **Bopscrk：** 【[ _GitHub传送门_](https://github.com/r3nt0n/bopscrk)】

## 参考地址

  * [ _https://blackarch.org/_](https://blackarch.org/)
  * [ _https://inventory.raw.pm/_](https://inventory.raw.pm/)
  * [ _https://github.com/initstring/lyricpass_](https://github.com/initstring/lyricpass)

