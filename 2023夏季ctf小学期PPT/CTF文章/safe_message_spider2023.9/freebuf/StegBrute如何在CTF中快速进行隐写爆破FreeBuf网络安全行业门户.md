![](https://image.3001.net/images/20210123/1611393652_600bea747307661d2b1b0.png!small)

## StegBrute

StegBrute是一款功能强大的隐写术暴力破解工具，该工具基于Rust开发，并且引入了线程机制以提升其性能，可以帮助广大研究人员在CTF比赛中迅速对隐写内容进行暴力破解。

## 工具依赖

StegBrute的运行必须依赖于Steghide，因此，我们在使用StegBrute之前需要先安装并运行Steghide：

    
    
    apt-get install -y steghide

如果你使用的并不是基于Debian的发行版系统的话，请直接点击【[
_这里_](http://steghide.sourceforge.net/)】访问Stetghide站点并下载最新版本。

## 工具安装&配置&运行

StegBrute提供了多种安装方式，具体如下。

### Cargo安装

广大研究人员可以通过cargo（Rust包管理器）来安装StegBrute。如果你的设备上还没有安装cargo的话，你可以通过apt来安装，或直接下载配置Rust环境：

    
    
    cargo install stegbrute

注意：这种安装方式适用于各种平台。

### 基于Debian的发行版系统

如果你使用的是uBuntu、Kali或其他基于Debian的发行版操作系统，你可以直接点击【[
_这里_](https://github.com/R4yGM/stegbrute/releases)】下载该工具预编译好的.deb文件来进行工具安装，下载完成后解压文件并运行即可：

    
    
    wget https://github.com/R4yGM/stegbrute/releases/download/0.1.1/stegbrute_0.1.1_amd64.deb &&
    
    dpkg --install stegbrute_0.1.1_amd64.deb

### Docker安装

提醒：如果你还没有在自己的设备上安装Docker的话，请参考这篇【[
_指引文档_](https://docs.docker.com/engine/install/)】。

首先，我们需要从【[
_Docker库_](https://hub.docker.com/r/r4yan/stegbrute)】中下载Docker镜像，大小仅为4.93MB。如果你没有下载该镜像的话，你还可以使用下列命令将该项目源码克隆至本地，然后运行命令来构建镜像以及Dockerfile：

    
    
    git clone https://github.com/R4yGM/stegbrute.git
    
    docker pull r4yan/stegbrute:latest

你还可以通过替换“latest”为不同的StegBrute版本号来下载不同版本的StegBrute镜像，比如说：

    
    
    docker pull r4yan/stegbrute:0.1.0

如果上述工作你都懒得做的话，你可以直接点击【[
_这里_](https://github.com/R4yGM/stegbrute/blob/main/Dockerfile)】下载/拷贝StegBrute的Dockerfile，然后利用Dockerfile构建工具镜像文件。

在启动容器之前，我们还需要创建一个卷来与容器共享文件：

    
    
    docker volume create --name stegbrute_data

然后，将你需要使用（即使用StegBurte进行爆破）的文件拷贝到这个卷中的文件夹内，假设路径为“/var/lib/docker/volumes/stegbrute_data/_data”，则需要运行的命令如下：

    
    
    cp wordlist.txt /var/lib/docker/volumes/stegbrute_data/_data && cp file.jpg /var/lib/docker/volumes/stegbrute_data/_data

现在，我们就可以使用下列命令运行StegBrute了：

    
    
    docker run -v stegbrute_data:/stegbrute_data -it --rm --name stegbrute r4yan/stegbrute:latest <options>

在使用过程中，还需要用你要提供给StegBrute的内容替换上述命令中的<options>参数。

重要：请及时将处理结果存储在卷内，而不要存储在容器中，因为这些结果会被删除！你可以在运行命令后面添加下列选项来实现结果自动保存：

    
    
    -x /$VOLUME_NAME/results.txt

或

    
    
    --extract-file /$VOLUME_NAME/results.txt

如果一切正常的话，你将会在“/var/lib/docker/volumes/stegbrute_data/_data”中查看到StegBrute的处理结果。

## 可执行程序

你还可以直接下载已编译好的程序并执行即可，命令如下：

    
    
    wget https://github.com/R4yGM/stegbrute/releases/download/0.1.1/stegbrute && chmod +x stegbrute
    
    mv stegbrute /usr/local/bin/

## 工具使用

StegBrute的使用非常简单，并且还提供了很多功能选项，你可以使用-h或--help命令来查看工具提供的所有功能：

    
    
    ============================================================
    
         ____  _             ____             _
    
        / ___|| |_ ___  __ _| __ ) _ __ _   _| |_ ___
    
        \___ \| __/ _ \/ _` |  _ \| '__| | | | __/ _ \
    
         ___) | ||  __/ (_| | |_) | |  | |_| | ||  __/
    
        |____/ \__\___|\__, |____/|_|   \__,_|\__\___|
    
                       |___/
    
     
    
    StegBrute v0.1.1 - By R4yan
    
    https://github.com/R4yGM/StegBrute
    
     
    
    StegBrute 0.1.1
    
    R4yan <yessou.rayan@gmail.com>
    
    Steganography bruteforce tool
    
     
    
    USAGE:
    
        stegbrute [FLAGS] [OPTIONS] --file-name <file-name> --wordlist <wordlist>
    
     
    
    FLAGS:
    
        -h, --help       Prints help information
    
        -V, --version    Prints version information
    
        -v, --verbose    shows every try the program does
    
     
    
    OPTIONS:
    
        -x, --extract-file <extract-file>    the file name path where you want to write the results [default:
    
                                             stegbrute_results.txt]
    
        -f, --file-name <file-name>          the file name path you want to crack
    
        -t, --threads <threads>              number of threads to bruteforce the file [default: 3]
    
    -w, --wordlist <wordlist>            path of the wordlist

## 选项参数

> -x或--extract-file
> <file_name>：命令执行后会将提取出的数据结果存储至file_name中，如果没有指定文件，StegBrute将会把结果存储至./stegbrute_results.txt文件中。
>
> -t或--threads with
> <number_of_threads>：同时执行多个文件爆破任务，盲目增加线程数量并不意味着总是能够提升爆破速度，具体取决于设备性能。
>
> -f或--file_name <file_name>：指定StegBrute需要爆破的文件名称，目前仅支持下列格式：JPEG、BMP、WAV或 AU。
>
> -w或--wordlist <wordlist>：指定爆破字典的路径和名称，每个密码占一行。

## 工具演示视频

视频地址：【[ _点我观看_](https://asciinema.org/a/5YUpQhY76MQE6vXDIVNNyK9T7)】

## 项目地址

StegBrute：【[ _GitHub传送门_](https://github.com/R4yGM/stegbrute)】

rockyou.txt字典：【[ _点我获取_](https://github.com/praetorian-inc/Hob0Rules/blob/master/wordlists/rockyou.txt.gz)】

