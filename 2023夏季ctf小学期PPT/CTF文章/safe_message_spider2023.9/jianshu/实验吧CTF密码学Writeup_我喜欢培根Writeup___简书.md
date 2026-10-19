实验吧CTF密码学Writeup-我喜欢培根Writeup

[ syxvip](https://www.jianshu.com/u/380fd93bae2c)关注赞赏支持

# 实验吧CTF密码学Writeup-我喜欢培根Writeup

### 我喜欢培根分值：20

  * 来源： [Ph0enix](http://www.shiyanbar.com/user/studentcourse/A55B8671D524B7)
  * 难度：中
  * 参与人数：5331人
  * Get Flag：2533人
  * 答题人数：2876人
  * 解题通过率：88%

key: CTF{}

解题链接： <http://ctf5.shiyanbar.com/crypto/enc1.txt>

* * *

肯定摩斯密码  
解码后：  
m o r s e _ i s _ c o o l _ b u t _ b a c o n _ i s _ c o o l e r _ d c c d c
c c d d d c d c c c d d c c c c c c c c c d d c d c c c c d c c c c c c d c c
c d c c d c c c c d c c d d d c c d d d c c d c d d

转化为：  
baabaaabbbabaaabbaaaaaaaaabbabaaaabaaaaa/abaaabaaba/aaabaabbbaabbbaababb

image.png

实在没想到，真的是败给了实验吧的格式。  
CTF{SHIYANBA IS COOL}

附上python解密培根：

    
    
    #!/usr/bin/python  
    # -*- coding: utf-8 -*-  
    import re  
    alphabet=['a','b','c','d','e','f','g','h','i','j','k',  
    'l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']  
      
    one_biao=["aaaaa","aaaab","aaaba","aaabb","aabaa","aabab",  
    "aabba","aabbb","abaaa","abaab","ababa","ababb","abbaa",  
    "abbab","abbba","abbbb","baaaa","baaab","baaba","baabb",  
    "babaa","babab","babba","babbb","bbaaa","bbaab"]  
      
    def encode():  
    #python3.0版本后用input替换了raw_input  
        string=input('请输入字符串加密')#明文  
        e_string=""  
        for index in string:  
            for i in range(0,26):  
                if(index==alphabet[i]):#字母匹配  
                    e_string+=one_biao  
                    break  
        print('编码'+e_string)  
        return  
          
    def decode():  
        e_string=input('请输入暗文解密')  
        e_array=re.findall(".{5}",e_string)  
        d_string=""  
        for index in e_array:  
            for i in range(0,26):  
                if index==one_biao[i]:  
                    d_string+=alphabet[i]  
        print("解码为："+d_string)  
        return  
      
    if __name__=="__main__":  
        number=input('输入数1或2，1加密，2解密: ')  
        if number=="1":  
            encode()  
        elif number=='2':  
            decode()  
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [snapshot-1.0.0.js](https://www.jianshu.com/p/b7dc909dcaae)

"use strict";function _classCallCheck(e,t){if(!(e instanc...

[久些](https://www.jianshu.com/u/8ef889f37263)阅读 1,925评论 0赞 2

  * [声律启蒙](https://www.jianshu.com/p/5e84ed5f0df4)

sì 支zhī茶chá 对duì 酒jiǔ，赋fù 对duì 诗shī，燕yàn子zi 对duì 莺yīng 儿é...

[每个人的孟母堂](https://www.jianshu.com/u/f5d9fb306c79)阅读 987评论 0赞 6

  * [密码学_我喜欢培根](https://www.jianshu.com/p/66261ffdf30f)

时间：2017.9.22 题目链接：http://ctf5.shiyanbar.com/crypto/enc1.t...

[jinxi197](https://www.jianshu.com/u/8548724a4b50)阅读 778评论 0赞 0

  * [To My Bride](https://www.jianshu.com/p/273d0951ac05)

There's always a voice keep asking me everyday when I wak...

[躲起来先生](https://www.jianshu.com/u/3f3391cb342e)阅读 188评论 0赞 1

  * [2017-10-22](https://www.jianshu.com/p/726d2e2ce564)

你是人，我是妖，人妖注定殊途。 相思树下约定再续情缘。 我等了你一世又一世。 看你一世又一世离我而...

[青狅](https://www.jianshu.com/u/6d79d74a121d)阅读 111评论 0赞 0

 