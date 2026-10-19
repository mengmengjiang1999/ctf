​

![图片1.png](https://image.3001.net/images/20200508/1588925179_5eb512fbcce28.png!small)
**Terrier是一款针对OCI镜像和容器的安全分析工具，Terrier可以帮助研究人员扫描OCI镜像和容器文件，并根据哈希来识别和验证特定文件是否存在。**

## 工具安装

### 源代码：

如需了解源代码安装步骤，请参考项目的[ _Releases页面_](https://github.com/heroku/terrier/releases)。

### 通过Go安装：

    
    
    $ go get github.com/heroku/terrier

## 源构建

### 通过Go：

    
    
    $ go build

或

    
    
    $ make all

## 工具使用

    
    
    $ ./terrier -h
    
    Usage of ./terrier:
    
    -cfg string
    
    Load config from provided yaml file (default "cfg.yml")

工具使用必须扫描镜像的OCI TAR，这个值需要通过cfg.yml文件提供给Terrier。``

下列Docker命令可以用来将一个Docker镜像转换成一个TAR文件，并提供给Terrier扫描：

    
    
    # docker save imageid -o image.tar
    
    $ ./terrier
    
    [+] Loading config: cfg.yml
    
    [+] Analysing Image
    
    [+] Docker Image Source:  image.tar
    
    [*] Inspecting Layer:  05c3c2c60920f68***6d3c66e0f6148b81a8b0831388c2d61be5ef02190bcd1f
    
    [!] All components were identified and verified: (493/493)

## 样本YML配置``

Terrier会对YAML文件进行解析，下列给出的是样本配置文件：

    
    
    #THIS IS AN EXAMPLE CONFIG, MODIFY TO YOUR NEEDS
    
    mode: image
    
    image: image.tar
    
    # mode: container
    
    # path: merged
    
    # verbose: true
    
    # veryverbose: true
    
    
    files:
    
    - name: '/usr/bin/curl'
    
    hashes:
    
    - hash: '2353cbb7b47d0782ba8cdd9c7438b053c982eaaea6fbef8620c31a58d1e276e8'
    
    - hash: '22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2aaa'
    
    - hash: '9a43cb726fef31f272333b236ff1fde4beab363af54d0bc99c304450065d9c96'
    
    - hash: '8b7c559b8cccca0d30d01bc4b5dc944766208a53d18a03aa8afe97252207521faa'
    
    - name: '/usr/bin/go'
    
     hashes:
    
    - hash: '2353cbb7b47d0782ba8cdd9c7438b053c982eaaea6fbef8620c31a58d1e276e8'
    
    #UNCOMMENT TO ANALYZE HASHES
    
    # hashes:
    
    #- hash: '8b7c559b8cccca0d30d01bc4b5dc944766208a53d18a03aa8afe97252207521faa'
    
    #- hash: '22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2aa'
    
    #- hash: '60a2c86db4523e5d3eb41a247b4e7042a21d5c9d483d59053159d9ed50c8aa41aa'

## Terrier会做什么？``

Terrier提供了一个命令行工具，可以允许我们：

1、扫描一个OCI镜像中一个或多个目标文件是否存在，需提供目标文件的SHA256哈希；

2、扫描一个正在运行的容器中一个或多个目标文件是否存在，需提供目标文件的SHA256哈希；

## Terrier使用场景

### 场景1

Terrier可以用来验证特定OCI镜像是否包含特定代码，这个功能可以使用在供应链验证场景中。比如说，我们可能需要检查特定Docker镜像是否由特定版本的代码构成的，此时就可以使用Terrier了。此时，我们需要提供特定代码的SHA256哈希。

此场景下的样本YAML文件如下所示：

    
    
    mode: image
    
    # verbose: true
    
    # veryverbose: true
    
    image: golang1131.tar
    
    files:
    
    - name: '/usr/local/bin/analysis.sh'
    
    hashes:
    
    - hash: '9adc0bf7362bb66b98005aebec36691a62c80d54755e361788c776367d11b105'
    
    - name: '/usr/bin/curl'
    
    hashes:
    
    - hash: '23afbfab4f35ac90d9841a6e05f0d1487b6e0c3a914ea8dab3676c6dde612495'
    
    - name: '/usr/local/bin/staticcheck'
    
    hashes:
    
    - hash: '73f89162bacda8dd2354021dc56dc2f3dba136e873e372312843cd895dde24a2'

### 场景2

Terrier可以用来验证一个OCI镜像中是否存在特定文件，需提供目标文件的SHA256哈希。这个给功能可以帮助我们检查OCI镜像中是否存在恶意文件。

此场景下的样本YAML文件如下所示：

    
    
    mode: image
    
    # verbose: true
    
    # veryverbose: true
    
    image: alpinetest.tar
    
    hashes:
    
    - hash: '8b7c559b8cccca0d30d01bc4b5dc944766208a53d18a03aa8afe97252207521f'
    
    - hash: '22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2'
    
    - hash: '60a2c86db4523e5d3eb41a247b4e7042a21d5c9d483d59053159d9ed50c8aa41'
    
    - hash: '9a43cb726fef31f272333b236ff1fde4beab363af54d0bc99c304450065d9c96'

### 场景3

Terrier可以用来在运行时对容器组件进行验证，并分析其中内容。

此场景下的样本YAML文件如下所示：

    
    
    mode: container
    
    verbose: true
    
    # veryverbose: true
    
    # image: latestgo13.tar
    
    path: merged
    
    files:
    
    - name: '/usr/local/bin/analysis.sh'
    
    hashes:
    
    - hash: '9adc0bf7362bb66b98005aebec36691a62c80d54755e361788c776367d11b105'
    
    - name: '/usr/local/go/bin/go'
    
    hashes:
    
    - hash: '23afbfab4f35ac90d9841a6e05f0d1487b6e0c3a914ea8dab3676c6dde612495'
    
    - name: '/usr/local/bin/staticcheck'
    
    hashes:
    
    - hash: '73f89162bacda8dd2354021dc56dc2f3dba136e873e372312843cd895dde24a2'
    
    - name: '/usr/local/bin/gosec'
    
    hashes:
    
    - hash: 'e7cb8304e032ccde8e342a7f85ba0ba5cb0b8383a09a77ca282793ad7e9f8c1f'
    
    - name: '/usr/local/bin/errcheck'
    
    hashes:
    
    - hash: '41f725d7a872cad4ce1f403938937822572e0a38a51e8a1b29707f5884a2f0d7'
    
    - name: '/var/lib/dpkg/info/apt.postrm'
    
     hashes:
    
    - hash: '6a8f9af3abcfb8c6e35887d11d41a83782***f5766d42bd1e32a38781cba0b1c'

## 工具使用``

### 样例1

Terrier提供了一个命令行接口，并使用了YAML。样本YAML配置如下：

    
    
    mode: image
    
    # verbose: true
    
    # veryverbose: true
    
    image: alpinetest.tar
    
    files:
    
    - name: '/usr/local/go/bin/go'
    
    hashes:
    
    - hash: '8b7c559b8cccca0d30d01bc4b5dc944766208a53d18a03aa8afe97252207521f'
    
    - hash: '22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2aaa'
    
    - hash: '60a2c86db4523e5d3eb41a247b4e7042a21d5c9d483d59053159d9ed50c8aa41aaa'
    
    - hash: '8b7c559b8cccca0d30d01bc4b5dc944766208a53d18a03aa8afe97252207521faa'
    
    - name: '/usr/bin/delpart'
    
    hashes:
    
    - hash: '9a43cb726fef31f272333b236ff1fde4beab363af54d0bc99c304450065d9c96aaa'
    
    - name: '/usr/bin/stdbuf'
    
    hashes:
    
    - hash: '8b7c559b8cccca0d30d01bc4b5dc944766208a53d18a03aa8afe97252207521faa'
    
    - hash: '22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2aa'
    
    - hash: '60a2c86db4523e5d3eb41a247b4e7042a21d5c9d483d59053159d9ed50c8aa41aa'

在下面的样例中，我们通过上述YAML来让Terrier验证多个文件是否存在：``

    
    
    $./terrier 
    
    [+] Loading config: cfg.yml
    
    [+] Analysing Image
    
    [+] Docker Image Source:  alpinetest.tar
    
    [*] Inspecting Layer:  05c3c2c60920f68***6d3c66e0f6148b81a8b0831388c2d61be5ef02190bcd1f
    
    [*] Inspecting Layer:  09c25a178d8a6f8b984f3e72ca5ec966215b24a700ed135dc062ad925aa5eb23
    
    [*] Inspecting Layer:  36351e8e1da92268d40245cfbcd499a1173eeacc23be428386c8fc0a16f0b10a
    
    [*] Inspecting Layer:  7224ca1e886eeb7e63a9e978b1a811ed52f4a53ccb65f7c510fa04a0d1103fdf
    
    [*] Inspecting Layer:  7a2e464d80c7a1d89dab4321145491fb94865099c59975cfc840c2b8e7065014
    
    [*] Inspecting Layer:  88a583fe02f250344f89242f88309c666671042b032411630de870a111bea971
    
    [*] Inspecting Layer:  8db14b6fdd2cf8b4c122824531a4d85e07f1fecd6f7f43eab7f2d0a90d8c4bf2
    
    [*] Inspecting Layer:  9196e3376d1ed69a647e728a444662c10ed21feed4ef7aaca0d10f452240a09a
    
    [*] Inspecting Layer:  92db9b9e59a64cdf486203189d02acff79c3360788b62214a49d2263874ee811
    
    [*] Inspecting Layer:  bc4bb4a45da628724c9f93400a9149b2dd8a5d437272cb4e572cfaec64512d98
    
    [*] Inspecting Layer:  be7d600e4e8ed3000e342ef6482211350069d935a14aeff4d9fc3289e1426ed3
    
    [*] Inspecting Layer:  c4cec85dfa44f0a8856064922cff1c39b872***6dd002e33664d11a80f75a149
    
    [*] Inspecting Layer:  c998d6f023b7b9e3c186af19bcd1c2574f0d01b943077281ac5bd32e02dc57a5
    
    [!] All components were identified and verified: (493/493)

### 样例2``

验证镜像中是否存在任意文件，需提供目标文件的SHA256哈希：

    
    
    mode: image
    
    # verbose: true
    
    # veryverbose: true
    
    image: 1070caa1a8d89440829fd35d9356143a9d6185fe7f7a015b992ec1d8aa81c78a.tar
    
    hashes:
    
    - hash: '8b7c559b8cccca0d30d01bc4b5dc944766208a53d18a03aa8afe97252207521f'
    
    - hash: '22e88c7d6da9b73fbb515ed6a8f6d133c680527a799e3069ca7ce346d90649b2'
    
    - hash: '60a2c86db4523e5d3eb41a247b4e7042a21d5c9d483d59053159d9ed50c8aa41'
    
    - hash: '9a43cb726fef31f272333b236ff1fde4beab363af54d0bc99c304450065d9c96'

运行Terrier：

    
    
    ./terrier 
    
    [+] Loading config: cfg.yml
    
    [+] Docker Image Source:  golang.tar
    
    [*] Inspecting Layer:  1070caa1a8d89440829fd35d9356143a9d6185fe7f7a015b992ec1d8aa81c78a
    
    [*] Inspecting Layer:  414833cdb33683ab8607565da5f40d3dc3f721e9a59e14e373fce206580ed40d
    
    [*] Inspecting Layer:  6bd93c6873c822f793f770fdf3973d8a02254a5a0d60d67827480797f76858aa
    
    [*] Inspecting Layer:  c40c240ae37a2d2982ebcc3a58e67bf07aeaebe0796b5c5687045083ac6295ed
    
    [*] Inspecting Layer:  d2850df0b6795c00bdce32eb9c1ad9afc0640c2b9a3e53ec5437fc5539b1d71a
    
    [*] Inspecting Layer:  f0c2fe7dbe3336c8ba06258935c8dae37dbecd404d2d9cd74c3587391a11b1af
    
    [!] Found file 'f0c2fe7dbe3336c8ba06258935c8dae37dbecd404d2d9cd74c3587391a11b1af/usr/bin/curl' with hash: 9a43cb726fef31f272333b236ff1fde4beab363af54d0bc99c304450065d9c96
    
    [*] Inspecting Layer:  f2d913644763b53196cfd2597f21b9739535ef9d5bf9250b9fa21ed223fc29e3
    
    echo $?
    
    1

## 项目地址

Terrier：【[GitHub传送门](https://github.com/heroku/terrier)】

 ***参考来源：[
_heroku_](https://github.com/heroku/terrier)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

