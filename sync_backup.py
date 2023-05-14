"""
文件同步脚本
"""

import os
import shutil
import fnmatch
import datetime
import hashlib
import yaml # pip install pyyaml
import pickle

# 函数：保存备份快照
def save_snapshot(snapshot, snapshot_file):
    with open(snapshot_file, 'wb') as f:
        pickle.dump(snapshot, f)

# 函数：加载备份快照
def load_snapshot(snapshot_file):
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

## 函数：读取配置文件
def read_config(config_file):
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config['dirs'], config['backup_dir']

# 函数：获取文件的MD5哈希值，用于比较文件是否有所改动
def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

# 函数：读取gitignore文件，获取需要忽略的文件和文件夹的列表
def read_gitignore(gitignore_path):
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

# 函数：向gitignore文件中添加当前备份的信息
def write_info_to_gitignore(gitignore_path, src, dst):
    info = f"# Backup Information\n# Original Directory: {src}\n# Backup Directory: {dst}\n# Backup Time: {datetime.datetime.now()}\n# Backup Information End\n\n"
    with open(gitignore_path, 'r+', encoding='utf-8') as f:
        content = f.read()
        backup_info_index = content.find("# Backup Information")
        if backup_info_index != -1:
            end_index = content.find("\n\n", backup_info_index)
            if end_index != -1:
                content = content[end_index+2:]
            else:
                content = ""
        f.seek(0, 0)
        f.write(info + content)
        f.truncate()

# 函数：根据ignore_patterns判断路径是否应被忽略
def should_ignore(path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

# 函数：拷贝目录并忽略特定文件，同时统计新增、删除和修改的文件数量
def copy_dir(src, dst, ignore_patterns, snapshot, stats={'copied': 0, 'deleted': 0, 'modified': 0, 'checked': 0}, counter={'count': 0}):
    names = os.listdir(src)  # 获取源文件夹中的文件和文件夹列表
    os.makedirs(dst, exist_ok=True)  # 确保目标文件夹存在

    ignored_names = set()  # 存放需要忽略的文件和文件夹名称

    if ignore_patterns:  # 如果有忽略规则
        for name in names:  # 遍历源文件夹中的所有文件和文件夹
            if should_ignore(name, ignore_patterns):  # 如果文件或文件夹符合忽略规则
                ignored_names.add(name)  # 将其添加到忽略集合中

    dst_names = set(os.listdir(dst))  # 获取目标文件夹中的文件和文件夹列表

    for name in names:  # 遍历源文件夹中的所有文件和文件夹
        if name in ignored_names:  # 如果文件或文件夹在忽略列表中
            continue  # 跳过此次循环

        # 每处理一个文件或目录，就增加counter
        counter['count'] += 1
        stats['checked'] += 1

        # 如果counter达到100，就输出进度，然后重置counter
        if counter['count'] >= 100:
            print(
                f'Checked {stats["checked"]} files/directories. Copied {stats["copied"]} files. Deleted {stats["deleted"]} files. Modified {stats["modified"]} files.')
            counter['count'] = 0

        srcname = os.path.join(src, name)  # 获取源文件/文件夹的完整路径
        dstname = os.path.join(dst, name)  # 获取目标文件/文件夹的完整路径

        try:
            if os.path.isdir(srcname):  # 如果是文件夹
                copy_dir(srcname, dstname, ignore_patterns, stats)  # 递归拷贝文件夹
            else:  # 如果是文件

                current_timestamp = os.path.getmtime(srcname)  # 获取文件的当前修改时间
                # 如果文件没有被修改，则跳过
                if name in dst_names and current_timestamp == snapshot.get(srcname, 0):
                    print(f'Skipped: {srcname} {current_timestamp} {snapshot.get(srcname, 0)}')
                    continue

                # 更新文件的时间戳快照
                snapshot[srcname] = current_timestamp

                if name not in dst_names:  # 如果目标文件夹中不存在该文件
                    shutil.copy2(srcname, dstname)  # 拷贝文件
                    stats['copied'] += 1  # 记录拷贝的文件数量
                    print(f'Copied: {srcname} to {dstname}')
                elif get_file_hash(srcname) != get_file_hash(dstname):  # 如果文件存在但内容有所改变
                    shutil.copy2(srcname, dstname)  # 覆盖拷贝文件
                    if name != 'backups.gitignore':  # 忽略.gitignore文件的更改
                        stats['modified'] += 1  # 记录修改的文件数量
                        print(f'modified: {srcname} to {dstname}')
        except Exception as err:
            print(f'Unable to copy {srcname}. Reason: {err}')  # 打印无法拷贝的文件和原因

    for name in dst_names:  # 遍历目标文件夹中的所有文件和文件夹
        if name not in names:  # 如果目标文件夹中的文件/文件夹在源文件夹中不存在
            stats['deleted'] += 1  # 记录删除的文件/文件夹数量
            delname = os.path.join(dst, name)  # 获取要删除的文件/文件夹的完整路径
            if os.path.isdir(delname):  # 如果是文件夹
                shutil.rmtree(delname)  # 删除文件夹
            else:  # 如果是文件
                os.remove(delname)  # 删除文件
            print(f'Deleted: {delname}')  # 打印删除的文件/文件夹信息

    return stats  # 返回统计信息

# 函数：备份多个目录到指定的备份文件夹
def backup_dirs(dirs, backup_dir, snapshot_file):
    total_stats = {'copied': 0, 'deleted': 0, 'modified': 0, 'checked': 0}  # 初始化总的统计信息
    snapshot = load_snapshot(snapshot_file)  # type:dict 加载快照
    for dir in dirs:  # 遍历所有需要备份的目录
        dir_name = os.path.basename(dir)  # 获取源目录的名称
        dir_backup_path = os.path.join(backup_dir, dir_name)  # 在备份路径上添加源目录的名称
        for root, subdirs, files in os.walk(dir):  # 使用os.walk获取目录中的所有文件和子目录
            if 'backups.gitignore' in files:  # 如果目录中存在.gitignore文件
                gitignore_path = os.path.join(root, 'backups.gitignore')  # 获取.gitignore文件的完整路径
                write_info_to_gitignore(gitignore_path, root, dir_backup_path)  # 向.gitignore文件中添加备份信息
                ignore_patterns = read_gitignore(gitignore_path)  # 读取.gitignore文件获取需要忽略的文件和文件夹
                rel_path = os.path.relpath(root, dir)  # 计算相对路径
                backup_path = os.path.join(dir_backup_path, rel_path)  # 根据相对路径计算备份路径
                stats = copy_dir(root, backup_path, ignore_patterns, snapshot)  # 拷贝目录并获取统计信息
                total_stats['copied'] += stats['copied']  # 更新总的拷贝文件数量
                total_stats['deleted'] += stats['deleted']  # 更新总的删除文件数量
                total_stats['modified'] += stats['modified']  # 更新总的修改文件数量
                total_stats['checked'] += stats['checked']  # 更新总的检查目录数量

    save_snapshot(snapshot, snapshot_file)  # 保存快照

    print(f'Checked {total_stats["checked"]} files/directories. Copied {total_stats["copied"]} files. Deleted {total_stats["deleted"]} files. Modified {total_stats["modified"]} files.')  # 打印总的统计信息


dirs, backup_dir = read_config('config.yml') # 读取配置文件
snapshot_file = 'snapshot.pickle'  # 快照文件
backup_dirs(dirs, backup_dir, snapshot_file) # 调用backup_dirs函数进行备份