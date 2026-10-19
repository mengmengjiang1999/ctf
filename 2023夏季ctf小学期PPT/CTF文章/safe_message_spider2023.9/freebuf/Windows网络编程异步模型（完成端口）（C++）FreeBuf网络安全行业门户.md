## 一、 **概述**

完成端口模型：创建完成端口

第一次创建完成端口时，没有文件句柄也没有完成端口。在第二次调用此函数时，吧完成端口和文件句柄进行关联。

第一个参数：文件句柄

第二个参数：已存在的完成端口，第一次调用传空

第三个参数：参数随意

第四个参数：最大并行线程数量，第二次创建不需要

![1684918925_646dd28d80a0deef0fe7e.png!small?1684918927569](https://image.3001.net/images/20230524/1684918925_646dd28d80a0deef0fe7e.png!small?1684918927569)

此时我们可以创建一个线程等待完成端口队列，队列中如果有客户端socket就会返回。

第一个参数：完成端口句柄

第二个参数：接收的数据

第三个参数：创建完成端口时的参数

第四个参数：创建完成端口时overlapped指针

第五个参数：等待多久函数返回，一般都是无限等待

![1684918944_646dd2a0d9e1371824fd5.png!small?1684918946348](https://image.3001.net/images/20230524/1684918944_646dd2a0d9e1371824fd5.png!small?1684918946348)

## 二、服务端代码

#include<winsock2.h>

#include<Windows.h>

#include<stdio.h>

#pragma comment(lib,"ws2_32.lib")

#define READ 0x1

#define WRITE 0x2

#define ACCEPT 0x3

#define MAXBUFFER 0x1000

typedef struct MYSOCKET

{

WSAOVERLAPPED S_OV;

SOCKET m_C;

SOCKADDR m_CC;

UINT state;//SOCKET状态

WSABUF Rece_Buff;

char Buffer1[MAXBUFFER];

WSABUF Send_Buff;

char Buffer2[MAXBUFFER];

DWORD Flags;

}MYSOCKET, * PMySOCKET;

PMySOCKET GetSocket()//用于获取结构体数组中空闲的socket，按照顺序遍历

{

PMySOCKET m_psocket = (PMySOCKET)HeapAlloc(GetProcessHeap(),
HEAP_GENERATE_EXCEPTIONS, sizeof(MYSOCKET));

if (m_psocket == NULL)

{

return NULL;

}

m_psocket->Rece_Buff.len = MAXBUFFER;

m_psocket->Send_Buff.len = MAXBUFFER;

m_psocket->Rece_Buff.buf = m_psocket->Buffer1;

m_psocket->Send_Buff.buf = m_psocket->Buffer2;

return m_psocket;

}

VOID FreeSocket(PMySOCKET p)

{

if (p->m_C)

{

closesocket(p->m_C);

}

HeapFree(GetProcessHeap(), 0, p);

printf("close socket");

}

DWORD Is_Over(WSABUF mybuf)

{

for (size_t i = 0; i < mybuf.len; i++)

{

if (mybuf.buf[i] == 'e')

{

return TRUE;

}

else if (mybuf.buf[i] == 0)

return FALSE;

}

return FALSE;

}

VOID ProcessData(WSABUF* pRecv_Buf,WSABUF* pSend_Buf) {

printf("Start process data...\n");

ZeroMemory(pSend_Buf->buf, MAXBUFFER);

CopyMemory(pSend_Buf->buf, pRecv_Buf->buf, pRecv_Buf->len -2);//减去命令结束符和字符串结束符

printf("Finish process data...\n");

}

DWORD WINAPI Rec_SOCKET(LPVOID lpParameter) {

HANDLE m_port = (HANDLE)lpParameter;

DWORD dw_Bytes;

DWORD key;

PMySOCKET m_socket;

BOOL re;

while (1)

{

re=GetQueuedCompletionStatus(m_port, &dw_Bytes, &key,
(LPOVERLAPPED*)&m_socket, INFINITE);

if (dw_Bytes == 0)

{

FreeSocket(m_socket);

continue;

}

else if (m_socket->state == READ)

{

if (Is_Over(m_socket->Rece_Buff))

{

//合并数据

m_socket->Rece_Buff.len = (m_socket->Rece_Buff.buf - m_socket->Buffer1) +
dw_Bytes;

m_socket->Rece_Buff.buf = m_socket->Buffer1;

ProcessData(&m_socket->Rece_Buff, &m_socket->Send_Buff);

m_socket->state = WRITE;

ZeroMemory(&m_socket->S_OV, sizeof(WSAOVERLAPPED));

int re1 = WSASend(m_socket->m_C, &m_socket->Send_Buff, 1, NULL,
m_socket->Flags, &m_socket->S_OV, NULL);

if (re1 == SOCKET_ERROR)

{

if (re1 != WSA_IO_PENDING) {

FreeSocket(m_socket);

}

}

else if (re1 == 0)

{

printf("This Send OK\n");

}

}

else

{

m_socket->Rece_Buff.buf = m_socket->Rece_Buff.buf + dw_Bytes;//更新接收数据指针位置

m_socket->Rece_Buff.len = MAXBUFFER - (m_socket->Rece_Buff.buf -m_socket->Buffer1);//计算剩余大小

ZeroMemory(&m_socket->S_OV, sizeof(WSAOVERLAPPED));

int re1 = WSASend(m_socket->m_C, &m_socket->Send_Buff, 1, NULL,
m_socket->Flags, &m_socket->S_OV, NULL);

if (re1 == SOCKET_ERROR)

{

if (re1 != WSA_IO_PENDING) {

FreeSocket(m_socket);

}

}

else if (re1 == 0)

{

printf("This Send OK\n");

}

}

}

else if (m_socket->state == WRITE)

{

ZeroMemory(&m_socket->Buffer1, MAXBUFFER);

m_socket->state = READ;

m_socket->Rece_Buff.len = MAXBUFFER;

ZeroMemory(&m_socket->S_OV, sizeof(WSAOVERLAPPED));

int re = WSARecv(m_socket->m_C, &m_socket->Rece_Buff, 1, NULL,
&m_socket->Flags, &m_socket->S_OV, NULL);

if (re != WSA_IO_PENDING)

{

FreeSocket(m_socket);

}

else if (re == 0)

{

printf("Write OK\n");

}

}

}

return 0;

}

int main()

{

WSADATA wsdata;

int wsa = WSAStartup(MAKEWORD(2, 2), &wsdata);

HANDLE m_port=CreateIoCompletionPort(INVALID_HANDLE_VALUE, NULL, NULL,
8);//初始化完成端口

CreateThread(NULL, 0, Rec_SOCKET, m_port, 0, NULL);//创建线程，吧完成端口句柄作为线程参数传进去

SOCKET m_S = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

sockaddr_in Sock_in = {0};

Sock_in.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");

Sock_in.sin_family = AF_INET;

Sock_in.sin_port = htons(0x1234);

int s=sizeof(Sock_in);

int re=bind(m_S, (sockaddr*)&Sock_in, s);

listen(m_S,0);

while (1)

{

PMySOCKET m_psocket = GetSocket();

if (m_psocket == NULL)

{

break;

}

//接受客户端连接

int m_len = sizeof(SOCKADDR_IN);

m_psocket->m_C=accept(m_S, (SOCKADDR*)&Sock_in, &m_len);

if (m_psocket->m_C == INVALID_SOCKET)

{

m_psocket->m_C = 0;

FreeSocket(m_psocket);

}

else

{

CreateIoCompletionPort((HANDLE)m_psocket->m_C, m_port, m_psocket->m_C,
0);//吧socket对象与完成端口进行关联

m_psocket->state = READ;

ZeroMemory(&m_psocket->S_OV, sizeof(WSAOVERLAPPED));

int re = WSARecv(m_psocket->m_C, &m_psocket->Rece_Buff, 1,
NULL,&m_psocket->Flags, &m_psocket->S_OV, NULL);

re = WSAGetLastError();

if (re == 0)

{

printf("Recv OK\n");

}

else if (re != WSA_IO_PENDING)

{

FreeSocket(m_psocket);

}

}

}

WSACleanup();

return 0;

}

## 三、服务器效果

![1684919027_646dd2f3270419655266a.png!small?1684919028042](https://image.3001.net/images/20230524/1684919027_646dd2f3270419655266a.png!small?1684919028042)

