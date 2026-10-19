> [本文作者：i春秋作家——阿甫哥哥](https://bbs.ichunqiu.com/space-uid-97258.html)  
>

  

系列文章专辑：
**[](https://bbs.ichunqiu.com/forum.php?mod=collection&action=view&ctid=96)**
**[https://bbs.ichunqiu.com/forum.php?mod=collection&action=view&ctid=96](https://bbs.ichunqiu.com/thread-34102-1-1.html?from=beef)**  
 **目录：**

> 0x00 前言  
>  
> 0x01 火车余票查询  
>  
> 0x02 Selenium模块简单介绍  
>  
> 0x03 打造SupremeBOT

 **0x00 前言**

一个AJ1联名OFF-White的鞋原价1399，炒卖价已经到了1w+(其实我也是个SneakerHead)以下是我近期的交易记录(拿来装X的)，很扎心.....But，现在都是抽签，跟抢貌似无关，就不写SneakerBot了...  

  

![图片.png](https://image.3001.net/images/20180302/15199791719594.png!small)  

再附上我在NIKE美国官网中签截图吧，听说Bred Toe还上了热搜，啊哈哈  

![图片.png](https://image.3001.net/images/20180302/15199791595484.png!small)  

所以就有了本篇文章吧....  
强调一下，本文的主要目的就是抢东西，从火车余票查询，到打造一个抢Supreme的BOT吧。。而这一切都是基于Python  

 **0x01 火车余票查询**

之前回家，不少人为了火车票发愁......

  

![图片.png](https://image.3001.net/images/20180302/15199791495422.png!small)  

所以，就有了本小节文章....监控火车余票...

本次环境是：Python2.7+deepinlinux

因为Windows编码问题多的我想打人，所以就换了linux

实现完的效果是这样的

  

![4.gif](https://image.3001.net/images/20180302/15199793651402.gif!small)  

咱们分步写

[https://kyfw.12306.cn/otn/leftTicket/init](https://bbs.ichunqiu.com/thread-34102-1-1.html?from=beef)，抓包

  

![图片.png](https://image.3001.net/images/20180302/15199791204906.png!small)  

![图片.png](https://image.3001.net/images/20180302/15199791146985.png!small)  

这是一个Get请求....所以看下这个url

[https://kyfw.12306.cn/otn/leftTi ...
purpose_codes=ADULT](https://bbs.ichunqiu.com/thread-34102-1-1.html?from=beef)

train_date参数后面是时间

from_station参数后是起点站

to_station参数后是到达站

分析了这些之后，就可以通过Python来实现这个url了

这里呢，有个问题，像这些城市地点的英文在哪获取，通过F12大法，发现在这

  

![图片.png](https://image.3001.net/images/20180302/15199791006124.png!small)  

[https://kyfw.12306.cn/otn/resour ...
tion_version=1.9047](https://bbs.ichunqiu.com/thread-34102-1-1.html?from=beef)

我事先爬好了这些，在这里感谢一下Onise表哥@0nise，为了保证代码的美观性吧，所以我就import它了

  
![图片.png](https://image.3001.net/images/20180302/15199790471153.png!small)

先获取页面内容，  

    
    
    # -*- coding: utf-8 -*-    import requests
    from stations import stations
    def Get_train_text():
        from_station = stations.get(raw_input('Please enter where you are from:'))
        to_station = stations.get(raw_input('Please enter where you want to go:'))
        date = raw_input('Please enter the date you want to inquire:')
        url = ('https://kyfw.12306.cn/otn/leftTicket/queryZ?'
              'leftTicketDTO.train_date={}&'
              'leftTicketDTO.from_station={}&'
              'leftTicketDTO.to_station={}&'
              'purpose_codes=ADULT').format(date,from_station,to_station)
           
        r=requests.get(url)
        trains_text = r.json()['data']['result']
        print trains_text
    if __name__ == '__main__':
        Get_train_text()

  
![图片.png](https://image.3001.net/images/20180302/1519979039587.png!small)  
然后for循环...

    
    
    def Get_train_information():[/size]
    [size=3]    for raw_train in Get_train_text():[/size]
    [size=3]        print raw_train

然后观察一下  

![图片.png](https://image.3001.net/images/20180302/15199785178603.png!small)

这样就很明朗了吧...  

    
    
    def Get_train_information():
        key_list = []
        value_list = []
        for key,value in stations.items():
            key_list.append(key)
            value_list.append(value)
        for raw_train in Get_train_text():
            data_list = raw_train.split('|')
            train_number = data_list[3]  #车次
            from_station_code = data_list[6]  #始发站信息
            to_station_code = data_list[7] #终点站信息
            from_station_index = value_list.index(from_station_code)
            to_station_index = value_list.index(to_station_code)
            from_station_name = key_list[from_station_index]
            to_station_name = key_list[to_station_index] 
            start_time = data_list[8] #出发时间
            arrive_time = data_list[9]  #到达时间
            time_duration = data_list[10]  #历时
            first_class_seat = data_list[31] #一等座
            second_class_seat = data_list[30] #二等座
            soft_sleep = data_list[23] or '--' #软卧
            hard_sleep = data_list[28] or '--'  #硬卧
            hard_seat= data_list[29] or '--' #硬座
            no_seat = data_list[26] or '--'  #无座

大概就是这样，然后让这些可观，就要用到PrettyTable了

pip install prettytable

    
    
    # -*- coding: utf-8 -*-    import requests
    from stations import stations
    from prettytable import PrettyTable
    def Get_train_text():
        from_station = stations.get(raw_input('Please enter where you are from:'))
        to_station = stations.get(raw_input('Please enter where you want to go:'))
        date = raw_input('Please enter the date you want to inquire:')
        url = ('https://kyfw.12306.cn/otn/leftTicket/queryZ?'
              'leftTicketDTO.train_date={}&'
              'leftTicketDTO.from_station={}&'
              'leftTicketDTO.to_station={}&'
              'purpose_codes=ADULT').format(date,from_station,to_station)
           
        r=requests.get(url)
        trains_text = r.json()['data']['result']
        return trains_text
    def Get_train_information():
        key_list = []
        value_list = []
        table = PrettyTable()
        table._set_field_names('车次 出发地点 到达地点 出发时间 到达时间 历时 一等 二等 软卧 硬卧 硬座 无座'.split())
        for key,value in stations.items():
            key_list.append(key)
            value_list.append(value)
        for raw_train in Get_train_text():
            data_list = raw_train.split('|')
            train_number = data_list[3]  #车次
            from_station_code = data_list[6]  #始发站信息
            to_station_code = data_list[7] #终点站信息
            from_station_index = value_list.index(from_station_code)
            to_station_index = value_list.index(to_station_code)
            from_station_name = key_list[from_station_index]
            to_station_name = key_list[to_station_index] 
            start_time = data_list[8] #出发时间
            arrive_time = data_list[9]  #到达时间
            time_duration = data_list[10]  #历时
            first_class_seat = data_list[31] #一等座
            second_class_seat = data_list[30] #二等座
            soft_sleeper = data_list[23] or '--' #软卧
            hard_sleeper = data_list[28] or '--'  #硬卧
            hard_seat= data_list[29] or '--' #硬座
            no_seat = data_list[26] or '--'  #无座
            table.add_row([
                train_number,
                from_station_name, 
                to_station_name,
                start_time, 
                arrive_time,
                time_duration,
                first_class_seat,
                second_class_seat,
                soft_sleeper,
                hard_sleeper,
                hard_seat,
                no_seat
                      ])
        print table
    if __name__ == '__main__':
        Get_train_information()

 **0x02 Selenium模块简单介绍**

之后的，咱们应该都要用Python中selenium模块，怎么说呢，这个东西，我感觉挺好用的唉  
这里呢，我简单的说下  
安装  
pip install selenium  
安装Firefox  
http://ftp.mozilla.org/pub/firefox/releases/  
安装FirefoxDriver，geckdriver  
https://github.com/mozilla/geckodriver/releases  
Chrome浏览器需要安装chromedriver，IE浏览器要安装IEdriver  
driver的路径可以直接放在python路径下，我这里把driver放在了python的Scripts路径下，同时把script路径加入环境变量。  
说几个简单用法..  
访问页面并获取源码

    
    
    #-*- coding: UTF-8 -*-    from selenium import webdriver
     
    browser = webdriver.Firefox()
    browser.get("http://www.baidu.com")
    print browser.page_source 
    browser.close()

浏览器最大化  

    
    
    driver.maximize_window()

设置浏览器大小  

    
    
    driver.set_window_size(480, 800)

浏览器前进后退

    
    
    driver.back()#浏览器后退
    driver.forward()#浏览器前进

  

> webdriver 提供了一系列的元素定位方法，常用的有以下几种：  
>  
> id  
> name  
> class name  
> tag name  
> link text  
> partial link text  
> xpath  
> css selector  
> 分别对应python webdriver 中的方法为：  
>  
> find_element_by_id()  
> find_element_by_name()  
> find_element_by_class_name()  
> find_element_by_tag_name()  
> find_element_by_link_text()  
> find_element_by_partial_link_text()  
> find_element_by_xpath()  
> find_element_by_css_selector()

  
就简单介绍到这，写的很不详细吧....  
这里呢？你可以去看官方文档  
<http://selenium-python.readthedocs.io/index.html>

 **0x03 打造属于自己的SupremeBOT**

  
![图片.png](https://image.3001.net/images/20180302/15199789408115.png!small)  

> Supreme1994年秋季诞生于美国纽约曼哈顿，由James Jebbia创办。supreme的本意是最高、至上的。Supreme是结合滑板、Hip-> hop等文化并以滑板为主的美国街头服饰品牌。

 **那什么，我要说一下，是supreme[su:ˈpri:m]（苏普瑞姆)，而不是super me**  
找人代购又太贵，价格炒的高的不要不要得，还有一堆BOT。。。。所以呢，我就有了个打造属于自己得SUPREMEBOT了，啊哈哈

在这里强调一下，人生苦短，我用Python

还是采用分步写，不看别的，只看思路，对对对  
官网地址：http://www.supremenewyork.com/  
首先，咱们先判断，商品是不是存在，并加入购物车，我拿supreme的配件做的演示，没有加判断SIZE的。。。我后面会贴上，很简单的，几行代码的事情，啊哈哈我定义了三个函数，第一个函数，是遍历商品关键字的，第二个函数是，判断商品是否存在的，第三个是main函数(主要是为了装X吧，啊哈哈)

我直接贴代码了。。

    
    
    #-*- coding: UTF-8 -*-    import time
    try:  
        from selenium import webdriver
    except ImportError:
        print "Selenium module is not installed...Exiting program."
        exit(1)
         
    def Check(keywords, text):
        for i in keywords:
            if i not in text:
                return False
        return True
     
    def searchCommodity(browser, category, keywords, color):    
        print " Searching Commodity ..."
        browser.get("http://www.supremenewyork.com/shop/all/" + category)
        links = browser.find_elements_by_class_name("name-link")
        i = 0
        while i < len(links):
            if (Check(keywords, links[i].text) & (color in links[i+1].text)):
                links[i].click()
                print "[/i][/i][i][i] Commodity found"
                return True
            i += 2
        print "[/i][/i][i][i] Commodity not found"
        return False
    def main():
        browser = webdriver.Firefox()
        browser.implicitly_wait(5)  #隐性等待5s，隐形等待是设置了一个最长等待时间，如果在规定时间内网页加载完成，则执行下一步，否则一直等到时间截止，然后执行下一步
        category = "accessories"  #商品类别
        keywords = []
        keywords.append("Gold Pendant")  #商品关键字
        color = "Gold"  #颜色
        if searchCommodity(browser, category, keywords, color) == False:
            return -1
        try:
            browser.find_element_by_name("commit").click()
        except:
             print "[/i][/i][i][i] Commodity sold out"
             return -1
    if __name__ == '__main__':
        main()

额，这里加个商品描述吧，好看一点，啊哈哈  

    
    
    print "Description : " + links[i].text
    print "Color : " + links[i+1].text

把商品加入了购物车了，就该买单了，是不是，啊哈哈，如果手动填，肯定会错过，所以selenium的功效来了

我又定义了函数fillForm，这里面的收货信息什么的都要改，改成你的信息

强调一下，我写的是美国官网，英国官网貌似在信息那多了个啥，忘了。。。。

    
    
    #-*- coding: UTF-8 -*-    import time
    try:  
        from selenium import webdriver
        from selenium.webdriver.support.ui import Select
    except ImportError:
        print "Selenium module is not installed...Exiting program."
        exit(1)
         
    def Check(keywords, text):
        for i in keywords:
            if i not in text:
                return False
        return True
     
    def searchCommodity(browser, category, keywords, color):    
        print "[/i][/i][/i][i][i][i] Searching Commodity ..."
        browser.get("http://www.supremenewyork.com/shop/all/" + category)
        links = browser.find_elements_by_class_name("name-link")
        i = 0
        while i < len(links):
            if (Check(keywords, links[i].text) & (color in links[i+1].text)):
                print "Description : " + links[i].text
                print "Color : " + links[i+1].text
                links[i].click()
                print "[/i][/i][/i][/i][/i][/i][i][i][i] Commodity found"
                return True
            i += 2
        print "[/i][/i][/i][i][i][i] Commodity not found"
        return False
    def fillForm(browser):
        billing_name = "xx xxx"
        email = "2014802836@qq.com"
        tel = "1111111111"
        billing_address = "xxxxxxxxx"
        billing_city = "Wauchula"
        billing_zip = "11111"
        billing_state = "FL"
        billing_country = "USA"
        nlb = "9999 999 999 9999"
        month = "02"
        year = "2018"
        rvv = "888"
        name = browser.find_element_by_name("order[billing_name]").send_keys(billing_name)
        email = browser.find_element_by_name("order[email]").send_keys(email)
        tel = browser.find_element_by_name("order[tel]").send_keys(tel)
        address = browser.find_element_by_name("order[billing_address]").send_keys(billing_address)
        address = browser.find_element_by_name("order[billing_city]").send_keys(billing_city)
        postCode = browser.find_element_by_name("order[billing_zip]").send_keys(billing_zip)
        billing_state = browser.find_element_by_name('order[billing_state]').send_keys(billing_state)
        countrySelect = Select(browser.find_element_by_name("order[billing_country]")).select_by_visible_text(billing_country)
        creditCardSelect = browser.find_element_by_name('credit_card[nlb]').send_keys(nlb)
        monthExpirationSelect = Select(browser.find_element_by_name("credit_card[month]")).select_by_visible_text(month)
        yearExpirationSelect = Select(browser.find_element_by_name("credit_card[year]")).select_by_visible_text(year)
        cvv = browser.find_element_by_name("credit_card[rvv]").send_keys(rvv)
        browser.find_element_by_class_name("terms").click()
    def main():
        browser = webdriver.Firefox()
        browser.implicitly_wait(5)  #隐性等待5s，隐形等待是设置了一个最长等待时间，如果在规定时间内网页加载完成，则执行下一步，否则一直等到时间截止，然后执行下一步
        category = "accessories"  #商品类别
        keywords = []
        keywords.append("Gold Pendant")  #商品关键字
        color = "Gold"  #颜色
        if searchCommodity(browser, category, keywords, color) == False:
            return -1
        try:
            browser.find_element_by_name("commit").click()
        except:
             print "[/i][/i] Commodity sold out"[/i]
    [i]         return -1[/i]
    [i]    time.sleep(1)  #睡一秒，主要是怕报错[/i]
    [i]    browser.find_element_by_class_name("checkout").click()[/i]
    [i]    fillForm(browser)[/i]
    [i]    browser.find_element_by_name("commit").click()[/i]
     
    [i]if __name__ == '__main__':[/i]
    [i]    main()

然后就这么好了，然后美化一下CODE吧

    
    
    #-*- coding: UTF-8 -*-[/i]
    [i]import time[/i]
    [i]try:  [/i]
    [i]    from selenium import webdriver[/i]
    [i]    from selenium.webdriver.support.ui import Select[/i]
    [i]except ImportError:[/i]
    [i]    print "Selenium module is not installed...Exiting program."[/i]
    [i]    exit(1)[/i]
     
    [i]def Check(keywords, text):[/i]
    [i]    for i in keywords:[/i]
    [i]        if i not in text:[/i]
    [i]            return False[/i]
    [i]    return True[/i]
     
    [i]def searchCommodity(browser, category, keywords, color):    [/i]
    [i]    print "[i][i] Searching Commodity ..."
        browser.get("http://www.supremenewyork.com/shop/all/" + category)
        links = browser.find_elements_by_class_name("name-link")
        i = 0
        while i < len(links):
            if (Check(keywords, links[i].text) & (color in links[i+1].text)):
                print "Description : " + links[i].text
                print "Color : " + links[i+1].text
                links[i].click()
                print "[/i][/i][/i][/i][/i][/i][i][i][i] Commodity found"
                return True
            i += 2
        print "[/i][/i][/i][i][i][i] Commodity not found"
        return False
    def fillForm(browser):
        billing_name = "xx xxx"
        email = "2014802836@qq.com"
        tel = "1111111111"
        billing_address = "xxxxxxxxx"
        billing_city = "Wauchula"
        billing_zip = "11111"
        billing_state = "FL"
        billing_country = "USA"
        nlb = "9999 999 999 9999"
        month = "02"
        year = "2018"
        rvv = "888"
        name = browser.find_element_by_name("order[billing_name]").send_keys(billing_name)
        email = browser.find_element_by_name("order[email]").send_keys(email)
        tel = browser.find_element_by_name("order[tel]").send_keys(tel)
        address = browser.find_element_by_name("order[billing_address]").send_keys(billing_address)
        address = browser.find_element_by_name("order[billing_city]").send_keys(billing_city)
        postCode = browser.find_element_by_name("order[billing_zip]").send_keys(billing_zip)
        billing_state = browser.find_element_by_name('order[billing_state]').send_keys(billing_state)
        countrySelect = Select(browser.find_element_by_name("order[billing_country]")).select_by_visible_text(billing_country)
        creditCardSelect = browser.find_element_by_name('credit_card[nlb]').send_keys(nlb)
        monthExpirationSelect = Select(browser.find_element_by_name("credit_card[month]")).select_by_visible_text(month)
        yearExpirationSelect = Select(browser.find_element_by_name("credit_card[year]")).select_by_visible_text(year)
        cvv = browser.find_element_by_name("credit_card[rvv]").send_keys(rvv)
        browser.find_element_by_class_name("terms").click()
    def main():
        print " ____                                      ____   ___ _____ "
        print "/ ___| _   _ _ __  _ __ ___ _ __ ___   ___| __ ) / _ \_   _|"
        print "\___ \| | | | '_ \| '__/ _ \ '_ ` _ \ / _ \  _ \| | | || |"
        print " ___) | |_| | |_) | | |  __/ | | | | |  __/ |_) | |_| || |" 
        print "|____/ \__,_| .__/|_|  \___|_| |_| |_|\___|____/ \___/ |_|  "
        print "            |_|                                             "
        print "[/i][/i][/i][i][i][i] Opening Browser ..."
        browser = webdriver.Firefox()
        browser.implicitly_wait(5)  #隐性等待5s，隐形等待是设置了一个最长等待时间，如果在规定时间内网页加载完成，则执行下一步，否则一直等到时间截止，然后执行下一步
        print "[/i][/i][/i][i][i][i] Browser Opened"
        category = "accessories"  #商品类别
        keywords = []
        keywords.append("Gold Pendant")  #商品关键字
        color = "Gold"  #颜色
        if searchCommodity(browser, category, keywords, color) == False:
            return -1
        try:
            browser.find_element_by_name("commit").click()
        except:
             print "[/i][/i][/i][i][i][i] Commodity sold out"
             return -1
        time.sleep(1)  #睡一秒，主要是怕报错
        browser.find_element_by_class_name("checkout").click()
        print "Filling in the information"
        fillForm(browser)
        print "Filled..."
        print "Prepare to buy a bill....."
        browser.find_element_by_name("commit").click()
        print "Finshed,congratulations on your favorite things!!!!!"
     
    if __name__ == '__main__':
        main()

  
![图片.png](https://image.3001.net/images/20180302/15199788189426.png!small)  
  

 _差不多是这样，可以加个raw_input,这样就可以省去打开浏览器的时间了，对对对，最后放上完全版的，可以抢帽衫什么的_  

    
    
    #-*- coding: UTF-8 -*-    import time
    try:  
        from selenium import webdriver
        from selenium.webdriver.support.ui import Select
    except ImportError:
        print "Selenium module is not installed...Exiting program."
        exit(1)
         
    def Check(keywords, text):
        for i in keywords:
            if i not in text:
                return False
        return True
     
    def searchCommodity(browser, category, keywords, color):    
        print "[/i][/i][/i][i][i][i] Searching Commodity ..."
        browser.get("http://www.supremenewyork.com/shop/all/" + category)
        links = browser.find_elements_by_class_name("name-link")
        i = 0
        while i < len(links):
            if (Check(keywords, links[i].text) & (color in links[i+1].text)):
                print "Description : " + links[i].text
                print "Color : " + links[i+1].text
                links[i].click()
                print "[/i][/i][/i][/i][/i][/i][i][i][i] Commodity found"
                return True
            i += 2
        print "[/i][/i][/i][i][i][i] Commodity not found"
        return False
    def fillForm(browser):
        billing_name = "xx xxx"
        email = "2014802836@qq.com"
        tel = "1111111111"
        billing_address = "xxxxxxxxx"
        billing_city = "Wauchula"
        billing_zip = "11111"
        billing_state = "FL"
        billing_country = "USA"
        nlb = "9999 999 999 9999"
        month = "02"
        year = "2018"
        rvv = "888"
        name = browser.find_element_by_name("order[billing_name]").send_keys(billing_name)
        email = browser.find_element_by_name("order[email]").send_keys(email)
        tel = browser.find_element_by_name("order[tel]").send_keys(tel)
        address = browser.find_element_by_name("order[billing_address]").send_keys(billing_address)
        address = browser.find_element_by_name("order[billing_city]").send_keys(billing_city)
        postCode = browser.find_element_by_name("order[billing_zip]").send_keys(billing_zip)
        billing_state = browser.find_element_by_name('order[billing_state]').send_keys(billing_state)
        countrySelect = Select(browser.find_element_by_name("order[billing_country]")).select_by_visible_text(billing_country)
        creditCardSelect = browser.find_element_by_name('credit_card[nlb]').send_keys(nlb)
        monthExpirationSelect = Select(browser.find_element_by_name("credit_card[month]")).select_by_visible_text(month)
        yearExpirationSelect = Select(browser.find_element_by_name("credit_card[year]")).select_by_visible_text(year)
        cvv = browser.find_element_by_name("credit_card[rvv]").send_keys(rvv)
        browser.find_element_by_class_name("terms").click()
    def main():
        print " ____                                      ____   ___ _____ "
        print "/ ___| _   _ _ __  _ __ ___ _ __ ___   ___| __ ) / _ \_   _|"
        print "\___ \| | | | '_ \| '__/ _ \ '_ ` _ \ / _ \  _ \| | | || |"
        print " ___) | |_| | |_) | | |  __/ | | | | |  __/ |_) | |_| || |" 
        print "|____/ \__,_| .__/|_|  \___|_| |_| |_|\___|____/ \___/ |_|  "
        print "            |_|                                             "
        print "[/i][/i][/i][i][i][i] Opening Browser ..."
        browser = webdriver.Firefox()
        browser.implicitly_wait(5)  #隐性等待5s，隐形等待是设置了一个最长等待时间，如果在规定时间内网页加载完成，则执行下一步，否则一直等到时间截止，然后执行下一步
        print "[/i][/i][/i][i][i][i] Browser Opened"
        raw_input('[/i][/i][/i][i][i][i]Press Enter to buy your Commodity')
        category = "pants"  #商品类别
        keywords = []
        keywords.append("Tiger Stripe Track Pant")  #商品关键字
        color = "Brown"  #颜色
        size = 'Medium'
        if searchCommodity(browser, category, keywords, color) == False:
            return -1
        if size != "":
            try:
                sizeSelect = Select(browser.find_element_by_id("s"))
                sizeSelect.select_by_visible_text(size)
            except:
                print "[/i][/i][/i][i][i][i] Commodity sold out......."
                return -1
        try:
            browser.find_element_by_name("commit").click()
        except:
             print "[/i][/i][/i][i][i][i] Commodity sold out"
             return -1
        time.sleep(1)  #睡一秒，主要是怕报错
        browser.find_element_by_class_name("checkout").click()
        print "Filling in the information"
        fillForm(browser)
        print "Filled..."
        print "Prepare to buy a bill....."
        browser.find_element_by_name("commit").click()
        print "Finshed,congratulations on your favorite things!!!!!"
     
    if __name__ == '__main__':
        main()

![图片.png](https://image.3001.net/images/20180302/15199788475511.png!small)  

 _在附上，今晚week2抢的成果吧，放个低调的网球算了，啊哈哈哈_  

![图片.png](https://image.3001.net/images/20180302/15199788603976.png!small)

 _祝各位新的一年，有supreme玩，还能追到自己的女神吧  
最后，再说一句，人生苦短，我用Python！！  
_  

  

  

