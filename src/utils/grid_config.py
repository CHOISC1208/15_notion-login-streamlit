from st_aggrid import GridOptionsBuilder, JsCode

def configure_grid(df):
    """AgGridの設定を構成する関数"""
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # 1. 並び替え機能
    gb.configure_default_column(sortable=True)
    
    # 2. フィルタリング機能
    gb.configure_default_column(filterable=True)
    
    # 3. グループ化機能
    gb.configure_default_column(
        groupable=True,
        enableRowGroup=True,
        aggFunc='sum'
    )
    
    # 4. ピボットテーブル機能
    gb.configure_default_column(
        enablePivot=True,
        enableValue=True
    )
    
    # 5. エクスポート機能（CSVとExcel）
    gb.configure_grid_options(
        enableRangeSelection=True,
        domLayout='normal',
        suppressExcelExport=False,
        suppressCsvExport=True
    )
    
    # 6. カラムの表示/非表示切り替え
    gb.configure_side_bar(
        defaultToolPanel='columns',
        columns_panel=True
    )
    
    # 7. 条件付きフォーマット
    # 例: 数値カラムに対して条件付きフォーマットを適用
    #numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    #for col in numeric_cols:
    #    cellStyle_jscode = JsCode("""
    #    function(params) {
    #        if (params.value > 30) {
    #            return { 'color': 'white', 'backgroundColor': 'green' };
    #        } else if (params.value < 10) {
    #            return { 'color': 'white', 'backgroundColor': 'red' };
    #        } else {
    #            return { 'color': 'black', 'backgroundColor': 'lightblue' };
    #        }
    #    }
    #    """)
    #    gb.configure_column(col, cellStyle=cellStyle_jscode)
    
    # その他の便利な設定
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_selection('multiple', use_checkbox=False)
    
    return gb.build()
