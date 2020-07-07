import requests
import pymysql
import json
import pandas as pd

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
        r = requests.get(LolApi.apiUrl + "/lol/summoner/v4/summoners/by-name/"+ userId +"?api_key="+ apiKey)        
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

        LolApi.getRankInfo(userList, apiKey)

    def getRankInfo(userList, apiKey):
        print("랭크 정보 조회")

        for userInfo in userList:            
            eucId = userInfo['EUC_ID']        

        LolApi.getLolUserRank(eucId, apiKey)
        
    def getLolUserRank(eucId, apiKey):
        print(eucId)

        ##랭크 정보 조회 API
        r = requests.get(LolApi.apiUrl + "/lol/league/v4/entries/by-summoner/"+ eucId +"?api_key="+ apiKey)        
        rankJson = r.json()

        LolApi.parsingRankInfo(rankJson)

    def parsingRankInfo(rankList):

        for rankInfo in rankList:            
            
            sql = " INSERT INTO L_USER_RANK (USER_GAME_ID, QUE_TYPE, TIER, RANK_LVL, LEAGUE_PT, WINS_CNT, LOSSES_CNT, REG_DATE, UPD_DATE) "
            sql += " VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW()) "
            sql += " ON DUPLICATE KEY "
            sql += " UPDATE "
            sql += " TIER = %s "
            sql += " , RANK_LVL = %s "
            sql += " , LEAGUE_PT = %s "
            sql += " , WINS_CNT = %s "
            sql += " , LOSSES_CNT = %s "
            sql += " , UPD_DATE = NOW() "
            curs.execute(sql, (rankInfo['summonerName'], rankInfo['queueType'], rankInfo['tier'], rankInfo['rank'], rankInfo['leaguePoints'], rankInfo['wins'], rankInfo['losses'], userJson['id'], userJson['accountId'], userJson['puuid']))
            conn.commit()
            
				    #{summonerName}
				   ,#{queueType}
				   ,#{tier}
				   ,#{rank}
				   ,#{leaguePoints}
				   ,#{wins}
				   ,#{losses}
				   ,NOW()
				   ,NOW()
		)


LolApi.createUserHs("고이우")
