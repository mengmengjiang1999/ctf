# 0x01 前言

腾讯在线文档是非常方便的软件，可以自定义等等。如果想自动打开，或大量修改数据可以使用python脚本实现。以前腾讯在线文档域名会有&c=XX，点击那个单元格会更改为单元格的行列，但腾讯文档的更新使域名中不会出现这个后缀，造成不能使用后缀进行更改单元格内容了，于是google了以下，发现python使用模拟鼠标键盘行为依然可以实现对腾讯在线文档的修改，于是开始设计脚本。

# 0x02 功能介绍

Tide安全团队的小伙伴每天都会把自己的学习过程及学习成功更新到语雀中，lmn设计的一个小程序可以每天获取一次当天在某个语雀知识库中的更新文章，<https://www.yuque.com/tidesec/wiki/gku6k7>

为了方便对文章进行整理，dream实现了将文章更新到腾讯在线文档中的脚本。

Tide安全团队Wiki知识库：<https://www.yuque.com/tidesec>

![1652085912_6278d498ce36918b63fb0.png!small](https://image.3001.net/images/20220509/1652085912_6278d498ce36918b63fb0.png!small)

# 0x03 功能实现

第一个功能对腾讯文档进行更新内容，因为lmn在语雀整理文章时已经写入txt文本文档中，我直接读取文本文档即可。

![1652085918_6278d49e499cdb9fdd52c.png!small](https://image.3001.net/images/20220509/1652085918_6278d49e499cdb9fdd52c.png!small)

在读取txt到list中，会出现\n和空行的出现，在输入腾讯文档时能造成错误。

![1652085924_6278d4a4d0164997505d2.png!small](https://image.3001.net/images/20220509/1652085924_6278d4a4d0164997505d2.png!small)

于是在读入list中将\n进去去除，先去除文件内的空行。

    
    
    def txt_os():
        file1 = open('wiki.txt', 'r', encoding='utf-8')  # 打开要去掉空行的文件,这里的文件改成语雀脚本生成的文件
        file2 = open('wiki2.txt', 'w', encoding='utf-8')  # 生成没有空行的文件
    
        for line in file1.readlines(): #去除空行
            if line == '\n':
                line = line.strip("\n")
            file2.write(line) #输出到新文件中
        print('输出成功....')
        file1.close()
        file2.close()

然后将list每个元素后面的\n进行去除。

    
    
    def txt_to_list():
        file = open("wiki2.txt","r",encoding='utf-8') #这里的文件对应txt_os中生产的文件
        list = file.readlines()
        list = [x.strip() for x in list if x.strip() != ''] #去除行中的回车
        print(list)
        return list #返回列表

这里返回list是为了腾讯文档的函数中进行读取。

对腾讯文档进行修改的话，需要使用chromedriver。

    
    
    下载地址https://registry.npmmirror.com/binary.html?path=chromedriver

先进行qq的登陆，使用python进行模拟鼠标点击和键盘输入。

find_element_by_id中的都为按钮或div的名字，在f12中可以搜到，这样就可以对元素进行定位了。

    
    
    def tx_write():
        list = txt_to_list()
        driver = webdriver.Chrome('C:\\Users\\missm\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe')
        #启动chrome的地址，需要下载chromedriver文件，下载地址https://registry.npmmirror.com/binary.html?path=chromedriver
        driver.get("XXXXXXXXXXXXXXXXXXXXXXXXXXXXX")#填写表的地址
        time.sleep(4)
        driver.find_element_by_id("blankpage-button-pc").click() #点击登陆按钮
        time.sleep(3)
        driver.find_element_by_id("qq-tabs-title").click() #点击QQ登陆
        driver.implicitly_wait(10)
        driver.switch_to.frame("login_frame")
        try:
            driver.find_element_by_id("img_out_3458589503").click() #这里的qq号改为快捷登陆的qq号，img_out_不用改，只改数字
            print("快捷登录成功")
        except:
            driver.find_element_by_id("switcher_plogin").click()
            time.sleep(1)
            #   会跳出输入手机令牌来，建议使用快捷登陆
            driver.find_element_by_id("u").send_keys("qq号")  # 改为使用用户名密码登陆的qq
            driver.find_element_by_id("p").send_keys("qq密码")  # 改为使用用户名密码登陆的密码
            driver.find_element_by_id("login_button").click()
            print("账号登录成功")
            time.sleep(5)
            # 转换frame
            driver.switch_to.parent_frame()
        #登入账号,用快速登入的功能,前提,已经电脑qq登入了
        #driver.switch_to.parent_frame()
        time.sleep(1)
        driver.maximize_window()
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="canvasContainer"]/div[1]/div[2]').click()
        time.sleep(0.5)

然后对腾讯文档进行添加。

    
    
    j = 0 #使用变量来定位列表
    for i in range(int(len(list)/7)): #使用列表的元素数来定义循环次数，7个为一组
        # 移动到网址一列
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.HOME)
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.CONTROL, Keys.UP)
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
        # 判断文章网址是否相同，单元格是否为空格
        for i in range(99999):
            b = list[j+2]
            a = driver.find_element_by_xpath('//*[@id="alloy-simple-text-editor"]').text #获取网址
            if a == b[5:]: #比对网址是否相同，相同则跳出循环
                j = j + 7  #如果网址相同，则j+7后跳出循环
                break
            if a != '': #判断单元格是否为空，为空则跳出循环
                driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
            else:
                break
        if a == b[5:]: #判断单元格是否为网址，如果为网址则跳出循环，进入下一次循环
            continue
        #   以下的的信息填写为自己的信息即可，你有多少列信息，就重复多少次
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.HOME) #先跳到第一列
        driver.find_element_by_id('alloy-simple-text-editor').click() #模拟鼠标点击
        s = driver.find_element_by_xpath('/html/body/div[3]/div/div[4]/div[2]/div/div/div[1]/div/div/div[1]/div[1]').text #获取此行的行数
        a = s[1:] #将A**去除A，留下数字
        a = int(a) #对数字进行转int型
        a = a - 2  #如果你的排序为行的相差则减去几即可
        # 编号
        str(a)
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(a) #输出a以形成序号
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB) #进入下一个单元格
        driver.find_element_by_id('alloy-simple-text-editor').click() #模拟鼠标点击
        # 题目
        b = list[j+1] #将list第j+1个元素赋值给b
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(b[5:]) #对b进行切割，输出b中第5个字符之后的字符
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB) #进入下一个单元格
        driver.find_element_by_id('alloy-simple-text-editor').click() #模拟鼠标点击
        # 地址
        c = list[j+2]
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(c[5:])
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
        driver.find_element_by_id('alloy-simple-text-editor').click()
        # 所属wiki
        d = list[j+3]
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(d[7:])
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
        driver.find_element_by_id('alloy-simple-text-editor').click()
        # 更新时间
        e = list[j+4]
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(e[5:16])
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
        driver.find_element_by_id('alloy-simple-text-editor').click()
        # 创建时间
        f = list[j+5]
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(f[5:16])
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
        driver.find_element_by_id('alloy-simple-text-editor').click()
        # 文章作者
        g = list[j+6]
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(g[5:])
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
        driver.find_element_by_id('alloy-simple-text-editor').click()
        j = j + 7;
    time.sleep(1)
    print('输入成功')

