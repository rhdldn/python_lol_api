import commonUtil

def modifyApiKey(apiKey):
    
    if apiKey != None and apiKey != '':

        sql = " UPDATE L_APIKEY "
        sql += " SET API_KEY = %s "
        sql += " , REG_DATE = NOW() "
        commonUtil.curs.execute(sql, apiKey)
        commonUtil.conn.commit() 

        print("APIKEY 갱신 성공")

