![](https://image.3001.net/images/20210430/1619794600_608c1aa8b7e9cabbf1b1d.png!small)

## Cook介绍

Cook是一款功能强大的字典生成工具，该工具可以通过创建单词的排列和组合以生成复杂的字典和密码。Cook可以使用一系列预定于前缀、后缀、单词和模式来创建复杂的节点、字典和密码。

## 工具安装

使用Go安装（要求本地主机安装好Go环境）：

    
    
    go get github.com/giteshnxtlvl/cook

或者

    
    
    GO111MODULE=on go get github.com/giteshnxtlvl/cook

工具更新：

    
    
    go get -u github.com/giteshnxtlvl/cook

## 自定义工具

通过自定义配置开发，研究人员可以轻松创建和使用自己的字典列表或密码模式：

  * 创建一个名为yaml的空文件，或直接下载【[ _cook.yaml_](https://github.com/giteshnxtlvl/cook/blob/main/cook.yaml)】文件。
  * 创建一个环境变量“COOK =Path of file”。
  * 最后，运行命令“cook -config”。

注意，如果你不想自定义配置工具的话，就不需要在环境变量中设置COOK了。

## 工具使用

### 基本排列

![](https://image.3001.net/images/20210430/1619794647_608c1ad79bc14a5c98afd.png!small)

 **使用秘诀：**

    
    
    cook -start admin,root  -sep _,-  -end secret,critical  start:sep:end
    
    
    cook admin,root:_,-:secret,criticalc'c'c'c'c

###
高级排列![](https://image.3001.net/images/20210430/1619794675_608c1af3116cbe3621295.png!small)

###
预定义数据集![](https://image.3001.net/images/20210430/1619794700_608c1b0c8677924ab751b.png!small)

 **使用秘诀：**

    
    
    cook -start admin,root  -sep _ -end secret  start:sep:archive
    
    
    cook admin,root:_:archive

###
创建你自己的数据集![](https://image.3001.net/images/20210430/1619794723_608c1b23436260ecd2ac2.png!small)

###
使用CRUNCH![](https://image.3001.net/images/20210430/1619794740_608c1b3423ff0e0276ace.png!small)

### 模式/功能

![](https://image.3001.net/images/20210430/1619794754_608c1b422b3d885b70684.png!small)

 **使用秘诀：**

    
    
    cook -name elliot -birth date(17,Sep,1994) name:birth

### 整数范围

![](https://image.3001.net/images/20210430/1619794772_608c1b54d320081d02862.png!small)

### 文件

 **从文件输入正则表达式**

![](https://image.3001.net/images/20210430/1619794793_608c1b6994665d9da9fc8.png!small)

使用秘诀：

    
    
    cook -exp raft-large-extensions.txt:\.asp.*  /:admin:exp

使用唯一名称保存字典：![](https://image.3001.net/images/20210430/1619794814_608c1b7ee102d9a01fd6a.png!small)

 **文件未找到**

如果参数中标记的文件未找到，并不会报错，而是将会运行下列命令：

    
    
    cook -file file_not_exists.txt admin,root:_:file
    
    
    admin_file_not_exists.txt
    
    root_file_not_exists.txt

### 拼写样例

![](https://image.3001.net/images/20210430/1619794850_608c1ba21c70d52b13b67.png!small)

## 结合其他工具使用Cook

使用GoBuster直接进行模糊测试：

    
    
    cook admin,root:_:archive | gobuster dir -u https://example.com/ -w -
## 所有的数据集

    
    
    # Character set like crunch
    
    charSet:
    
        sep   : [_- ] #common separators
    
        n     : [0123456789]
    
        A     : [ABCDEFGHIJKLMNOPQRSTUVWXYZ]
    
        a     : [abcdefghijklmnopqrstuvwxyz]
    
        aAn   : [abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]
    
        An    : [ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]
    
        an    : [abcdefghijklmnopqrstuvwxyz0123456789]
    
        aA    : [abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ]
    
        s     : ["!#$%&'()*+,-./:;<=>?@[\\]^_`{|}~&\""]
    
        all   : ["!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\""]
    
     
    
    # File to access from anywhere
    
    files:
    
        raft_ext     : [E:\tools\wordlists\SecLists\Discovery\Web-Content\raft-large-extensions.txt]
    
        raft_dir     : [E:\tools\wordlists\SecLists\Discovery\Web-Content\raft-large-directories.txt]
    
        raft_files   : [E:\tools\wordlists\SecLists\Discovery\Web-Content\raft-large-files.txt]
    
        robot_1000   : [E:\tools\wordlists\SecLists\Discovery\Web-Content\RobotsDisallowed-Top1000.txt]
    
     
    
    # Create your lists
    
    lists:
    
        schemas      : [aim, callto, cvs, data, facetime, feed, file, ftp, git, gopher, gtalk, h323, hdl, http, https, imap, irc, irc6, ircs, itms, javascript, magnet, mailto, mms, msnim, news, nntp, prospero, rsync, rtsp, rtspu, sftp, shttp, sip, sips, skype, smb, snews, ssh, svn, svn, svn+ssh, telnet, tel, wais, ymsg]
    
        bypass       : ["%00", "%09", "%0A", "%0D", "%0D%0A"]
    
     
    
        admin_set    : [admin, root, su, superuser, administration]
    
        api          : [/v1/,/v2/,/v3/,/v4/,/v5/,/api/]
    
        pass_ends    : [123, "@123", "#123"]
    
     
    
        months       : [January, February, March, April, May, June, July, August, September, October, November, December]
    
        mons         : [Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec]
    
     
    
    # Patterns
    
    patterns:
    
        date :
    
            - date(D,M,Y)
    
            - DMY  
    
            - MDY
    
            - D/M/Y  
    
            - M/D/Y
    
            - D-M-Y  
    
            - M-D-Y   
    
            - D.M.Y  
    
            - M.D.Y  
    
            - D.Y  
    
            - M.Y  
    
            - D.M
    
     
    
     
    
    # Extension Set, . will added before using this
    
    extensions:
    
        config  : [conf, confq, config]
    
        data    : [xml, json, yaml, yml]
    
        backup  : [bak, backup, backup1, backup2]
    
        exec    : [exe, msi, bin, command, sh, bat, crx]
    
        web     : [html, html5, htm, js, jsx, jsp, wasm, php, php3, php5, php7]
    
        iis     : [asax, ascx, asmx, aspx, exe, aspx.cs, ashx, axd, config, htm, jar, js, rdl, swf, txt, xls, xml, xsl, zpd, suo, sln]
    
        archive : [7z, a, apk, xapk, ar, bz2, cab, cpio, deb, dmg, egg, gz, iso, jar, lha, mar, pea, rar, rpm, s7z, shar, tar, tbz2, tgz, tlz, war, whl, xpi, zip, zipx, xz, pak, tar.gz, gz]
    
        code    : [c, cc, class, clj, cpp, cs, cxx, el, go, h, java, lua, m, m4, php, php3, php5, php7, pl, po, py, rb, rs, sh, swift, vb, vcxproj, xcodeproj, xml, diff, patch, js, jsx]
    
     
    
        #Rest
    
        css_type: [css, less, scss]
    
        sheet   : [ods, xls, xlsx, csv, ics vcf]
    
        slide   : [ppt, pptx, odp]
    
        font    : [eot, otf, ttf, woff, woff2]
    
        text    : [doc, docx, ebook, log, md, msg, odt, org, pages, pdf, rtf, rst, tex, txt, wpd, wps]
    
        audio   : [aac, aiff, ape, au, flac, gsm, it, m3u, m4a, mid, mod, mp3, mpa, pls, ra, s3m, sid, wav, wma, xm]
    
        book    : [mobi, epub, azw1, azw3, azw4, azw6, azw, cbr, cbz]
    
        video   : [3g2, 3gp, aaf, asf, avchd, avi, drc, flv, m2v, m4p, m4v, mkv, mng, mov, mp2, mp4, mpe, mpeg, mpg, mpv, mxf, nsv, ogg, ogv, ogm, qt, rm, rmvb, roq, srt, svi, vob, webm, wmv, yuv]
    
        image   : [3dm, 3ds, max, bmp, dds, gif, jpg, jpeg, png, psd, xcf, tga, thm, tif, tiff, yuv, ai, eps, ps, svg, dwg, dxf, gpx, kml, kmz, webp]

## 项目地址

 **Cook：** https://github.com/giteshnxtlvl/cook

