import getLolUserRank

#랭크 정보 조회
def getRankInfo(userId, userList, apiKey):
    print("랭크 정보 조회")

    for userInfo in userList:
        eucId = userInfo['EUC_ID']
        accountId = userInfo['ACCOUNT_ID']

    getLolUserRank.getLolUserRank(userId, eucId, accountId, apiKey)
        
