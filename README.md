# ExplAIn Notes

**Description:** This notetaking app explains your notes in real time using an in-built LLM that explains all concepts, answers all questions, and computes all calculations. 


## Getting Started: 
**Prerequisites**
If you don't have python3 default on your computer, use
```bash
python3 -m venv venv
source venv/bin/activate
```
You should see (venv) at the beginning of your terminal line.

**Installations**
To install the dependencies, run
```bash
pip install fastapi uvicorn pydantic openai
```

**API Key**
To run the program, you need a Gemini API key. You can get a free API key through Google AI Studio with the free tier. Then, in the terminal, run
```bash
export GEMINI_API_KEY="your_gemini_api_key"
```

**IP Address**
In the index.html, change the variable "API_BASE" to "http://your_ip_address:8000". You can find your IP address by going to Settings --> Network --> choose your WiFi & select Details.

## Running
To run the program, open one terminal (in the python3 virtual environment) and run the frontend
```bash
python3 -m http.server 3000
```
Then open another terminal (in the python3 virtual environment) and run the backend
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```


## Usage
To use the web app on your iPad / tablet, open the url "http://your_ip_address:3000" in your Safari app. 
You can use the Pen and Eraser tool to write a message on the notes. If you pause writing for 4 seconds, the LLM will analyze what you have written so far and send its result in the sidebar. If you end with a question mark, it will answer your question. If you end with an equal sign, it will compute the result of the calculation. Otherwise, it will define or explain any concepts you write down. 
The web app keeps a history of the past LLM results, and it only processes your most recent writing. You can click the clear button to clear the page of notes. 