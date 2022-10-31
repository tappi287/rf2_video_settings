import logging

from rf2settings.chat import youtube


def test_yt_chat():
    channel_id = youtube.get_channel_id_by_username('Tappi287')
    live_stream = youtube.get_live_stream_by_channel_id(channel_id)
    chat_messages = youtube.get_chat_messages(live_stream=live_stream)
    print(chat_messages)


if __name__ == '__main__':
    test_yt_chat()
