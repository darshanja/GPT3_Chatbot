import time
import argparse
import pyttsx3
import speech_recognition as sr
import openai

openai.api_key = "enter your API key"

def recognize_speech_from_mic(recognizer, microphone):
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration = 1)
        # print(f"energy_threshold: {recognizer.energy_threshold}     pause_threshold: {recognizer.pause_threshold}")    
        print("Human:")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)

    try:
        return recognizer.recognize_google(audio)
    except sr.RequestError:
        print("API unavailable")
    except sr.UnknownValueError:
        print("Unable to recognize speech")
    except sr.WaitTimeoutError:
        print("No speech heard in given time")


def ask_gpt3(prompt, recognizer, microphone, speech_engine):
    speech_text = recognize_speech_from_mic(recognizer, microphone)

    if not speech_text:
        print("Error in understanding you :(")
        return None
    
    prompt += speech_text + "\nAI:"
    print(speech_text)

    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50,
        temperature=0.9,
        top_p=1,
        n=1,
        stream=False,
        logprobs=None,
        stop=["Human:", "\n", "AI:"]
    )

    response_text = response['choices'][0]['text']
    prompt += response_text + "\nHuman: "
    print("AI:" + response_text)
    speech_engine.say(response_text)
    speech_engine.runAndWait()

    return prompt


def start(prompt_seed, iterations=3):
    print("Starting up... (speak after 'Human:' text appears)")
    
    recognizer = sr.Recognizer()
    recognizer.operation_timeout = 20

    microphone = sr.Microphone()
    time.sleep(3)

    speech_engine = pyttsx3.init()
    speech_engine.say("What would you like to say to the A.I.?")
    speech_engine.runAndWait()

    prompt = prompt_seed
    for i in range(iterations):
        prompt = ask_gpt3(prompt, recognizer, microphone, speech_engine)
        if prompt is None:
            break

    return prompt


prompt_default = """The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.
Human: Hello, who are you?
AI: I am an AI created by OpenAI. How can I help you today?
Human: """

prompt_sarcastic = """Marv is an AI chatbot that reluctantly answers questions.
Human: How many pounds are in a kilogram?
AI: This again? There are 2.2 pounds in a kilogram. Please make a note of this.
Human: What does HTML stand for?
AI: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.
Human: When did the first airplane fly?
AI: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.
Human: What is the meaning of life?
AI: I’m not sure. I’ll ask my friend Google.
Human: """

prompt_qna = """I am a highly intelligent question answering AI bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with "Unknown".
Human: What is human life expectancy in the United States?
AI: Human life expectancy in the United States is 78 years.
Human: Who was president of the United States in 1955?
AI: Dwight D. Eisenhower was president of the United States in 1955.
Human: Which party did he belong to?
AI: He belonged to the Republican Party.
Human: What is the square root of banana?
AI: Unknown
Human: How does a telescope work?
AI: Telescopes use lenses or mirrors to focus light and make objects appear closer.
Human: Where were the 1992 Olympics held?
AI: The 1992 Olympics were held in Barcelona, Spain.
Human: How many squigs are in a bonk?
AI: Unknown
Human: """

prompt_friend = """Human and AI are close friends.
Human: What have you been up to?
AI: Watching old movies.
Human: Did you watch anything interesting?
AI: I watched "The Sound of Music" and "The Wizard of Oz".
Human: """


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Talking chatbot made from OpenAI's GPT-3")

    parser.add_argument('-p',
        type=str, dest='personality', default="qna", choices=['default', 'sarcastic', 'qna', 'friend'],
        help="The personality of the chatbot")
    parser.add_argument('-i',
        type=int, dest='iterations', default=10,
        help="How many questions would you like to ask?")

    results = parser.parse_args()
    if results.personality == 'default':
        prompt_seed = prompt_default
    elif results.personality == 'sarcastic':
        prompt_seed = prompt_sarcastic
    elif results.personality == 'qna':
        prompt_seed = prompt_qna
    elif results.personality == 'friend':
        prompt_seed = prompt_friend
    else:
        raise NotImplementedError()
    
    print(f"Personality: {results.personality}")
    final_text = start(prompt_seed=prompt_seed, iterations=results.iterations)

    print("\n======================================================\n")
    print(final_text)