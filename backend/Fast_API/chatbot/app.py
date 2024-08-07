import os
import re
import requests
import math
import json
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from typing import List
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .Chatbot import Chatbot, DiarySummarizeChatbot, SummarizeChatbot
from packages.dependencies import decode_jwt
from models import ChatRequest, TestMod
import httpx
from pprint import pprint
from .HappyreKoBert import HappyreKoBert
from .Personas import PERSONAS
from .kobert_tokenizer import KoBERTTokenizer

# ----------------------------전역 변수-------------------------------
router = APIRouter()
load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')  # OPEN AI 키

user_session = {}    # 유저 챗봇 세션

user_emotion_russel = {}    # 유저 러셀 좌표 - {유저 : {문장 : 좌표}}

user_message = {}    # 유저 메시지 저장  -  {유저 : [{문장 :"문장", "speaker":"user", "audioKey":"ddd.wav"}]}

KOBERT_CHECKPOINT_X = os.environ.get('KOBERT_CHECKPOINT_X')
KOBERT_CHECKPOINT_Y = os.environ.get('KOBERT_CHECKPOINT_Y')

print(KOBERT_CHECKPOINT_X)
print(KOBERT_CHECKPOINT_Y)

kobert_x = HappyreKoBert(KOBERT_CHECKPOINT_X)
kobert_y = HappyreKoBert(KOBERT_CHECKPOINT_Y)

# 현재 경로와 BASE_DIR 경로
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(current_dir, ".."))

SPRING_MESSAGE_POST_URL=os.environ.get("SPRING_MESSAGE_POST_URL")
SPRING_KEYWORD_SUMMARY_URL = os.environ.get("SPRING_KEYWORD_SUMMARY_URL")


personas = PERSONAS


# -------------------------------사용자 정의 함수-------------------------------

async def emotion_analysis(text : str):
    return (kobert_x(text), kobert_y(text))

async def emotion_tagging(user_id: str, text: str):
    '''
    user_emotion_russel 딕셔너리에 문장과 추출된 러셀 감정 좌표를 매칭
    
    - user_emotion_russel 구조
    {
    "user_id": {
        "text": "(0,0)"
    }
    '''
    print("Emotion tagging start")
    trigger = False
    
    russel_coord = await emotion_analysis(text)
    
    if user_id not in user_emotion_russel:
        user_emotion_russel[user_id] = {}
        
    if russel_coord[0] < -0.8:
        trigger = True
        
    user_emotion_russel[user_id][text] = russel_coord
    print("Emotion tagging End")
    return trigger


def message_session_update(user_id:str, text:str, speaker:str, audio:str="None"):
    '''
    유저의 메세지 세션에 유저의 대화와 챗봇의 대화를 업데이트
    '''
    print("Message session update start")
    if user_id not in user_message:
        user_message[user_id] = []
    user_message[user_id].append({
        "content":text,
        "speaker":speaker,
        "audioKey":audio
    })
    print(f"Message session update End")
    
# ----------------------------------라우팅 함수--------------------------------------------

# POST 요청으로 chabot 사용
# chatbot 처리와 함께 딕셔너리 형태로 감정 저장
@router.post('/')
async def chatbot(requestforP:Request, request: ChatRequest, user_id: str = Depends(decode_jwt)):
    '''
    유저의 챗봇 세션이 없는 경우 챗봇 세션 생성
    들어온 텍스트를 OpenAI에 보내고 유저 메세지 세션 업데이트
    응답온 텍스트를 메세지 세션에 업데이트하고 반환
    '''
    print("Chatbot Post Start")
    
    # front에서 header에 담긴 페르소나 정보 받기
    persona_number = int(requestforP.headers["persona"])
    # persona_number = 2
    
    if user_id not in user_session:
        # Chatbot 생성시에 persona를 선택
        user_session[user_id] = Chatbot(api_key=api_key,persona=personas[persona_number])
        
    api_instance = user_session[user_id]
    user_input = request.user_input
    audio = request.audio
    
    if request.request == "user":
        message_session_update(user_id, user_input, "user", audio)
    elif request.request == "chatbot":
        message_session_update(user_id, user_input, "starter", audio)
    
    
    response = api_instance.generateResponse(user_input)

    trigger = False
    if request.request == "user":
        trigger = await emotion_tagging(user_id, user_input)
    
    print(f"response : {response}")
    print("---------------------------------------")
    print(f"user session: {user_session}")
    print("---------------------------------------")
    pprint(f"user message: {user_message}")
    
    content = {
        "content":response,
        "trigger":trigger
    }
    print("Chatbot Post End")
    return JSONResponse(content=content, status_code=200)

