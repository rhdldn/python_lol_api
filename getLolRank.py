import json
import pandas as pd
import commonUtil

#랭크 정보 조회
def getLolRank(userId, userType):

    selFlag_1 = False
    selFlag_2 = False
    retList = []

    sql = " SELECT USER_GAME_ID "
    sql += " , USER_TYPE "
    sql += " , GAME_LVL "
    sql += " , EUC_ID "
    sql += " , ACCOUNT_ID "
    sql += " , PUUID "
    sql += " , REG_DATE "
    sql += " , UPD_DATE "
    sql += " FROM L_USER "
    sql += " WHERE 1=1 "

    if userId != None and userId != '':
        sql += " AND USER_GAME_ID = %s "
        selFlag_1 = True
    
    if userType != None and userType != '':
        sql += " AND USER_TYPE = %s "
        selFlag_2 = True

    if selFlag_1 and selFlag_2:
        commonUtil.curs.execute(sql, (userId, userType))
    elif selFlag_1:
        commonUtil.curs.execute(sql, userId)
    elif selFlag_2:
        commonUtil.curs.execute(sql, userType)
    else:
        commonUtil.curs.execute(sql)
    
    userList = commonUtil.curs.fetchall()
    print(pd.DataFrame(userList))

    for userInfo in userList:
        retJson = {}
        userId = userInfo['USER_GAME_ID']

        #솔로 랭크 정보 조회
        sql = " SELECT USER_GAME_ID "
        sql += " , QUE_TYPE "
        sql += " , TIER "
        sql += " , LOWER(TIER) AS TIER_IMG "
        sql += " , RANK_LVL "
        sql += " , LEAGUE_PT "
        sql += " , WINS_CNT "
        sql += " , LOSSES_CNT "
        sql += " , REG_DATE "
        sql += " , UPD_DATE "
        sql += " , TIMESTAMPDIFF(MINUTE, UPD_DATE, NOW()) AS DIFF_MIN "
        sql += " , TIMESTAMPDIFF(HOUR, UPD_DATE, NOW()) AS DIFF_HOUR "
        sql += " , TIMESTAMPDIFF(DAY, UPD_DATE, NOW()) AS DIFF_DAY "
        sql += " FROM L_USER_RANK "
        sql += " WHERE QUE_TYPE = %s "
        sql += " AND USER_GAME_ID = %s "

        commonUtil.curs.execute(sql, ("RANKED_SOLO_5x5", userId))        
        soloRankInfo = commonUtil.curs.fetchall()

        #자유 랭크 정보 조회
        commonUtil.curs.execute(sql, ("RANKED_FLEX_SR", userId))        
        freeRankInfo = commonUtil.curs.fetchall()

        #최근 10게임 정보 조회
        sql = " SELECT USER_GAME_ID "
        sql += " , GAME_MATCH_ID "
        sql += " , CHAMPION_ID "
        sql += " , CHAMPION_ENG_NAME "
        sql += " , CHAMPION_KOR_NAME "
        sql += " , QUE_TYPE "
        sql += " , SEASON "
        sql += " , GAME_DATE "
        sql += " , GAME_ROLE "
        sql += " , LANE "
        sql += " , CASE WHEN GAME_ROLE_PARSE = 'support' THEN GAME_ROLE_PARSE ELSE LANE_PARSE END AS POSITION_IMG "
        sql += " , KILLS "
        sql += " , DEATHS "
        sql += " , ASSISTS "
        sql += " , WIN_FLAG "
        sql += " , REG_DATE "
        sql += " , UPD_DATE "
        sql += " FROM ( "
        sql += "   SELECT A.USER_GAME_ID "
        sql += "   , A.GAME_MATCH_ID "
        sql += "   , A.CHAMPION_ID "
        sql += "   , B.CHAMPION_ENG_NAME "
        sql += "   , B.CHAMPION_KOR_NAME "
        sql += "   , A.QUE_TYPE "
        sql += "   , A.SEASON "
        sql += "   , A.GAME_DATE "
        sql += "   , A.GAME_ROLE "            
        sql += "   , A.LANE "
        sql += "   , IF(A.GAME_ROLE = 'DUO_SUPPORT', 'support', 'support') as GAME_ROLE_PARSE "
        sql += "   , CASE WHEN A.LANE = 'BOTTOM' THEN 'AD' WHEN A.LANE = 'TOP' THEN 'top' WHEN A.LANE = 'JUNGLE' THEN 'jg' WHEN A.LANE = 'MID' THEN 'mid' ELSE '' END AS LANE_PARSE "
        sql += "   , A.KILLS "
        sql += "   , A.DEATHS "
        sql += "   , A.ASSISTS "
        sql += "   , A.WIN_FLAG "
        sql += "   , A.REG_DATE "
        sql += "   , A.UPD_DATE "
        sql += "   FROM L_USER_MATCH A, L_CHAMPION B "
        sql += "   WHERE A.CHAMPION_ID = B.CHAMPION_ID "
        sql += "   AND A.USER_GAME_ID = %s "
        sql += "   ORDER BY A.REG_DATE DESC "
        sql += "   LIMIT 8) A "

        commonUtil.curs.execute(sql, userId)        
        lastGameList = commonUtil.curs.fetchall()            

        userJson = json.dumps(userInfo, default=LolApi.json_default)
        soloRankJson = json.dumps(soloRankInfo, default=LolApi.json_default)
        freeRankJson = json.dumps(freeRankInfo, default=LolApi.json_default)
        lastGameJson = json.dumps(lastGameList, default=LolApi.json_default)

        retJson["userMap"] = userJson
        retJson["soloRankMap"] = soloRankJson
        retJson["freeRankMap"] = freeRankJson
        retJson["lastGameList"] = lastGameJson    

        retList.append(retJson)