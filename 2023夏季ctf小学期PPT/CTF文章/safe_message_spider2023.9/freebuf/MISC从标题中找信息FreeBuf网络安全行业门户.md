在做隐写的时候，思路很重要，当然有时候会感觉思路不够用，那怎么办呢？记住看隐写的题目名字很重要，因为很多时候，隐写题的标题里就隐藏了信息。

本文实验地址为：https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014112610044700001&pk_campaign=freebuf-wemedia。

进入实验机，打开http://www.ctfmisc.com/firstbl00d/后，我们仅仅看到一张图片以及一段简单的文字描述，除了网页的标题“BASE64
& MD5 & COOKIE”外，表面上没有任何有用的信息。

继续看题目，此时查看页面的Cookie也看不到任何有用的信息。

这里找不到异常是不是可以看一下图片本身是否携带了提示信息（比如Exif等）。将网页中的xctf.jpg图片保存下来之后，通过Exif.py文件，通可以读取xctf.jpg中的Exif信息，如图所示：

![图片1.png](https://image.3001.net/images/20210415/1618478304_607804e0d50ceabe73fd6.png!small)

发现了一个可疑的字符串RkFCQTgzOEY4QkIyOEU3NUZGNjVGMzRENEY5NDMwRDc=

这明显就是一个base64题目的标题也有说明我们解密一下在主机的桌面有一个JPK工具，打开JPK，输入RkFCQTgzOEY4QkIyOEU3NUZGNjVGMzRENEY5NDMwRDc=，在JPK的菜单中依次选择ASCII、Decode、Base64菜单项，就可以对其进行解码操作了，得到的结果为FABA838F8BB28E75FF65F34D4F9430D7。

注意标题，这是md5加密，我们网页在线解密一下

![图片2.png](https://image.3001.net/images/20210415/1618478305_607804e17187a2e14f53f.png!small)

套路防不胜防，xctf。

进行做题访问http://www.ctfmisc.com/firstbl00d/xctf.php，网页的内容仍然没有有用的提示信息，不过网页的标题是COOKIE，因此我们可以查看网页的Cookie。使用Google
Chrome浏览器打开xctf.php页面，按下F12调出开发者工具，切换到Network选项卡，按F5刷新页面，就可以看到Cookie里面的内容了，如图所示：

![图片3.png](https://image.3001.net/images/20210415/1618478306_607804e216a5b89b640e9.png!small)

Cookie内容为next-step=bjN4dDV0M3A%3D，其中%3D为等于号“=”的编码，因此字符串也就是bjN4dDV0M3A=，这也是一个BASE64编码的字符串，再次使用JPK工具对其进行解码，得到明文n3xt5t3p。

我们访问http://www.ctfmisc.com/firstbl00d/n3xt5t3p>这个URL，发现页面跳转到了http://www.ctfmisc.com/firstbl00d/n3xt5t3p/index.html，这本是再正常不过的事情，不过根据页面的文字提示“你刚才看见KEY了吗”，是不是在跳转的过程中还有什么提示信息呢？同样在Google
Chrome浏览器中按下F12打开开发者工具，并切换到Network选项，再次访问http://www.ctfmisc.com/firstbl00d/n3xt5t3p页面，我们看到了两个301跳转，如图所示：

![图片4.png](https://image.3001.net/images/20210415/1618478306_607804e2a543647886b16.png!small)

对于访问目录的URL，通过一次跳转来到index.html页面是正常的事情，但是这里居然有两次跳转，显然就不太正常了。我们点击两个301跳转，看看里面都有什么信息。我们看到的是，第二个301跳转的HTTP响应头信息中存在这样一个选项Set-Cookie:check=0，其他就没有什么特殊的了。

这里需要发挥一下想象，我们访问的是n3xt5t3p，而最终跳转到的页面是n3xt5t3p/index.html，因为有两次跳转，也就是说在这中间还有一个页面。因为之前访问的都是php页面，所以我们猜测其中有一个index.php（是的，CTF比赛的时候就是需要大胆的去猜想，然后通过实际操作来进行验证）。访问http://www.ctfmisc.com/firstbl00d/n3xt5t3p/index.php，没有出现404错误，而是跳转到了index.html，实际结果表明index.php页面是存在的。

结合上面的分析，可能需要Cookie中的check=1时，访问index.php才不会进行跳转。

我们尝试一下用，burp截包，然后我们把Cookie字段的check=0改为check=1，然后点击Forward按钮将HTTP请求发出去，如图所示：

![图片5.png](https://image.3001.net/images/20210415/1618478307_607804e33378c09414193.png!small)

此时，我们就可以在浏览器端看到进一步的提示信息了，提示信息如下：

WORD is a common english word

len(WORD) = 4

md5(WORD + '_heetian') = '84323c9b4fdb2539b4fb69b82b0189e7'

FLAG = md5(WORD)

这里嗯！看到flag了md5（WORD），但是好像需要解密。利用python的hashlib库可以十分方便的进行MD5哈希值计算，对于4个字母的单词，我们可以通过暴力枚举的方式，方便而又快速的找到上面的Flag。将下面的内容保存为一个py文件，双击后等待一会就可以看到运算结果了。

import hashlib

import string

def crackMd5(dst):

dst = dst.lower()

for a in string.lowercase:

for b in string.lowercase:

for c in string.lowercase:

for d in string.lowercase:

word = a + b + c +d + "_heetian"

tmp = hashlib.md5(word).hexdigest()

if dst == tmp:

return word

return None

if **name** == " **main** ":

raw_input(crackMd5("84323c9b4fdb2539b4fb69b82b0189e7"))

Python基于缩进来控制语句块，如果直接复制运行时提示错误，也可以访问C:\Misc\crackMd5.py来进行计算。计算的结果为misc，如图所示：

![图片6.png](https://image.3001.net/images/20210415/1618478307_607804e3cce70766450ad.png!small)

这一类的题目不要以为得到了flag就轻松了，后面还有解密过程。思维要严谨，不能老是看题目表象，真题往往没那么容易得出答案。