# spring 메세지 저장 요청 함수
@router.post("/post_message")
async def post_message_request(request:Request):
    '''
    Spring 서버로 메세지 세션 저장 요청
    
    '''
    print("--------------------------------------------------메세지 포스트 시작--------------------------------------------------------------")
    print(f"{SPRING_MESSAGE_POST_URL}")
    
    header = request.headers
    token = header["authorization"].split(" ")[-1]
    user_id = decode_jwt(token)
    message_item = []
    try:
        for idx, data in enumerate(user_message[user_id]):
            data = user_message[user_id][idx]
            russel_coord = user_emotion_russel[user_id]
            data["sequence"] = idx+1
            if data["speaker"] == "starter":
                continue
            elif data["speaker"] == "user":
                if data["content"] in russel_coord:
                    data["russelX"], data["russelY"] = russel_coord[data["content"]]
                    
                else:
                    data["russelX"] = None
                    data["russelY"] = None
            else:
                data["russelX"] = None
                data["russelY"] = None
            message_item.append(data)
        print("메세지 만들기 완료")
        try:
            new_headers = {
                "authorization": header["authorization"],
                "content-type": "application/json"
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(SPRING_MESSAGE_POST_URL, json=message_item, headers=new_headers)
                print(f"response : {response}")
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail=f"Error: {response.text}")
        except Exception as e:
            print(f"Message Sending Error : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
    except Exception as e:
        print(f"Message Posting Error : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    print("----------------------------------------------------메시지 포스트 완료 -------------------------------------------")
    
    return user_message
# 세션에서 삭제
@router.delete('/')
async def session_delete(request:Request):
    print("# ------------------------------------------------섹션 삭제 시작 --------------------------------------------------")
    header = request.headers["authorization"]
    user_id = decode_jwt(header.split(" ")[-1])
    
    new_header = {
        "authorization": header,
        "content-type": "application/json"
    }
    
    chatbot_instance = user_session[user_id]
    prompt = '지금까지의 대화에서 전체적인 대화에서 느껴지는 감정과 긍정적인 감정이 느껴지는 키워드 0~3개와 부정적인 키워드가 느껴지는 키워드 0~3개를 뽑아 유저 메세지와 함께 보여줘. 응답 결과는 반드시 요약 결과만을 리스트 안에 1개 이상의 딕셔너리가 있는 형태로 , 딕셔너리는 키값으로 "keyword","summary","message"를 갖고, "keyword"에는 요약된 1 ~ 2단어짜리 키워드를, "summary"에는 키워드를 뽑은 유저 메세지를 사건 중심으로 짧게 요약한 문장을, 마지막으로 "message"에는 사용한 유저의 메시지를 매칭시켜줘. 만약 요약할 내용이 없다면 "None"으로 응답해줘.'
    
    response = chatbot_instance.generateResponse(prompt)
    print(f"SPRING_KEYWORD_SUMMARY_URL : {SPRING_KEYWORD_SUMMARY_URL}")
    
    try:
        result = json.loads(response.strip())
        file = response.replace("`", "").strip()
        temp = file.replace("json","").strip()
        result = json.loads(temp)
        
        summary_list = []
        for idx, data in enumerate(result):
            print(f"data : \n {data}")
            print(f"user emotion russel : \n {user_emotion_russel[user_id]}")
            if data["message"] not in user_emotion_russel[user_id]:
                continue
            data["russelX"], data["russelY"] = user_emotion_russel[user_id][data["message"]]
            data["sequence"] = idx+1

            del data["message"]
            summary_list.append(data)
            print(f"data after russel: \n {data}")
        print(f"Summary List : {summary_list}")
    except Exception as e:
            print(f"Error while summarize : {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SPRING_KEYWORD_SUMMARY_URL, json=summary_list, headers=new_header)
            print(f"returned response : {response}")
            
            if user_id in user_session:
                del user_session[user_id]
                print('User Session Deleted')

            if user_id in user_emotion_russel:
                del user_emotion_russel[user_id]
                print('User Emotion Russel Deleted')
                
            if user_id in user_message:
                del user_message[user_id]
                print("User Message Deleted")
            print(f'''
                    삭제 확인
                    User Session : {user_session}
                    ----------------------------------------
                    User Emotion Russel : {user_emotion_russel}
                    ---------------------------------------
                    User Message : {user_message}
                ''')
            print("------------------------------------------------ 섹션 삭제 완료 ----------------------------------------")
            return {"content":response.status_code}
    except Exception as e:
        print(f"Error While Summary Posting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))