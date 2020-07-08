import commonUtil
import parsingMatchDetail

#매치 정보 파싱
def parsingMatchInfo(matchJson, userId, accountId, apiKey):
    print("매치 정보 파싱")

    matchList = matchJson['matches']
    for matchInfo in matchList:

        print(matchInfo)

        sql = " INSERT INTO L_USER_MATCH (USER_GAME_ID, GAME_MATCH_ID, CHAMPION_ID, QUE_TYPE, SEASON, GAME_DATE, GAME_ROLE, LANE, REG_DATE, UPD_DATE) "
        sql += " VALUES (%s, %s, %s, %s, %s, FROM_UNIXTIME(%s/1000, '%%Y-%%c-%%d %%H:%%i:%%s'), %s, %s, NOW(), NOW()) "
        sql += " ON DUPLICATE KEY "
        sql += " UPDATE "
        sql += " CHAMPION_ID = %s "
        sql += " , QUE_TYPE = %s "
        sql += " , SEASON = %s "
        sql += " , GAME_DATE = FROM_UNIXTIME(%s/1000,  '%%Y-%%c-%%d %%H:%%i:%%s')"
        sql += " , GAME_ROLE = %s "
        sql += " , LANE = %s "
        sql += " , UPD_DATE = NOW() "
        commonUtil.curs.execute(sql, (userId, matchInfo['gameId'], matchInfo['champion'], matchInfo['queue'], matchInfo['season'], matchInfo['timestamp'], matchInfo['role'], matchInfo['lane'], matchInfo['champion'], matchInfo['queue'], matchInfo['season'], matchInfo['timestamp'], matchInfo['role'], matchInfo['lane']))
        commonUtil.conn.commit() 

        parsingMatchDetail.parsingMatchDetail(userId, accountId, matchInfo['gameId'], apiKey)     

