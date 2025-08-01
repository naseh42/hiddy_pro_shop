import os
import shutil
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

class BackupAdmin:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    async def create_backup(self) -> dict:
        """ایجاد بکاپ از دیتابیس"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # کپی کردن فایل دیتابیس
            db_path = "./hiddyshop.db"  # مسیر فایل دیتابیس
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
                return {
                    "success": True,
                    "filename": backup_filename,
                    "path": backup_path,
                    "timestamp": timestamp
                }
            else:
                return {
                    "success": False,
                    "error": "فایل دیتابیس یافت نشد"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> list:
        """دریافت لیست بکاپ‌ها"""
        try:
            backups = []
            if os.path.exists(self.backup_dir):
                for filename in os.listdir(self.backup_dir):
                    if filename.startswith("backup_") and filename.endswith(".db"):
                        file_path = os.path.join(self.backup_dir, filename)
                        file_stat = os.stat(file_path)
                        backups.append({
                            "filename": filename,
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(file_stat.st_mtime)
                        })
            return sorted(backups, key=lambda x: x["modified"], reverse=True)
        except Exception as e:
            return []
    
    def restore_backup(self, backup_filename: str) -> dict:
        """بازیابی بکاپ"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            db_path = "./hiddyshop.db"
            
            if not os.path.exists(backup_path):
                return {
                    "success": False,
                    "error": "فایل بکاپ یافت نشد"
                }
            
            # بستن اتصال دیتابیس قبل از بازیابی
            # این بخش نیاز به مدیریت خاص دارد
            
            # کپی کردن بکاپ به جای دیتابیس فعلی
            shutil.copy2(backup_path, db_path)
            
            return {
                "success": True,
                "message": "بکاپ با موفقیت بازیابی شد"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_backup(self, backup_filename: str) -> bool:
        """حذف بکاپ"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            if os.path.exists(backup_path):
                os.remove(backup_path)
                return True
            return False
        except Exception as e:
            return False

# نمونه استفاده
# backup_admin = BackupAdmin(db_session)
# result = await backup_admin.create_backup()
