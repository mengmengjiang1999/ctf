平时接触到的 python 项目并不多，对 python 的代码审计更是没有接触，偶然朋友发来了一个漏洞 `Flask
send_file函数导致的绝对路径遍历`，感觉打开了新世界的大门，于是就以一个初学者的角度，进行复现分析一下。详情也可以根据 [Python :
Flask Path Traversal
Vulnerability](https://github.com/github/securitylab/issues/669)进行分析学习

## send_file 的妙用

在以 flask 框架开发的系统中，为了直接实现用户访问某一个 URL 时就可以下载到文件，我们就使用 `send_file`来实现

    
    
    from flask import Flask  
    from flask import send_file  
    ​  
    app = Flask(__name__)  
    ​  
    ​  
    @app.route('/download')  
    def downloadFile():  
      path = "test.txt"  
      return send_file(path)  
    ​  
    ​  
    if __name__ == '__main__':  
      app.run()

![image-20220712143740-tgapluo.png](https://image.3001.net/images/20220718/1658133798_62d51d26e1c0d3aa015cb.png!small)

我们看到 如此运行的效果是直接返回了文件的内容，浏览器并没有识别成一个文件下载下来。

要想让浏览器识别成为文件下载的话，只需要加上 `as_attachment=True`

    
    
    from flask import Flask  
    from flask import send_file  
    ​  
    app = Flask(__name__)  
    ​  
    ​  
    @app.route('/download')  
    def downloadFile():  
      path = "test.txt"  
      return send_file(path, as_attachment=True)  
    ​  
    ​  
    if __name__ == '__main__':  
      app.run()

![image-20220712144129-5lfxoh1.png](https://image.3001.net/images/20220718/1658133799_62d51d27d932a2af9d5d3.png!small)

当下载的文件名是中文时

    
    
    from flask import Flask  
    from flask import send_file  
    ​  
    app = Flask(__name__)  
    ​  
    ​  
    @app.route('/download')  
    def downloadFile():  
      path = "测试.txt"  
      return send_file(path, as_attachment=True)  
    ​  
    ​  
    if __name__ == '__main__':  
      app.run()  
    ​

![image-20220712144553-rfsklrr.png](https://image.3001.net/images/20220718/1658133800_62d51d28abb48079f3a2e.png!small)

Content-Disposition:

[Content-Disposition](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Content-Disposition)

在常规的 HTTP 应答中，Content-Disposition
响应头指示回复的内容该以何种形式展示，是以内联的形式（即网页或者页面的一部分），还是以附件的形式下载并保存到本地。其可以是inline(默认值,所以可以不指定)或者是attachment,attachment表示附件,浏览器看到这个值一般会弹出一个保持文件的确认框,或者像chrome直接下载。

![image-20220712154546-xp04gz8.png](https://image.3001.net/images/20220718/1658133801_62d51d299cf742d1343e3.png!small)

![image-20220712154611-sdocylf.png](https://image.3001.net/images/20220718/1658133802_62d51d2a81b5dfc9dc7e8.png!small)

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 漏洞分析

漏洞的触发是在 `send_file`中，我们跟进看一下

`flask.helpers.send_file`

![image-20220712150848-4oxc0ge.png](https://image.3001.net/images/20220718/1658133803_62d51d2b97c606d0f9324.png!small)

继续跟进查看

`werkzeug.utils.send_file`

![image-20220712151150-j2xa0en.png](https://image.3001.net/images/20220718/1658133804_62d51d2ca8eda9d680690.png!small)

我们在本地构造一个简单的语句进行尝试

    
    
    >>> import os.path  
    >>> _root_path = "path/to/mySafeStaticDir"  
    >>> path_or_file = "/../../../../../../../etc/passwd"  
    >>> os.path.join(_root_path,path_or_file)  
    '/../../../../../../../etc/passwd'

![image-20220712150358-6rvt143.png](https://image.3001.net/images/20220718/1658133805_62d51d2da6851699e6885.png!small)

我们发现 `os.path.join`使用不受信任的输入调用时不安全的。当
`os.path.join`调用遇到绝对路径时，它会忽略在该点之前遇到的所有参数并开始使用新的绝对路径。当参数可控时，我们控制恶意参数输入绝对路径，`os.path.join`会完全忽略静态目录。所以，当
`os.path.join`来获取来自 `flask.send_file`的不受信任的输入时，可能会目录遍历攻击。

## 漏洞复现

我们在本地构造简单的代码进行测试，获取从外部传入的参数 `filename`

    
    
    from flask import Flask, request  
    from flask import send_file  
    ​  
    app = Flask(__name__)  
    ​  
    ​  
    @app.route('/download')  
    def downloadFile():  
      filename = request.args.get('filename')  
      return send_file(filename, as_attachment=True)  
    ​  
    if __name__ == '__main__':  
      app.run()

通过控制 `filename`为绝对路径，就实现了目录穿越漏洞

![image-20220712152202-lh364go.png](https://image.3001.net/images/20220718/1658133806_62d51d2e7da9769d17c99.png!small)

![image-20220712152036-vivv0sk.png](https://image.3001.net/images/20220718/1658133807_62d51d2f85276a7e48b3a.png!small)

![image-20220712152100-pcc4riv.png](https://image.3001.net/images/20220718/1658133808_62d51d305712b63e9ac44.png!small)

## 总结反思

这个漏洞非常的有趣，漏洞的修复是可以使用`flask.safe_join`加入不受信任的路径或用`flask.send_file`调用替换`flask.send_from_directory`调用。

这个漏洞虽然很简单，但是在 github 上很多用 python 开发的项目都用了这个函数，如果不加以修复，会造成很大的危害。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

