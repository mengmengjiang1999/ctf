React Native 网络请求封装ajax

[ 刘宇航iOS](https://www.jianshu.com/u/4970598c5214)关注赞赏支持

# React Native 网络请求封装ajax

###### 1.新建Fetch.tsx(作者采用的是TypeScript)

    
    
    import _ from 'lodash'
    import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
    import {Toast} from "antd-mobile-rn"
    
    import {DeviceEventEmitter} from 'react-native'
    import config from "./config";
    
    interface ajaxOptions {
      baseURL?: string
      version?: string
      headers?: object
      method?: string
      data?: object
    }
    
    export const ajax = (url: string, options: ajaxOptions) => {
      let axiosOptions: AxiosRequestConfig = {}
      axiosOptions.baseURL = config.host
      axiosOptions.headers = {
    //无请求头可忽略
        Authorization:'BasicAuth ' + config.ticket,
        ...options.headers
      }
    //请求方式
      axiosOptions.method = options.method || 'get'
    //超时时间
      axiosOptions.timeout = 30 * 1000
    
      if (options.data && _.includes(['get', 'delete'], options.method))
        axiosOptions.params = options.data
      else
        axiosOptions.data = options.data
    
      return new Promise<AJAXErrorResult>((resolve:any, reject:any) => {
        axios(url, axiosOptions)
          .then(async (res: AxiosResponse<ServerResponseData>) => {
    
            if(res.data.status === 1){
              resolve(res.data)
              return
              // @ts-ignore
            } else if (res.data.Status === 1) {
              resolve(res.data)
              return
            }
    
            Toast.fail(res.data.error)
            reject({
              ...res,
              handled:false
            })
          })
          .catch(async (err: AxiosError) => {
            console.warn(err)
            console.log(url,axiosOptions)
            if (!err.response) {
              Toast.fail('服务繁忙，稍候请重试')
              reject({ ...err, handled: true })
              return
            }
    
            if (err.response.status == 401) {
              reject({ handled: true })
              Toast.info('登录状态失效，请重新登录')
    
              DeviceEventEmitter.emit('LogoutEvent',null  )
            }
            else if (err.response.status == 400) {
              reject({
                data: err.response.data,
                message: _.get(err.response.data, 'msg'),
                handled: false
              })
            }
            else {
              reject({ ...err, handled: true })
              Toast.fail('服务繁忙，稍候请重试')
            }
          })
      })
    }
    
    export const GET = (url: string, options: ajaxOptions) => ajax(url, {
      ...options,
      method: 'get'
    })
    export const PUT = (url: string, options: ajaxOptions) => ajax(url, {
      ...options,
      method: 'put'
    })
    export const POST = (url: string, options: ajaxOptions) => ajax(url, {
      ...options,
      method: 'post'
    })
    export const DEL = (url: string, options: ajaxOptions) => ajax(url, {
      ...options,
      method: 'delete'
    })
    
    

###### 2.创建RequestHelper.ts

    
    
    //引用
    import { POST, GET, PUT, DEL } from "./Fetch";
    
    // 获取验证码
    export function requestForValidCode() {
      return GET('/api/User/GetValidateNumKey', {})
    }
    // 登录
    export function requestForlogin(params: FormLoginModel) {
      return POST('Api/User/UserLogin', {
        data: {
          ...params
        }
      })
    }
    
    

###### 3.使用RequestHelper

    
    
    requestForlogin({
          LoginName: phoneStr,
          LoginPass: password
        })
          .then((res: any) => {
           
          })
          .catch((err: any) => {
            if (!err.data.handled) {
            }
          })
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [翻译 | 开始使用 TypeScript 和 React](https://www.jianshu.com/p/71bbcdc8c1fc)

原文地址：Getting started with TypeScript and React 原文作者：Jack_...

[沪江技术学院](https://www.jianshu.com/u/ebe59666d016)阅读 19,602评论 4赞 34

  * [搭建Typescript+React项目模板(3) --- 整理项目和杂项](https://www.jianshu.com/p/1798ed80f70d)

相关文章和阅读顺序 搭建Typescript+React项目模板(1) --- 项目初始化搭建 Typescrip...

[大春春](https://www.jianshu.com/u/38278ed3f4e1)阅读 5,772评论 2赞 9

  * [[HCTF2014]丘比龙的最爱](https://www.jianshu.com/p/dd93d5444ef9)

题目链接：http://oj.xctf.org.cn/problems/5 分析： 直接百度出结果 答案：比丘龙 ...

[王一航](https://www.jianshu.com/u/bf30f18c872c)阅读 705评论 2赞 3

  * [26/100 每一天都是新的](https://www.jianshu.com/p/6da91ac08282)

写下这个标题的时候，我在想第一次说这句话是多大的时候，看上去好土，但充满了幸福感。 可能是超长长长的阴雨天终于结束...

[温以沫](https://www.jianshu.com/u/3ea82673ddcb)阅读 122评论 0赞 0

  * [程序员常用软件](https://www.jianshu.com/p/122fae5ff066)

1、 Sublime Text 性感的编辑器，插件丰富，界面清爽。可跨平台支持Windows/Mac/Linux;...

[三国战记](https://www.jianshu.com/u/5107961d6acc)阅读 357评论 0赞 1

 