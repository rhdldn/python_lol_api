import requests
import parsingRankInfo
import getLstMatchInfo
import commonUtil
        
#랭크 정보 조회 API
def getLolUserRank(userId, eucId, accountId, apiKey):
    print(eucId)

    ##랭크 정보 조회 API
    r = requests.get(commonUtil.apiUrl + "lol/league/v4/entries/by-summoner/"+ eucId +"?api_key="+ apiKey)
    rankJson = r.json()

    parsingRankInfo.parsingRankInfo(rankJson)
    getLstMatchInfo.getLstMatchInfo(rankJson, userId, accountId, apiKey)