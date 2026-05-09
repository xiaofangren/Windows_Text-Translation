# QuickTranslator - 划词翻译工具

一个轻量级的 Windows 划词翻译软件，在任意应用中选中文本后，自动弹出翻译按钮，点击即可快速翻译。

## 功能特性

- 浮动翻译按钮：拖动选中文字后自动显示绿色"译"按钮
- 智能翻译：在记事本等原生应用中直接读取选中文字；在浏览器中自动激活窗口并复制
- 浮动翻译窗口：在鼠标位置弹出半透明翻译窗口
- 多引擎支持：支持百度翻译 API（免费版）
- 系统托盘运行：后台常驻，随时可用
- 一键复制：翻译结果可直接复制到剪贴板

## 系统要求

- Windows 7/8/10/11
- Python 3.8+

## 安装

### 方式一：从源码运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行程序：

```bash
python main.py
```

### 方式二：使用打包好的 exe

1. 下载打包好的 exe 文件
2. 双击运行即可

## 打包说明

使用 PyInstaller 打包为 Windows 可执行文件：

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name QuickTranslator main.py
```

打包后的 exe 文件位于 `dist/QuickTranslator.exe`。

## 使用说明

### 首次使用

1. 运行程序后，会提示配置百度翻译 API
2. 前往 [百度翻译开放平台](https://fanyi-api.baidu.com/) 注册账号
3. 在"管理控制台"中创建应用，获取 App ID 和密钥
4. 在设置对话框中输入 App ID 和密钥

### 日常使用

1. 在任意应用（浏览器、终端、编辑器等）中**拖动选中**要翻译的文本
2. 松开鼠标后，绿色"译"按钮会在鼠标附近自动出现
3. 点击绿色"译"按钮
   - 记事本/编辑器等原生应用：直接读取选中文字并翻译
   - 浏览器等现代应用：按钮自动隐藏，自动激活原窗口并模拟 Ctrl+C，然后翻译
4. 翻译结果会在鼠标位置以浮动窗口形式显示
5. 点击"复制"按钮可复制翻译结果
6. 点击"关闭"按钮或按 ESC 键关闭窗口

### 修改设置

1. 在系统托盘图标上右键点击
2. 选择"设置"
3. 可修改以下内容：
   - 百度翻译 App ID 和密钥
   - 翻译引擎选择

## 项目结构

```
translator/
├── main.py              # 程序入口
├── hotkey_listener.py   # 鼠标监听 & 浮动按钮
├── clipboard.py         # 剪贴板操作
├── translator.py        # 翻译引擎
├── popup_window.py      # 浮动翻译窗口
├── settings.py          # 设置管理
├── settings_dialog.py   # 设置对话框
├── system_tray.py       # 系统托盘
├── config.py            # 配置常量
├── requirements.txt     # 依赖列表
└── build.spec           # PyInstaller 打包配置
```

## 常见问题

### Q: 为什么翻译结果不准确？
A: 百度翻译免费版的翻译质量对于日常使用已经足够。如需更高翻译质量，可以考虑使用付费版或其他翻译引擎。

### Q: 为什么按钮没出来？
A: 请确保是**拖动选中**文字，而不是只是点击一下。需要有一定的拖拽距离才会显示按钮。

### Q: 为什么部分应用无法直接翻译？
A: 浏览器等高权限应用为了安全限制了直接读取，程序会自动激活原窗口并模拟 Ctrl+C 来获取文字。

### Q: 如何申请百度翻译 API？
A: 前往 https://fanyi-api.baidu.com/ 注册账号，在"管理控制台"中创建应用即可获取免费 API 密钥（每月 200 万字符免费额度）。

## 许可证

MIT License