# 基础

![](https://image.3001.net/images/20210908/1631068960_613823200006943f4a1ca.png!small)

![](https://image.3001.net/images/20210908/1631068962_613823222031ee13c9cf8.png!small)

![](https://image.3001.net/images/20210908/1631068963_613823236a8b11adbabed.png!small)

![](https://image.3001.net/images/20210908/1631068964_61382324824a72ea1e08f.png!small)

# 大致使用方法

注意：这里创建的ip指向的开cs服务器的ip不是cs应用的ip

如果kali开服务

win开应用

则下面的ip指向kali

![](https://image.3001.net/images/20210908/1631068965_613823254efc84ece84f2.png!small)

![](https://image.3001.net/images/20210908/1631068966_6138232669aed9558c526.png!small)

![](https://image.3001.net/images/20210908/1631068968_61382328b7a573c3cbcc3.png!small)

![](https://image.3001.net/images/20210908/1631068969_61382329a08a2f70f1f35.png!small)

# cs与msf联动

## cs发送给msf

cs拿到服务器后再新建个监听

![](https://image.3001.net/images/20210908/1631068970_6138232ad2fdac81e0082.png!small)

建好过后去msf开启监听

![](https://image.3001.net/images/20210908/1631068972_6138232ccf087ce9b4067.png!small)

run一下

![](https://image.3001.net/images/20210908/1631068974_6138232e359934e523e4d.png!small)

![](https://image.3001.net/images/20210908/1631068975_6138232f1b22cf7e77443.png!small)

进入beacon即可看见运行![](https://image.3001.net/images/20210908/1631068976_613823304ec8599eb2c19.png!small)

![](https://image.3001.net/images/20210908/1631068976_61382330e305f76e6a415.png!small)

这样就顺利连上了![](https://image.3001.net/images/20210908/1631068977_613823318c43fc7209d0d.png!small)

![](https://image.3001.net/images/20210908/1631068978_61382332abe5c0da60100.png!small)

## msf发送给cs

比如我在msf上提权过后发送给cs

首先提权![](https://image.3001.net/images/20210908/1631068980_61382334a03a165e50c32.png!small)

提权成功后

    
    
    use exploit/windows/local/payload_inject 

![](https://image.3001.net/images/20210908/1631068981_61382335bda9356899a12.png!small)

![](https://image.3001.net/images/20210908/1631068983_61382337bdabd26696d21.png!small)

run一下即可![](https://image.3001.net/images/20210908/1631068984_61382338e6d899586d952.png!small)

这几个报错是正常现象，我们看cs上线成功即可![](https://image.3001.net/images/20210908/1631068986_6138233a4d5fe7225d4aa.png!small)

  

