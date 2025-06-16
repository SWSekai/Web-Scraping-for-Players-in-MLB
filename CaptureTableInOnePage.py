import requests
import pandas as pd
import os

from bs4 import BeautifulSoup

def getTableData(soup, include_players_name = True):
    """_
        若已經獲取到表格標頭，則不再獲取
    """
    table = []
    headers = []
    headers_text = []
    players = []
    players_text = []
    players_data = []
    players_data_text = []
    
    table = soup.find('table')
    
    if table:
        try:
            # 標題
            headers = table.find_all('abbr') # class_ = 'bui-text cellheader bui-text'
            headers_text = [header.get_text(strip=True) for header in headers]

            # 去除連續重複值
            deduped_headers = [headers_text[0]] if headers_text else []
            for i in range(1, len(headers_text)):
                if headers_text[i] != headers_text[i - 1]:
                    deduped_headers.append(headers_text[i])
                    
            column_num = len(deduped_headers)
            
            # 球員
            players = table.find_all('span', class_ = 'short-IiSPVSQp')
            players_text = [player.get_text(strip=True) for player in players]
            
            row_num = len(players)+1
            
            # 球員資料
            players_data = table.find_all('td')
            players_data_text = [player.get_text(strip=True) for player in players_data]
            
            # 將球員資料轉換為二維列表
            if include_players_name:
                players_data_two_dim = [[players_text[i]] + players_data_text[i*(column_num-1):(i+1)*(column_num-1)] for i in range(row_num-1)]
            else:
                players_data_two_dim = [players_data_text[i*(column_num-1):(i+1)*(column_num-1)] for i in range(row_num-1)]
            
                return pd.DataFrame(players_data_two_dim, columns=deduped_headers)
        except Exception as e:
            print(f"處理表格數據時出現錯誤: {e}")
            
            return pd.DataFrame()
    else:
        print("未找到表格")
        
        return pd.DataFrame()

def storeInCSV(df, fileName, mode='w'):
    """
        將DataFrame儲存到CSV檔案。
        mode='a' 表示附加寫入, mode='w' 表示覆蓋寫入。
    """
    if not os.path.exists(fileName) and mode == 'a':
        mode = 'w'
        print(f"檔案 {fileName} 不存在，將使用覆蓋模式寫入。")
    
    df.to_csv(fileName, mode= mode, header= not(mode=='a' and os.path.exists(fileName)), index=False) # 若檔案不存在，則寫入標題
    
    print(f"數據已儲存到 {fileName}，模式: {mode}")

if __name__ == "__main__":
    url = "https://www.mlb.com/stats/pitching/2003"
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    print(soup)
    fileName = "players_stats.csv"
    
    table_data = getTableData(soup)
    
    storeInCSV(table_data, fileName= fileName, mode = 'a')
    print("資料覆蓋寫入完成。")
    storeInCSV(table_data, fileName= fileName, mode = 'w')
    print("資料附加寫入完成。")