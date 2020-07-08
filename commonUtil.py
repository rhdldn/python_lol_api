import pymysql
import datetime

conn = pymysql.connect(host="localhost", user="root", password="dkgk12,,", db="lolapi", charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)
apiUrl = "https://kr.api.riotgames.com/"

def json_default(value): 
    if isinstance(value, datetime.date): 
        return value.strftime('%Y-%m-%d') 
    raise TypeError('not JSON serializable')