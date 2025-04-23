# 📞 Lexus Support Chatbot – Project Documentation

## ✅ Overview
This project implements a customer support chatbot for Lexus using Streamlit and LangChain. It is capable of answering questions from PDF manuals and creating GitHub support tickets when an answer cannot be found. The bot uses OpenAI’s GPT for natural conversation and document summarization, and supports document retrieval using FAISS.

---

## 📋 Task Objectives
The objective was to build a web-based customer support solution with the following requirements:
- Provide accurate responses from documentation via chat interface.
- Automatically suggest creating a support ticket if the answer is not found.
- Collect user name and email only once.
- Submit support tickets to a GitHub issue tracker.
- Cite source documents and page numbers when providing answers.
- Use at least 3 documents (2 PDFs, one of 400+ pages).
- Preserve conversation history and context.
- Use Python with a Streamlit or Gradio interface.
- Deploy to Hugging Face Spaces.

---

## 📁 Project Structure

- `app.py` — Main Streamlit interface and logic  
- `chatbot.py` — Handles vector store and retrieval-based Q&A using LangChain  
- `data_ingestion.py` — Loads PDFs and text documents into FAISS vector store  
- `ticket.py` — Submits GitHub issues via REST API  

---

## 💡 Key Features

- OpenAI key entry UI for secure runtime setup  
- Automatic summary generation for unclear questions  
- Memory and context-aware retrieval of answers using LangChain  
- Conditional GitHub ticket creation flow  
- AI-based extraction of name and email from freeform chat input  
- Persistent user profile stored for future tickets  
- Clean conversation blocks with sources and timestamps  

---

## ✅ How Each Requirement Was Fulfilled

- ✔️ Web chat interface: Streamlit chat input  
- ✔️ Document citation: filenames and page numbers from FAISS metadata  
- ✔️ Ticket suggestion logic: Based on weak/unknown answers  
- ✔️ Name/email collected only once and reused  
- ✔️ Ticket creation: GitHub API integration  
- ✔️ Documents: 3 loaded including large LS500 manual  
- ✔️ Technologies: Python, LangChain, Streamlit, FAISS, OpenAI  
- ✔️ Hosted on Hugging Face: Ready for `app.py` + requirements  

---

## 📦 How to Run Locally

```bash
pip install -r requirements.txt
python data_ingestion.py
streamlit run app.py
```

---

## 🌐 Deployment to Hugging Face

All source code and requirements.txt are uploaded to Hugging Face Spaces. It will automatically run `app.py`.

The link: https://huggingface.co/spaces/ukhalilov2/lexus-support-chatbot

`
Please, take into consideration that answers in the screenshots below can be slightly different from the current version in Hugging Face Space. The reason is because I had to resolve a 'Pydantic version conflict'. The original vector store was incompatible with the server environment. I regenerated it locally using compatible library versions (especially LangChain and Pydantic v2) and uploaded the new store. This necessary change can slightly alter which documents the chatbot finds most relevant.
`

Also, while testing on Hugging Face Space server I noticed that sometimes database is not loaded meaning it will offer creating a support ticket until you refresh the page. 

---

## Dataset
Data are stored in data directory. As one of the pdf file that has more than 400 pages couldn't be uploaded to the github because it is too large to upload, I archived and uploaded as a .zip file. If you want to see the largest dataset in pdf, you need to uzip it.

## 🧪 Example Flow

```text
User: What is the market price of Lexus ES 2018 price?  
Bot: I couldn't provide a clear answer. Would you like me to create a support ticket?  
User: Yes  
Bot: Please provide your name and email.  
User: Ulugbek ulugbek@example.com  
Bot: ✅ Your support ticket has been submitted!
```

---

## Screenshots
![openai.png](screenshots%2Fopenai.png)

**The chat user should use own OpenAI API key to chat**


![ask-questions.png](screenshots%2Fask-questions.png)
![hi.png](screenshots%2Fhi.png)

**The bot understands that this is not a question, so does not search for the answer**


![about-company.png](screenshots%2Fabout-company.png)

**Knows about the company**


![phone-number.png](screenshots%2Fphone-number.png)

![email.png](screenshots%2Femail.png)

![warranty.png](screenshots%2Fwarranty.png)

**Now looking for an answer in the database**


![dvd.png](screenshots%2Fdvd.png)

![tires.png](screenshots%2Ftires.png)

![ticket-creation.png](screenshots%2Fticket-creation.png)

**This is a question that the bot does not kwow so it suggests to create a support ticket**


![ticket-creation2.png](screenshots%2Fticket-creation2.png)

**After successfully gets name and email, it will automatically create the ticket**

![ticket-creation3.png](screenshots%2Fticket-creation3.png)

**After getting the name and email of the user, it never asks as it stores this information for future tickets**


![cancelling-ticket.png](screenshots%2Fcancelling-ticket.png)

**If the user does not want to create a ticket, the system understands that**

---

## 📌 Summary

This project demonstrates a robust generative AI solution for real-world customer support scenarios using LangChain and OpenAI APIs, with complete lifecycle handling from Q&A to ticket escalation.