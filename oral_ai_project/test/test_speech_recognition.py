from speech_recognition import SpeechRecognition

def test_recognition():
    # 创建语音识别实例
    recognizer = SpeechRecognition()
    
    # 测试音频文件路径
    audio_file = './cache/audio/recording_20250612_150104.wav'
    
    # 进行识别
    result = recognizer.recognize_audio(audio_file)
    
    if result:
        print(f'识别结果: {result}')
    else:
        print('识别失败')

if __name__ == '__main__':
    test_recognition() 