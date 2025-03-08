import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.kintone_fetch_v3 import KintoneDataManager

API_SETTINGS={
    'base_url':'https://qhlwv3k5c4j1.cybozu.com/k/v1/records.json',
    'configs':{
      'config1':{
          'app_no':'14',
          'apitoken':'CCte4r7VzGbpOqRPFSZzJBiEcj6yr4yphOiJVo4M',
          'query':''
      }
    }
}

manager=KintoneDataManager(API_SETTINGS)
manager.fetch_data()

#main_df=manager.get_dataframe('config1_main')
result_df=manager.get_dataframe('config1_df_sub_1')