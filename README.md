An agentic tool that uses LangGraph and Google Gemini API to crawl and summarize content from a given website (up to a limited number of pages).
nglish** how to create and use a `GEMINI_API_KEY` for your project.

# Domain Crawler
An agentic tool that uses **LangGraph** and **Google Gemini API** to crawl and summarize content from a given website (up to a limited number of pages).

---

## creating Your GEMINI_API_KEY
Before running this project, you need an API key from Google Gemini. Follow these steps:
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click on **Get API Key** and in the right upper click on "Create API" and create it and use it for future reference
4. Copy the generated API key (it will look like a long random string).

   
## Setting Up the API Key

We store the API key in a `.env` file so it is **not hardcoded** in the code for safety purpose
1. create your project folder and create a new file with ".env" name
2. Open `.env` and paste this line:
   GEMINI_API_KEY=your_api_key_here
   Replace `your_api_key_here` with the key you copied from Google AI Studio.
3. Save the file.

##
Now, 
git clone https://github.com/your-username/domain_crawler.git
cd domain_crawler

install the requirements.txt
pip install -r requirements.txt

then, activate the created enviornment
env\scripts\activate

execute the file
streamlit run domain_crawler.py
