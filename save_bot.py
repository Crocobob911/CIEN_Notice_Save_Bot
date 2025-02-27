import discord
import aiohttp
import os
import asyncio

TOKEN = ""
SAVE_PATH = "./downloads"
TARGET_EMOJI = "👻"  # 감지할 이모지
REQUIRED_REACTIONS = 1  # 최소 반응 개수
CHANNEL_ID = 1270901061627936851  # 감시할 채널 ID (변경 필요)
MESSAGE_LIMIT = 10  # 검사할 최근 메시지 개수

# 봇 권한 설정
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
client = discord.Client(intents=intents)

# 저장 폴더 생성
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH, exist_ok=True)
    print(f"'{SAVE_PATH}' 폴더가 생성되었습니다.")


async def check_recent_messages():
    """최근 메시지 10개 확인하여 파일 저장"""
    await client.wait_until_ready()  # 봇이 완전히 실행될 때까지 대기
    channel = client.get_channel(CHANNEL_ID)  # 감시할 채널 가져오기

    if not channel:
        print(f"채널 ID {CHANNEL_ID}을 찾을 수 없습니다.")
        await client.close()  # 연결 종료
        return

    print("최근 메시지 검사 시작...")

    messages_checked = 0  # 확인한 메시지 개수 카운트

    async for message in channel.history(limit=MESSAGE_LIMIT):  # 최근 10개 메시지 조회
        messages_checked += 1
        print(f"메시지 확인: {message.id} (보낸 사람: {message.author})")

    if messages_checked == 0:
        print("최근 메시지를 가져오지 못했습니다. 메시지 권한을 확인하세요.")

    async for message in channel.history(limit=MESSAGE_LIMIT):  # 최근 10개 메시지 조회
        print(f"메시지 확인: {message.id} (보낸 사람: {message.author})")

        if message.reactions:
            for reaction in message.reactions:
                print(f"이모지 감지: {reaction.emoji}, 개수: {reaction.count}")

                if (
                    str(reaction.emoji) == TARGET_EMOJI
                    and reaction.count >= REQUIRED_REACTIONS
                ):
                    print(
                        f"목표 이모지 '{TARGET_EMOJI}' 감지됨! (현재 개수: {reaction.count})"
                    )

                    if message.attachments:  # 메시지에 파일이 포함된 경우
                        for attachment in message.attachments:
                            file_url = attachment.url
                            file_name = attachment.filename
                            file_path = os.path.join(SAVE_PATH, file_name)

                            print(f"파일 다운로드 시도: {file_url}")

                            # 이미지 다운로드
                            try:
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(file_url) as resp:
                                        if resp.status == 200:
                                            with open(file_path, "wb") as f:
                                                f.write(await resp.read())
                                            print(f"파일 저장 완료: {file_path}")
                                        else:
                                            print(f"다운로드 실패: HTTP {resp.status}")
                            except Exception as e:
                                print(f"파일 다운로드 중 오류 발생: {e}")
                    else:
                        print("⚠️ 파일이 포함되지 않은 메시지입니다.")
        else:
            print("메시지에 반응이 없습니다.")

    print("검사 완료, 봇 종료 중...")
    await client.close()  # 검사 완료 후 종료


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await check_recent_messages()  # 메시지 검사 실행 후 종료


# 봇 실행
client.run(TOKEN)