![1652085932_6278d4acf010bf5c2845f.png!small](https://image.3001.net/images/20220509/1652085932_6278d4acf010bf5c2845f.png!small)![1652085937_6278d4b1746cc0806cd66.png!small](https://image.3001.net/images/20220509/1652085937_6278d4b1746cc0806cd66.png!small)

添加成功。

# 完整代码如下：

    
    
    # -*- coding: utf-8 -*-  不统计只输入脚本
    # 需要修改的:10行的文件名；36行的chrome地址；37行的表地址；47行的qq号；54和55行用户名密码
    import os
    import time
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    
    # 去除txt文档中的空格行
    def txt_os():
        file1 = open('wiki.txt', 'r', encoding='utf-8')  # 打开要去掉空行的文件,这里的文件改成语雀脚本生成的文件
        file2 = open('wiki2.txt', 'w', encoding='utf-8')  # 生成没有空行的文件
    
        for line in file1.readlines(): #去除空行
            if line == '\n':
                line = line.strip("\n")
            file2.write(line) #输出到新文件中
        print('输出成功....')
        file1.close()
        file2.close()
    
    
    
    # 将txt文件读入列表去除行中的回车
    def txt_to_list():
        file = open("wiki2.txt","r",encoding='utf-8') #这里的文件对应txt_os中生产的文件
        list = file.readlines()
        list = [x.strip() for x in list if x.strip() != ''] #去除行中的回车
        print(list)
        return list #返回列表
    
    
    def tx_write():
        list = txt_to_list()
        driver = webdriver.Chrome('C:\\Users\\missm\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe')
        #启动chrome的地址，需要下载chromedriver文件，下载地址https://registry.npmmirror.com/binary.html?path=chromedriver
        driver.get("https://docs.qq.com/sheet/DUmJmaG9ma2JtTWhE?tab=BB08J2")#填写表的地址
        time.sleep(4)
        driver.find_element_by_id("blankpage-button-pc").click() #点击登陆按钮
        time.sleep(3)
        driver.find_element_by_id("qq-tabs-title").click() #点击QQ登陆
        driver.implicitly_wait(10)
        driver.switch_to.frame("login_frame")
        try:
            driver.find_element_by_id("img_out_3458589503").click() #这里的qq号改为快捷登陆的qq号，img_out_不用改，只改数字
            print("快捷登录成功")
        except:
            driver.find_element_by_id("switcher_plogin").click()
            time.sleep(1)
            #   会跳出输入手机令牌来，建议使用快捷登陆
            driver.find_element_by_id("u").send_keys("2064662418")  # 改为使用用户名密码登陆的qq
            driver.find_element_by_id("p").send_keys("mhw1724282931")  # 改为使用用户名密码登陆的密码
            driver.find_element_by_id("login_button").click()
            print("账号登录成功")
            time.sleep(5)
            # 转换frame
            driver.switch_to.parent_frame()
        #登入账号,用快速登入的功能,前提,已经电脑qq登入了
        #driver.switch_to.parent_frame()
        time.sleep(1)
        driver.maximize_window()
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="canvasContainer"]/div[1]/div[2]').click()
        time.sleep(0.5)
    
    
    
        ####################################################################################
        j = 0 #使用变量来定位列表
        for i in range(int(len(list)/7)): #使用列表的元素数来定义循环次数，7个为一组
            # 移动到网址一列
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.HOME)
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.CONTROL, Keys.UP)
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
            # 判断文章网址是否相同，单元格是否为空格
            for i in range(99999):
                b = list[j+2]
                a = driver.find_element_by_xpath('//*[@id="alloy-simple-text-editor"]').text #获取网址
                if a == b[5:]: #比对网址是否相同，相同则跳出循环
                    j = j + 7  #如果网址相同，则j+7后跳出循环
                    break
                if a != '': #判断单元格是否为空，为空则跳出循环
                    driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
                else:
                    break
            if a == b[5:]: #判断单元格是否为网址，如果为网址则跳出循环，进入下一次循环
                continue
            #   以下的的信息填写为自己的信息即可，你有多少列信息，就重复多少次
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.HOME) #先跳到第一列
            driver.find_element_by_id('alloy-simple-text-editor').click() #模拟鼠标点击
            s = driver.find_element_by_xpath('/html/body/div[3]/div/div[4]/div[2]/div/div/div[1]/div/div/div[1]/div[1]').text #获取此行的行数
            a = s[1:] #将A**去除A，留下数字
            a = int(a) #对数字进行转int型
            a = a - 2  #如果你的排序为行的相差则减去几即可
            # 编号
            str(a)
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(a) #输出a以形成序号
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB) #进入下一个单元格
            driver.find_element_by_id('alloy-simple-text-editor').click() #模拟鼠标点击
            # 题目
            b = list[j+1] #将list第j+1个元素赋值给b
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(b[5:]) #对b进行切割，输出b中第5个字符之后的字符
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB) #进入下一个单元格
            driver.find_element_by_id('alloy-simple-text-editor').click() #模拟鼠标点击
            # 地址
            c = list[j+2]
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(c[5:])
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
            driver.find_element_by_id('alloy-simple-text-editor').click()
            # 所属wiki
            d = list[j+3]
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(d[7:])
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
            driver.find_element_by_id('alloy-simple-text-editor').click()
            # 更新时间
            e = list[j+4]
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(e[5:16])
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
            driver.find_element_by_id('alloy-simple-text-editor').click()
            # 创建时间
            f = list[j+5]
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(f[5:16])
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
            driver.find_element_by_id('alloy-simple-text-editor').click()
            # 文章作者
            g = list[j+6]
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(g[5:])
            driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
            driver.find_element_by_id('alloy-simple-text-editor').click()
            j = j + 7;
        time.sleep(1)
        print('输入成功')
        driver.close()
    
    
    
    if __name__ == "__main__":
        txt_os()
        txt_to_list()
        tx_write()

