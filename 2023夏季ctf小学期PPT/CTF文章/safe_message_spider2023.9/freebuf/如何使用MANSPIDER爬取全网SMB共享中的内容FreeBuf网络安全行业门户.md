![](https://image.3001.net/images/20210827/1630060844_6128c12c61fcd97e81ab4.jpg!small)

## 关于MANSPIDER

MANSPIDER是一款资源爬取工具，该工具能够爬取全网SMB共享中我们所感兴趣的内容，并支持通过正则表达式搜索目标文件名或文件内容。

## 支持得文件类型

> PDF
>
> DOCX
>
> XLSX
>
> PPTX
>
> 任意基于文本的格式

![](https://image.3001.net/images/20210827/1630060855_6128c137b8fa8a078352b.gif!small)

## 工具安装

（可选）我们需要安装下列依赖项以添加额外的文件解析功能：

    
    
    # 针对图片 (png, jpeg)
    
    $ sudo apt install tesseract tesseract-data-eng
    
     
    
    # 针对遗留文档格式支持 (.doc)
    
    $ sudo apt install antiword

安装MANSPIDER（安装需要一点时间，请耐心等待）：

    
    
    $ pip install pipx
    
    $ pipx install man-spider

## 使用样例#1：使用文件名搜索包含凭证的文件

    
    
    $ manspider 192.168.0.0/24 -f passw user admin account network login logon cred -d evilcorp -u bob -p Passw0rd

## 使用样例#2：搜索包含“password”的XLSX文件

    
    
    $ manspider share.evilcorp.local -c password -e xlsx -d evilcorp -u bob -p Passw0rd

## 使用样例#3：搜索感兴趣的文件后缀

    
    
    $ manspider share.evilcorp.local -e bat com vbs ps1 psd1 psm1 pem key rsa pub reg txt cfg conf config -d evilcorp -u bob -p Passw0rd

## 使用样例#4：搜索金融相关的文件

    
    
    $ manspider share.evilcorp.local --dirnames bank financ payable payment reconcil remit voucher vendor eft swift -f '[0-9]{5,}' -d evilcorp -u bob -p Passw0rd

## 使用样例#5：搜索凭证数据

    
    
    $ manspider share.evilcorp.local -e pfx p12 pkcs12 pem key crt cer csr jks keystore key keys der -d evilcorp -u bob -p Passw0rd

## 工具使用帮助

    
    
    usage: manspider [-h] [-u USERNAME] [-p PASSWORD] [-d DOMAIN] [-m MAXDEPTH] [-H HASH] [-t THREADS] [-f REGEX [REGEX ...]] [-e EXT [EXT ...]] [--exclude-extensions EXT [EXT ...]]
    
                     [-c REGEX [REGEX ...]] [--sharenames SHARE [SHARE ...]] [--exclude-sharenames [SHARE ...]] [--dirnames DIR [DIR ...]] [--exclude-dirnames DIR [DIR ...]] [-q] [-n]
    
                     [-mfail INT] [-o] [-s SIZE] [-v]
    
                     targets [targets ...]
    
     
    
    Scan for juicy data on SMB shares. Matching files and logs are stored in $HOME/.manspider. All filters are case-insensitive.
    
     
    
    positional arguments:
    
      targets               IPs, Hostnames, CIDR ranges, or files containing targets to spider (NOTE: local searching also supported, specify directory name or keyword "loot" to search
    
                            downloaded files)
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -u USERNAME, --username USERNAME
    
                            username for authentication
    
      -p PASSWORD, --password PASSWORD
    
                            password for authentication
    
      -d DOMAIN, --domain DOMAIN
    
                            domain for authentication
    
      -m MAXDEPTH, --maxdepth MAXDEPTH
    
                            maximum depth to spider (default: 10)
    
      -H HASH, --hash HASH  NTLM hash for authentication
    
      -t THREADS, --threads THREADS
    
                            concurrent threads (default: 5)
    
      -f REGEX [REGEX ...], --filenames REGEX [REGEX ...]
    
                            filter filenames using regex (space-separated)
    
      -e EXT [EXT ...], --extensions EXT [EXT ...]
    
                            only show filenames with these extensions (space-separated, e.g. `docx xlsx` for only word & excel docs)
    
      --exclude-extensions EXT [EXT ...]
    
                            ignore files with these extensions
    
      -c REGEX [REGEX ...], --content REGEX [REGEX ...]
    
                            search for file content using regex (multiple supported)
    
      --sharenames SHARE [SHARE ...]
    
                            only search shares with these names (multiple supported)
    
      --exclude-sharenames [SHARE ...]
    
                            don't search shares with these names (multiple supported)
    
      --dirnames DIR [DIR ...]
    
                            only search directories containing these strings (multiple supported)
    
      --exclude-dirnames DIR [DIR ...]
    
                            don't search directories containing these strings (multiple supported)
    
      -q, --quiet           don't display matching file content
    
      -n, --no-download     don't download matching files
    
      -mfail INT, --max-failed-logons INT
    
                            limit failed logons
    
      -o, --or-logic        use OR logic instead of AND (files are downloaded if filename OR extension OR content match)
    
      -s SIZE, --max-filesize SIZE
    
                            don't retrieve files over this size, e.g. "500K" or ".5M" (default: 10M)
    
      -v, --verbose         show debugging messages

## 工具使用样例

MANSPIDER可以爬取每一个目标系统中的共享文件，如果提供的凭证无法使用，该工具将会使用“访客”账号开启空会话。

![](https://image.3001.net/images/20210827/1630060944_6128c190af650be3b3bd7.png!small)

## 项目地址

 **MANSPIDER：** 【[
_GitHub传送门_](https://github.com/blacklanternsecurity/MANSPIDER)】

