***本文作者：koerle，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  

> 如何根据目标WiFi的用户信息，用Python生成一份独特的WPA2密码表？

**随着无线网络的不断发展，几乎所有场合都会覆盖WIFI信号，无论是公共地点还是家庭之中。众所周知，目前WIFI普遍的认证方式为wpa2，这种认证方式安全性相当不错，但由于人们设置密码时的随意性和固有思维，使得我们可以利用字典暴力破解。普通的字典大多是全覆盖的、总结性的，针对部分弱口令或许有用，不过1g的字典就算跑也要跑几个小时。那么如何利用已知目标wifi用户的信息生成一个不错的字典呢？**  

##  **寻找wifi及具体信息**

首先，生成字典的目的是为了破解密码，而想要破解密码，得先寻找一个wifi，假设找到了你邻居的wifi，那么接下来要做的就是收集信息。譬如：邻居的名字，生日，工作，老婆叫什么，儿子叫什么，生日是哪天。我们获得的信息越多，生成的密码字典就越丰富，破解可能性就越大。

##  **填写信息文件**

收集信息后，要做的是创建一个文件。

![根据目标用户信息，Python生成WPA2密码字典](https://image.3001.net/images/20180228/15197994622611.png!small)

如图，首先创建一个名为 **information** 的文件，无后缀。格式如下，以 **“:”**
为分界线（英文冒号），左侧为信息名称，右侧为信息的具体内容，内容不清楚则填no，由于代码关系，不要少于20行。  

## 生成字典

信息文件创建完毕后，便可以生成字典。这里我使用python来完成这一工作。生成的算法策略如下。

>  **1\. 大于8位的直接保留，小于8位的舍弃。**
>
>  **2\. 信息相互组合，小于8位舍弃。**
>
>  **3\. 生日提取年份、日月与其他信息组合，小于8位舍弃。**
>
>  **4\. 所有小于8位的信息与短数字（0-9的全排列）进行组合，生成8位密码。**
>
>  **5\. 所有信息与的9位以内短数字进行组合如（1233456789，000000000）。**
>
>  **6\. 所有组合与特殊符号相结合，如“#”、“%”等。特殊字符的位置可以是开头中间和结尾。**

接下来，使用python根据以上策略对信息进行结合处理。首先将信息存入一个list中。

    
    
    		f = open('information','r')
    		lines = f.read().split('\r')
    		name = lines[0].split(':')[1]
    		list.append(name)
    
    		simple_name = lines[1].split(':')[1]
    		list.append(simple_name)
    
    		family_name = lines[2].split(':')[1]
    		list.append(family_name)
    
    		phone_number = lines[3].split(':')[1]
    		list.append(phone_number)
    
    		study_number = lines[4].split(':')[1]
    		list.append(study_number)
    
    		birthday = lines[5].split(':')[1]
    		list.append(birthday)
    
    		if birthday!='no' and birthday!= 'NO':
    			birthday_month_day = birthday[4:]
    			birthday_year = birthday[0:4]
    			list.append(birthday_month_day)
    			list.append(birthday_year)
    		else:
    			birthday_month_day = 'no'
    			birthday_year = 'no'
    			list.append(birthday_month_day)
    			list.append(birthday_year)
    
    		idol_name = lines[6].split(':')[1]
    		list.append(idol_name)
    
    		idol_simple_name = lines[7].split(':')[1]
    		list.append(idol_simple_name)
    
    		father_name = lines[8].split(':')[1]
    		list.append(family_name)
    
    		father_simple_name = lines[9].split(':')[1]
    		list.append(father_simple_name)
    
    		mather_name = lines[10].split(':')[1]
    		list.append(mather_name)
    
    		mather_simple_name = lines[11].split(':')[1]
    		list.append(mather_simple_name)
    
    		son_name = lines[12].split(':')[1]
    		list.append(son_name)
    
    		son_simple_name = lines[13].split(':')[1]
    		list.append(son_simple_name)
    
    		father_birthday = lines[14].split(':')[1]
    		list.append(father_birthday)
    
    		if father_birthday!='no' and father_birthday!= 'NO':
    			father_birthday_month_day = father_birthday[4:]
    			father_birthday_year = father_birthday[0:4]
    			list.append(father_birthday_month_day)
    			list.append(father_birthday_year)
    		else:
    			father_birthday_month_day = 'no'
    			father_birthday_year = 'no'
    			list.append(father_birthday_month_day)
    			list.append(father_birthday_year)
    
    		mather_birthday = lines[15].split(':')[1]
    		list.append(mather_birthday)
    
    		if mather_birthday!='no' and mather_birthday!= 'NO':
    			mather_birthday_month_day = mather_birthday[4:]
    			mather_birthday_year = mather_birthday[0:4]
    			list.append(mather_birthday_month_day)
    			list.append(mather_birthday_year)
    		else:
    			mather_birthday_month_day = 'no'
    			mather_birthday_year = 'no'
    			list.append(mather_birthday_month_day)
    			list.append(mather_birthday_year)
    
    		son_birthday = lines[16].split(':')[1]
    		list.append(son_birthday)
    
    		if son_birthday !='no' and son_birthday != 'NO':
    			son_birthday_month_day = son_birthday[4:]
    			son_birthday_year = son_birthday[0:4]
    			list.append(son_birthday_month_day)
    			list.append(son_birthday_year)
    		else:
    			son_birthday_month_day = 'no'
    			son_birthday_year = 'no'
    			list.append(son_birthday_month_day)
    			list.append(son_birthday_year)
    
    		address = lines[17].split(':')[1]
    		list.append(address)
    
    		university_name = lines[18].split(':')[1]
    		list.append(university_name)
    
    		university_simple_name = lines[19].split(':')[1]
    		list.append(university_simple_name)
    
    
    
    		for i in range(20,len(lines)):
    			list.append(lines[i].split(':')[1])
    		f.close()  
    

为了阅读方便，information文件中前20个信息写的很具体。最后三行则是对20行之后的补充。  

随后，将短数字与特殊符号放入其他两个list中，代码见最后。并根据策略进行相互组合。 **最后生成符合我们心意的字典** 。最后附上代码~

    
    
    #coding:utf-8
    import itertools
    
    def read_file():
    	try:
    		f = open('information','r')
    		lines = f.read().split('\r')
    		name = lines[0].split(':')[1]
    		list.append(name)
    
    		simple_name = lines[1].split(':')[1]
    		list.append(simple_name)
    
    		family_name = lines[2].split(':')[1]
    		list.append(family_name)
    
    		phone_number = lines[3].split(':')[1]
    		list.append(phone_number)
    
    		study_number = lines[4].split(':')[1]
    		list.append(study_number)
    
    		birthday = lines[5].split(':')[1]
    		list.append(birthday)
    
    		if birthday!='no' and birthday!= 'NO':
    			birthday_month_day = birthday[4:]
    			birthday_year = birthday[0:4]
    			list.append(birthday_month_day)
    			list.append(birthday_year)
    		else:
    			birthday_month_day = 'no'
    			birthday_year = 'no'
    			list.append(birthday_month_day)
    			list.append(birthday_year)
    
    		idol_name = lines[6].split(':')[1]
    		list.append(idol_name)
    
    		idol_simple_name = lines[7].split(':')[1]
    		list.append(idol_simple_name)
    
    		father_name = lines[8].split(':')[1]
    		list.append(family_name)
    
    		father_simple_name = lines[9].split(':')[1]
    		list.append(father_simple_name)
    
    		mather_name = lines[10].split(':')[1]
    		list.append(mather_name)
    
    		mather_simple_name = lines[11].split(':')[1]
    		list.append(mather_simple_name)
    
    		son_name = lines[12].split(':')[1]
    		list.append(son_name)
    
    		son_simple_name = lines[13].split(':')[1]
    		list.append(son_simple_name)
    
    		father_birthday = lines[14].split(':')[1]
    		list.append(father_birthday)
    
    		if father_birthday!='no' and father_birthday!= 'NO':
    			father_birthday_month_day = father_birthday[4:]
    			father_birthday_year = father_birthday[0:4]
    			list.append(father_birthday_month_day)
    			list.append(father_birthday_year)
    		else:
    			father_birthday_month_day = 'no'
    			father_birthday_year = 'no'
    			list.append(father_birthday_month_day)
    			list.append(father_birthday_year)
    
    		mather_birthday = lines[15].split(':')[1]
    		list.append(mather_birthday)
    
    		if mather_birthday!='no' and mather_birthday!= 'NO':
    			mather_birthday_month_day = mather_birthday[4:]
    			mather_birthday_year = mather_birthday[0:4]
    			list.append(mather_birthday_month_day)
    			list.append(mather_birthday_year)
    		else:
    			mather_birthday_month_day = 'no'
    			mather_birthday_year = 'no'
    			list.append(mather_birthday_month_day)
    			list.append(mather_birthday_year)
    
    		son_birthday = lines[16].split(':')[1]
    		list.append(son_birthday)
    
    		if son_birthday !='no' and son_birthday != 'NO':
    			son_birthday_month_day = son_birthday[4:]
    			son_birthday_year = son_birthday[0:4]
    			list.append(son_birthday_month_day)
    			list.append(son_birthday_year)
    		else:
    			son_birthday_month_day = 'no'
    			son_birthday_year = 'no'
    			list.append(son_birthday_month_day)
    			list.append(son_birthday_year)
    
    		address = lines[17].split(':')[1]
    		list.append(address)
    
    		university_name = lines[18].split(':')[1]
    		list.append(university_name)
    
    		university_simple_name = lines[19].split(':')[1]
    		list.append(university_simple_name)
    
    
    
    		for i in range(20,len(lines)):
    			list.append(lines[i].split(':')[1])
    		f.close()
    	except:
    		pass
    
    def combination():
    	f = open('create_key','w')
    	for i in range(len(list)):
    		if list[i]!='no':
    			if len(list[i]) >= 8:
    				f.write(list[i]+'\n')
    
    			elif len(list[i])<8:
    				n = 8 - len(list[i])
    				for j in itertools.permutations('1234567890',n):
    					f.write(list[i]+''.join(j)+'\n')
    
    			for j in range(0,len(list)):
    				if len(list[i]+list[j])>=8 and list[i]!='no' and list[j]!='no' and list[i]!=list[j]:
    					f.write(list[i]+list[j]+'\n')
    					for m in range(0,len(list_special)):
    						f.write(list_special[m]+list[i] + list[j] + '\n')
    						f.write(list[i] + list_special[m] + list[j] + '\n')
    						f.write(list[i] + list[j] + list_special[m] + '\n')
    
    
    			for k in range(0,12):
    				for l in range(10):
    					if len(list[i]+list_number[k][0:l])>=8:
    						f.write(list[i]+list_number[k][0:l]+'\n')
    						f.write(list_number[k][0:l]+list[i]+'\n')
    
    						for m in range(0, len(list_special)):
    							f.write(list_special[m] + list[i] + list_number[k][0:l] + '\n')
    							f.write(list[i] + list_special[m] + list_number[k][0:l] + '\n')
    							f.write(list[i] + list_number[k][0:l] + list_special[m] + '\n')
    							f.write(list_special[m] + list_number[k][0:l] + list[i] + '\n')
    							f.write(list_number[k][0:l] +list_special[m] + list[i] + '\n')
    							f.write(list_number[k][0:l] + list[i] + list_special[m]+'\n')
    
    				f.write(list[i]+list_number[k]+'\n')
    				for m in range(0, len(list_special)):
    					f.write(list_special[m]+list[i] + list_number[k] + '\n')
    					f.write(list[i]+list_special[m]+list_number[k]+'\n')
    					f.write(list[i]+list_number[k]+list_special[m]+'\n')
    
    				f.write(list_number[k]+list[i]+'\n')
    				for m in range(0, len(list_special)):
    					f.write(list_special[m]+list_number[k] + list[i] + '\n')
    					f.write(list_number[k]+list_special[m]+list[i]+'\n')
    					f.write(list_number[k]+list[i]+list_special[m]+'\n')
    
    	f.close()
    
    def create_list_number():
    	simple_number1 = '123456789'
    	list_number.append(simple_number1)
    
    	simple_number2 = '000000000'
    	list_number.append(simple_number2)
    
    	simple_number3 = '111111111'
    	list_number.append(simple_number3)
    
    	simple_number4 = '222222222'
    	list_number.append(simple_number4)
    
    	simple_number5 = '333333333'
    	list_number.append(simple_number5)
    
    	simple_number6 = '444444444'
    	list_number.append(simple_number6)
    
    	simple_number7 = '555555555'
    	list_number.append(simple_number7)
    
    	simple_number8 = '666666666'
    	list_number.append(simple_number8)
    
    	simple_number9 = '777777777'
    	list_number.append(simple_number9)
    
    	simple_number10 = '888888888'
    	list_number.append(simple_number10)
    
    	simple_number11 = '999999999'
    	list_number.append(simple_number11)
    
    	simple_number12 = '987654321'
    	list_number.append(simple_number12)
    
    def create_list_special():
    	list_special.append(',')
    	list_special.append('.')
    	list_special.append('?')
    	list_special.append('#')
    	list_special.append('/')
    	list_special.append(';')
    	list_special.append(':')
    	list_special.append('!')
    	list_special.append('@')
    	list_special.append('$')
    	list_special.append('%')
    	list_special.append('^')
    	list_special.append('&')
    	list_special.append('*')
    
    def main():
    	global list
    	list = []
    	global list_number
    	list_number = []
    	global list_special
    	list_special = []
    	create_list_special()
    	create_list_number()
    	read_file()
    	combination()
    
    if __name__ == '__main__':
    	main()  
    

 ***本文作者：koerle，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

