1、打开软件，输入密码错误时提示“密码错误，请重新输入”![](https://image.3001.net/images/20210129/1611902727_6013af078efbbeaeef620.png!small)

2、将软件导入OllyDBG工具![](https://image.3001.net/images/20210129/1611902753_6013af2185d01adbf9abb.png!small)

3、右键->中文搜索引擎->智能搜索![](https://image.3001.net/images/20210129/1611902771_6013af33b1608e227762c.png!small)

4、按下CTRL+F，打开查找，输入“密码错误，请重新输入！”，在结果中双击找到的结果

![](https://image.3001.net/images/20210129/1611902806_6013af56dc9c2c50a3287.png!small)

回到主界面，发现验证过程是有一个跳转来实现的![](https://image.3001.net/images/20210129/1611902827_6013af6b1ffed26da682f.png!small)

5、为了验证这个跳转是程序用于在用户输入密码后进行判断的，可以在跳转的起始位设置一个断点，这时再次运行程序会发现，输入错误密码时不再报错了

![](https://image.3001.net/images/20210129/1611902845_6013af7d143ae2a570012.png!small)

6、先取消断点，为了实现NOP法绕过登录验证，在跳转起始行点击右键->二进制->用NOP填充![](https://image.3001.net/images/20210129/1611902877_6013af9d6c2b1ca6870e5.png!small)

![](https://image.3001.net/images/20210129/1611902904_6013afb832d1b2ac3a08f.png!small)

7、按F9运行软件，随便输入一个密码后能直接就进入软件内部了

![](https://image.3001.net/images/20210129/1611902919_6013afc76428254de697d.png!small)

