[i春秋作家：大木瓜](https://bbs.ichunqiu.com/thread-40908-1-1.html?from=beef)  

  

环境：  
Python 3  
模块：  
Lxml  
Request  
Beautifulsoup  
开始：  
首先看一下目标站：

    
    
    http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-1.html

  
![image.png](https://image.3001.net/images/20180530/15276631266821.png!small)  

这里有一个目录：我们点击第一个北京市，就可以看到其中的表格，和北京市所有的大学名字

我们的目标就是吧每一个城市的所有大学，分别放在不同的txt文本中。

![image.png](https://image.3001.net/images/20180530/15276631397214.png!small)  

正式开始分析：

我们审查元素，我们要取的目标为学校名称![image.png](https://image.3001.net/images/20180530/15276631605921.png!small)

可以清晰的看到网页的结构，我们要取的目标在一个tbodyz中，并在一个tr标签内。继续分析下一个名字找到他们的规律  

![image.png](https://image.3001.net/images/20180530/15276631801084.png!small)  

可以看到每个名字都在一个单独的tr标签中。

好我们在看一下这个北京市的url和第二个城市网页对应的url。

`<http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-2.html>`

`<http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-3.html>`

可以看到最后的数字不同，从二开始。依次增加。好我们已经基本获得了目标的信息，下面我们开始激动人心的敲代码。

我们先从一页开始。

    
    
    #coding=utf-8
    import requests
    import lxml
    from bs4 import BeautifulSoup as bs #导入我们的BF,并且命名为bs，名字太长了偷个懒。
    def school(): #定义一个函数
            url="http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-2.html"
            r=requests.get(url=url) #利用requests请求我们的目标网站。
            soup=bs(r.content,"lxml")#利用beautifulsoup解析，将返回内容赋值给soup
            print (soup)       #打印出内容。
    if __name__ == '__main__':  #程序开始运行的地方，需要调用刚才设置的函数，不然程序是不会运行的。
        school()

写完之后点一下运行，成功返回发现并不需要设置头信息。省去了一些麻烦。

![image.png](https://image.3001.net/images/20180530/15276632283875.png!small)  

现在我们开始取内容：

我们的内容在<tr height=”29”>这个标签中，我们以这个标签为标准，查找所有的这个标签中的内容。代码是这样的。运行

def school():
url="[http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-2.html](https://bbs.ichunqiu.com/thread-40908-1-1.html?from=beef)"

r=requests.get(url=url)

soup=bs(r.content,"lxml")
content=soup.find_all(name="tr",attrs={"height":"29"})

print(content)

![image.png](https://image.3001.net/images/20180530/15276632478879.png!small)Ok
成功返回了我们需要的东西，但是有很多其他没有用的选项，现在我们要去掉这些东西。继续编辑school函数。我们需要用循环遍历我们的取出的内容。让每一个tr标签中的内容作为一个独立的列表，然后利用find_all方法找出而每一个td标签为list中的内容，方便我们取参数。学校名称位于第二个td标签中，在list中的位置则为1.代码如下。

    
    
    def school():        url="http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-2.html"
            r=requests.get(url=url)        soup=bs(r.content,"lxml")        content=soup.find_all(name="tr",attrs={"height":"29"})
            for content1 in content:
                soup_content=bs(str(content1),"lxml")
                soup_content1=soup_content.find_all(name="td")
                print(soup_content1[1])

  
![image.png](https://image.3001.net/images/20180530/1527663264729.png!small)  

加好之后我们运行代码。发现报错了，不慌我们看一下报错的内容

报错大意为列出索引超出范围。但是我们发现还是成功返回了一个内容，我们再去分析一下网页源代码。

![image.png](https://image.3001.net/images/20180530/1527663278900.png!small)

可以看到前三个tr标签，我们成功的取到了第一个tr标签中的”学校名称”这行的内容，然后第二个tr报错。我们的代码打印的的是list的第二个内容，但是在第二个tr标签中只有一个内容。然后剩下的都恢复了正常，我们怎么解决这个问题呢。可以用python的异常处理。当他报错时，然后忽略错误继续运行。把代码变成这样。

    
    
    def school():
            url="http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-2.html"
            r=requests.get(url=url) 
            soup=bs(r.content,"lxml")
            content=soup.find_all(name="tr",attrs={"height":"29"})
            for content1 in content:
                try:               soup_content=bs(str(content1),"lxml")                soup_content1=soup_content.find_all(name="td")
                    print(soup_content1[1])
                except IndexError:
                    pass 

再次运行。

![image.png](https://image.3001.net/images/20180530/15276633138047.png!small)  

成功了，但这只是一个城市，我们还需要其他的。接下来我们需要用一个for循环，从2到33，每次加1，并修改url中的控制页面的参数中。  
  

    
    
    #coding=utf-8
    import requests
    import lxml
    from bs4 import BeautifulSoup as bs 
    def school(): 
        for i in range(2,34,1):
            url="http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-%s.html"%(str(i))
            r=requests.get(url=url)
            soup=bs(r.content,"lxml")
            content=soup.find_all(name="tr",attrs={"height":"29"})
            for content1 in content:
                try:
                    soup_content=bs(str(content1),"lxml")
                    soup_content1=soup_content.find_all(name="td")
                    print(soup_content1[1])
                except IndexError:
                    pass
    if __name__ == '__main__': 
        school()

  
![image.png](https://image.3001.net/images/20180530/15276633318329.png!small)  

我们可以看到不仅有北京的学校，还有天津的，当然下面所有的学校都打印出来了。我们还要去掉标签。修改打印为如下代码，这样就只会看到文本。

`print(soup_content1[1].string)`

主要功能就写完了，我们还需要，将他们分别存放在不同的文件夹内并保持为特定的文件名，当然我们不可能手动输入每个城市的名字。还记的我们刚才报错的地方吗，那个地方刚刚好有我们要的城市名称。理一下思路，我们首先从网页中取出城市名称，并新建一个对应城市名称的TXT文本，然后把我们取得的内容分别放入不同的文件内。为了防止报错停止，我们再加一个异常处理好让我们继续把我们的代码写完。

    
    
    def school():
        for i in range(2,34,1):
            try:
                url="http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-%s.html"%(str(i))
                r=requests.get(url=url)
                soup=bs(r.content,"lxml")
                content2=soup.find_all(name="td",attrs={"colspan":"7"})[0].string
                f1=open("%s.txt"%(content2),"w")
                content=soup.find_all(name="tr",attrs={"height":"29"})
                for content1 in content:
                    try:
                        soup_content=bs(str(content1),"lxml")
                        soup_content1=soup_content.find_all(name="td")
                        f1.write(soup_content1[1].string+"/n")
                        print(soup_content1[1].string)
                    except IndexError:
                        pass
            except IndexError:
                pass

  
![image.png](https://image.3001.net/images/20180530/15276633522006.png!small)完整代码：  

    
    
    #coding=utf-8
    import requests
    import lxml
    from bs4 import BeautifulSoup as bs
    def school():
        for i in range(2,34,1):
            try:
                url="http://gaokao.chsi.com.cn/gkxx/zszcgd/dnzszc/201706/20170615/1611254988-%s.html"%(str(i))
                r=requests.get(url=url)
                soup=bs(r.content,"lxml")
                content2=soup.find_all(name="td",attrs={"colspan":"7"})[0].string
                f1=open("%s.txt"%(content2),"w")
                content=soup.find_all(name="tr",attrs={"height":"29"})
                for content1 in content:
                    try:
                        soup_content=bs(str(content1),"lxml")
                        soup_content1=soup_content.find_all(name="td")
                        f1.write(soup_content1[1].string+"/n")
                        print(soup_content1[1].string)
                    except IndexError:
                        pass
            except IndexError:
                pass
    
    if __name__ == '__main__':
        school()

总结：  
这个程序的难度并不大，也没有用什么多线程，类，非常的简单，并不一定是代码越多的程序越好，有的时候我们只是想快速的完成我们的要实现的目标，这时候代码就要越简洁越好。希望可以给初学者一些好的学习思路，最后我之所以要再加一个异常处理，是因为又出现了一个和上面一样的报错，而为了快速实现我们的目标，我直接尝试添加一个异常处理，程序正常运行。最后，写的不好的地方，希望大家多多指点。  
PS:附件我就不打包了，自己动手丰衣足食，虽然附上了所有代码但是还是希望大家可以自己动手写一下。

有问题大家可以留言哦，也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

