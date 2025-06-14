"""
   table數據處理功能新增(擷取、併入dataframe、匯出csv)(另開程式碼小規模單頁測試)
   流程確認
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from bs4 import BeautifulSoup
import time
import pandas as pd

from CaptureTableInOnePage import getTableData

class WebScrapper:
    e_soup = None
    s_soup = None
    e_table = None 
    s_table = None
    page_data = None
    column_flag = False # 是否獲取到表格標頭的標誌
    
    __max_year = 2023 # 最大年份
    __max_column = 39 # 最大列數
    __current_year = 2003 # 當前年份，由遠到近
    __max_year_flag = True # 是否到達最大年份的標誌
    
    __page_source = None # 當前頁面的HTML源碼
    __table = None # 用於存儲表格數據
    
    def __init__(self, url):
        """
        初始化WebScrapper類別，設置瀏覽器驅動和網址
        """
        self.url = url
        self.driver = EdgeChromiumDriverManager().install() # 安裝Edge驅動
        self.service = Service(self.driver) # 安裝Edge驅動
        
        self.options = webdriver.EdgeOptions()
        self.options.add_experimental_option("detach", True) # 保持瀏覽器打開
        self.driver = webdriver.Edge(service=self.service, options=self.options) # 初始化瀏覽器
        
        self.driver.get(url)
        self.cookieAccept() # 接受cookie
    
    def processing(self):
        """
        每頁處理數據流程
        """
        print("開始處理數據")
        print(self.driver)
        while self.__max_year_flag is not False:
            s_soup = BeautifulSoup(self.getPageSource(), 'html.parser') # 獲取當前standrad頁面的HTML源碼
            s_table = getTableData(s_soup) # 獲取standrad表格數據
            self.goToExpandView() # 查找expand按鈕元素
            e_soup = BeautifulSoup(self.getPageSource(), 'html.parser') # 獲取當前expand頁面的HTML源碼
            e_table = getTableData(e_soup) # 獲取expand表格數據
            page_data = pd.concat([s_table, e_table], axis=1) # 合併數據
            self.goToNextPage() # 查找下一頁按鈕元素
            
        print("所有頁面數據處理完成")
        
    def cookieAccept(self):
        """
        等待cookie確認頁面加載並點擊確認按鈕
        """
        self.waitForPageLoad()
        
        try:
            # 使用XPATH查找按鈕元素，根據按鈕的文本內容查找
            __cookie_button = self.driver.find_element(By.XPATH, '//button[text()="OK"]')
            __cookie_button.click()
            print("Cookie確認按鈕已點擊")
        except:
            print("未找到cookie確認按鈕")
            
    def getPageSource(self):
        """
        獲取當前頁面的HTML源碼
        """
        self.waitForPageLoad()
        
        __page_source = None # 初始化頁面源碼
        __page_source = self.driver.page_source # 獲取當前頁面的HTML源碼
        
        if __page_source is None:
            print("無法獲取當前頁面的HTML源碼")
            return None
        else:
            print("獲取當前頁面的HTML源碼成功")
        return __page_source
    
    def goToExpandView(self):
        """
        查找按鈕元素
        """
        try:
            # 使用XPATH查找按鈕元素，根據按鈕的文本內容查找
            __expand_view_button = self.driver.find_element(By.XPATH, '/html/body/main/div[2]/section/section/div[1]/div[2]/div/div[1]/div/div[2]/button')
            self.driver.execute_script("arguments[0].click();", __expand_view_button)
            print("找到expand按鈕，並點擊")
        except:
            print("未找到按鈕")
    
    def goToNextPage(self):
        """
        查找下一頁按鈕元素
        """
        try:
            # 使用XPATH查找按鈕元素，根據按鈕的文本內容查找
            __next_page_button = self.driver.find_element(By.XPATH, '/html/body/main/div[2]/section/section/div[4]/div[2]/div/div/div[2]/button')
            self.driver.execute_script("arguments[0].click();", __next_page_button)
            self.goToStandradView()
            
            print("找到下一頁按鈕，跳至下一頁的standrad view")
        except: 
            self.goToNextYear()
            
            print("未找到下一頁按鈕，將跳至下一年")
    
    def waitForPageLoad(self):
        """
        等待頁面加載完成
        """
        self.driver.implicitly_wait(10)
        
    def goToNextYear(self):
        """
        跳轉到下一年
        """
        self.__current_year += 1 # 更新年份
        self.url = "https://www.mlb.com/stats/pitching/" + str(self.__current_year) # 更新網址
        
        if self.__current_year <= self.__max_year:
            self.driver.get("https://www.mlb.com/stats/pitching/" + str(self.__current_year))
            self.waitForPageLoad()
            self.goToStandradView()
            
            print("跳轉到下一年: " + str(self.__current_year))
        else:
            self.__max_year_flag = False
            print("已經超過最大年分，結束資料擷取")
    
    def goToStandradView(self):
        """
        返回standrad view
        """
        try:
            # 使用XPATH查找按鈕元素，根據按鈕的文本內容查找
            __standard_view_button = self.driver.find_element(By.XPATH, '//*[@id="stats-app-root"]/section/section/div[1]/div[2]/div/div[1]/div/div[1]/button')
            self.driver.execute_script("arguments[0].click();", __standard_view_button) 
            print(f"返回{self.__current_year}年的standrad view")
        except:
            print(f"未找到{self.__current_year}年的standrad按鈕")

if __name__ == "__main__":
    url = "https://www.mlb.com/stats/pitching/2003"
    
    scraper = WebScrapper(url)
    scraper.processing() # 開始處理數據

    scraper.driver.quit()