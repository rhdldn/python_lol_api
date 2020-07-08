import commonUtil
import requests
import LolMatchService

#랭크 정보 조회
def getRankInfo(userId, userList, apiKey):
    print("랭크 정보 조회")

    for userInfo in userList:
        eucId = userInfo['EUC_ID']
        accountId = userInfo['ACCOUNT_ID']

    getLolUserRank(userId, eucId, accountId, apiKey)

#랭크 정보 조회 API
def getLolUserRank(userId, eucId, accountId, apiKey):
    print(eucId)

    ##랭크 정보 조회 API
    r = requests.get(commonUtil.apiUrl + "lol/league/v4/entries/by-summoner/"+ eucId +"?api_key="+ apiKey)
    rankJson = r.json()

    parsingRankInfo(rankJson)
    LolMatchService.getLstMatchInfo(rankJson, userId, accountId, apiKey)

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