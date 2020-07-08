import requests
import json
import commonUtil

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

