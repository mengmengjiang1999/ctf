## 0x00前言

考研人考研魂，本该考研的我还赖在这里挖洞...不过多亏这次挖洞，有了我下面的经历。早上背完英语单词，瞥到浏览器上某项目的标签，又没忍住，开搞。

## 0x01

首先进入该系统，可以看到注册口中有一个上传营业执照的位置。  
![142013891.png](https://image.3001.net/images/20220321/1647820423_6237be87ac6bdd5586405.png!small)  
于是尝试上传，都可以成功，但是不能获取路径，无法利用，先记下该位置。  
![3600607779.png](https://image.3001.net/images/20220321/1647820439_6237be97333d3fa18c2ad.png!small)  
注册成功后，进入该系统，在httphistory中发现一个可以返回系统中模板文件目录的包，可以看到系统中作为模板文件以及对应的参数。  
![3240646183.png](https://image.3001.net/images/20220321/1647820458_6237beaacfa7f1f7235b5.png!small)  
于是尝试将图2中上传文件的参数进行拼接，然后惊喜的发现可以获取当前用户的上传文件目录  
![3581034680.png](https://image.3001.net/images/20220321/1647820475_6237bebb2073727e4393b.png!small)  
那么说明参数fileType01代表的是用户id，于是尝试找到带有模板文件的用户，成功找到：  
![2068457866.png](https://image.3001.net/images/20220321/1647820496_6237bed0a34b804ad47b2.png!small)  
现在可以拿到文件各种参数，那么下一步就是要找到如何读取或者下载文件，在系统中下载模板位置找到：  
![2190041200.png](https://image.3001.net/images/20220321/1647820517_6237bee5222b8984f9f04.png!small)  
但是此时获取的参数是加密的，抱着尝试的想法，第一次尝试解密，然后F12，在某一js文件中找到fileRelatId参数，发现这是一处aes加密，且密钥在前端泄露  
![353071651.png](https://image.3001.net/images/20220321/1647820533_6237bef591d7f30b00832.png!small)  
![1759258705.png](https://image.3001.net/images/20220321/1647820555_6237bf0bacc947818214d.png!small)  
然后编写js脚本，加密的参数同样为filrRelatId，尝试解密，成功：  
![624812364.png](https://image.3001.net/images/20220321/1647820569_6237bf194eb70b35df232.png!small)  
![43795473.png](https://image.3001.net/images/20220321/1647820587_6237bf2bb0b49e90655b3.png!small)  
![3853316471.png](https://image.3001.net/images/20220321/1647820599_6237bf37496809aab56e7.png!small)

    
    
    const CryptoJS = require('crypto-js'); //引用AES源码js
    
    const key = CryptoJS.enc.Utf8.parse('104a45db14f4ffde')
    
    //解密方法
    function Decrypt(word) {
        let decrypt = CryptoJS.AES.decrypt(word, key, { mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.Pkcs7 });
        return CryptoJS.enc.Utf8.stringify(decrypt).toString();
    }
    
    //加密方法
    function Encrypt(word) {
        let srcs = CryptoJS.enc.Utf8.parse(word);
        let encrypted = CryptoJS.AES.encrypt(srcs, key, {  mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.Pkcs7 });
        return encrypted.toString();
    }
    

到此实现了全站任意文件下载。

## 0x02

然后我又把目光放到了获取用户信息的包上，该包同样是加密的参数。  
![2813776823.png](https://image.3001.net/images/20220321/1647820618_6237bf4a98a1860dd4bb7.png!small)  
对他也进行解密，成功,可以读取到大量用户信息（商家姓名、商家名、法人姓名、手机号、邮箱、开户银行及卡号、地址、营业执照号等等敏感信息），且可以直接遍历读取  
![1202238098.png](https://image.3001.net/images/20220321/1647820652_6237bf6c10f48b5f9ed07.png!small)

## 0x03

这次挖掘，我对加解密做出了首次尝试，虽然脚本不是我写的，甚至不是我跑的（此处感谢风溯大佬），但是让我学到了更多的越权姿势。

