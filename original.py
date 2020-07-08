import requests
import pymysql
import json
import pandas as pd
import datetime

conn = pymysql.connect(host="localhost", user="root", password="dkgk12,,", db="lolapi", charset="utf8")
curs = conn.cursor(pymysql.cursors.DictCursor)

class LolApi:

    apiUrl = "https://kr.api.riotgames.com/"

    def __init__(self, intVal):
        print(intVal)

    #유저 전적 등록/갱신
    def createUserHs(userId):
        
        ##API KEY DB 조회
        sql = " SELECT API_KEY "
        sql += " FROM L_APIKEY "
        curs.execute(sql)
        rows = curs.fetchall()
        print(pd.DataFrame(rows))

        for row in rows:
            apiKey = row['API_KEY']
        
        ##유저 정보 조회 API
        r = requests.get(LolApi.apiUrl + "lol/summoner/v4/summoners/by-name/"+ userId +"?api_key="+ apiKey)
        userJson = r.json()
        print(userJson)
        userJson['userId'] = userId
        userJson['userType'] = ""
        
        sql = " INSERT INTO L_USER (USER_GAME_ID, USER_TYPE, GAME_LVL, EUC_ID, ACCOUNT_ID, PUUID, REG_DATE, UPD_DATE) "
        sql += " VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW()) "
        sql += " ON DUPLICATE KEY "
        sql += " UPDATE "
        sql += " GAME_LVL = %s "
        sql += " , EUC_ID = %s "
        sql += " , ACCOUNT_ID = %s "
        sql += " , PUUID = %s "
        sql += " , UPD_DATE = NOW() "
        curs.execute(sql, (userJson['userId'], userJson['userType'], userJson['summonerLevel'], userJson['id'], userJson['accountId'], userJson['puuid'], userJson['summonerLevel'], userJson['id'], userJson['accountId'], userJson['puuid']))
        conn.commit()

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

        if userId != None :
            sql += " AND USER_GAME_ID = %s "
            curs.execute(sql, userId)
   
        userList = curs.fetchall()
        print(pd.DataFrame(userList))

        LolApi.getRankInfo(userId, userList, apiKey)

    #랭크 정보 조회
    def getRankInfo(userId, userList, apiKey):
        print("랭크 정보 조회")

        for userInfo in userList:
            eucId = userInfo['EUC_ID']
            accountId = userInfo['ACCOUNT_ID']

        LolApi.getLolUserRank(userId, eucId, accountId, apiKey)
        
    #랭크 정보 조회 API
    def getLolUserRank(userId, eucId, accountId, apiKey):
        print(eucId)

        ##랭크 정보 조회 API
        r = requests.get(LolApi.apiUrl + "lol/league/v4/entries/by-summoner/"+ eucId +"?api_key="+ apiKey)
        rankJson = r.json()

        LolApi.parsingRankInfo(rankJson)
        LolApi.getLstMatchInfo(rankJson, userId, accountId, apiKey)

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
            curs.execute(sql, (rankInfo['summonerName'], rankInfo['queueType'], rankInfo['tier'], rankInfo['rank'], rankInfo['leaguePoints'], rankInfo['wins'], rankInfo['losses'], rankInfo['tier'], rankInfo['rank'], rankInfo['leaguePoints'], rankInfo['wins'], rankInfo['losses']))
            conn.commit()		

    #매치 정보 조회
    def getLstMatchInfo(rankList, userId, accountId, apiKey):        
        print("매치 정보 조회")

        ##매치 정보 조회 API
        params = {'beginIndex': 0, 'endIndex': 8}
        r = requests.get(LolApi.apiUrl + "lol/match/v4/matchlists/by-account/"+ accountId +"?api_key="+ apiKey, params)
        matchJson = r.json()

        #print(matchJson)

        LolApi.parsingMatchInfo(matchJson, userId, accountId, apiKey)

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
            curs.execute(sql, (userId, matchInfo['gameId'], matchInfo['champion'], matchInfo['queue'], matchInfo['season'], matchInfo['timestamp'], matchInfo['role'], matchInfo['lane'], matchInfo['champion'], matchInfo['queue'], matchInfo['season'], matchInfo['timestamp'], matchInfo['role'], matchInfo['lane']))
            conn.commit() 

            LolApi.parsingMatchDetail(userId, accountId, matchInfo['gameId'], apiKey)     

    #매치 상세 정보 파싱
    def parsingMatchDetail(userId, accountId, gameId, apiKey):
        print("매치 상세 정보 파싱")

        ##매치 상세 정보 조회 API
        r = requests.get(LolApi.apiUrl + "lol/match/v4/matches/"+ str(gameId) +"?api_key="+ apiKey)
        matchDtlJson = r.json()

        if matchDtlJson['participantIdentities'] != None :
            matchUserList = matchDtlJson['participantIdentities']

        for matchUserInfo in matchUserList :
            userInfo = matchUserInfo['player']
            userAccountId = userInfo['accountId']

            if accountId == userAccountId :
                participantId = matchUserInfo['participantId']

        if matchDtlJson['participants'] != None :
            matchUserDtlList = matchDtlJson['participants']
        
        for matchUserDtlInfo in matchUserDtlList :
            igParticipantId = matchUserDtlInfo['participantId']

            if participantId == igParticipantId :
                matchUserSts = matchUserDtlInfo['stats']

                sql = " UPDATE L_USER_MATCH "
                sql += " SET KILLS = %s "
                sql += " , DEATHS = %s "
                sql += " , ASSISTS = %s "
                sql += " , WIN_FLAG = %s "
                sql += " , UPD_DATE = NOW() "
                sql += " WHERE USER_GAME_ID = %s "
                sql += " AND GAME_MATCH_ID = %s "
                curs.execute(sql, (matchUserSts['kills'], matchUserSts['deaths'], matchUserSts['assists'], matchUserSts['win'], userId, gameId))
                conn.commit() 

                print("적재성공")

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
            curs.execute(sql, (userId, userType))
        elif selFlag_1:
            curs.execute(sql, userId)
        elif selFlag_2:
            curs.execute(sql, userType)
        else:
            curs.execute(sql)
        
        userList = curs.fetchall()
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

            curs.execute(sql, ("RANKED_SOLO_5x5", userId))        
            soloRankInfo = curs.fetchall()

            #자유 랭크 정보 조회
            curs.execute(sql, ("RANKED_FLEX_SR", userId))        
            freeRankInfo = curs.fetchall()

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

            curs.execute(sql, userId)        
            lastGameList = curs.fetchall()            

            userJson = json.dumps(userInfo, default=LolApi.json_default)
            soloRankJson = json.dumps(soloRankInfo, default=LolApi.json_default)
            freeRankJson = json.dumps(freeRankInfo, default=LolApi.json_default)
            lastGameJson = json.dumps(lastGameList, default=LolApi.json_default)

            retJson["userMap"] = userJson
            retJson["soloRankMap"] = soloRankJson
            retJson["freeRankMap"] = freeRankJson
            retJson["lastGameList"] = lastGameJson    

            retList.append(retJson)

    def modifyApiKey(apiKey):
        
        if apiKey != None and apiKey != '':

            sql = " UPDATE L_APIKEY "
            sql += " SET API_KEY = %s "
            sql += " , REG_DATE = NOW() "
            curs.execute(sql, apiKey)
            conn.commit() 

            print("APIKEY 갱신 성공")

    def json_default(value): 
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d') 
        raise TypeError('not JSON serializable')