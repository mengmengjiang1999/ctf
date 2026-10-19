![](https://image.3001.net/images/20201115/1605442149_5fb11a6599a0715f5bc51.png!small)

## Grype

Grype是一款针对容器镜像和文件系统的漏洞扫描器。在该工具的帮助下，广大研究人员可以轻松完成针对容器镜像和文件系统的漏洞扫描和安全审计任务。

## 功能特性

扫描一个容器镜像或文件系统中的内容，尝试寻找其中存在的已知的安全漏洞；

支持对主流操作系统包进行安全漏洞扫描：

> Alpine
>
> BusyBox
>
> CentOS / Red Hat
>
> Debian
>
> Ubuntu

支持对特定语言的软件包进行漏洞扫描：

> Ruby (Bundler)
>
> Java (JARs等)
>
> JavaScript (NPM/Yarn)
>
> Python (Egg/Wheel)
>
> Python pip/requirements.txt/setup.py

支持Docker和OCI镜像格式；

## 工具安装

如果你使用的是macOS或Linux系统，我们建议大家使用下列方式进行工具的安装和配置：

    
    
    # 将最新版本的Grype安装至/usr/local/bin
    
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
    
     
    
    # 将特定版本的Grype安装到指定目录中
    
    curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b <SOME_BIN_PATH> <RELEASE_VERSION>

针对macOS，我们也推荐使用Homebrew进行安装：

    
    
    brew tap anchore/grype
    
    brew install grype

## 工具配置

 **配置文件搜索路径如下：**

    
    
    .grype.yaml
    
    .grype/config.yaml
    
    ~/.grype.yaml
    
    <XDG_CONFIG_HOME>/grype/config.yaml

 **配置选项（样例值为默认值）：**

    
    
    # enable/disable checking for application updates on startup
    
    check-for-app-update: true
    
     
    
    # same as --fail-on ; upon scanning, if a severity is found at or above the given severity then the return code will be 1
    
    # default is unset which will skip this validation (options: negligible, low, medium, high, critical)
    
    fail-on-severity: ''
    
     
    
    # same as -o ; the output format of the vulnerability report (options: table, json, cyclonedx)
    
    output: "table"
    
     
    
    # same as -s ; the search space to look for packages (options: all-layers, squashed)
    
    scope: "squashed"
    
     
    
    # same as -q ; suppress all output (except for the vulnerability list)
    
    quiet: false
    
     
    
    db:
    
      # check for database updates on execution
    
      auto-update: true
    
     
    
      # location to write the vulnerability database cache
    
      cache-dir: "$XDG_CACHE_HOME/grype/db"
    
     
    
      # URL of the vulnerability database
    
      update-url: "https://toolbox-data.anchore.io/grype/databases/listing.json"
    
     
    
    log:
    
      # location to write the log file (default is not to have a log file)
    
      file: ""
    
     
    
      # the log level; note: detailed logging suppress the ETUI
    
      level: "error"
    
     
    
      # use structured logging
    
      structured: false

## 工具使用

安装好Grype之后，我们还需要确保可以直接在命令行中调用Grype。接下来，我们就可以使用下列命令来扫描一个镜像中的安全漏洞了：

    
    
    grype <image>

上述命令将寻找一个容器镜像中的安全漏洞，如需在漏洞扫描任务中包含所有镜像层的软件，可以使用--scope all-layers选项：

    
    
    grype <image> --scope all-layers

Grype还可以扫描除了Docker之外的其他各种源：

    
    
    # scan a container image archive (from the result of `docker image save ...`, `podman save ...`, or `skopeo copy` commands)
    
    grype path/to/image.tar
    
     
    
    # scan a directory
    
    grype dir:path/to/dir

Grype的输出数据格式同样是可配置的：

    
    
    grype <image> -o <format>

 **这里的format可选项如下：**

> json
>
> cyclonedx
>
> table

Grype还可以获取Anchore Feed服务所提供的漏洞数据库，这个数据库会在每一次扫描任务开始之前进行更新，不过我们也可以使用下列命令来进行手动更新：

    
    
    grype db update

## Shell命令补全

Grype还支持CLI命令行中的Shell补全，我们可以通过运行下列命令来生成针对Shell补全的代码：

    
    
    grype completion <bash|fish>
    
    go run main.go completion <bash|fish>

上述命令将输出一个Shell脚本，它将作为Grpe的补全脚本使用。

## 工具使用样例

![](https://image.3001.net/images/20201115/1605445909_5fb1291516bfbe2ed9550.gif!small)

## 项目地址

Grype：【[ _GitHub传送门_](https://github.com/anchore/grype)】

