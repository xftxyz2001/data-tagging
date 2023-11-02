import datetime
import os
import zipfile

import tqdm
import win32clipboard as w
import win32con


# 打包文件夹到zip文件
def pack_folders_to_zip(zip_filename, *folders):
    if not zip_filename.endswith(".zip"):
        zip_filename += ".zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for folder in tqdm.tqdm(folders):
            base_folder_name = os.path.basename(folder)
            zipf.write(folder, base_folder_name)  # 在zip文件中创建与第一个文件夹同名的文件夹
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if not file.endswith(".pdf"):  # 排除PDF文件
                        file_path = os.path.join(root, file)
                        zipf.write(
                            file_path,
                            os.path.join(
                                base_folder_name, os.path.relpath(file_path, folder)
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


main("通晓宇宙")
