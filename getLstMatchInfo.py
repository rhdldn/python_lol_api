import requests
import json
import parsingMatchInfo
import commonUtil

#매치 정보 조회
def getLstMatchInfo(rankList, userId, accountId, apiKey):        
    print("매치 정보 조회")

    ##매치 정보 조회 API
    params = {'beginIndex': 0, 'endIndex': 8}
    r = requests.get(commonUtil.apiUrl + "lol/match/v4/matchlists/by-account/"+ accountId +"?api_key="+ apiKey, params)
    matchJson = r.json()

    #print(matchJson)

    parsingMatchInfo.parsingMatchInfo(matchJson, userId, accountId, apiKey)

