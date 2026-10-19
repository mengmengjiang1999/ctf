## 这里指的敏感数据是什么？

这里所说的敏感数据，指的是任何类型的机密或私有数据，是只有授权用户可以访问的关键IT基础设施（如帐户、设备、网络、基于云的服务）、应用程序、存储数据、数据库和组织中其他类型的关键数据。比如说，密码、AWS访问ID、AWS秘密访问密钥、Google
OAuth密钥等都属于敏感数据，这些敏感数据都应该严格地安全存储并保密。然而，有时由于有缺陷的安全策略或开发人员的疏忽错误，攻击者将能够轻松访问这些敏感数据。有时候，开发人员会使用默认的或在容器映像中保留硬编码的敏感数据，比如说密码、API密钥、加密密钥、SSH密钥、令牌等，这种情况在CI/CD管道中的快速开发和部署周期中普遍存在。除此之外，有时用户以纯文本形式存储密码，而向未经授权的实体泄漏敏感数据会使你的组织和基础设施面临严重的安全风险。

## 关于SecretScanner

SecretScanner可以帮助广大研究人员和开发人员扫描主机上的容器镜像或本地目录，并输出一个JSON文件，其中会包含SecretScanner找到的所有敏感数据的详细信息。

## SecretScanner命令行选项

    
    
    $ ./SecretScanner --help
    
     
    
    Usage of ./SecretScanner:
    
      -config-path string
    
         Searches for config.yaml from given directory. If not set, tries to find it from SecretScanner binary's and current directory
    
      -debug-level string
    
         Debug levels are one of FATAL, ERROR, IMPORTANT, WARN, INFO, DEBUG. Only levels higher than the debug-level are displayed (default "ERROR")
    
      -image-name string
    
         Name of the image along with tag to scan for secrets
    
      -json-filename string
    
         Output json file name. If not set, it will automatically create a filename based on image or dir name
    
      -local string
    
         Specify local directory (absolute path) which to scan. Scans only given directory recursively.
    
      -max-multi-match uint
    
         Maximum number of matches of same pattern in one file. This is used only when multi-match option is enabled. (default 3)
    
      -max-secrets uint
    
         Maximum number of secrets to find in one container image or file system. (default 1000)
    
      -maximum-file-size uint
    
         Maximum file size to process in KB (default 256)
    
      -multi-match
    
         Output multiple matches of same pattern in one file. By default, only one match of a pattern is output for a file for better performance
    
      -output-path string
    
         Output directory where json file will be stored. If not set, it will output to current directory
    
      -temp-directory string
    
         Directory to process and store repositories/matches (default "/tmp")
    
      -threads int
    
         Number of concurrent threads (default number of logical CPUs)

## Docker快速使用

使用下列命令安装Docker并在容器镜像中运行和使用SecretScanner。

1、构建SecretScanner：

    
    
    docker build --rm=true --tag=deepfenceio/secretscanning:latest -f Dockerfile

2、或者，使用下列命令从Docker拉取最新构建版本：

    
    
    docker pull deepfenceio/secretscanning

3、拉取一个容器镜像并进行扫描：

    
    
    docker pull node:8.11

4、运行SecretScanner，扫描一个容器镜像：

    
    
    docker run -it --rm --name=deepfence-secretscanner -v $(pwd):/home/deepfence/output -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker deepfenceio/secretscanning -image-name node:8.11

5、运行SecretScanner，扫描一个本地目录：

    
    
    docker run -it --rm --name=deepfence-secretscanner -v $(pwd):/home/deepfence/output -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker deepfenceio/secretscanning -local /home/deepfence/src/SecretScanner/test

默认配置下，SecretScanner将会在当前工作目录下创建一个包含所有扫描到的敏感数据的JSON文件，你也可以使用参数配置指定输出目录和JSON输出文件名称。

## 工具构建

1、安装Docker；

2、安装Hyperscan；

3、在你的平台上安装Go环境（v1.14）；

4、安装Go模块：gohs、yaml.v3和color；

5、运行下列命令，在$GOPATH/bin或$HOME/go/bin目录中自动下载并构建SecretScanner：

    
    
    go get github.com/deepfence/SecretScanner

6、或者，广大研究人员也可以使用下列命令将该项目源码克隆至本地，并运行命令将SecretScanner在当前目录下构建为可执行程序：

    
    
    git clone https://github.com/deepfence/SecretScanner.git
    
    go build -v -i

7、根据编辑config.yaml文件中的配置信息，然后运行SecretScanner。

## 在本地主机上运行SecretScanner

    
    
    ./SecretScanner --help
    
     
    
    ./SecretScanner -config-path /path/to/config.yaml/dir -local test
    
     
    
    ./SecretScanner -config-path /path/to/config.yaml/dir -image-name node:8.11

## SecretScanner输出样例

![](https://image.3001.net/images/20210405/1617609034_606ac14a8760f2d6c723e.png!small)

## 依赖项目

SecretScanner所使用的配置文件依赖于[
_shhgit_](https://github.com/eth0izzle/shhgit)项目进行构建。

## 免责声明

该工具旨在辅助研究人员进行负责任的安全研究，请不要将其用于非法目的。请在你拥有的基础设施上进行扫描，而不是将其用于他人的基础设施。

## 项目地址

SecretScanner：【[ _GitHub传送门_](https://github.com/deepfence/SecretScanner)】

## 参考资料

[ _https://medium.com/deepfence-cloud-native-security/detecting-secrets-to-reduce-attack-surface-3405ee6329b5_](https://medium.com/deepfence-cloud-native-security/detecting-secrets-to-reduce-attack-surface-3405ee6329b5)

[
_https://github.com/deepfence/SecretScanner/blob/master/Install.Ubuntu_](https://github.com/deepfence/SecretScanner/blob/master/Install.Ubuntu)

[ _https://github.com/eth0izzle/shhgit﻿_](https://github.com/eth0izzle/shhgit)

