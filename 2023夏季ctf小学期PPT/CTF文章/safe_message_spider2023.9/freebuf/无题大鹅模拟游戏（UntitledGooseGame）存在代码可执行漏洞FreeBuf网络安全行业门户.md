***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径**

**![maxresdefault.jpg](https://image.3001.net/images/20191031/1572513344_5dbaa6409ee52.jpg!small)**

 **Untitled Goose Game（无题大鹅模拟、捣蛋鹅）是一款画风简单的第三人称模拟类游戏，通过模拟一只大鹅去完成一些捣乱任务，是House
House制作的一款农场题材搞笑游戏。经作者发现，Untitled Goose Game由于在其游戏存档加载器（Save Game
Loader）中存在不安全的反序列化机制从而可导致代码执行漏洞，攻击者可以针对目标玩家的在启动游戏存档加载器时实施恶意代码执行攻击。**

## 漏洞详情

Untitled Goose
Game使用.NET的BinaryFormatter去读取和反序列化游戏存档文件，由于其中未采用特定的SerializationBinder去控制反序列化过程，因此，控制了游戏存档文件的攻击者可以利用其反序列化过程来执行任意代码。攻击者只需在游戏存档文件中写入一个恶意的序列化对象，让Untitled
Goose Game去读取即可实现攻击。游戏存档文件在操作系统中的存储位置为C:\Users\<USER>\AppData\LocalLow\House
House\Untitled Goose Game\savegame0.save.

Untitled Goose Game中的反序列化过程发生在Untitled_Data\Managed\Assembly-CSharp.dll文件的StandaloneSaveSystem类中，以下是其中存在安全风险的方法函数：

    
    
    public SaveGameData LoadSlot(int slot)
    
     {
    
      string savePath = this.GetSavePath(slot);
    
      SaveGameData result;
    
      if (File.Exists(savePath))
    
      {
    
       Debug.Log("loading from " + savePath);
    
       using (FileStream fileStream = File.Open(savePath, FileMode.Open))
    
       {
    
        result = (SaveGameData)new BinaryFormatter().Deserialize(fileStream);
    
       }
    
       Debug.Log("sucessfully loaded savegame data from " + savePath);
    
      }
    
      else
    
      {
    
       Debug.Log("savefile doesn't exist. didn't load any data");
    
       result = new SaveGameData();
    
      }
    
      return result;
    
     }

## 漏洞利用所需工具

要成功利用该漏洞，需要用到 James Forshaw
改进过的一个反序列组件TypeConfuseDelegate，具体可以[参考此处](https://gist.github.com/denandz/aa2b7bd145c95b430cfc0386a9e6ce40)。其实，该改进组件已经整合到了反序列化工具ysoserial.net中了，可以[在此下载](https://github.com/pwntester/ysoserial.net)。

可用以下命令生成PoC漏洞利用：

> ysoserial.exe -f BinaryFormatter -t TypeConfuseDelegateMono -o raw -c "calc"
> > "C:\Users\<user>\AppData\LocalLow\House House\Untitled Goose
> Game\savegame0.save"

新发布的TypeConfuseDelegateMono组件，可用来发起对其它基于MONO平台开发游戏的攻击测试。

## 漏洞上报处置进程

07/10/2019 - 向House House公司通报

09/10/2019 - House House确认漏洞

22/10/2019 - House House发布补丁

29/10/2019 - 公开漏洞

 ***参考来源：[pulsesecurity](https://pulsesecurity.co.nz/advisories/untitled-goose-game-deserialization)，clouds编译整理，转载请注明来自FreeBuf.COM**  

