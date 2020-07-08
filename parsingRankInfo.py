import commonUtil

#랭크 정보 파싱
def parsingRankInfo(rankList):
    print("랭크 정보 파싱")

    for rankInfo in rankList:
        
        sql = " INSERT INTO L_USER_RANK (USER_GAME_ID, QUE_TYPE, TIER, RANK_LVL, LEAGUE_PT, WINS_CNT, LOSSES_CNT, REG_DATE, UPD_DATE) "
        sql += " VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW()) "
        sql += " ON DUPLICATE KEY "
        sql += " UPDATE "
        sql += " TIER = %s "
        sql += " , RANK_LVL = %s "
        sql += " , LEAGUE_PT = %s "
        sql += " , WINS_CNT = %s "
        sql += " , LOSSES_CNT = %s "
        sql += " , UPD_DATE = NOW() "
        commonUtil.curs.execute(sql, (rankInfo['summonerName'], rankInfo['queueType'], rankInfo['tier'], rankInfo['rank'], rankInfo['leaguePoints'], rankInfo['wins'], rankInfo['losses'], rankInfo['tier'], rankInfo['rank'], rankInfo['leaguePoints'], rankInfo['wins'], rankInfo['losses']))
        commonUtil.conn.commit()		

