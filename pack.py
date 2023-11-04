import datetime
import os
import random
import re
import zipfile

import tqdm
import win32clipboard as w
import win32con


# 获取路径映射
def get_root_map(folder):
    root_map = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".xml"):
                # 正则拿到<process_time>2023-09-27 08:12:23</process_time>中的时间（20230927081223）
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    m = re.search(
                        r"<process_time>(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})</process_time>",
                        content,
                    )
                    if len(m.groups()) == 6:
                        root_map[root] = (
                            root
                            + "-"
                            + (
                                m.group(1)
                                + m.group(2)
                                + m.group(3)
                                + m.group(4)
                                + m.group(5)
                                + m.group(6)
                                + str(random.randint(100000, 999999))
                            )
                        )
                    else:
                        print("warning: " + os.path.join(root, file))

    return root_map


# 打包文件夹到zip文件
def pack_folders_to_zip(zip_filename, *folders):
    if not zip_filename.endswith(".zip"):
        zip_filename += ".zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder in tqdm.tqdm(folders):
            base_folder_name = os.path.basename(folder)
            zipf.write(folder, base_folder_name)  # 在zip文件中创建与第一个文件夹同名的文件夹
            root_map = get_root_map(folder)  # 获取路径映射
            # print("路径映射: ")
            # for key in root_map:
            #     print(" ", key, "=>", root_map[key])
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if not file.endswith(".pdf"):  # 排除PDF文件
                        file_path = os.path.join(root, file)
                        # print("添加文件: " + file_path)
                        zip_file_path = os.path.join(root_map[root], file)
                        zipf.write(
                            file_path,
                            os.path.join(
                                base_folder_name, os.path.relpath(zip_file_path, folder)
                            ),
                        )


# 获取剪贴板中的文件夹路径
def get_clipboard_paths():
    w.OpenClipboard()
    d = w.GetClipboardData(win32con.CF_TEXT)
    w.CloseClipboard()
    lst = d.decode("gbk").split("\r\n")
    for path in lst:
        if not os.path.isdir(path):
            print("remove(not dir): " + path)
            lst.remove(path)
        elif not path.endswith(".pdf"):
            print("warning(not pdf): " + path)
    return lst


def main(name):
    lst = get_clipboard_paths()
    if len(lst) == 0:
        print("剪贴板中没有文件夹路径")
        exit()

    print("获取到文件夹路径: ")
    for path in lst:
        print(" ", path)

    pack_folders_to_zip(
        name + "_交付_" + datetime.datetime.now().strftime("%Y年%m月%d日"), *lst
    )


# 产出人名称
main("通晓宇宙")
