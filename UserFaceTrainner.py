import pymysql
import os
import cv2
import numpy as np

dbUrl = "url"
dbPort = 3306
dbId = "id"
dbPwd = "pwd"


#전체 칼럼 수 구하기
def getColumnCount():
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "SELECT COUNT(*) FROM INFO"
    cursor.execute(sql)

    for list in cursor:
        count = list[0]

    cursor.close()
    con.close()

    return count

#추가된 로우 데이터 받아오기
def getResentRow():
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "SELECT UNAME,FLOOR,FILENAME FROM INFO ORDER BY REGDATE DESC LIMIT 1"
    cursor.execute(sql)

    for list in cursor:
        uname_ = list[0]
        floor_ = list[1]
        filename_ = list[2]

    cursor.close()
    con.close()

    return uname_,floor_,filename_

#얼굴 자르기
def faceScrap(uname_,floor_,filename_):
    cascade_path = 'C:/Users/song4/AppData/Local/Programs/Python/Python37-32/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml'
    face_casecade = cv2.CascadeClassifier(cascade_path)

    def face_extractor(img):
        img
        faces = face_casecade.detectMultiScale(img,1.3,5)

        if faces is():
            return None
        for(x,y,w,h) in faces:
            cropped_face = img[y:y+h, x:x+w]
        return cropped_face

    def createFolder(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error : Creating directory.' + directory)

    savePath = 'C:/Users/song4/faceImage/'
    createFolder(os.path.join(savePath,str(floor_)))

    filePass = "C:/workspace/eclipse-work/.metadata/.plugins/org.eclipse.wst.server.core/tmp1/wtpwebapps/ElevatorPrj/upload/"
    videoFile = os.path.join(filePass,filename_)
    cap = cv2.VideoCapture(videoFile)
    count = 0

    if filename_.endswith("mp4") or filename_.endswith("mov") or filename_.endswith("avi") or filename_.endswith("wmv") or filename_.endswith("gif"):
        while True:
            ret, frame = cap.read()
            if face_extractor(frame) is not None:
                count+=1
                face = cv2.resize(face_extractor(frame),(200,200))

                file_name_pass = 'C:/Users/song4/faceImage/'+str(floor_)+'/'+str(uname_)+str(count)+'.jpg'
                cv2.imwrite(file_name_pass, face)
            else:
                print("face not founded")
                pass

            if cv2.waitKey(1) == 13 or count == 5:
                print("Scrap End")
                break

#학습 파일 생성
def faceTrain():
    cascade_path = 'C:/Users/song4/AppData/Local/Programs/Python/Python37-32/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml'
    face_casecade = cv2.CascadeClassifier(cascade_path)
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    Face_ID = -1
    pev_person_name = ""
    y_ID = []
    x_train = []

    Face_Image = 'C:/Users/song4/faceImage'
    print(Face_Image)

    for root, dirs, files in os.walk(Face_Image):
        for file in files:
            if file.endswith("jpeg") or file.endswith("jpg") or file.endswith("png"):
                path = os.path.join(root, file)
                person_name = os.path.basename(root)

                if pev_person_name != person_name:
                    Face_ID = Face_ID + 1
                    pev_person_name = person_name

                img = cv2.imread(path)
                gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_casecade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)

                print(Face_ID, faces)

                for (x, y, w, h) in faces:
                    roi = gray_image[y:y + h, x:x + w]
                    x_train.append(roi)
                    y_ID.append(Face_ID)

                    recognizer.train(x_train, np.array(y_ID))
                    recognizer.save("C:/workspace/sftp/face_trainner.yml")
    print("Train End")

#목록 리스트 저장
def saveLabel():
    floorList = os.listdir('C:/Users/song4/faceImage')
    floorList = np.array(floorList)

    path = 'C:/workspace/sftp/'
    npyName = 'floorList.npy'

    np.save(path+npyName,floorList)

    return

def triggerOn():
    con = pymysql.connect(host=dbUrl, port=dbPort, user=dbId, password=dbPwd, db="elevator")
    cursor = con.cursor()
    sql = "UPDATE TRIG SET FLAG='1' WHERE FLAG='0'"
    cursor.execute(sql)

    cursor.close()
    con.commit()
    con.close()

#조건 초기화
prevCount = getColumnCount()
nextCount = getColumnCount()

while(1):
    while(1):
        if(prevCount!=nextCount):
            print("Learning Start")
            resentColumn = getResentRow()
            uname = resentColumn[0]
            floor = resentColumn[1]
            filename = resentColumn[2]

            faceScrap(uname,floor,filename)

            filePass = "C:/workspace/eclipse-work/.metadata/.plugins/org.eclipse.wst.server.core/tmp1/wtpwebapps/ElevatorPrj/upload/"
            videoFile = os.path.join(filePass, filename)
            os.remove(videoFile)

            faceTrain()
            saveLabel()
            triggerOn()
        else:
            pass
        prevCount = nextCount
        nextCount = getColumnCount()



