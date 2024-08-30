import os
import string
import shutil


PICTURE_EXT_LIST = ['.jpg', '.png']
PYTHON_EXT_LIST = ['py']





class FolderManager:
    Default_Imagefolder = "images"

    def __init__(self, imagefolder, valid_ext = None):

        if(imagefolder == ""):
            self.Imagefolder = self.Default_Imagefolder
        else:
            self.Imagefolder = imagefolder
       
        self.Valid_ext = valid_ext

    def Count_File(self, valid_ext=None):
        if valid_ext is None:
            valid_ext = self.Valid_ext

        if not os.path.exists(self.Imagefolder):
            print(f"資料夾 '{self.Imagefolder}' 不存在。")
            return

        total_images = 0
        total_size = 0

        # 計算 Imagefolder 本身的照片
        folder_image_count, folder_size = self._count_files_in_folder(self.Imagefolder, valid_ext)
        print(f"{self.Imagefolder} 底下有 {folder_image_count} 個檔案, 總大小: {self._format_size(folder_size)}")

        total_images += folder_image_count
        total_size += folder_size

        # 計算子資料夾中的圖片
        subfolder_names = [d for d in os.listdir(self.Imagefolder) if os.path.isdir(os.path.join(self.Imagefolder, d)) and d != 'ignore']

        print(f"{self.Imagefolder} 底下有 {len(subfolder_names)} 個資料夾 :")
        for subfolder in subfolder_names:
            print(f"資料夾名稱: {subfolder}")
            subfolder_path = os.path.join(self.Imagefolder, subfolder)
            label_folders = [d for d in os.listdir(subfolder_path) if os.path.isdir(os.path.join(subfolder_path, d))]
            subfolder_image_count = 0
            subfolder_size = 0

            for label_folder in label_folders:
                label_folder_path = os.path.join(subfolder_path, label_folder)
                image_count, folder_size = self._count_files_in_folder(label_folder_path, valid_ext)
                
                subfolder_image_count += image_count
                subfolder_size += folder_size
                print(f"  {label_folder}: {image_count} 個檔案, 大小: {self._format_size(folder_size)}")

            print(f"{subfolder} 總共有 {subfolder_image_count} 個檔案, 總大小: {self._format_size(subfolder_size)}\n")
            total_images += subfolder_image_count
            total_size += subfolder_size

        print(f"{self.Imagefolder} ({self._est_tostring(valid_ext)}) 總共有 {total_images} 個檔案, 總大小: {self._format_size(total_size)}")

    def _count_files_in_folder(self, folder_path, valid_ext):
        """
        計算資料夾中的圖片數量和總大小，根據 valid_ext 過濾檔案
        """
        if not os.path.exists(folder_path):
            return 0, 0

        if valid_ext:
            valid_ext = [ext.lower() for ext in valid_ext]
        else:
            valid_ext = []

        image_files = [f for f in os.listdir(folder_path) 
                       if os.path.isfile(os.path.join(folder_path, f)) and 
                          (not valid_ext or os.path.splitext(f)[1].lower() in valid_ext)]

        image_count = len(image_files)
        total_size = sum(os.path.getsize(os.path.join(folder_path, f)) for f in image_files)
        
        return image_count, total_size

    @staticmethod
    def _format_size(size):
        # 格式化檔案大小 (Bytes -> KB, MB, GB)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    @staticmethod
    def _est_tostring(valid_ext): # 把 副檔名 列表 轉換成 字串
        if(valid_ext is not None):
            return " ".join(valid_ext)
        else:
            return "沒有附檔名限制"

    @classmethod
    def Build_Train_Folders(cls):
        base_folder = cls.Default_Imagefolder
        subfolders = ["ignore", "train", "test"]

        # 數字和字母資料夾名稱
        digits = [str(i) for i in range(10)]
        letters = list(string.ascii_uppercase)

        # 創建主資料夾
        os.makedirs(base_folder, exist_ok=True)

        # 在每個子資料夾中創建數字和字母資料夾
        for subfolder in subfolders:
            subfolder_path = os.path.join(base_folder, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)
            
            for digit in digits:
                os.makedirs(os.path.join(subfolder_path, digit), exist_ok=True)
            
            for letter in letters:
                os.makedirs(os.path.join(subfolder_path, letter), exist_ok=True)

        print(f"{base_folder} 資料夾結構已建立完畢。")

    @staticmethod
    def Import_image_to_image(frompath, to_path):
        try:
            # 確認來源資料夾是否存在
            if not os.path.isdir(frompath):
                print(f"來源資料夾 {frompath} 不存在。")
                return

            # 檢查目標資料夾是否為空字符串
            if not to_path:
                print("目標資料夾名稱不能是空字符串。")
                return

            # 生成目標資料夾名稱
            target_folder = to_path + '_TARGET'

            # 如果目標資料夾不存在，創建與來源資料夾相同的結構
            if not os.path.isdir(target_folder):
                print(f"目標資料夾 {target_folder} 不存在，正在創建...")
                shutil.copytree(frompath, target_folder, dirs_exist_ok=True)
                print(f"資料夾結構 {target_folder} 已建立完成。")
            else:
                # 如果目標資料夾存在，先備份
                backup_path = target_folder + '_BACKUP'
                if not os.path.isdir(backup_path):
                    shutil.copytree(target_folder, backup_path)
                    print(f"備份資料夾 {target_folder} 到 {backup_path} 完成。")
                else:
                    print(f"備份資料夾 {backup_path} 已存在，請手動處理。")

            # 將來源資料夾中的檔案複製到目標資料夾中
            for root, dirs, files in os.walk(frompath):
                for file in files:
                    src_file = os.path.join(root, file)
                    # 生成相對路徑，以保持資料夾結構
                    rel_path = os.path.relpath(src_file, frompath)
                    dest_file = os.path.join(target_folder, rel_path)
                    dest_folder = os.path.dirname(dest_file)

                    # 創建目標資料夾（如果不存在）
                    os.makedirs(dest_folder, exist_ok=True)

                    # 檢查目標檔案是否已存在
                    if os.path.isfile(dest_file):
                        print(f"{file} 已存在於 {dest_folder}。")
                    else:
                        shutil.copy2(src_file, dest_file)
                        print(f"檔案 {file} 從 {src_file} 複製到 {dest_file} 完成。")

        except Exception as e:
            print(f"導入圖像時發生錯誤: {e}")








if __name__ == "__main__":

    # FolderManager.Build_Train_Folders()
    
    # while(True):
    #     print(f"輸入 查詢的圖片資料夾.\n輸入 -1 退出(預設位置為: {FolderManager.Default_Imagefolder})")
    #     Manage_Path = input("資料夾地址: ")

    #     if(Manage_Path == "-1"):
    #         break


    #     manager = FolderManager(Manage_Path)
    #     manager.Count_File(PICTURE_EXT_LIST)  # 輸入您需要的副檔名
    FolderManager.Import_image_to_image("images", "New_Images")
