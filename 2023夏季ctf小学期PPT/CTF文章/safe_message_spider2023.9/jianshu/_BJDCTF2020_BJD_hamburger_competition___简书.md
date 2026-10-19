[BJDCTF2020]BJD hamburger competition

[ Du1in9](https://www.jianshu.com/u/32aab16373de)关注赞赏支持

# [BJDCTF2020]BJD hamburger competition

dnSpy打开Assembly-CSharp.dll文件，分析代码

    
    
      1 using System;
      2 using System.Security.Cryptography;
      3 using System.Text;
      4 using UnityEngine;
      5 
      6 // Token: 0x02000004 RID: 4
      7 public class ButtonSpawnFruit : MonoBehaviour
      8 {
      9     // Token: 0x0600000A RID: 10 RVA: 0x00002110 File Offset: 0x00000310
     10     public static string Md5(string str)
     11     {
     12         byte[] bytes = Encoding.UTF8.GetBytes(str);
     13         byte[] array = MD5.Create().ComputeHash(bytes);
     14         StringBuilder stringBuilder = new StringBuilder();
     15         foreach (byte b in array)
     16         {
     17             stringBuilder.Append(b.ToString("X2"));
     18         }
     19         return stringBuilder.ToString().Substring(0, 20);
     20     }
     21 
     22     // Token: 0x0600000B RID: 11 RVA: 0x00002170 File Offset: 0x00000370
     23     public static string Sha1(string str)
     24     {
     25         byte[] bytes = Encoding.UTF8.GetBytes(str);
     26         byte[] array = SHA1.Create().ComputeHash(bytes);
     27         StringBuilder stringBuilder = new StringBuilder();
     28         foreach (byte b in array)
     29         {
     30             stringBuilder.Append(b.ToString("X2"));
     31         }
     32         return stringBuilder.ToString();
     33     }
     34 
     35     // Token: 0x0600000C RID: 12 RVA: 0x000021C8 File Offset: 0x000003C8
     36     public void Spawn()
     37     {
     38         FruitSpawner component = GameObject.FindWithTag("GameController").GetComponent<FruitSpawner>();
     39         if (component)
     40         {
     41             if (this.audioSources.Length != 0)
     42             {
     43                 this.audioSources[Random.Range(0, this.audioSources.Length)].Play();
     44             }
     45             component.Spawn(this.toSpawn);
     46             string name = this.toSpawn.name;
     47             if (name == "汉堡底" && Init.spawnCount == 0)
     48             {
     49                 Init.secret += 997;
     50             }
     51             else if (name == "鸭屁股")
     52             {
     53                 Init.secret -= 127;
     54             }
     55             else if (name == "胡罗贝")
     56             {
     57                 Init.secret *= 3;
     58             }
     59             else if (name == "臭豆腐")
     60             {
     61                 Init.secret ^= 18;
     62             }
     63             else if (name == "俘虏")
     64             {
     65                 Init.secret += 29;
     66             }
     67             else if (name == "白拆")
     68             {
     69                 Init.secret -= 47;
     70             }
     71             else if (name == "美汁汁")
     72             {
     73                 Init.secret *= 5;
     74             }
     75             else if (name == "柠檬")
     76             {
     77                 Init.secret ^= 87;
     78             }
     79             else if (name == "汉堡顶" && Init.spawnCount == 5)
     80             {
     81                 Init.secret ^= 127;
     82                 string str = Init.secret.ToString();
     83                 if (ButtonSpawnFruit.Sha1(str) == "DD01903921EA24941C26A48F2CEC24E0BB0E8CC7")
     84                 {
     85                     this.result = "BJDCTF{" + ButtonSpawnFruit.Md5(str) + "}";
     86                     Debug.Log(this.result);
     87                 }
     88             }
     89             Init.spawnCount++;
     90             Debug.Log(Init.secret);
     91             Debug.Log(Init.spawnCount);
     92         }
     93     }
     94 
     95     // Token: 0x04000005 RID: 5
     96     public GameObject toSpawn;
     97 
     98     // Token: 0x04000006 RID: 6
     99     public int spawnCount = 1;
    100 
    101     // Token: 0x04000007 RID: 7
    102     public AudioSource[] audioSources;
    103 
    104     // Token: 0x04000008 RID: 8
    105     public string result = "";
    106 }
    

85行，就是输出的flag，对 “DD01903921EA24941C26A48F2CEC24E0BB0E8CC7” Sha1解密，得到str=1001

  

图片.png

带入ButtonSpawnFruit.Md5( )函数  
10~20行，flag是str经过Md5加密的前20位

  

图片.png

BJDCTF{b8c37e33defde51cf91e}

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [14、python常用模块](https://www.jianshu.com/p/55f301ddb901)

常用模块 认识模块 什么是模块 什么是模块？ 常见的场景：一个模块就是一个包含了python定义和声明的文件，文...

[go以恒](https://www.jianshu.com/u/cca1069190c9)阅读 1,708评论 0赞 6

  * [C#热更新方案的选择](https://www.jianshu.com/p/50eafdb20cf1)

前项目的C#热更方案 小甜甜的C#热更方案 前段时间 noodle 说他把 小甜甜 项目中他做的 C#热更方案 开...

[恶毒的狗](https://www.jianshu.com/u/8f5bfc31553e)阅读 2,149评论 0赞 0

  * [Unity3D DLL加密](https://www.jianshu.com/p/916a1a5c35cc)

Unity3D打包android应用程序时，如果不对DLL加密，很容易被反编译，导致代码的泄露。通常的做法是通过加...

[某人在](https://www.jianshu.com/u/4673233b8b76)阅读 1,956评论 0赞 2

  * [【BUUCTF】RE WP](https://www.jianshu.com/p/fe1baa5bb1e9)

题目地址：https://buuoj.cn/challenges 0x01 easyre 拖入ida看代码，得到f...

[Du1in9](https://www.jianshu.com/u/32aab16373de)阅读 2,487评论 0赞 2

  * [Unity中的Mono & Linux上编译Mono的流程](https://www.jianshu.com/p/9fd169b4d920)

前段时间编译了一下Unity的Mono,看了很多相关的文章，也遇到很多新坑。所以来总结一下，加深自己对Mono的理...

[李嘉的博客](https://www.jianshu.com/u/aaa3e4347850)阅读 2,428评论 0赞 3

 