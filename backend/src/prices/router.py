from fastapi import APIRouter, Query
import requests
from typing import Optional, Any, Dict, List

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])

@router.get("/necessities-price")
def get_necessities_prices(
    category: Optional[str] = Query(None, description="民生必需品類別名稱"),
    commodity: Optional[str] = Query(None, description="商品名稱")
) -> List[Dict[str, Any]]:
    """
    從政府開放資料 API 獲取民生用品的價格資訊。
    """
    # 這是原始 main.py 中調用的外部 API
    api_url = "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice"
    
    params = {}
    if category:
        params["CategoryName"] = category
    if commodity:
        params["Name"] = commodity
        
    response = requests.get(api_url, params=params)
    
    # 建議加上錯誤處理，但在您的原始碼中是直接返回 .json()
    response.raise_for_status() # 如果狀態碼不是 200，拋出異常
    
    return response.json()
