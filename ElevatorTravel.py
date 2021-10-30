import pymysql
import time

dbUrl = "elevator-db.cdpfvc1hzmbi.ap-northeast-2.rds.amazonaws.com"
dbPort = 3306
dbId = "admin"
dbPwd = "kongys11"

request_floors = set()
now_floor = 1
min_floor = 0

def GetWebRequest():
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "SELECT CTL_FLOOR_WEB FROM CTL_FLOOR_WEB GROUP BY CTL_FLOOR_WEB"
    cursor.execute(sql)

    for list in cursor:
        request_floors.add(int(list[0]))

    cursor.close()
    con.close()

def GetJetsonRequest():
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "SELECT CTL_FLOOR_JETSON FROM CTL_FLOOR_JETSON GROUP BY CTL_FLOOR_JETSON"
    cursor.execute(sql)

    for list in cursor:
        request_floors.add(int(list[0]))

    cursor.close()
    con.close()

def DeleteWebRequest(floor_):
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "DELETE FROM CTL_FLOOR_WEB WHERE CTL_FLOOR_WEB=%s"
    cursor.execute(sql,floor_)

    cursor.close()
    con.commit()
    con.close()

def DeleteJetsonRequest(floor_):
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "DELETE FROM CTL_FLOOR_JETSON WHERE CTL_FLOOR_JETSON=%s"
    cursor.execute(sql,floor_)

    cursor.close()
    con.commit()
    con.close()

def NowFloorUpdate(now_floor_):
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "UPDATE NOW_FLOOR SET NOW_FLOOR=%s WHERE NOW_FLOOR<100"
    cursor.execute(sql,now_floor_)

    cursor.close()
    con.commit()
    con.close()

def Travel(now_floor_):
    print("travel to %d" %min(request_floors))
    min_floor = min(request_floors)

    if(now_floor_ < min_floor):
        min_floor = min(request_floors)
        while(now_floor_ < min_floor):
            time.sleep(1)
            now_floor_ = now_floor_ + 1
            print("now_floor %d"%now_floor_)
            NowFloorUpdate(now_floor_)

        if len(request_floors) != 0:
            request_floors.remove(min_floor)
            DeleteWebRequest(min_floor)
            DeleteJetsonRequest(min_floor)
            GetWebRequest()

        time.sleep(1)

    elif(now_floor_ == min_floor):
        min_floor = min(request_floors)

        if len(request_floors) != 0:
            request_floors.remove(min_floor)
            DeleteWebRequest(min_floor)
            DeleteJetsonRequest(min_floor)
            GetWebRequest()

        time.sleep(1)

    else:
        min_floor = min(request_floors)
        while (now_floor_ > min_floor):

            time.sleep(1)
            now_floor_ = now_floor_ - 1
            print("now_floor %d" % now_floor_)
            NowFloorUpdate(now_floor_)

        if len(request_floors) != 0:
            request_floors.remove(min_floor)
            DeleteWebRequest(min_floor)
            DeleteJetsonRequest(min_floor)
            GetWebRequest()

        time.sleep(1)


    return now_floor_


while(True):
    print("------------------")
    if len(request_floors) == 0:
        GetWebRequest()
        request_floors.add(1)
    else:
        if now_floor == 1:
            GetJetsonRequest()
        now_floor = Travel(now_floor)
