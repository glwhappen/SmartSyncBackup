"""
文件同步脚本

"""

import os
import shutil
import fnmatch
import datetime
import hashlib

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def read_gitignore(gitignore_path):
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

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


def should_ignore(path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def copy_dir(src, dst, ignore_patterns, stats={'copied': 0, 'deleted': 0, 'modified': 0}):
    names = os.listdir(src)
    os.makedirs(dst, exist_ok=True)

    ignored_names = set()

    if ignore_patterns:
        for name in names:
            if should_ignore(name, ignore_patterns):
                ignored_names.add(name)

    dst_names = set(os.listdir(dst))

    for name in names:
        if name in ignored_names:
            continue

        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)

        try:
            if os.path.isdir(srcname):
                copy_dir(srcname, dstname, ignore_patterns, stats)
            else:
                if name not in dst_names:
                    shutil.copy2(srcname, dstname)
                    stats['copied'] += 1
                    print(f'Copied: {srcname} to {dstname}')
                elif get_file_hash(srcname) != get_file_hash(dstname):
                    shutil.copy2(srcname, dstname)
                    if name != 'backups.gitignore':
                        stats['modified'] += 1
                        print(f'modified: {srcname} to {dstname}')
        except Exception as err:
            print(f'Unable to copy {srcname}. Reason: {err}')

    for name in dst_names:
        if name not in names:
            stats['deleted'] += 1
            delname = os.path.join(dst, name)
            if os.path.isdir(delname):
                shutil.rmtree(delname)
            else:
                os.remove(delname)
            print(f'Deleted: {delname}')

    return stats

def backup_dirs(dirs, backup_dir):
    total_stats = {'copied': 0, 'deleted': 0, 'modified': 0}
    for dir in dirs:
        for root, subdirs, files in os.walk(dir):
            if 'backups.gitignore' in files:
                gitignore_path = os.path.join(root, 'backups.gitignore')
                write_info_to_gitignore(gitignore_path, root, backup_dir)
                ignore_patterns = read_gitignore(gitignore_path)
                rel_path = os.path.relpath(root, dir)
                backup_path = os.path.join(backup_dir, rel_path)
                stats = copy_dir(root, backup_path, ignore_patterns)
                total_stats['copied'] += stats['copied']
                total_stats['deleted'] += stats['deleted']
                total_stats['modified'] += stats['modified']
    print(f'Copied {total_stats["copied"]} files. Deleted {total_stats["deleted"]} files. Modified {total_stats["modified"]} files.')


dirs = ['C:\\happen\\拷贝测试\\待备份的目录']  # directories to backup
backup_dir = 'C:\\happen\\拷贝测试\\备份后的位置'  # backup directory
backup_dirs(dirs, backup_dir)
