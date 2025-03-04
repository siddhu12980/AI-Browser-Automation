
from speech_handler import SpeechHandler


def main():
    speech_handler = SpeechHandler()
    while True:
        success, response = speech_handler.listen_and_respond()
        if not success:
            print(f"Error: {response}")
        
        user_input = input("Press Enter to continue or 'q' to quit: ")
        if user_input.lower() == 'q':
            break

if __name__ == "__main__":
    main()

