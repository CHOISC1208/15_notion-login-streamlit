import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.kintone_fetch_v3 import KintoneDataManager

API_SETTINGS={
    'base_url':'https://qhlwv3k5c4j1.cybozu.com/k/v1/records.json',
    'configs':{
      'config1':{
          'app_no':'31',
          'apitoken':os.getenv('31_query'),
          'query':''
      }
    }
}

manager=KintoneDataManager(API_SETTINGS)
manager.fetch_data()

result_df=manager.get_dataframe('config1_main')