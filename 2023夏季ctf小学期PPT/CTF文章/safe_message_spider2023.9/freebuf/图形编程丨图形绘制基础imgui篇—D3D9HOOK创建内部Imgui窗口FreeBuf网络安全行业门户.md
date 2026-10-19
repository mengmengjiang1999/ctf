Imgui又称为Dear
ImGui，它是与平台无关的C++轻量级跨平台图形界面库，没有任何第三方依赖，可以将Imgui的源码直接加到项目中使用，也可以编译成dll,
Imgui使用DX或者OpenGL进行界面渲染，Imgui主要用于游戏行业。

这里我们需要用到两个工具Detours-master（微软的hook库）和imgui-master，主要讲D3D9HOOK。

 **我们先来创建一个DLL项目。步骤如下：**

1.选择新建项目。

![](https://image.3001.net/images/20220609/1654777222_62a1e586bce950839e0f9.png!small)

2.选择Windows桌面->动态链接库（DLL）->D3D9HOOK，点击确定

![](https://image.3001.net/images/20220609/1654777224_62a1e5889a7649a2b9da2.png!small)

3.删除framework.h、pch.h以及pch.cpp文件。添加一个dllmain.h头文件

![](https://image.3001.net/images/20220609/1654777225_62a1e58973c8e5dc27c25.png!small)

4.dllmain.cpp中要包含头文件添加#include

![](https://image.3001.net/images/20220609/1654777228_62a1e58c052e03d2422d2.png!small)

5\. 配置

5.1 选择属性

![](https://image.3001.net/images/20220609/1654777230_62a1e58ea5b0232d5d592.png!small)

5.2 修改运行库以及Spectre缓解，选择应用

![](https://image.3001.net/images/20220609/1654777231_62a1e58f4309b4834d922.png!small)

5.3 配置include路径，点击“宏”，搜索DX，根据地址找到文件位置，将 $(DXSDK_DIR)include填入，应用

![](https://image.3001.net/images/20220609/1654777231_62a1e58fda9eab98106c4.png!small)

5.4
搜索DX，将$(DXSDK_DIR)Lib填入，搜索$(platformTarget)，将$(DXSDK_DIR)lib\$(platformTarget)填入，应用

（图片注释：配置好会自动匹配x86/x64不需要再改）

![](https://image.3001.net/images/20220609/1654777232_62a1e5907fb9e832c389c.png!small)

5.5 新增d3d9.lib，d3dx9.lib这两个依赖项，应用

![](https://image.3001.net/images/20220609/1654777233_62a1e5911aa3bb9c1337b.png!small)

6\. 配置好环境后，编译HOOK库(编译x86和x64两个版本)

X86：找到Visual Studio2017，打开“x86 Native Tools Prompt for VS
2017”，然后cd到路径里nmake进行编译

![](https://image.3001.net/images/20220609/1654777233_62a1e591a3a7e583492a6.png!small)

X64：找到Visual Studio2017，打开“适用于VS 2017的 x64 本机工具命令提示”，然后cd到路径里nmake进行编译

![](https://image.3001.net/images/20220609/1654777234_62a1e59223da1505edbfd.png!small)

7.打开项目文件夹

![](https://image.3001.net/images/20220609/1654777234_62a1e592c4bdaa4753648.png!small)

8.新建一个目录Detours，将lib.x86、lib.x64和include复制过来（将lib.去掉方便后续识别）

![](https://image.3001.net/images/20220609/1654777235_62a1e5934701e09600081.png!small)

9.新建筛选器，命名Detours

![](https://image.3001.net/images/20220609/1654777235_62a1e593d07a8fe139d77.png!small)

10.在Detours中添加现有项，选定两个头文件detours.h和detver.h

![](https://image.3001.net/images/20220609/1654777236_62a1e594cc898c7dcfa89.png!small)

 **11.配置lib库**

11.1选择属性

![](https://image.3001.net/images/20220609/1654777237_62a1e59559d51d8ae55aa.png!small)

11.2 编辑包含目录，宏-包含目录-$(ProjectDir)Detours\include，应用

![](https://image.3001.net/images/20220609/1654777238_62a1e59600b5880c2917c.png!small)

11.3编辑附加库目录，宏-附加库目录-$(ProjectDir)Detours\Lib\$(platformTarget)，应用

![](https://image.3001.net/images/20220609/1654777238_62a1e596a3bb0c46f7da4.png!small)

11.4 编辑附加依赖项，添加detours.lib，应用

![](https://image.3001.net/images/20220609/1654777239_62a1e5977653d4c33758c.png!small)

11.5 不使用预编译头

![](https://image.3001.net/images/20220609/1654777240_62a1e598095c79b1199d7.png!small)

 **12.配置imgui**

12.1在D3D9HOOK目录下，新建imgui文件夹，将imgui-master中backends里imgui_impl_dx9.cpp、imgui_impl_dx9.h和imgui_impl_win32.cpp、imgui_impl_win32.h；及主目录下所有.cpp和.h都复制到imgui文件夹中

![](https://image.3001.net/images/20220609/1654777240_62a1e5988c97cb06aa0f9.png!small)

12.2新建筛选器，命名imgui

![](https://image.3001.net/images/20220609/1654777241_62a1e59976e8c81609521.png!small)

12.3在imgui中添加现有项，选定目录下所有文件

![](https://image.3001.net/images/20220609/1654777242_62a1e59a30b918daa33ee.png!small)

12.4.dllmain.h中包含导进来的所有头文件

![](https://image.3001.net/images/20220609/1654777242_62a1e59ae2f365e8fb7de.png!small)

13.主线程imgui窗口的实现

typedef HRESULT (WINAPI * FuncReset)(IDirect3DDevice9
*pIDirect3DDevice9,D3DPRESENT_PARAMETERS *pPresentationParameters);

typedef HRESULT (WINAPI * FuncEndScene)(IDirect3DDevice9 *pIDirect3DDevice9);

typedef LRESULT(WINAPI * FuncWndProc)(const HWND, UINT, WPARAM, LPARAM);

HWND g_hWnd = NULL;

IDirect3D9 * g_IDirect3D9;

D3DPRESENT_PARAMETERS g_d3dpp;

IDirect3DDevice9* g_pIDirect3DDevice9;

FuncReset OldReset;

FuncEndScene OldEndScene;

FuncWndProc OldWndProc;

DWORD * dwDeviceVirtualTable = NULL;

extern LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT message, WPARAM
wParam, LPARAM lParam);

LRESULT WINAPI GrkWndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM
lParam)

{

if (ImGui_ImplWin32_WndProcHandler(hWnd, message, wParam, lParam))

{

return TRUE;

}

return CallWindowProc(OldWndProc, hWnd, message, wParam, lParam);

}

VOID StartHook(PVOID * OldFunctionAddr, PVOID NewFunctionAddr)

{

DetourTransactionBegin();

DetourUpdateThread(GetCurrentThread());

DetourAttach(OldFunctionAddr, NewFunctionAddr);

DetourTransactionCommit();

}

VOID UnHook(PVOID * OldFunctionAddr, PVOID NewFunctionAddr)

{

DetourTransactionBegin();

DetourUpdateThread(GetCurrentThread());

DetourDetach(OldFunctionAddr, NewFunctionAddr);

DetourTransactionCommit();

}

HRESULT WINAPI GrkReset(IDirect3DDevice9 *pIDirect3DDevice9,
D3DPRESENT_PARAMETERS *d3dpp)

{

UnHook((PVOID*)(&OldReset), GrkReset);

ImGui_ImplDX9_InvalidateDeviceObjects();

HRESULT bRet = pIDirect3DDevice9->Reset(d3dpp);

ImGui_ImplDX9_CreateDeviceObjects();

StartHook((PVOID*)(&OldReset), GrkReset);

return bRet;

}

HRESULT WINAPI GrkEndScene(IDirect3DDevice9 *pIDirect3DDevice9)

{

UnHook((PVOID*)(&OldEndScene), GrkEndScene);

static bool bFlag = TRUE;

if (bFlag)

{

bFlag = FALSE;

IMGUI_CHECKVERSION();

ImGui::CreateContext();

ImGuiIO & io = ImGui::GetIO();

io.ConfigFlags = ImGuiConfigFlags_NoMouseCursorChange;

io.WantSaveIniSettings = false;

io.IniFilename = NULL;

ImGui::StyleColorsClassic();

ImFontConfig imfConfig;

imfConfig.FontDataOwnedByAtlas = false;

ImGui_ImplWin32_Init(g_hWnd);

ImGui_ImplDX9_Init(pIDirect3DDevice9);

OldWndProc = (WNDPROC)SetWindowLongPtr(g_hWnd, GWL_WNDPROC,
(LONG_PTR)GrkWndProc);

}

HRESULT hRet = pIDirect3DDevice9->EndScene();

ImGui_ImplDX9_NewFrame();

ImGui_ImplWin32_NewFrame();

ImGui::NewFrame();

ImGui::SetNextWindowPos(ImVec2(0, 0), ImGuiCond_FirstUseEver);

ImGui::SetNextWindowSize(ImVec2(300, 300));

ImGui::Begin("GrkTools");

ImGui::End();

ImGui::EndFrame();

ImGui::Render();

ImGui_ImplDX9_RenderDrawData(ImGui::GetDrawData());

StartHook((PVOID*)(&OldEndScene), GrkEndScene);

return hRet;

}

DWORD WindowThreadCallBack(LPVOID lpBuffer)

{

g_hWnd = FindWindowA("Direct3DWindowClass", NULL);

g_IDirect3D9 = Direct3DCreate9(D3D_SDK_VERSION);

memset(&g_d3dpp, 0, sizeof(g_d3dpp));

g_d3dpp.Windowed = TRUE;

g_d3dpp.SwapEffect = D3DSWAPEFFECT_DISCARD;

g_d3dpp.BackBufferFormat = D3DFMT_UNKNOWN;

g_d3dpp.EnableAutoDepthStencil = TRUE;

g_d3dpp.AutoDepthStencilFormat = D3DFMT_D16;

HRESULT hRet = g_IDirect3D9->CreateDevice(D3DADAPTER_DEFAULT, D3DDEVTYPE_HAL,
g_hWnd, D3DCREATE_SOFTWARE_VERTEXPROCESSING, &g_d3dpp, &g_pIDirect3DDevice9);

dwDeviceVirtualTable = (DWORD *)*(DWORD *)g_pIDirect3DDevice9;

OldReset = (FuncReset)dwDeviceVirtualTable[16];

OldEndScene = (FuncEndScene)dwDeviceVirtualTable[42];

StartHook((PVOID*)(&OldReset), GrkReset);

StartHook((PVOID*)(&OldEndScene), GrkEndScene);

return 0;

}

BOOL APIENTRY DllMain( HMODULE hModule,

DWORD ul_reason_for_call,

LPVOID lpReserved

)

{

switch (ul_reason_for_call)

{

case DLL_PROCESS_ATTACH:

CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)WindowThreadCallBack, NULL,
NULL, NULL);

break;

case DLL_THREAD_ATTACH:

break;

case DLL_THREAD_DETACH:

break;

case DLL_PROCESS_DETACH:

break;

}

return TRUE;

}

 **14.测试**

14.1打开文件夹，把动态链接库D3D9HOOK.dll粘贴到桌面上

![](https://image.3001.net/images/20220609/1654777243_62a1e59bb79715f535949.png!small)

14.2打开pick，启动代码注入器，将动态链接库D3D9HOOK.dll进行注入

测试成功：在pick左上角出现窗口<span< span=""></span<>

![](https://image.3001.net/images/20220609/1654777244_62a1e59c31deb8aba76ce.png!small)

这样，就手动创建了一个基础的imgui的框架

