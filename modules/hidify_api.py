import requests
import logging
from typing import Dict, List, Optional, Any
from config import Config
import asyncio

logger = logging.getLogger(__name__)

class HiddifyAPI:
    def __init__(self):
        self.base_url = Config.HIDDIFY_BASE_URL.rstrip('/')
        self.api_key = Config.HIDDIFY_API_KEY
        self.proxy_path = Config.HIDDIFY_PROXY_PATH
        self.headers = {
            "Hiddify-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _get_url(self, endpoint: str) -> str:
        """ساخت URL کامل"""
        return f"{self.base_url}/{self.proxy_path}/api/v2{endpoint}"
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """ارسال درخواست به API"""
        try:
            url = self._get_url(endpoint)
            response = requests.request(method, url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"خطا در اتصال به Hiddify API: {e}")
            return None
        except Exception as e:
            logger.error(f"خطای نامشخص در API: {e}")
            return None
    
    # مدیریت کاربران
    def get_all_users(self) -> Optional[List[Dict]]:
        """دریافت همه کاربران"""
        return self._make_request("GET", "/admin/user/")
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """ایجاد کاربر جدید"""
        return self._make_request("POST", "/admin/user/", user_data)
    
    def get_user(self, uuid: str) -> Optional[Dict]:
        """دریافت اطلاعات کاربر خاص"""
        return self._make_request("GET", f"/admin/user/{uuid}/")
    
    def update_user(self, uuid: str, user_data: Dict) -> Optional[Dict]:
        """ویرایش کاربر"""
        return self._make_request("PATCH", f"/admin/user/{uuid}/", user_data)
    
    def delete_user(self, uuid: str) -> bool:
        """حذف کاربر"""
        result = self._make_request("DELETE", f"/admin/user/{uuid}/")
        return result is not None
    
    def get_user_configs(self, secret_uuid: str) -> Optional[Dict]:
        """دریافت کانفیگ‌های کاربر"""
        return self._make_request("GET", f"/panel/{secret_uuid}/api/v2/user/all-configs/")
    
    def get_user_profile(self, secret_uuid: str) -> Optional[Dict]:
        """دریافت پروفایل کاربر"""
        return self._make_request("GET", f"/panel/{secret_uuid}/api/v2/user/me/")
    
    # مدیریت ادمین‌ها
    def get_all_admins(self) -> Optional[List[Dict]]:
        """دریافت همه ادمین‌ها"""
        return self._make_request("GET", "/admin/admin_user/")
    
    def create_admin(self, admin_data: Dict) -> Optional[Dict]:
        """ایجاد ادمین جدید"""
        return self._make_request("POST", "/admin/admin_user/", admin_data)
    
    def get_admin(self, uuid: str) -> Optional[Dict]:
        """دریافت اطلاعات ادمین خاص"""
        return self._make_request("GET", f"/admin/admin_user/{uuid}/")
    
    # اطلاعات سیستم
    def get_server_status(self) -> Optional[Dict]:
        """دریافت وضعیت سرور"""
        return self._make_request("GET", "/admin/server_status/")
    
    def get_panel_info(self) -> Optional[Dict]:
        """دریافت اطلاعات پنل"""
        return self._make_request("GET", "/panel/info/")
    
    def get_all_configs(self) -> Optional[Dict]:
        """دریافت همه تنظیمات"""
        return self._make_request("GET", "/admin/all-configs/")

# نمونه استفاده
# api = HiddifyAPI()
# users = api.get_all_users()
