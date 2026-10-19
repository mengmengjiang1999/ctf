## 前言

* * *

前几天看了一片关于如何使用Golang来实现爬虫，今天来跟着学习一下

## 基础

* * *

在本篇中，我们使用Golang本身的net/http库来实现，http包提供了HTTP客户端和服务端的实现：

## Http客户端

* * *

### 基本的HTTP/HTTPS请求

首先我们要来创建一个请求，常见的net/http包创建请求的方式有：

    
    
    //Get
    resp , err := http.Get(url)
    
    //Post
    resp , err := http.Post("http://example.com/upload","image/jpeg",&buf)
    
    //PostForm
    resp ,err := http.PostForm("http;//example/form",url.values{"key":{"Valuw"},"id",{"k3zy"}})
    

程序在使用完response后必须关闭回复的主体

    
    
    resp, err := http.Get("http://example.com/")
    if err != nil {
    	// handle error
    }
    defer resp.Body.Close()
    body, err := ioutil.ReadAll(resp.Body)
    

### 携带参数

当我们想要在请求中携带参数是，我们可以使用Go语言内置的`net/url`标准库来实现:

  *  **Get请求**

    
    
    func main() {
    	Url := "http://127.0.0.1:9090/get"
    	// URL param
    	data := url.Values{}
    	data.Set("name", "黑客")
    	data.Set("age", "18")
    	u, err := url.ParseRequestURI(Url)
    	if err != nil {
    		fmt.Printf("parse url requestUrl failed, err:%v\n", err)
    	}
    	u.RawQuery = data.Encode() // URL encode
    	fmt.Println(u.String())
    	resp, err := http.Get(u.String())
    	if err != nil {
    		fmt.Printf("post failed, err:%v\n", err)
    		return
    	}
    	defer resp.Body.Close()
    	b, err := ioutil.ReadAll(resp.Body)
    	if err != nil {
    		fmt.Printf("get resp failed, err:%v\n", err)
    		return
    	}
    	fmt.Println(string(b))
    

  * **POST请求**

    
    
    package main
    
    import (
    	"fmt"
    	"io/ioutil"
    	"net/http"
    	"strings"
    )
    
    // net/http post demo
    
    func main() {
    	url := "http://127.0.0.1:9090/post"
    	// 表单数据
    	//contentType := "application/x-www-form-urlencoded"
    	//data := "name=小王子&age=18"
    	// json
    	contentType := "application/json"
    	data := `{"name":"黑客","age":18}`
    	resp, err := http.Post(url, contentType, strings.NewReader(data))
    	if err != nil {
    		fmt.Printf("post failed, err:%v\n", err)
    		return
    	}
    	defer resp.Body.Close()
    	b, err := ioutil.ReadAll(resp.Body)
    	if err != nil {
    		fmt.Printf("get resp failed, err:%v\n", err)
    		return
    	}
    	fmt.Println(string(b))
    }
    

### 复杂请求

当需要自在请求的时候设置头参数，cookie之类的时候，就可以使用http.Do方法

    
    
    client := &http.Client{}
    req,_ := http.NewRequest("GET",url,nil)
    //(参数头设置)
    resp , err := client.Do(req)
    

**参数头设置**  
设置请求header和cookie

    
    
    req.Header.Set("User-Agent","*****")
    req.Header.Set("Cookie","****")
    //也可以使用Add方法
    req.Header.Add("User-Agent","****")
    req.Header.Add("Cookie","****")
    

**Add和Set的区别**

  * 当我们使用Set的时候，如果原本就存在这一项数据，那么我们就修改已有的

  * 当我们使用Add的时候，如果原本不存在，那我们则添加，如果原本存在，则不做任何修改

 **发出请求**

    
    
    resp , err := client.Do(req)
    if err != nil {
        fmt.Println("Http get err:",err)
        return ""
    }
    
    if resp.StatusCode != 200 {
        fmt.Println("Http status code:", resp.Statuscode)
        return ""
    }
    defer resp.Body.Close() // 程序在使用完回复后必须关闭回复的主体
    body,err := ioutil.ReadAll(resp.Body) //ioutil.Readall用于读取文件或者网络请求
    if err != nil {
        fmt.Println("Read error",err)
        return ""
    }
    

最终调用一下定义的方法，返回请求，完整代码：

    
    
    package main
    
    import (
    	"fmt"
    	"io/ioutil"
    	"net/http"
    )
    
    func fetch(url string) string {
    	client := &http.Client{}
    	req, _ := http.NewRequest("GET", url, nil)
    	req.Header.Set("User-Agent", "1")
    	req.Header.Set("Cookie", "1")
    	resp, err := client.Do(req)
    	if err != nil {
    		fmt.Println("Http get err:", err)
    		return ""
    	}
    	if resp.StatusCode != 200 {
    		fmt.Println("http status code:", resp.StatusCode)
    	}
    	defer resp.Body.Close()
    	body, err := ioutil.ReadAll(resp.Body) //读取文件或者网络请求时
    	if err != nil {
    		fmt.Println("Read error", err)
    		return ""
    	}
    	return string(body)
    }
    
    func main() {
    	s := fetch("https://www.baidu.com")
    	fmt.Println(s)
    }
    

### 解析页面

通过正则表达式来解析页面

    
    
    func parse(html string) {
       // 替换空格
       html = strings.Replace(html, "\n", "", -1)
       //正则匹配内容块
       r_sidebar := regexp.MustCompile(`<aside id="sidebar" role="navigation">(.*?)</aside>`)
       //从传入的html开始匹配
       sidebar := r_sidebar.FindString(html)
       //正则匹配链接
       r_link := regexp.MustCompile(`href="(.*?)"`)
       //从上方匹配的内容中再次匹配链接
       link := r_link.FindAllString(sidebar, -1)
       url := "https://gorm.io/zh_CN/docs/"
       //切片遍历链接
       for _, v := range link {
          s := v[6 : len(v)-1]
          url1 := url + s
          fmt.Println(url1)
          body := fetch(url)
       }
    }
    

![](https://image.3001.net/images/20220801/1659323353_62e743d9d801c635f7729.png!small)

### 保存文件

当解析完页面，提取出我们想要的内容后，下一步我们就要进行保存内容，用的是原生的os库

    
    
    func Save(title string, content string) {
       err := os.WriteFile("/xxx/xxx/xxx/xxx"+title+".html", []byte(content), 0644)
       if err != nil {
          panic(err)
       }
    }
    

![](https://image.3001.net/images/20220801/1659323355_62e743dba40dbd62f2958.png!small)

### goquery

goquery为go语言带来了一种语法喝一组类似于jQuery的功能。它是基于Go的net/html包和CSS
Selector库cascadia。提供了和Jquery相近的借口。

 **Goquery的语法**  
创建文档：

    
    
    dom, err := goquery.NewDocument(url)
    dom ,err := goquery.NewDocumentFromResponse(url)//这里搭配http的话就是resp.body,传入的是数据
    dom, err := goquery.NewDocumentFromReader(reader io.Reader)
    

  * NewDocumentFromResponse 是一个 Document 构造函数，它将 http 响应作为参数。它加载指定响应的文档，对其进行分析，并存储根文档节点，以便随时进行操作。响应的主体在返回时关闭。

  * NewDocumentFromReader从io返回一个Document。读者。如果无法将读取器的数据解析为 html，它将返回错误作为第二个值。它不检查读取器是否也是 io。更近一点，提供的读取器永远不会被此调用关闭。如果需要，调用方有责任将其关闭。

内容查找：

    
    
    dom.Find("#sidebar") //  通过id查找
    dom.Fine(".sidebar-link") // 通过class查找
    dom.Find("asideid").Fine("a") //通过标签链式查找
    

获取内容：

    
    
    selection.Html()
    selection.Text()
    

属性获取：

    
    
    selection.Attr("href")
    
    selection.AttrOr("href", "")
    

遍历

    
    
    dom.Find(".sidebar-link").Each(func(i int, selection *goquery.Selection) {
    }
    

简单运用：

    
    
    package main
    
    import (
       "fmt"
       "github.com/PuerkitoBio/goquery"
    )
    
    func main() {
       url := "https://gorm.io/zh_CN/docs/"
       dom, _ := goquery.NewDocument(url)
       dom.Find(".sidebar-link").Each(func(i int, selection *goquery.Selection) {
          href, _ := selection.Attr("href")
          text := selection.Text()
          fmt.Println(i, url+href, text)
       })
    }
    

Goquery也可以从字符串中读取内容

    
    
    data := `
    <html>
       <head>
          <title>Sentiment</title>
       </head>
       <body>
          <h1>Hello</h1>
       </body>
    </html>`
    
       dom, _ := goquery.NewDocumentFromReader(strings.NewReader(data))
       dom.Find("title").Each(func(i int, selection *goquery.Selection) {
          text := selection.Text()
          fmt.Println(text)
       })
    

在字符串中通过class，标签，id查找：

    
    
    id：
    data := `
    <head>
       <title id="t1">Sentiment</title>//id="t1"
    </head>
    <body>
       <h1 class="c1">Hello</h1>
    </body>`
    
    dom, _ := goquery.NewDocumentFromReader(strings.NewReader(data))
    dom.Find("#t1").Each(func(i int, selection *goquery.Selection) {
       text := selection.Text()
       fmt.Println(text)
    })
    
    标签：
    data := `
    <head>
       <title id="t1">Sentiment</title>//title标签
    </head>
    <body>
       <h1 class="c1">Hello</h1>
    </body>`
    
    dom, _ := goquery.NewDocumentFromReader(strings.NewReader(data))
    dom.Find("title").Each(func(i int, selection *goquery.Selection) {
       text := selection.Text()
       fmt.Println(text)
    })
    
    id：
    data := `
    <head>
       <title id="t1">Sentiment</title>//id="t1"
    </head>
    <body>
       <h1 class="c1">Hello</h1>
    </body>`
    
    dom, _ := goquery.NewDocumentFromReader(strings.NewReader(data))
    dom.Find("#t1").Each(func(i int, selection *goquery.Selection) {
       text := selection.Text()
       fmt.Println(text)
    })
    

上述方法是通过Http包获取response，然后解析，记下来用Goquery爬虫重构一下：

    
    
    package main
    
    import (
    	"fmt"
    	"github.com/PuerkitoBio/goquery"
    	"os"
    )
    
    func save2(title string, content string) {
    	err := os.WriteFile("/Users/k3zy/Desktop/code/Go/Pachong/"+title+".html", []byte(content), 0644)
    	if err != nil {
    		panic(err)
    	}
    }
    
    func main() {
    	url := "https://gorm.io/zh_CN/docs/"
    	dom, _ := goquery.NewDocument(url)
    	dom.Find(".sidebar-link").Each(func(i int, selection *goquery.Selection) {
    		href, _ := selection.Attr("href")
    		text := selection.Text()
    		fmt.Println(i, url+href, text)
    		dom, _ = goquery.NewDocument(url + href)
    		//获取标题
    		title := dom.Find(".article-title").Text()
    		fmt.Println(title)
    		//获取内容
    		content, _ := dom.Find(".article").Html()
    		fmt.Println(content)
    		save2(title, content)
    	})
    }
    

### Colly

> colly一款快速优雅的golang爬虫框架，简单易用，功能完备。

 **他有如下特性：**

  * 干净的API

  * 快速(单核>1k请求/秒)

  * 管理每个域的请求延迟和最大并发性

  * 自动cookie和会话处理

  * 同步/异步并行抓取

  * 分布式抓取

  * 缓存

  * 非unicode响应的自动编码

  * robots . txt的支持

  * 谷*支持

主要使用方式分为三步：

  1. 创建一个采集器

  2. 注册一个回调函数

  3. 访问具体的网站

当我们创建采集器的时候，我们可以指定一些配置参数，比如useragent，爬取的深度以及日志等等。

    
    
    colly.NewCollector(colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"),
    colly.MaxDepth(1), 
    colly.Debugger(&debug.LogDebugger{}))
    

#### Colly爬虫的基本实现：

    
    
    package main
    
    import (
       "fmt"
       "github.com/gocolly/colly"
    )
    
    func main() {
       c := colly.NewCollector()
       c.OnHTML(".sidebar-link", func(element *colly.HTMLElement) {
          element.Request.Visit(element.Attr("href"))
       })
       c.OnRequest(func(request *colly.Request) {
          fmt.Println(request.URL)
       })
       c.Visit("https://gorm.io/zh_CN/docs/")
    }
    

## 总结

个人学习的一些总结和思考，如有不对多多指教

