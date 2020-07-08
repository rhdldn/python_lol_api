import requests
import json
import commonUtil

#매치 정보 조회
def getLstMatchInfo(rankList, userId, accountId, apiKey):        
    print("매치 정보 조회")

    ##매치 정보 조회 API
    params = {'beginIndex': 0, 'endIndex': 8}
    r = requests.get(commonUtil.apiUrl + "lol/match/v4/matchlists/by-account/"+ accountId +"?api_key="+ apiKey, params)
    matchJson = r.json()

    #print(matchJson)

    parsingMatchInfo(matchJson, userId, accountId, apiKey)

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

        parsingMatchDetail(userId, accountId, matchInfo['gameId'], apiKey)     

#매치 상세 정보 파싱
def parsingMatchDetail(userId, accountId, gameId, apiKey):
    print("매치 상세 정보 파싱")

    ##매치 상세 정보 조회 API
    r = requests.get(commonUtil.apiUrl + "lol/match/v4/matches/"+ str(gameId) +"?api_key="+ apiKey)
    matchDtlJson = r.json()
    print(matchDtlJson)

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
            commonUtil.curs.execute(sql, (matchUserSts['kills'], matchUserSts['deaths'], matchUserSts['assists'], matchUserSts['win'], userId, gameId))
            commonUtil.conn.commit() 

            print("적재성공")