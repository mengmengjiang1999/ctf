**i春秋作家：tllm**

**原文来自：[利用python完成大学刷课（从0到完成的思路）](https://bbs.ichunqiu.com/thread-46865-1-1.html?from=beef)**

> 最近刚刚开学，学校总是有很多让人无语的课要修，还不能不修。然后我想写一个自动修课的脚本。大佬们不要笑我 是边面向百度学selenium边写脚本的
> 然后踩了一些坑 记录一下

先放最终效果视频

PS:室友在打lol说看见中单 不是说我哈 哈哈哈哈  
<http://ow2cltt3t.bkt.clouddn.com/15d3ed600eb39af4d80c4a49088b5c06.mp4>

## 0x01:

首先分析一下它是怎么验证你看完这个课的。![image.png](https://image.3001.net/images/20181018/1539844952_5bc82b58c92fe.png!small)当学习完成时会发出这个请求
![image.png](https://image.3001.net/images/20181018/1539844961_5bc82b6159810.png!small)然后看看这几个请求的数据都是在前端哪里生成的![image.png](https://image.3001.net/images/20181018/1539844968_5bc82b68b0e3e.png!small)一番寻找就看到了是wx.js下的function
finishWxCourse() 。控制台执行 finishWxCourse() 果然会发起完成修课的请求
![image.png](https://image.3001.net/images/20181018/1539844977_5bc82b71ec879.png!small)

## 0x02:

然后剩下就是脚本的思路 首先要获取课程的链接 然后打开以后执行js finishWxCourse() 后来发现requests不是很好的能执行js
然后我就听从了几个师傅的意见用selenium...所以是边学边写的 遇到了几个小坑记一记

安装不表 网上很多教程 chromedriver装在环境变量里面就好了 比如python的环境变量 如果遇到问题可以留言评论

先说一下 代码最终的整体思路是 打开网站----设置cookie----然后通过点击打开所有的隐藏元素-----定位点击----后退
---------------点击打开所有的隐藏元素-------定位点击----------后退..然后重复之前的步骤

### 这是简单的启动浏览器和发起请求

    
    
            driver = webdriver.Chrome("C:/Python27/chromedriver.exe")
            driver.get("http://wb.mycourse.cn/")

### 删除所有的cookie并设置cookie。我是手动登陆然后再添加 有一个要记住的就是先要请求一次网页 才能设置cookie 再请求网页

    
    
    driver.add_cookie({'name':'JSESSIONID','value':'93BEC0FDEF428F98DA1F69A6B3C2BF88'})  #已经过期的了 师傅们
    driver.add_cookie({'name':'acw_tc','value':'7b39758715392684428742395e7ed4b94ed4e9616cb11d4b9df9e244ec7573'})        
    driver.add_cookie({'name':'SERVERID','value':'02cc313090e3650844ab417ac43bf774|1539357767|1539357719'})
    driver.get("http://wb.mycourse.cn/svnweiban/student/study_studyAndTest.action")

### 接着就是定位元素了 首先要看到我们要点击的课程链接

![image.png](https://image.3001.net/images/20181018/1539844998_5bc82b86bf9d3.png!small)  

看到class属性 有一个坑就是这里多个class属性 不能直接多个class一起定位 不然会找到 如果全部一起定位要用css寻找并且用.来链接
然后我这里用的是 courseLink定位 这个名字也很明显是做什么的。然后我也发现是98个课程都能定位到 前面几个class能定位到1000多个

    
    
    link2s = driver.find_elements_by_class_name("courseLink")

#### 我原本就很开心的以为差不多做完了准备写出一个这样子的代码

    
    
            for i in range(99):
                    link2s = driver.find_elements_by_class_name("courseText")
                    link2s[i].click()
                    driver.execute_script("finishWxCourse()")

但是结果发现无法获取到元素 什么鬼 然后一直报错···苦苦百度以后发现···原来是没有展开元素 是diplay:none。 隐藏了
然后我百度以后找到的方法一直是 通过执行js把none改为block结果发现不好定位啊

![image.png](https://image.3001.net/images/20181018/1539845008_5bc82b9041913.png!small)  

    
    
    <div class="widthPercent100 paddingL_30 border-box displayNone" style="transition: all 0.5s ease 0s; display: none;">

class属性都是不唯一的 然后很蛋疼 后来师傅推荐说通过xpath定位 可是好多个 不想嫌弃麻烦 洗了个澡回来以后发现可以通过定位元素 然后点击元素
来实现自动展开列表

通过 前面截图的cursorPointer 能够成功定位20多个地方出来 但是前面几个定位是什么首页 搜索 不是我们想要的
问题不大。我们删除这几个定位就好了

    
    
     blockclass = driver.find_elements_by_class_name("cursorPointer")
            del blockclass[0]
            del blockclass[0]
            del blockclass[0]
            for blockc in blockclass:
                    blockc.click()

删除几个定位就好了  
然后现在调试以后 集合代码跑了一次发现了几个问题，第一个就是 当

    
    
    driver.execute_script("finishWxCourse()")    #执行js代码

执行代码以后，会alert一个窗口出来说 完成了课程。然后就会导致selenium不能点后退 面向百度编程以后

    
    
      dig_alert = driver.switch_to.alert     #搜索弹窗
            dig_alert.accept()                     #点击确定

接着就是最后一个坑了`driver.back()`以后蛋疼了 back以后 之前定位的会失效···所以只能每回退一次重新定位
还有要注意的就是在一些关键地方之前要time sleep一秒 不然还没请求完成出来就执行下一步了 会导致报错 最后就大功告成了

下面贴完整代码

#coding=utf-8

from selenium import webdriver

import time

def login():

driver = webdriver.Chrome("C:/Python27/chromedriver.exe")

driver.get("<http://wb.mycourse.cn/>")

driver.delete_all_cookies()

driver.add_cookie({'name':'JSESSIONID','value':'93BEC0FDEF428F98DA1F69A6B3C2BF88'})
#cookie都过期了的 不用试

driver.add_cookie({'name':'acw_tc','value':'7b39758715392684428742395e7ed4b94ed4e9616cb11d4b9df9e244ec7573'})

driver.add_cookie({'name':'SERVERID','value':'02cc313090e3650844ab417ac43bf774|1539357767|1539357719'})

driver.get("<http://wb.mycourse.cn/svnweiban/student/study_studyAndTest.action>")

blockclass = driver.find_elements_by_class_name("cursorPointer")

del blockclass[0]

del blockclass[0]

del blockclass[0]

for blockc in blockclass:

blockc.click()

for i in range(99):

link2s = driver.find_elements_by_class_name("courseText")

link2s _.click()  
driver.execute_script("finishWxCourse()")  
time.sleep(1)  
dig_alert = driver.switch_to.alert  
dig_alert.accept()  
driver.back()  
time.sleep(1)  
blockclass = driver.find_elements_by_class_name("cursorPointer")  
del blockclass[0]  
del blockclass[0]  
del blockclass[0]  
for blockc in blockclass:  
blockc.click()  
time.sleep(0.5)  
login()_

 _  
_

**大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~**  

