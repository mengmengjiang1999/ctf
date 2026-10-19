VPS上的Nmap还在扫描工作着，而你已经把它忘了忙着其他事情。突然，一封邮件发来，向你汇报本次扫描完毕，和具体的扫描报告。是不是觉得很方便？借助Nmap的库文件和NSE引擎，这件事情将变得简单。

## 0x01 从SMTP协议说起

优秀的扫描器都有邮件通知的功能，Nmap也一样，在Nmap的库文件中已经为我们提供了用来操作SMTP协议的库文件`smtp.lua`。

邮件的发送依靠的是SMTP协议，在`smtp.lua`这个库文件，共14个函数有关SMTP邮件的发送，且该库支持SMTP指令`EHLO`，`HELP`，`AUTH`，`MAIL`，`RCPT`，`DATA`，`STARTTLS`，`RSET`，`VREY`，`EXPN`10个指令，借助socket我们其实可以发送任何的SMTP指令。

为了便于我们来理解SMTP指令的使用，下面我简单介绍下，在CMD下，如何用telnet发送SMTP指令的方式发出一封邮件。

`telnet smtp.163.com 25`

`![25.png](https://image.3001.net/images/20180403/15227212241735.png!small)  
`

`  
`

打开163邮箱，收到发出的邮件。

![邮件.png](https://image.3001.net/images/20180403/15227212485670.png!small)  

熟悉了以上过程，就能够明白`smtp.lua`这个库的每个函数都是在干些什么了，也方便我们去扩充和修改。

## 0x02 smtp库文件

根据上述过程，我们来认识下`smtp.lua`我们需要用到的几个函数。

  *  **connect函数** 发起SMTP连接，并确认对方是否需要`ssl`的支持。

  *  **ehlo函数**`ehlo`函数，其实就是发送`ehlo`的指令，是扩展的`helo`指令，服务器会在响应中表明自己支持的认证方式。

  *  **login函数**`login = function(socket, username, password, mech)``mech`：指得是认证方式，该函数支持`LOGIN`, `PLAIN`, `CRAM-MD5`, `DIGEST-MD5`和`NTLM`这5种方式，一般我们使用`LOGIN`。

  *  **mail函数**`mail = function(socket, address, esmtp_opts)`：发送`mail`指令。`address`：参数用来指定发件人地址。`esmtp_opts`： 用来设定邮件大小，envid，transid等，不设定可以设为nil

  *  **recipient函数**`recipient = function(socket, address)``address`：参数用来指定收件人地址。

  *  **datasend函数**`datasend = function(socket, data)`发送邮件内容。

  *  **query函数**`query = function(socket, cmd, data, lines)`发送邮件请求。`cmd`：是SMTP的指令参数。`data`：是指令的内容。

## 0x03 编写NSE脚本发送扫描报告

编写脚本遇到的两个问题，一个是如何获取扫描结果，另外一个是如何发送邮件正文。

虽然我们有API可以调用，但是一直没有找到调用所有结果的那个API，所以就决定先把扫描结果写在一个文件里，然后读取该文件。`nmap <TARGET>
--script smtp -oG 1.txt`这个方法有点简单粗暴哈，有更好方案的小伙伴吗？

注意，因为发送邮件头和邮件正文是有一个回车换行的，但是实际代码，我确是拼接了2个`\r\n`才区分开正文和邮件头。

完整的NSE脚本：

    
    
    local shortport = require "shortport"
    local smtp = require "smtp"
    
    description = [[send the scan result use smtp]]
    author = "reborn"
    license = "Same as Nmap--See http://nmap.org/book/man-legal.html"
    categories = {"default"}
    
    --[[
        example:nmap <TARGET> --script smtp -oG 1.txt
        1.txt is the smtp.nse use ,if you want replace or rename , modify the code.
    ]]
    
    postrule = function () return true end
    action = function(host, port)
        local socket,resp = smtp.connect("smtp.163.com",25,{ssl = false,recv_before = true})
    
        if ( not(socket) ) then return fail("Failed to connect to SMTP server") end
    
        local st, resp =smtp.ehlo(socket,"smtp.163.com") -- 发送ehlo，获取邮件服务器支持的登陆方式
        local status, err =smtp.login(socket,"rebornxxx@163.com","xxxxxx","LOGIN") -- 登陆
    
        if(status) then
            local mail_st,mail_response = smtp.mail(socket,"rebornxxx@163.com",nil) --设置发件人
    
            local recipient_st,recipient_response = smtp.recipient(socket,"rebornxxx@163.com")    --设置收件人 
    
            -- 读取扫描结果，设置邮件头和正文
            local result = ''
            for line in io.lines("1.txt") do
                line = string.gsub(line,"/","     ")
                line = string.gsub(line,",","\r\n")
                result = result .. line .. "\r\n"
            end    
            senddata="subject:The scan result\r\n" .. "from:reborn\r\n" .."\r\n".. result
            -- 邮件发送
            local st2 ,resp2 = smtp.datasend(socket,senddata)  
            print(st2,resp2)
            smtp.quit(socket)
            socket:close()
        end
        return "send mail test...."
    end
    

![end.png](https://image.3001.net/images/20180403/15227213012844.png!small)  

**收取到Nmap扫描结果的邮件：**

 **![邮件
1.png](https://image.3001.net/images/20180403/15227213414318.png!small)  
**

![邮件 2.png](https://image.3001.net/images/20180403/15227213637920.png!small)  

## 0x04 关于写上述脚本的一些其他思路

  * 有的小伙伴说python玩得溜，为啥要用lua。

没错，用python发邮件更加容易，而且我们可以在lua中来执行python脚本，简单粗暴的方式如下：直接用lua的`os.execute`命令执行系统命令，而`sendmail.py`则写好了如何发送邮件。`os.execute('python
"C:\\Program Files (x86)\\Nmap\\nselib\\sendmail.py"')`

  * 关于扩展`smtp.lua`库其实smtp库的各种连接，登陆，发送数据，完全可以用`socket`来直接完成了，之前一直不会用`datasend`这个函数的用法，是采用如下方式替代：
    
        local st, ret, response
    st,response =smtp.query(socket, "DATA")
    st,ret = socket:send("subject:test message\r\n")
    st,ret = socket:send("from:reborn\r\n")
    st,ret = socket:send("to:rebornxxx@163.com\r\n")
    st,ret = socket:send("\r\n")
    st,ret = socket:send("content\r\n")
    st, response =smtp.query(socket, "\r\n.")
    

## 0x05 小结

邮件发送扫描报告解决了平时不知何时扫描结束的一个痛点，经常做扫描任务的童鞋可以试试哈。本期内容就到这里，我们下期见。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180403/15227213867727.jpg!small)  

 _注：本文仅限于学习和研究使用，禁止用于非法用途。一切非法用途，与原作者无关。_  

