**Trivy是一款针对容器适用于CI的漏洞扫描器。**

**![1.png](https://image.3001.net/images/20190707/1562458180_5d213844540ad.png!small)**

## 准确性对比

在Alpine Linux上检测到的漏洞数量（截至2019/05/12）

![2.png](https://image.3001.net/images/20190707/1562458197_5d2138558d460.png!small)

有关详请，请参阅与其他扫描器的比较部分。

## 概要

Trivy（tri发音像trigger，vy发音像envy）是一个简单而全面的容器漏洞扫描程序。Trivy可检测操作系统软件包（Alpine，RHEL，CentOS等）和应用程序依赖项（Bundler，Composer，npm，yarn等）的漏洞。此外，Trivy也非常易于使用。只需安装二进制文件即可执行扫描，你只需指定扫描容器的镜像名称即可。

它被认为适用于CI。在推送到容器注册表之前，你可以轻松扫描本地容器镜像。详情[请参阅此处](https://github.com/knqyf263/trivy#continuous-integration-ci)。

## 特性

### 全面的漏洞检测

> 操作系统（Alpine，Red Hat Universal Base Image，Red Hat Enterprise
> Linux，CentOS，Debian和Ubuntu）
>
> 应用程序依赖（Bundler，Composer，Pipenv，Poetry，npm，yarn和Cargo）

### 使用简单

> 仅需指定镜像名称
>
> 请参阅快速入门和示例

### 安装简便

> 无需安装DB，库等先决条件。
>
> apt-get install，yum install和brew install都可以。

### 高精确度

> 特别是针对Alpine Linux和RHEL/CentOS；
>
> 其他操作系统的精确度也很高。

### DevSecOps

适用于CI，如Travis CI，CircleCI，Jenkins等。

## 安装

### RHEL/CentOS

将存储库设置添加到/etc/yum.repos.d。

    
    
    $ sudo vim /etc/yum.repos.d/trivy.repo
    [trivy]
    name=Trivy repository
    baseurl=https://knqyf263.github.io/trivy-repo/rpm/releases/$releasever/$basearch/
    gpgcheck=0
    enabled=1
    $ sudo yum -y update
    $ sudo yum -y install trivy

或

    
    
    $ rpm -ivh https://github.com/knqyf263/trivy/releases/download/v0.0.15/trivy_0.0.15_Linux-64bit.rpm

### Debian/Ubuntu

将[CODE_NAME]替换为你的代码名称

CODE_NAME：wheezy，jessie，stretch，buster，trusty，xenial，bionic

    
    
    $ sudo apt-get install apt-transport-https gnupg
    $ wget -qO - https://knqyf263.github.io/trivy-repo/deb/public.key | sudo apt-key add -    $ echo deb https://knqyf263.github.io/trivy-repo/deb [CODE_NAME] main | sudo tee -a /etc/apt/sources.list.d/trivy.list
    $ sudo apt-get update
    $ sudo apt-get install trivy

或

    
    
    $ sudo apt-get install rpm
    $ wget https://github.com/knqyf263/trivy/releases/download/v0.0.15/trivy_0.0.15_Linux-64bit.deb
    $ sudo dpkg -i trivy_0.0.15_Linux-64bit.deb

### Mac OS X / Homebrew

你可以在Mac OS上使用homebrew。

    
    
    $ brew install knqyf263/trivy/trivy

###  **二进制（包括Windows）**

从[此页面](https://github.com/knqyf263/trivy/releases/latest)获取最新版本，并下载适用于你操作系统/架构的存档文件。解压缩该文件，并将二进制文件放在$PATH中（在UNIX-y系统上，位于/usr/local/bin）。确保执行位已打开。

你需要安装rpm命令来扫描RHEL/CentOS。

### 从源码

    
    
    $ mkdir -p $GOPATH/src/github.com/knqyf263
    $ cd $GOPATH/src/github.com/knqyf263
    $ git clone https://github.com/knqyf263/trivy
    $ cd trivy/cmd/trivy/
    $ export GO111MODULE=on
    $ go install

## 快速开始

只需指定镜像名称（和标签）即可。缓存中出现问题时应避免使用最新标签。请参阅清除镜像缓存部分。

### 基本使用

    
    
    $ trivy [YOUR_IMAGE_NAME]

### 示例

    
    
    $ trivy python:3.4-alpine

### 结果

    
    
    2019-05-16T01:20:43.180+0900    INFO    Updating vulnerability database...
    2019-05-16T01:20:53.029+0900    INFO    Detecting Alpine vulnerabilities...
    
    python:3.4-alpine3.9 (alpine 3.9.2)
    ===================================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | openssl | CVE-2019-1543    | MEDIUM   | 1.1.1a-r1         | 1.1.1b-r1     | openssl: ChaCha20-Poly1305     |
    |         |                  |          |                   |               | with long nonces               |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+

### Docker

将[YOUR_CACHE_DIR]替换为计算机上的缓存目录。

    
    
    $ docker run --rm -v [YOUR_CACHE_DIR]:/root/.cache/ knqyf263/trivy [YOUR_IMAGE_NAME]

macOS示例：

    
    
    $ docker run --rm -v $HOME/Library/Caches:/root/.cache/ knqyf263/trivy python:3.4-alpine

如果要扫描主机上的镜像，则需安装docker.sock。

    
    
    $ docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        -v $HOME/Library/Caches:/root/.cache/ knqyf263/trivy python:3.4-alpine

如果发生错误，请重新pull最新的knqyf263/trivy。

结果：

    
    
    2019-05-16T01:20:43.180+0900    INFO    Updating vulnerability database...
    2019-05-16T01:20:53.029+0900    INFO    Detecting Alpine vulnerabilities...
    
    python:3.4-alpine3.9 (alpine 3.9.2)
    ===================================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | openssl | CVE-2019-1543    | MEDIUM   | 1.1.1a-r1         | 1.1.1b-r1     | openssl: ChaCha20-Poly1305     |
    |         |                  |          |                   |               | with long nonces               |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+

## 示例

### 扫描镜像

只需指定镜像名称（和标签）即可。

    
    
    $ trivy knqyf263/test-image:1.2.3

结果：

    
    
    2019-05-16T12:58:55.967+0900    INFO    Updating vulnerability database...
    2019-05-16T12:59:03.150+0900    INFO    Detecting Alpine vulnerabilities...
    2019-05-16T12:59:03.156+0900    INFO    Updating bundler Security DB...
    2019-05-16T12:59:04.941+0900    INFO    Detecting bundler vulnerabilities...
    2019-05-16T12:59:04.942+0900    INFO    Updating cargo Security DB...
    2019-05-16T12:59:05.967+0900    INFO    Detecting cargo vulnerabilities...
    2019-05-16T12:59:05.967+0900    INFO    Updating composer Security DB...
    2019-05-16T12:59:07.834+0900    INFO    Detecting composer vulnerabilities...
    2019-05-16T12:59:07.834+0900    INFO    Updating npm Security DB...
    2019-05-16T12:59:10.285+0900    INFO    Detecting npm vulnerabilities...
    2019-05-16T12:59:10.285+0900    INFO    Updating pipenv Security DB...
    2019-05-16T12:59:11.487+0900    INFO    Detecting pipenv vulnerabilities...
    
    knqyf263/test-image:1.2.3 (alpine 3.7.1)
    ========================================
    Total: 26 (UNKNOWN: 0, LOW: 3, MEDIUM: 16, HIGH: 5, CRITICAL: 2)
    
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |              TITLE               |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | curl    | CVE-2018-14618   | CRITICAL | 7.61.0-r0         | 7.61.1-r0     | curl: NTLM password overflow     |
    |         |                  |          |                   |               | via integer overflow             |
    +         +------------------+----------+                   +---------------+----------------------------------+
    |         | CVE-2018-16839   | HIGH     |                   | 7.61.1-r1     | curl: Integer overflow leading   |
    |         |                  |          |                   |               | to heap-based buffer overflow in |
    |         |                  |          |                   |               | Curl_sasl_create_plain_message() |
    +         +------------------+          +                   +---------------+----------------------------------+
    |         | CVE-2019-3822    |          |                   | 7.61.1-r2     | curl: NTLMv2 type-3 header       |
    |         |                  |          |                   |               | stack buffer overflow            |
    +         +------------------+          +                   +---------------+----------------------------------+
    |         | CVE-2018-16840   |          |                   | 7.61.1-r1     | curl: Use-after-free when        |
    |         |                  |          |                   |               | closing "easy" handle in         |
    |         |                  |          |                   |               | Curl_close()                     |
    +         +------------------+----------+                   +               +----------------------------------+
    |         | CVE-2018-16842   | MEDIUM   |                   |               | curl: Heap-based buffer          |
    |         |                  |          |                   |               | over-read in the curl tool       |
    |         |                  |          |                   |               | warning formatting               |
    +         +------------------+          +                   +---------------+----------------------------------+
    |         | CVE-2018-16890   |          |                   | 7.61.1-r2     | curl: NTLM type-2 heap           |
    |         |                  |          |                   |               | out-of-bounds buffer read        |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3823    |          |                   |               | curl: SMTP end-of-response       |
    |         |                  |          |                   |               | out-of-bounds read               |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | git     | CVE-2018-17456   | HIGH     | 2.15.2-r0         | 2.15.3-r0     | git: arbitrary code execution    |
    |         |                  |          |                   |               | via .gitmodules                  |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2018-19486   |          |                   |               | git: Improper handling of        |
    |         |                  |          |                   |               | PATH allows for commands to be   |
    |         |                  |          |                   |               | executed from...                 |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | libssh2 | CVE-2019-3855    | CRITICAL | 1.8.0-r2          | 1.8.1-r0      | libssh2: Integer overflow in     |
    |         |                  |          |                   |               | transport read resulting in      |
    |         |                  |          |                   |               | out of bounds write...           |
    +         +------------------+----------+                   +               +----------------------------------+
    |         | CVE-2019-3859    | MEDIUM   |                   |               | libssh2: Unchecked use of        |
    |         |                  |          |                   |               | _libssh2_packet_require and      |
    |         |                  |          |                   |               | _libssh2_packet_requirev         |
    |         |                  |          |                   |               | resulting in out-of-bounds       |
    |         |                  |          |                   |               | read                             |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3858    |          |                   |               | libssh2: Zero-byte allocation    |
    |         |                  |          |                   |               | with a specially crafted SFTP    |
    |         |                  |          |                   |               | packed leading to an...          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3863    |          |                   |               | libssh2: Integer overflow        |
    |         |                  |          |                   |               | in user authenticate             |
    |         |                  |          |                   |               | keyboard interactive allows      |
    |         |                  |          |                   |               | out-of-bounds writes             |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3862    |          |                   |               | libssh2: Out-of-bounds memory    |
    |         |                  |          |                   |               | comparison with specially        |
    |         |                  |          |                   |               | crafted message channel          |
    |         |                  |          |                   |               | request                          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3860    |          |                   |               | libssh2: Out-of-bounds reads     |
    |         |                  |          |                   |               | with specially crafted SFTP      |
    |         |                  |          |                   |               | packets                          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3857    |          |                   |               | libssh2: Integer overflow in     |
    |         |                  |          |                   |               | SSH packet processing channel    |
    |         |                  |          |                   |               | resulting in out of...           |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3861    |          |                   |               | libssh2: Out-of-bounds reads     |
    |         |                  |          |                   |               | with specially crafted SSH       |
    |         |                  |          |                   |               | packets                          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3856    |          |                   |               | libssh2: Integer overflow in     |
    |         |                  |          |                   |               | keyboard interactive handling    |
    |         |                  |          |                   |               | resulting in out of bounds...    |
    +---------+------------------+          +-------------------+---------------+----------------------------------+
    | libxml2 | CVE-2018-14567   |          | 2.9.7-r0          | 2.9.8-r1      | libxml2: Infinite loop when      |
    |         |                  |          |                   |               | --with-lzma is used allows for   |
    |         |                  |          |                   |               | denial of service...             |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2018-14404   |          |                   |               | libxml2: NULL pointer            |
    |         |                  |          |                   |               | dereference in                   |
    |         |                  |          |                   |               | xpath.c:xmlXPathCompOpEval()     |
    |         |                  |          |                   |               | can allow attackers to cause     |
    |         |                  |          |                   |               | a...                             |
    +         +------------------+----------+                   +               +----------------------------------+
    |         | CVE-2018-9251    | LOW      |                   |               | libxml2: infinite loop in        |
    |         |                  |          |                   |               | xz_decomp function in xzlib.c    |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | openssh | CVE-2019-6109    | MEDIUM   | 7.5_p1-r9         | 7.5_p1-r10    | openssh: Missing character       |
    |         |                  |          |                   |               | encoding in progress display     |
    |         |                  |          |                   |               | allows for spoofing of scp...    |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-6111    |          |                   |               | openssh: Improper validation     |
    |         |                  |          |                   |               | of object names allows           |
    |         |                  |          |                   |               | malicious server to overwrite    |
    |         |                  |          |                   |               | files...                         |
    +         +------------------+----------+                   +               +----------------------------------+
    |         | CVE-2018-20685   | LOW      |                   |               | openssh: scp client improper     |
    |         |                  |          |                   |               | directory name validation        |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | sqlite  | CVE-2018-20346   | MEDIUM   | 3.21.0-r1         | 3.25.3-r0     | sqlite: Multiple flaws in        |
    |         |                  |          |                   |               | sqlite which can be triggered    |
    |         |                  |          |                   |               | via corrupted internal...        |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | tar     | CVE-2018-20482   | LOW      | 1.29-r1           | 1.31-r0       | tar: Infinite read loop in       |
    |         |                  |          |                   |               | sparse_dump_region function in   |
    |         |                  |          |                   |               | sparse.c                         |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    
    ruby-app/Gemfile.lock
    =====================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +----------------------+------------------+----------+-------------------+---------------+--------------------------------+
    |       LIBRARY        | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +----------------------+------------------+----------+-------------------+---------------+--------------------------------+
    | rails-html-sanitizer | CVE-2018-3741    | MEDIUM   | 1.0.3             | >= 1.0.4      | rubygem-rails-html-sanitizer:  |
    |                      |                  |          |                   |               | non-whitelisted attributes     |
    |                      |                  |          |                   |               | are present in sanitized       |
    |                      |                  |          |                   |               | output when input with         |
    |                      |                  |          |                   |               | specially-crafted...           |
    +----------------------+------------------+----------+-------------------+---------------+--------------------------------+
    
    rust-app/Cargo.lock
    ===================
    Total: 3 (UNKNOWN: 3, LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0)
    
    +---------+-------------------+----------+-------------------+---------------+--------------------------------+
    | LIBRARY | VULNERABILITY ID  | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +---------+-------------------+----------+-------------------+---------------+--------------------------------+
    | ammonia | RUSTSEC-2019-0001 | UNKNOWN  | 1.9.0             | >= 2.1.0      | Uncontrolled recursion leads   |
    |         |                   |          |                   |               | to abort in HTML serialization |
    +---------+-------------------+          +-------------------+---------------+--------------------------------+
    | openssl | RUSTSEC-2016-0001 |          | 0.8.3             | >= 0.9.0      | SSL/TLS MitM vulnerability due |
    |         |                   |          |                   |               | to insecure defaults           |
    +         +-------------------+          +                   +---------------+--------------------------------+
    |         | RUSTSEC-2018-0010 |          |                   | >= 0.10.9     | Use after free in CMS Signing  |
    +---------+-------------------+----------+-------------------+---------------+--------------------------------+
    
    php-app/composer.lock
    =====================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +-------------------+------------------+----------+-------------------+---------------------+--------------------------------+
    |      LIBRARY      | VULNERABILITY ID | SEVERITY | INSTALLED VERSION |    FIXED VERSION    |             TITLE              |
    +-------------------+------------------+----------+-------------------+---------------------+--------------------------------+
    | guzzlehttp/guzzle | CVE-2016-5385    | MEDIUM   | 6.2.0             | 6.2.1, 4.2.4, 5.3.1 | PHP: sets environmental        |
    |                   |                  |          |                   |                     | variable based on user         |
    |                   |                  |          |                   |                     | supplied Proxy request header  |
    +-------------------+------------------+----------+-------------------+---------------------+--------------------------------+
    
    node-app/package-lock.json
    ==========================
    Total: 4 (UNKNOWN: 0, LOW: 0, MEDIUM: 3, HIGH: 1, CRITICAL: 0)
    
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | jquery  | CVE-2019-5428    | MEDIUM   | 3.3.9             | >=3.4.0       | Modification of                |
    |         |                  |          |                   |               | Assumed-Immutable Data (MAID)  |
    +         +------------------+          +                   +               +--------------------------------+
    |         | CVE-2019-11358   |          |                   |               | js-jquery: prototype pollution |
    |         |                  |          |                   |               | in object's prototype leading  |
    |         |                  |          |                   |               | to denial of service or...     |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | lodash  | CVE-2018-16487   | HIGH     | 4.17.4            | >=4.17.11     | lodash: Prototype pollution in |
    |         |                  |          |                   |               | utilities function             |
    +         +------------------+----------+                   +---------------+                                +
    |         | CVE-2018-3721    | MEDIUM   |                   | >=4.17.5      |                                |
    |         |                  |          |                   |               |                                |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    
    python-app/Pipfile.lock
    =======================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +---------+------------------+----------+-------------------+---------------+------------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |               TITLE                |
    +---------+------------------+----------+-------------------+---------------+------------------------------------+
    | django  | CVE-2019-6975    | MEDIUM   | 2.0.9             | 2.0.11        | python-django:                     |
    |         |                  |          |                   |               | memory exhaustion in               |
    |         |                  |          |                   |               | django.utils.numberformat.format() |
    +---------+------------------+----------+-------------------+---------------+------------------------------------+

### 扫描镜像文件

    
    
    $ docker save ruby:2.3.0-alpine3.9 -o ruby-2.3.0.tar
    $ trivy --input ruby-2.3.0.tar

结果：

    
    
    2019-05-16T12:45:57.332+0900    INFO    Updating vulnerability database...
    2019-05-16T12:45:59.119+0900    INFO    Detecting Debian vulnerabilities...
    
    ruby-2.3.0.tar (debian 8.4)
    ===========================
    Total: 7447 (UNKNOWN: 5, LOW: 326, MEDIUM: 5695, HIGH: 1316, CRITICAL: 105)
    
    +------------------------------+---------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------+
    |           LIBRARY            |  VULNERABILITY ID   | SEVERITY |     INSTALLED VERSION      |          FIXED VERSION           |                        TITLE                        |
    +------------------------------+---------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------+
    | apt                          | CVE-2019-3462       | CRITICAL | 1.0.9.8.3                  | 1.0.9.8.5                        | Incorrect sanitation of the                         |
    |                              |                     |          |                            |                                  | 302 redirect field in HTTP                          |
    |                              |                     |          |                            |                                  | transport method of...                              |
    +                              +---------------------+----------+                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2016-1252       | MEDIUM   |                            | 1.0.9.8.4                        | The apt package in Debian                           |
    |                              |                     |          |                            |                                  | jessie before 1.0.9.8.4, in                         |
    |                              |                     |          |                            |                                  | Debian unstable before...                           |
    +                              +---------------------+----------+                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2011-3374       | LOW      |                            |                                  |                                                     |
    +------------------------------+---------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------+
    | bash                         | CVE-2016-7543       | HIGH     | 4.3-11                     | 4.3-11+deb8u1                    | bash: Specially crafted                             |
    |                              |                     |          |                            |                                  | SHELLOPTS+PS4 variables allows                      |
    |                              |                     |          |                            |                                  | command substitution                                |
    +                              +---------------------+          +                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2019-9924       |          |                            | 4.3-11+deb8u2                    | bash: BASH_CMD is writable in                       |
    |                              |                     |          |                            |                                  | restricted bash shells                              |
    +                              +---------------------+----------+                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2016-0634       | MEDIUM   |                            | 4.3-11+deb8u1                    | bash: Arbitrary code execution                      |
    |                              |                     |          |                            |                                  | via malicious hostname                              |
    +                              +---------------------+----------+                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2016-9401       | LOW      |                            | 4.3-11+deb8u2                    | bash: popd controlled free                          |
    +                              +---------------------+          +                            +----------------------------------+-----------------------------------------------------+
    |                              | TEMP-0841856-B18BAF |          |                            |                                  |                                                     |
    +------------------------------+---------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------    ...

### 将结果保存为JSON

    
    
    $ trivy -f json -o results.json golang:1.12-alpine

结果：

    
    
    2019-05-16T01:46:31.777+0900    INFO    Updating vulnerability database...
    2019-05-16T01:47:03.007+0900    INFO    Detecting Alpine vulnerabilities...

JSON：

    
    
    [
      {
        "Target": "php-app/composer.lock",
        "Vulnerabilities": null
      },
      {
        "Target": "node-app/package-lock.json",
        "Vulnerabilities": [
          {
            "VulnerabilityID": "CVE-2018-16487",
            "PkgName": "lodash",
            "InstalledVersion": "4.17.4",
            "FixedVersion": "\u003e=4.17.11",
            "Title": "lodash: Prototype pollution in utilities function",
            "Description": "A prototype pollution vulnerability was found in lodash \u003c4.17.11 where the functions merge, mergeWith, and defaultsDeep can be tricked into adding or modifying properties of Object.prototype.",
            "Severity": "HIGH",
            "References": [
              "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16487",
            ]
          }
        ]
      },
      {
        "Target": "trivy-ci-test (alpine 3.7.1)",
        "Vulnerabilities": [
          {
            "VulnerabilityID": "CVE-2018-16840",
            "PkgName": "curl",
            "InstalledVersion": "7.61.0-r0",
            "FixedVersion": "7.61.1-r1",
            "Title": "curl: Use-after-free when closing \"easy\" handle in Curl_close()",
            "Description": "A heap use-after-free flaw was found in curl versions from 7.59.0 through 7.61.1 in the code related to closing an easy handle. ",
            "Severity": "HIGH",
            "References": [
              "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16840",
            ]
          },
          {
            "VulnerabilityID": "CVE-2019-3822",
            "PkgName": "curl",
            "InstalledVersion": "7.61.0-r0",
            "FixedVersion": "7.61.1-r2",
            "Title": "curl: NTLMv2 type-3 header stack buffer overflow",
            "Description": "libcurl versions from 7.36.0 to before 7.64.0 are vulnerable to a stack-based buffer overflow. ",
            "Severity": "HIGH",
            "References": [
              "https://curl.haxx.se/docs/CVE-2019-3822.html",
              "https://lists.apache.org/thread.html/8338a0f605bdbb3a6098bb76f666a95fc2b2f53f37fa1ecc89f1146f@%3Cdevnull.infra.apache.org%3E"
            ]
          },
          {
            "VulnerabilityID": "CVE-2018-16839",
            "PkgName": "curl",
            "InstalledVersion": "7.61.0-r0",
            "FixedVersion": "7.61.1-r1",
            "Title": "curl: Integer overflow leading to heap-based buffer overflow in Curl_sasl_create_plain_message()",
            "Description": "Curl versions 7.33.0 through 7.61.1 are vulnerable to a buffer overrun in the SASL authentication code that may lead to denial of service.",
            "Severity": "HIGH",
            "References": [
              "https://github.com/curl/curl/commit/f3a24d7916b9173c69a3e0ee790102993833d6c5",
            ]
          },
          {
            "VulnerabilityID": "CVE-2018-19486",
            "PkgName": "git",
            "InstalledVersion": "2.15.2-r0",
            "FixedVersion": "2.15.3-r0",
            "Title": "git: Improper handling of PATH allows for commands to be executed from the current directory",
            "Description": "Git before 2.19.2 on Linux and UNIX executes commands from the current working directory (as if '.' were at the end of $PATH) in certain cases involving the run_command() API and run-command.c, because there was a dangerous change from execvp to execv during 2017.",
            "Severity": "HIGH",
            "References": [
              "https://usn.ubuntu.com/3829-1/",
            ]
          },
          {
            "VulnerabilityID": "CVE-2018-17456",
            "PkgName": "git",
            "InstalledVersion": "2.15.2-r0",
            "FixedVersion": "2.15.3-r0",
            "Title": "git: arbitrary code execution via .gitmodules",
            "Description": "Git before 2.14.5, 2.15.x before 2.15.3, 2.16.x before 2.16.5, 2.17.x before 2.17.2, 2.18.x before 2.18.1, and 2.19.x before 2.19.1 allows remote code execution during processing of a recursive \"git clone\" of a superproject if a .gitmodules file has a URL field beginning with a '-' character.",
            "Severity": "HIGH",
            "References": [
              "http://www.securitytracker.com/id/1041811",
            ]
          }
        ]
      },
      {
        "Target": "python-app/Pipfile.lock",
        "Vulnerabilities": null
      },
      {
        "Target": "ruby-app/Gemfile.lock",
        "Vulnerabilities": null
      },
      {
        "Target": "rust-app/Cargo.lock",
        "Vulnerabilities": null
      }
    ]

### 按严重性过滤漏洞

    
    
    $ trivy --severity HIGH,CRITICAL ruby:2.3.0

结果：

    
    
    2019-05-16T01:51:46.255+0900    INFO    Updating vulnerability database...
    2019-05-16T01:51:49.213+0900    INFO    Detecting Debian vulnerabilities...
    
    ruby:2.3.0 (debian 8.4)
    =======================
    Total: 1785 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 1680, CRITICAL: 105)
    
    +-----------------------------+------------------+----------+---------------------------+----------------------------------+-------------------------------------------------+
    |           LIBRARY           | VULNERABILITY ID | SEVERITY |     INSTALLED VERSION     |          FIXED VERSION           |                      TITLE                      |
    +-----------------------------+------------------+----------+---------------------------+----------------------------------+-------------------------------------------------+
    | apt                         | CVE-2019-3462    | CRITICAL | 1.0.9.8.3                 | 1.0.9.8.5                        | Incorrect sanitation of the                     |
    |                             |                  |          |                           |                                  | 302 redirect field in HTTP                      |
    |                             |                  |          |                           |                                  | transport method of...                          |
    +-----------------------------+------------------+----------+---------------------------+----------------------------------+-------------------------------------------------+
    | bash                        | CVE-2019-9924    | HIGH     | 4.3-11                    | 4.3-11+deb8u2                    | bash: BASH_CMD is writable in                   |
    |                             |                  |          |                           |                                  | restricted bash shells                          |
    +                             +------------------+          +                           +----------------------------------+-------------------------------------------------+
    |                             | CVE-2016-7543    |          |                           | 4.3-11+deb8u1                    | bash: Specially crafted                         |
    |                             |                  |          |                           |                                  | SHELLOPTS+PS4 variables allows                  |
    |                             |                  |          |                           |                                  | command substitution                            |
    +-----------------------------+------------------+          +---------------------------+----------------------------------+-------------------------------------------------+
    | binutils                    | CVE-2017-8421    |          | 2.25-5                    |                                  | binutils: Memory exhaustion in                  |
    |                             |                  |          |                           |                                  | objdump via a crafted PE file                   |
    +                             +------------------+          +                           +----------------------------------+-------------------------------------------------+
    |                             | CVE-2017-14930   |          |                           |                                  | binutils: Memory leak in                        |
    |                             |                  |          |                           |                                  | decode_line_info                                |
    +                             +------------------+          +                           +----------------------------------+-------------------------------------------------+
    |                             | CVE-2017-7614    |          |                           |                                  | binutils: NULL                                  |
    |                             |                  |          |                           |                                  | pointer dereference in                          |
    |                             |                  |          |                           |                                  | bfd_elf_final_link function                     |
    +                             +------------------+          +                           +----------------------------------+-------------------------------------------------+
    |                             | CVE-2014-9939    |          |                           |                                  | binutils: buffer overflow in                    |
    |                             |                  |          |                           |                                  | ihex.c                                          |
    +                             +------------------+          +                           +----------------------------------+-------------------------------------------------+
    |                             | CVE-2017-13716   |          |                           |                                  | binutils: Memory leak with the                  |
    |                             |                  |          |                           |                                  | C++ symbol demangler routine                    |
    |                             |                  |          |                           |                                  | in libiberty                                    |
    +                             +------------------+          +                           +----------------------------------+-------------------------------------------------+
    |                             | CVE-2018-12699   |          |                           |                                  | binutils: heap-based buffer                     |
    |                             |                  |          |                           |                                  | overflow in finish_stab in                      |
    |                             |                  |          |                           |                                  | stabs.c                                         |
    +-----------------------------+------------------+          +---------------------------+----------------------------------+-------------------------------------------------+
    | bsdutils                    | CVE-2015-5224    |          | 2.25.2-6                  |                                  | util-linux: File name                           |
    |                             |                  |          |                           |                                  | collision due to incorrect                      |
    |                             |                  |          |                           |                                  | mkstemp use                                     |
    +                             +------------------+          +                           +----------------------------------+-------------------------------------------------+
    |                             | CVE-2016-2779    |          |                           |                                  | util-linux: runuser tty hijack                  |
    |                             |                  |          |                           |                                  | via TIOCSTI ioctl                               |
    +-----------------------------+------------------+----------+---------------------------+----------------------------------+-------------------------------------------------+

### 按类型过滤漏洞

    
    
    $ trivy --vuln-type os ruby:2.3.0

可用值：

    
    
    library
    
    os

结果：

    
    
    2019-05-22T19:36:50.530+0200	�[34mINFO�[0m	Updating vulnerability database...
    2019-05-22T19:36:51.681+0200	�[34mINFO�[0m	Detecting Alpine vulnerabilities...
    2019-05-22T19:36:51.685+0200	�[34mINFO�[0m	Updating npm Security DB...
    2019-05-22T19:36:52.389+0200	�[34mINFO�[0m	Detecting npm vulnerabilities...
    2019-05-22T19:36:52.390+0200	�[34mINFO�[0m	Updating pipenv Security DB...
    2019-05-22T19:36:53.406+0200	�[34mINFO�[0m	Detecting pipenv vulnerabilities...
    
    ruby:2.3.0 (debian 8.4)
    Total: 4751 (UNKNOWN: 1, LOW: 150, MEDIUM: 3504, HIGH: 1013, CRITICAL: 83)
    
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |              TITLE               |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | curl    | CVE-2018-14618   | CRITICAL | 7.61.0-r0         | 7.61.1-r0     | curl: NTLM password overflow     |
    |         |                  |          |                   |               | via integer overflow             |
    +         +------------------+----------+                   +---------------+----------------------------------+
    |         | CVE-2018-16839   | HIGH     |                   | 7.61.1-r1     | curl: Integer overflow leading   |
    |         |                  |          |                   |               | to heap-based buffer overflow in |
    |         |                  |          |                   |               | Curl_sasl_create_plain_message() |
    +         +------------------+          +                   +---------------+----------------------------------+
    |         | CVE-2019-3822    |          |                   | 7.61.1-r2     | curl: NTLMv2 type-3 header       |
    |         |                  |          |                   |               | stack buffer overflow            |
    +         +------------------+          +                   +---------------+----------------------------------+
    |         | CVE-2018-16840   |          |                   | 7.61.1-r1     | curl: Use-after-free when        |
    |         |                  |          |                   |               | closing "easy" handle in         |
    |         |                  |          |                   |               | Curl_close()                     |
    +         +------------------+----------+                   +---------------+----------------------------------+
    |         | CVE-2019-3823    | MEDIUM   |                   | 7.61.1-r2     | curl: SMTP end-of-response       |
    |         |                  |          |                   |               | out-of-bounds read               |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2018-16890   |          |                   |               | curl: NTLM type-2 heap           |
    |         |                  |          |                   |               | out-of-bounds buffer read        |
    +         +------------------+          +                   +---------------+----------------------------------+
    |         | CVE-2018-16842   |          |                   | 7.61.1-r1     | curl: Heap-based buffer          |
    |         |                  |          |                   |               | over-read in the curl tool       |
    |         |                  |          |                   |               | warning formatting               |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | git     | CVE-2018-17456   | HIGH     | 2.15.2-r0         | 2.15.3-r0     | git: arbitrary code execution    |
    |         |                  |          |                   |               | via .gitmodules                  |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2018-19486   |          |                   |               | git: Improper handling of        |
    |         |                  |          |                   |               | PATH allows for commands to be   |
    |         |                  |          |                   |               | executed from...                 |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | libssh2 | CVE-2019-3855    | CRITICAL | 1.8.0-r2          | 1.8.1-r0      | libssh2: Integer overflow in     |
    |         |                  |          |                   |               | transport read resulting in      |
    |         |                  |          |                   |               | out of bounds write...           |
    +         +------------------+----------+                   +               +----------------------------------+
    |         | CVE-2019-3861    | MEDIUM   |                   |               | libssh2: Out-of-bounds reads     |
    |         |                  |          |                   |               | with specially crafted SSH       |
    |         |                  |          |                   |               | packets                          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3857    |          |                   |               | libssh2: Integer overflow in     |
    |         |                  |          |                   |               | SSH packet processing channel    |
    |         |                  |          |                   |               | resulting in out of...           |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3856    |          |                   |               | libssh2: Integer overflow in     |
    |         |                  |          |                   |               | keyboard interactive handling    |
    |         |                  |          |                   |               | resulting in out of bounds...    |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3863    |          |                   |               | libssh2: Integer overflow        |
    |         |                  |          |                   |               | in user authenticate             |
    |         |                  |          |                   |               | keyboard interactive allows      |
    |         |                  |          |                   |               | out-of-bounds writes             |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3862    |          |                   |               | libssh2: Out-of-bounds memory    |
    |         |                  |          |                   |               | comparison with specially        |
    |         |                  |          |                   |               | crafted message channel          |
    |         |                  |          |                   |               | request                          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3860    |          |                   |               | libssh2: Out-of-bounds reads     |
    |         |                  |          |                   |               | with specially crafted SFTP      |
    |         |                  |          |                   |               | packets                          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3858    |          |                   |               | libssh2: Zero-byte allocation    |
    |         |                  |          |                   |               | with a specially crafted SFTP    |
    |         |                  |          |                   |               | packed leading to an...          |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-3859    |          |                   |               | libssh2: Unchecked use of        |
    |         |                  |          |                   |               | _libssh2_packet_require and      |
    |         |                  |          |                   |               | _libssh2_packet_requirev         |
    |         |                  |          |                   |               | resulting in out-of-bounds       |
    |         |                  |          |                   |               | read                             |
    +---------+------------------+          +-------------------+---------------+----------------------------------+
    | libxml2 | CVE-2018-14404   |          | 2.9.7-r0          | 2.9.8-r1      | libxml2: NULL pointer            |
    |         |                  |          |                   |               | dereference in                   |
    |         |                  |          |                   |               | xpath.c:xmlXPathCompOpEval()     |
    |         |                  |          |                   |               | can allow attackers to cause     |
    |         |                  |          |                   |               | a...                             |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2018-14567   |          |                   |               | libxml2: Infinite loop when      |
    |         |                  |          |                   |               | --with-lzma is used allows for   |
    |         |                  |          |                   |               | denial of service...             |
    +         +------------------+----------+                   +               +----------------------------------+
    |         | CVE-2018-9251    | LOW      |                   |               | libxml2: infinite loop in        |
    |         |                  |          |                   |               | xz_decomp function in xzlib.c    |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | openssh | CVE-2019-6109    | MEDIUM   | 7.5_p1-r9         | 7.5_p1-r10    | openssh: Missing character       |
    |         |                  |          |                   |               | encoding in progress display     |
    |         |                  |          |                   |               | allows for spoofing of scp...    |
    +         +------------------+          +                   +               +----------------------------------+
    |         | CVE-2019-6111    |          |                   |               | openssh: Improper validation     |
    |         |                  |          |                   |               | of object names allows           |
    |         |                  |          |                   |               | malicious server to overwrite    |
    |         |                  |          |                   |               | files...                         |
    +         +------------------+----------+                   +               +----------------------------------+
    |         | CVE-2018-20685   | LOW      |                   |               | openssh: scp client improper     |
    |         |                  |          |                   |               | directory name validation        |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | sqlite  | CVE-2018-20346   | MEDIUM   | 3.21.0-r1         | 3.25.3-r0     | CVE-2018-20505 CVE-2018-20506    |
    |         |                  |          |                   |               | sqlite: Multiple flaws in        |
    |         |                  |          |                   |               | sqlite which can be triggered    |
    |         |                  |          |                   |               | via...                           |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+
    | tar     | CVE-2018-20482   | LOW      | 1.29-r1           | 1.31-r0       | tar: Infinite read loop in       |
    |         |                  |          |                   |               | sparse_dump_region function in   |
    |         |                  |          |                   |               | sparse.c                         |
    +---------+------------------+----------+-------------------+---------------+----------------------------------+

### 跳过漏洞数据库的更新

Trivy在开始运行时会更新漏洞数据库。这通常不会花费太多的时间，因为它是一个差异的更新。但是如果你想跳过这个过程，可以使用--skip-update选项。

    
    
    $ trivy --skip-update python:3.4-alpine3.9

结果：

    
    
    2019-05-16T12:48:08.703+0900    INFO    Detecting Alpine vulnerabilities...
    
    python:3.4-alpine3.9 (alpine 3.9.2)
    ===================================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | openssl | CVE-2019-1543    | MEDIUM   | 1.1.1a-r1         | 1.1.1b-r1     | openssl: ChaCha20-Poly1305     |
    |         |                  |          |                   |               | with long nonces               |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+

### 仅更新你指定分发的漏洞数据库

默认情况下，Trivy会更新所有分发的漏洞数据库。你也可以使用--only-update选项，指定分发的漏洞数据库。

    
    
    $ trivy --only-update alpine,debian python:3.4-alpine3.9
    $ trivy --only-update alpine python:3.4-alpine3.9

结果：

    
    
    2019-05-21T19:37:06.301+0900    INFO    Updating vulnerability database...
    2019-05-21T19:37:07.793+0900    INFO    Updating alpine data...
    2019-05-21T19:37:08.127+0900    INFO    Detecting Alpine vulnerabilities...
    
    python:3.4-alpine3.9 (alpine 3.9.2)
    ===================================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | openssl | CVE-2019-1543    | MEDIUM   | 1.1.1a-r1         | 1.1.1b-r1     | openssl: ChaCha20-Poly1305     |
    |         |                  |          |                   |               | with long nonces               |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+

### 忽略未修复的漏洞

默认情况下，Trivy还会检测未修补/不可修复的漏洞。这意味着即使你更新了所有的软件包，也无法修复这些漏洞。如果你想忽略它们，可以使用--ignore-unfixed选项。

    
    
    $ trivy --ignore-unfixed ruby:2.3.0

结果：

    
    
    2019-05-16T12:49:52.656+0900    INFO    Updating vulnerability database...
    2019-05-16T12:50:14.786+0900    INFO    Detecting Debian vulnerabilities...
    
    ruby:2.3.0 (debian 8.4)
    =======================
    Total: 4730 (UNKNOWN: 1, LOW: 145, MEDIUM: 3487, HIGH: 1014, CRITICAL: 83)
    
    +------------------------------+------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------+
    |           LIBRARY            | VULNERABILITY ID | SEVERITY |     INSTALLED VERSION      |          FIXED VERSION           |                        TITLE                        |
    +------------------------------+------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------+
    | apt                          | CVE-2019-3462    | CRITICAL | 1.0.9.8.3                  | 1.0.9.8.5                        | Incorrect sanitation of the                         |
    |                              |                  |          |                            |                                  | 302 redirect field in HTTP                          |
    |                              |                  |          |                            |                                  | transport method of...                              |
    +                              +------------------+----------+                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2016-1252    | MEDIUM   |                            | 1.0.9.8.4                        | The apt package in Debian                           |
    |                              |                  |          |                            |                                  | jessie before 1.0.9.8.4, in                         |
    |                              |                  |          |                            |                                  | Debian unstable before...                           |
    +------------------------------+------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------+
    | bash                         | CVE-2019-9924    | HIGH     | 4.3-11                     | 4.3-11+deb8u2                    | bash: BASH_CMD is writable in                       |
    |                              |                  |          |                            |                                  | restricted bash shells                              |
    +                              +------------------+          +                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2016-7543    |          |                            | 4.3-11+deb8u1                    | bash: Specially crafted                             |
    |                              |                  |          |                            |                                  | SHELLOPTS+PS4 variables allows                      |
    |                              |                  |          |                            |                                  | command substitution                                |
    +                              +------------------+----------+                            +                                  +-----------------------------------------------------+
    |                              | CVE-2016-0634    | MEDIUM   |                            |                                  | bash: Arbitrary code execution                      |
    |                              |                  |          |                            |                                  | via malicious hostname                              |
    +                              +------------------+----------+                            +----------------------------------+-----------------------------------------------------+
    |                              | CVE-2016-9401    | LOW      |                            | 4.3-11+deb8u2                    | bash: popd controlled free                          |
    +------------------------------+------------------+----------+----------------------------+----------------------------------+-----------------------------------------------------+
    ...

### 指定退出代码

默认情况下，即使检测到漏洞，Trivy也会以代码0退出。如果要使用非0代码退出，可以使用--exit-code选项。

    
    
    $ trivy --exit-code 1 python:3.4-alpine3.9

结果：

    
    
    2019-05-16T12:51:43.500+0900    INFO    Updating vulnerability database...
    2019-05-16T12:52:00.387+0900    INFO    Detecting Alpine vulnerabilities...
    
    python:3.4-alpine3.9 (alpine 3.9.2)
    ===================================
    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 0, CRITICAL: 0)
    
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION |             TITLE              |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+
    | openssl | CVE-2019-1543    | MEDIUM   | 1.1.1a-r1         | 1.1.1b-r1     | openssl: ChaCha20-Poly1305     |
    |         |                  |          |                   |               | with long nonces               |
    +---------+------------------+----------+-------------------+---------------+--------------------------------+

此选项对CI/CD很有用。在以下示例中，仅当发现严重漏洞时，测试才会失败。

    
    
    $ trivy --exit-code 0 --severity MEDIUM,HIGH ruby:2.3.0
    $ trivy --exit-code 1 --severity CRITICAL ruby:2.3.0

### 忽略指定漏洞

使用.trivyignore。

    
    
    $ cat .trivyignore
    # Accept the risk
    CVE-2018-14618
    
    # No impact in our settings
    CVE-2019-1543
    
    $ trivy python:3.4-alpine3.9

结果：

    
    
    2019-05-16T12:53:10.076+0900    INFO    Updating vulnerability database...
    2019-05-16T12:53:28.134+0900    INFO    Detecting Alpine vulnerabilities...
    
    python:3.4-alpine3.9 (alpine 3.9.2)
    ===================================
    Total: 0 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0)

### 清除镜像缓存

使用--clear-cache选项清除镜像缓存。如果更新具有相同标签的镜像（例如使用最新标签时），则此选项很有用。

    
    
    $ trivy --clear-cache python:3.7

结果：

    
    
    2019-05-16T12:55:24.749+0900    INFO    Removing image caches...
    2019-05-16T12:55:24.769+0900    INFO    Updating vulnerability database...
    2019-05-16T12:56:14.055+0900    INFO    Detecting Debian vulnerabilities...
    
    python:3.7 (debian 9.9)
    =======================
    Total: 3076 (UNKNOWN: 0, LOW: 127, MEDIUM: 2358, HIGH: 578, CRITICAL: 13)
    
    +------------------------------+---------------------+----------+--------------------------+------------------+-------------------------------------------------------+
    |           LIBRARY            |  VULNERABILITY ID   | SEVERITY |    INSTALLED VERSION     |  FIXED VERSION   |                         TITLE                         |
    +------------------------------+---------------------+----------+--------------------------+------------------+-------------------------------------------------------+
    | apt                          | CVE-2011-3374       | LOW      | 1.4.9                    |                  |                                                       |
    +------------------------------+---------------------+          +--------------------------+------------------+-------------------------------------------------------+
    | bash                         | TEMP-0841856-B18BAF |          | 4.4-5                    |                  |                                                       |
    +------------------------------+---------------------+----------+--------------------------+------------------+-------------------------------------------------------+
    ...

### 重启

使用--reset选项清除所有缓存和数据库。在此之后，需要很长时间才能在本地重建漏洞数据库。

    
    
    $ trivy --reset

结果：

    
    
    2019-05-16T13:05:31.935+0900    INFO    Resetting...

## 持续集成（CI）

扫描Travis CI/CircleCI内置的镜像。如果发现漏洞，测试将失败。如果你不想测试失败，请指定--exit-code 0。

 **注意：** 第一次可能需要等待一段时间（第二次缓存后会快许多）

### Travis CI

    
    
    $ cat .travis.yml
    services:
      - docker
    
    env:
      global:
        - COMMIT=${TRAVIS_COMMIT::8}
    
    before_install:
      - docker build -t trivy-ci-test:${COMMIT} .
      - export VERSION=$(curl --silent "https://api.github.com/repos/knqyf263/trivy/releases/latest" | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
      - wget https://github.com/knqyf263/trivy/releases/download/v${VERSION}/trivy_${VERSION}_Linux-64bit.tar.gz
      - tar zxvf trivy_${VERSION}_Linux-64bit.tar.gz
    script:
      - ./trivy --exit-code 0 --severity HIGH --quiet --auto-refresh trivy-ci-test:${COMMIT}
      - ./trivy --exit-code 1 --severity CRITICAL --quiet --auto-refresh trivy-ci-test:${COMMIT}
    cache:
      directories:
        - $HOME/.cache/trivy

示例：<https://travis-ci.org/knqyf263/trivy-ci-test>

存储库：<https://github.com/knqyf263/trivy-ci-test>

### CircleCI

    
    
    $ cat .circleci/config.yml
    jobs:
      build:
        docker:
          - image: docker:18.09-git
        steps:
          - checkout
          - setup_remote_docker
          - restore_cache:
              key: vulnerability-db
          - run:
              name: Build image
              command: docker build -t trivy-ci-test:${CIRCLE_SHA1} .
          - run:
              name: Install trivy
              command: |
                apk add --update curl
                VERSION=$(
                    curl --silent "https://api.github.com/repos/knqyf263/trivy/releases/latest" | \
                    grep '"tag_name":' | \
                    sed -E 's/.*"v([^"]+)".*/\1/'
                )
    
                wget https://github.com/knqyf263/trivy/releases/download/v${VERSION}/trivy_${VERSION}_Linux-64bit.tar.gz
                tar zxvf trivy_${VERSION}_Linux-64bit.tar.gz
                mv trivy /usr/local/bin
          - run:
              name: Scan the local image with trivy
              command: trivy --exit-code 0 --quiet --auto-refresh trivy-ci-test:${CIRCLE_SHA1}
          - save_cache:
              key: vulnerability-db
              paths:
                - $HOME/.cache/trivy
    workflows:
      version: 2
      release:
        jobs:
          - build

示例：<https://circleci.com/gh/knqyf263/trivy-ci-test>

存储库：<https://github.com/knqyf263/trivy-ci-test>

## 私有Docker Registry的授权

Trivy可以从私有注册表下载镜像，而无需安装Docker和任何第三方的工具。那是因为它很容易在CI进程中运行。

你所要做的就是安装Trivy并设置ENV vars。但我并不建议在你的本地计算机上使用ENV vars。

### Docker Hub

Docker
Hub需要TRIVY_AUTH_URL，TRIVY_USERNAME和TRIVY_PASSWORD。从公共存储库下载时，你不需要设置ENV变量。

    
    
    export TRIVY_AUTH_URL=https://registry.hub.docker.com
    export TRIVY_USERNAME={DOCKERHUB_USERNAME}
    export TRIVY_PASSWORD={DOCKERHUB_PASSWORD}

### Amazon ECR（弹性容器注册表）

Trivy使用AWS SDK。你不需要安装aws CLI工具。你可以使用AWS CLI的ENV Vars。

### GCR（谷歌容器注册表）

Trivy使用Google Cloud SDK。你不需要安装gcloud命令。

如果你想使用目标项目的存储库，可以通过GOOGLE_APPLICATION_CREDENTIAL设置。

    
    
    # must set TRIVY_USERNAME empty char
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credential.json

### 自托管注册表（BasicAuth）

BasicAuth服务器需要TRIVY_USERNAME和TRIVY_PASSWORD。

    
    
    export TRIVY_USERNAME={USERNAME}
    export TRIVY_PASSWORD={PASSWORD}
    
    # if you want to use 80 port, use NonSSL
    export TRIVY_NON_SSL=true

## 漏洞检测

### 系统软件包

未修复/不可修复的漏洞意味着尚未在其分发中提供该修补程序。

系统 | 支持版本 | 目标软件包 | 检测未修复的漏洞  
---|---|---|---  
Alpine Linux | 2.2 - 2.7, 3.0 - 3.10 | Installed by apk | NO  
Red Hat Universal Base Image | 7, 8 | Installed by yum/rpm | YES  
Red Hat Enterprise Linux | 6, 7, 8 | Installed by yum/rpm | YES  
CentOS | 6, 7 | Installed by yum/rpm | YES  
Debian GNU/Linux | wheezy, jessie, stretch, buster | Installed by apt/apt-get/dpkg | YES  
Ubuntu | 12.04, 14.04, 16.04, 18.04, 18.10, 19.04 | Installed by apt/apt-get/dpkg | YES  
  
### 应用程序依赖项

Trivy会自动检测容器中的以下文件，并扫描应用程序依赖项中的漏洞。

    
    
    Gemfile.lock
    
    Pipfile.lock
    
    poetry.lock
    
    composer.lock
    
    package-lock.json
    
    yarn.lock
    
    Cargo.lock

这些文件的路径不重要。

示例：<https://npm.pkg.github.com/knqyf263/trivy-ci-test/blob/master/Dockerfile>

## 使用

    
    
    NAME:
      trivy - A simple and comprehensive vulnerability scanner for containers
    USAGE:
      main [options] image_name
    VERSION:
      0.0.15
    OPTIONS:
      --format value, -f value    format (table, json) (default: "table")
      --input value, -i value     input file path instead of image name
      --severity value, -s value  severities of vulnerabilities to be displayed (comma separated) (default: "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL")
      --output value, -o value    output file name
      --exit-code value           Exit code when vulnerabilities were found (default: 0)
      --skip-update               skip db update
      --reset                     remove all caches and database
      --clear-cache, -c           clear image caches
      --quiet, -q                 suppress progress bar
      --ignore-unfixed            display only fixed vulnerabilities
      --refresh                   refresh DB (usually used after version update of trivy)
      --auto-refresh              refresh DB automatically when updating version of trivy
      --debug, -d                 debug mode
      --vuln-type value           comma-separated list of vulnerability types (os,library)
      --help, -h                  show help
      --version, -v               print the version

## 与其他扫描器的对比

扫描器 | 系统软件包 | 应用依赖项 | 简易使用 | 精确度 | 适用于CI  
---|---|---|---|---|---  
Trivy | ◯ | ◯ | ◯ | ◎ | ◯  
Clair | ◯ | × | △ | ◯ | △  
Anchore Engine | ◯ | △ | △ | ◯ | △  
Quay | ◯ | × | ◯ | ◯ | ×  
MicroScanner | ◯ | × | ◯ | △ | ◯  
Docker Hub | ◯ | × | ◯ | × | ×  
GCR | ◯ | × | ◯ | ◯ | ×  
  
### 准确性

以下条形图显示了扫描[composer:1.7.2](https://hub.docker.com/_/composer?tab=tags) 和
[crate:3.2.2](https://hub.docker.com/_/crate?tab=tags) 的结果。这些镜像都是随机选择的。

扫描器：[Clair](https://github.com/coreos/clair)，[Quay](https://quay.io/)，[MicroScanner（免费）](https://github.com/aquasecurity/microscanner)，[Docker
Hub](https://hub.docker.com/)，[Anchore Engine](https://anchore.com/engine/)

请参阅[电子表格](https://docs.google.com/spreadsheets/d/16uj9vGh2PHMcVwb_D4h0nYUSvzCAxcnUz9UgQaDCYs4/edit#gid=0)了解有关详情

在这种情况下，所有漏洞扫描器检测到的漏洞的联合将用作数据集。

 **注意：**

可能存在所有扫描程序都无法检测到的漏洞。

可能存在误报，因为我已手动进行了确认。

### Alpine Linux

使用Alpine Linux
3.7.1的[composer:1.7.2](https://hub.docker.com/_/composer?tab=tags)结果（截至2019/05/12）。

![3.png](https://image.3001.net/images/20190707/1562458293_5d2138b55895a.png!small)

Trivy具有较高的精确度，而GCR没有检测到任何的漏洞。虽然Docker Hub有许多True Positive，但它也存在很多误报。

### RHEL/CentOS

使用CentOS
7.6.1810的[crate:3.2.2](https://hub.docker.com/_/crate?tab=tags)结果（截至2019/05/14）。

以下图表仅包含可修复的漏洞。

![4.png](https://image.3001.net/images/20190707/1562458308_5d2138c4a1ed4.png!small)

大多数扫描程序仅检测RHEL/CentOS上的修补/可修复的漏洞，但Trivy还会检测未修补/无法修复的漏洞。

此图还包括无法修复的漏洞。

![5.png](https://image.3001.net/images/20190707/1562458322_5d2138d21a49f.png!small)

### 其他系统

在其他OS的情况下，结果类似于其他容器扫描程序。

### vs Clair

[Clair](https://github.com/coreos/clair)使用[alpine-secdb](https://github.com/alpinelinux/alpine-secdb/)。但该数据库的目的是知道哪些包具有backport的修复。正如README描述的那样，它不是Alpine中所有安全问题的完整数据库。

Trivy从[Alpine Linux
Redmine](https://bugs.alpinelinux.org/projects/alpine/issues)收集Alpine
Linux中的漏洞信息。然后，这些漏洞将被保存在[vuln-list](https://github.com/knqyf263/vuln-list/tree/master/alpine)上。

alpine-secdb有6959个漏洞（截至2019/05/12）。vuln-list有11101个与Alpine
Linux相关的漏洞（截至2019/05/12）。检测准确性存在差异，因为漏洞数量几乎翻了一番。

此外，Trivy还分析了中间层，并找出了哪个版本的库用于静态链接。

Clair无法处理以下情况，因为它在应用所有图层后分析图像。

    
    
    RUN apk add --no-cache sqlite-dev \
     && wget https://xxx/yyy.tar.gz \
     && tar zxvf yyy.tar.gz && cd yyy \
     && make && make install \
     && apk del sqlite-dev

正如许多人所知，很难选择Clair客户端，因为很多客户都被弃用了。

最后，Trivy还可以检测应用程序相关库中的漏洞，例如Bundler，Composer，Pipenv等。

### vs Anchore Engine

与Clair类似，Alpine Linux的检测准确度也有所不同。Anchore
Engine不会检测RHEL/CentOS上的无法修复的漏洞，而Trivy则会进行检测。

此外，Anchore Engine需要一些额外操作才能开始扫描。Trivy则更容易使用。

### vs Quay，Docker Hub，GCR

由于Quay在内部使用Clair，因此它具有与Clair相同的精确度。Docker Hub只能扫描官方镜像。GCR几乎无法检测到Alpine
Linux上的漏洞。此外，它还被锁定到了特定的注册表。

无论注册表如何，都可以使用Trivy。而且它也很容易与CI/CD服务集成。

## 问答

### Homebrew

###  **Error: Your macOS keychain GitHub credentials do not have sufficient
scope!**

    
    
    $ brew tap knqyf263/trivy
    Error: Your macOS keychain GitHub credentials do not have sufficient scope!
    Scopes they need: none
    Scopes they have:
    Create a personal access token:
    https://github.com/settings/tokens/new?scopes=gist,public_repo&description=Homebrew
    echo 'export HOMEBREW_GITHUB_API_TOKEN=your_token_here' >> ~/.zshrc

尝试：

    
    
    $ printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain erase

### Error: knqyf263/trivy/trivy 64 already installed

    
    
    $ brew upgrade
    ...
    Error: knqyf263/trivy/trivy 64 already installed

尝试：

    
    
    $ brew unlink trivy && brew uninstall trivy
    ($ rm -rf /usr/local/Cellar/trivy/64)
    $ brew install knqyf263/trivy/trivy

### 其他

 **检测到trivy的新版本。请使用--refresh选项再试一次**

    
    
    $ trivy --refresh alpine:3.9

### 未知错误

请使用--reset选项再试一次

    
    
    $ trivy --reset

## 相关项目

[Remic](https://github.com/knqyf263/remic)

漏洞扫描程序，用于检测应用程序依赖项中公开披露的漏洞

## 贡献

    
    
    fork存储库：github.com/knqyf263/trivy to github.com/you/repo
    
    获取源码：go get github.com/knqyf263/trivy
    
    处理原始代码
    
    远程添加到你的存储库：git remote add myfork <https://github.com/you/repo.git>
    
    push你的更改：git push myfork
    
    创建一个新的Pull Request

请参阅：[GitHub 和 Go: forking, pull requests 和 go-getting](http://blog.campoy.cat/2014/03/github-and-go-forking-pull-requests-and.html)

***参考来源：[GitHub](https://github.com/knqyf263/trivy)，FB小编secist编译，转载请注明来自FreeBuf.COM**

