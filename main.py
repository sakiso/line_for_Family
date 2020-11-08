from datetime import date
from datetime import timedelta
import requests
from bs4 import BeautifulSoup

def line_bot(event, context):

    #今日と明日のdate取得
    #アイオワ州リージョン（日本より15時間遅い）なので
    #いずれも+1する
    kyou = date.today()  + timedelta(days=1)
    asu  = date.today()  + timedelta(days=2)

    #今日のdayと曜日
    d = kyou.day
    youbi = date.weekday(kyou)
    #明日のdayと曜日
    d2 = asu.day
    youbi2 = date.weekday(asu)

    #今日が第n○曜日かを出す
    #d<=7:第1,8<=d<=14:第2,15<=d<=21:第3,22<=d<=28:第4,29<=d:第5
    if d <= 7:
        th = 1
    if 8 <= d and d <= 14:
        th = 2
    if 15 <= d and d <= 21:
        th = 3
    if 22 <= d <= 28:
        th = 4
    if 29 <= d:
        th = 5

    #明日が第n○曜日かを出す
    #d<=7:第1,8<=d<=14:第2,15<=d<=21:第3,22<=d<=28:第4,29<=d:第5
    if d2 <= 7:
        th2 = 1
    if 8 <= d2 and d2 <= 14:
        th2 = 2
    if 15 <= d2 and d2 <= 21:
        th2 = 3
    if 22 <= d2 <= 28:
        th2 = 4
    if 29 <= d2:
        th2 = 5

    #所沢のゴミカレンダー
    #月 :燃やせるゴミ
    #火1:破砕
    #火2:びん缶
    #水 :プラ
    #木 :燃やせるゴミ
    #金1:小型家電/古着/古布
    #金2:ペットボトル
    #金3:雑誌/段ボール
    #火金の5週目以降と三が日は回収なし

    gomi_table=[ 
                ["月曜日","火曜日","水曜日","木曜日","金曜日","土曜日","日曜日"],
                ["燃やせるゴミ","破砕ゴミ","プラゴミ","燃やせるゴミ","小型家電・古着","*ゴミ収集なし","*ゴミ収集なし"],
                ["燃やせるゴミ","ビン・カン","プラゴミ","燃やせるゴミ","ペットボトル","*ゴミ収集なし","*ゴミ収集なし"],
                ["燃やせるゴミ","破砕ゴミ","プラゴミ","燃やせるゴミ","雑誌","*ゴミ収集なし","*ゴミ収集なし"],
                ["燃やせるゴミ","ビン・カン","プラゴミ","燃やせるゴミ","ペットボトル","*ゴミ収集なし","*ゴミ収集なし"],
                ["燃やせるゴミ","*ゴミ収集なし","プラゴミ","燃やせるゴミ","*ゴミ収集なし","*ゴミ収集なし","*ゴミ収集なし"]
                ]

    #結果メッセージの保存
    gomi_text = (("\n【ゴミ収集情報】\n")
    +            ("今日の回収 : " + gomi_table[th][youbi] + "\n")
    +            ("明日の回収 : " + gomi_table[th2][youbi2] + "\n")
             )

    #天気セクション
    #tenki.jpの目的の地域のページのURL（今回は所沢）
    url = 'https://tenki.jp/forecast/3/14/4310/11208/'
    #HTTPリクエスト
    r = requests.get(url)

    #プロキシ環境下の場合は以下を記述
    """
    proxies = {
        "http":"http://proxy.xxx.xxx.xxx:8080",
        "https":"http://proxy.xxx.xxx.xxx:8080"
    }
    r = requests.get(url, proxies=proxies)
    """
    #HTMLの解析
    bsObj = BeautifulSoup(r.content, "html.parser")
    #今日の天気を取得
    today = bsObj.find(class_="today-weather")
    weather = today.p.string
    #気温情報のまとまり
    temp=today.div.find(class_="date-value-wrap")
    #気温の取得
    temp=temp.find_all("dd")
    temp_max = temp[0].span.string #最高気温
    temp_max_diff=temp[1].string #最高気温の前日比
    temp_min = temp[2].span.string #最低気温
    temp_min_diff=temp[3].string #最低気温の前日比

    #結果メッセージの保存
    weather_text = (("\n【所沢の天気】\n")
    +              ("天気:{}\n".format(weather))
    +              ("最高気温:{} 前日比{}\n".format(temp_max,temp_max_diff))
    +              ("最低気温:{} 前日比{}".format(temp_min,temp_min_diff))
                   )

    #line送信
    #line_APIのURLとtokenを設定
    url = "https://notify-api.line.me/api/notify"
    access_token = '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
    #トークンは公開用にマスキングしている
    headers = {'Authorization': 'Bearer ' + access_token}

    #send message(日付)
    today_text = ("\n今日は" + str(kyou.year) 
    + "年"   + str(kyou.month) 
    + "月"   + str(kyou.day) 
    + "日(" + gomi_table[0][youbi] + ")")
    message = today_text
    payload = {'message': message}
    r = requests.post(url, headers=headers, params=payload,)

    #send message(天気)
    message = weather_text
    payload = {'message': message}
    r = requests.post(url, headers=headers, params=payload,)
    
    #send message(ゴミ)
    message = gomi_text
    payload = {'message': message}
    r = requests.post(url, headers=headers, params=payload,)
