import requests
import logging
from typing import Dict, List, Optional, Any
from config import Config
import json

logger = logging.getLogger(__name__)

class HiddifyAPI:
    def __init__(self, base_url: str = None, api_key: str = None, proxy_path: str = None):
        self.base_url = base_url or Config.HIDDIFY_BASE_URL.rstrip('/')
        self.api_key = api_key or Config.HIDDIFY_API_KEY
        self.proxy_path = proxy_path or Config.HIDDIFY_PROXY_PATH
        self.headers = {
            "Hiddify-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info(f"HiddifyAPI initialized with base_url: {self.base_url}")
    
    def _get_url(self, endpoint: str) -> str:
        """ساخت URL کامل"""
        return f"{self.base_url}/{self.proxy_path}/api/v2{endpoint}"
    
    def _make_request(self, method: str, endpoint: str,  Dict = None) -> Optional[Dict]:
        """ارسال درخواست به API"""
        try:
            url = self._get_url(endpoint)
            logger.info(f"API Request: {method} {url}")
            
            response = requests.request(
                method, 
                url, 
                headers=self.headers, 
                json=data, 
                timeout=30
            )
            
            logger.info(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json() if response.content else {}
                logger.info("API Success")
                return result
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network Error in Hiddify API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected Error in Hiddify API: {e}")
            return None
    
    # مدیریت کاربران
    def get_all_users(self) -> Optional[List[Dict]]:
        """دریافت همه کاربران"""
        logger.info("Getting all users from Hiddify")
        return self._make_request("GET", "/admin/user/")
    
    def create_user(self, user_ Dict) -> Optional[Dict]:
        """ایجاد کاربر جدید"""
        logger.info(f"Creating user in Hiddify: {user_data}")
        return self._make_request("POST", "/admin/user/", user_data)
    
    def get_user(self, uuid: str) -> Optional[Dict]:
        """دریافت اطلاعات کاربر خاص"""
        logger.info(f"Getting user from Hiddify: {uuid}")
        return self._make_request("GET", f"/admin/user/{uuid}/")
    
    def update_user(self, uuid: str, user_ Dict) -> Optional[Dict]:
        """ویرایش کاربر"""
        logger.info(f"Updating user in Hiddify: {uuid}")
        return self._make_request("PATCH", f"/admin/user/{uuid}/", user_data)
    
    def delete_user(self, uuid: str) -> bool:
        """حذف کاربر"""
        logger.info(f"Deleting user from Hiddify: {uuid}")
        result = self._make_request("DELETE", f"/admin/user/{uuid}/")
        return result is not None
    
    def get_user_configs(self, secret_uuid: str) -> Optional[Dict]:
        """دریافت کانفیگ‌های کاربر"""
        logger.info(f"Getting user configs from Hiddify: {secret_uuid}")
        return self._make_request("GET", f"/panel/{secret_uuid}/api/v2/user/all-configs/")
    
    def get_user_profile(self, secret_uuid: str) -> Optional[Dict]:
        """دریافت پروفایل کاربر"""
        logger.info(f"Getting user profile from Hiddify: {secret_uuid}")
        return self._make_request("GET", f"/panel/{secret_uuid}/api/v2/user/me/")
    
    # مدیریت ادمین‌ها
    def get_all_admins(self) -> Optional[List[Dict]]:
        """دریافت همه ادمین‌ها"""
        logger.info("Getting all admins from Hiddify")
        return self._make_request("GET", "/admin/admin_user/")
    
    def create_admin(self, admin_ Dict) -> Optional[Dict]:
        """ایجاد ادمین جدید"""
        logger.info(f"Creating admin in Hiddify: {admin_data}")
        return self._make_request("POST", "/admin/admin_user/", admin_data)
    
    def get_admin(self, uuid: str) -> Optional[Dict]:
        """دریافت اطلاعات ادمین خاص"""
        logger.info(f"Getting admin from Hiddify: {uuid}")
        return self._make_request("GET", f"/admin/admin_user/{uuid}/")
    
    # اطلاعات سیستم
    def get_server_status(self) -> Optional[Dict]:
        """دریافت وضعیت سرور"""
        logger.info("Getting server status from Hiddify")
        return self._make_request("GET", "/admin/server_status/")
    
    def get_panel_info(self) -> Optional[Dict]:
        """دریافت اطلاعات پنل"""
        logger.info("Getting panel info from Hiddify")
        return self._make_request("GET", "/panel/info/")
    
    def get_all_configs(self) -> Optional[Dict]:
        """دریافت همه تنظیمات"""
        logger.info("Getting all configs from Hiddify")
        return self._make_request("GET", "/admin/all-configs/")

# نمونه استفاده و تست
if __name__ == "__main__":
    # تست اتصال
    api = HiddifyAPI(
        base_url="https://subgerman.kudanshop.ir",
        api_key="ULTfkcPpjxdDA3SnJ",
        proxy_path="ULTfkcPpjxdDA3SnJ"
    )
    
    # تست دریافت اطلاعات پنل
    print("Testing panel connection...")
    panel_info = api.get_panel_info()
    if panel_info:
        print("✅ Connection successful!")
        print(f"Panel version: {panel_info.get('version', 'Unknown')}")
    else:
        print("❌ Connection failed!")
