# 文件夹同步备份工具

## 简介

A Python tool for synchronizing and backing up directories with .gitignore style ignore rules.

一个使用 .gitignore 风格的忽略规则来同步和备份目录的 Python 工具。

这个 Python 脚本是一个简单但功能强大的文件夹同步备份工具。它可以把源文件夹（可以是多个）的内容复制到目标备份文件夹中，同时遵循源文件夹中定义的 `.gitignore` 样式的规则来决定哪些文件或文件夹应该被忽略。

该工具的主要特点是：

- 同步目录筛选：只会同步文件夹下包含 `backups.gitignore` 文件的文件夹，这样你可以在一个文件夹中放置多个源文件夹，然后通过 `backups.gitignore` 文件来控制每个源文件夹的同步规则。
- 同步：它不仅复制源文件夹中的新文件和修改过的文件到目标文件夹，而且还会删除目标文件夹中已经在源文件夹中不存在的文件，从而保持两个文件夹的同步。
- 忽略规则：它可以读取一个名为 `backups.gitignore` 的文件来获取忽略规则，这个文件应该放在源文件夹的根目录下。这个文件的格式和 `.gitignore` 文件一样，每一行定义一个匹配模式，匹配的文件或文件夹会被忽略。
- 备份记录：在每次执行备份操作后，它会在 `backups.gitignore` 文件的头部添加一条备份记录，记录源文件夹、目标文件夹和备份时间。

## 快速使用

```txt

备份测试
 ├── 备份后的位置
 │   ├── ChatGPT_flask_API_vue
 │   │   ├── backups.gitignore
 │   │   ├── index.html
 │   │   ├── package-lock.json
 │   │   ├── package.json
 │   │   ├── public
 │   │   │   └── favicon.ico
 │   │   ├── README.md
 │   │   ├── src
 │   │   │   ├── App.vue
 │   │   │   └── views
 │   │   └── vite.config.js
 │   └── js脚本
 │       ├── backups.gitignore
 │       ├── package.json
 │       └── 查看时间数组是否排序成功.js
 └── 待备份的目录
     ├── ChatGPT_flask_API_vue
     │   ├── backups.gitignore
     │   ├── dist
     │   │   └── index.html
     │   ├── index.html
     │   ├── node_modules
     │   │   ├── @babel
     │   │   └── vue-router
     │   ├── package-lock.json
     │   ├── package.json
     │   ├── public
     │   │   └── favicon.ico
     │   ├── README.md
     │   ├── src
     │   │   ├── App.vue
     │   │   └── views
     │   └── vite.config.js
     ├── js脚本
     │   ├── backups.gitignore
     │   ├── package.json
     │   └── 查看时间数组是否排序成功.js
     └── 一些杂乱的文件
         ├── 新建 Microsoft Word 文档.docx
         └── 新建 RTF 文档.rtf

```

1. 有一个待备份的目录（这个目录需要写入代码中），里面可能有许许多多的待备份的目录，自己的项目，图片，视频，都可以
2. 只需要在想备份的目录下面写一个 `backups.gitignore` 的文件，就可以自动备份这个目录
3.  `backups.gitignore` 的文件中是可以写忽略列表的，例如我们忽略 `node_modules` 文件夹，那么这个文件夹就不会被备份

## 使用说明

1. 确保你的 Python 版本是 3.6 或更高版本。

2. 下载或复制脚本代码到本地文件，例如命名为 `sync_backup.py`。

3. 修改脚本代码中的 `dirs` 变量和 `backup_dir` 变量，分别指定源文件夹和目标备份文件夹的路径。

4. 在你想要同步的文件夹中创建一个 `backups.gitignore` 文件，写入你想要忽略的文件或文件夹的匹配模式，可以为空，说明同步这个文件夹中的所有内容。

5. 打开命令行窗口，切换到脚本所在的目录，然后运行下面的命令：

    ```
    python sync_backup.py
    ```

    或者你可以直接双击脚本文件来运行。


## 注意事项

- 如果你在运行脚本时遇到权限问题，你可能需要以管理员权限运行命令行窗口或 Python 环境。
- 脚本会自动忽略 `.git` 目录，如果你希望备份 `.git` 目录，你需要修改脚本代码。
- 在 `backups.gitignore` 文件中，你可以使用标准的 `.gitignore` 文件的匹配模式，例如 `*.tmp`（忽略所有的 .tmp 文件）、`debug/`（忽略所有的 debug 文件夹）等。

## 结语

这个脚本为文件夹备份提供了一种简单而有效的方法，通过同步和忽略规则的功能，你可以精确地控制你的备份过程。希望这个工具能帮助你更好地管理你的文件和数据，让数据备份和同步变得更加轻松。

## 常见问题解答

**Q: 我在运行脚本时遇到了权限问题，怎么办？**

A: 你可能需要以管理员权限运行你的命令行窗口或 Python 环境。在 Windows 上，你可以右键点击 Python 或命令行快捷方式并选择 "以管理员身份运行"。

**Q: 我可以同时备份多个源文件夹吗？**

A: 是的，你可以在 `dirs` 变量中定义多个源文件夹，脚本会依次备份这些文件夹中包含 `backups.gitignore` 文件的文件夹。

**Q: 我如何定义忽略规则？**

A: 你可以在每个源文件夹中创建一个 `backups.gitignore` 文件，写入你想要忽略的文件或文件夹的匹配模式。这个文件的格式和 `.gitignore` 文件一样，每一行定义一个匹配模式，匹配的文件或文件夹会被忽略。

**Q: backups.gitignore 文件怎么写？**

A: 你可以使用标准的 `.gitignore` 文件的匹配模式，例如 `*.tmp`（忽略所有的 .tmp 文件）、`debug/`（忽略所有的 debug 文件夹）等。
```txt
node_modules
.DS_Store
dist
dist-ssr
*.local

# Editor directories and files
.vscode
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
```