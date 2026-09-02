import sys
import functools
import os
from groq import Groq # groq client to call api key
from dotenv import load_dotenv # to read my env file
from retriever import retrieve_relevant_chunks,format_chunks_for_context


print=functools.partial(print,flush=True)
sys.stdout.reconfigure(encoding='utf-8')

# loading the api key
load_dotenv()
api_key=os.getenv("GROQ_API_KEY")

if not api_key:
    print("Error: GROQ_API_KEY is not found")
    exit()

print("API key loaded successfully")

client=Groq(api_key=api_key) # creating groq client
print("Groq client ready")

# instuctions for the AI model

SYSTEM_PROMPT=""" You are a helpful german language tutor, you help students learn german at A1,A2,B1
levels.

You will be given
1. A question for a student
2. relevant context extracted from the study materials

Your job is to 
- Answer the question clearly and helpfully
-use the provided context as your primary source
-give examples in both german and english
-keep explanation simple and beginner friendly
-if the context doesn't contain enough information say so honestly and give 
a general answer

Always structure your answer like this:
1. Direct answer to the question
2.examples from the study material
3.extra tips if relevant """


def generate_answer(question,level_filter=None):
    """
    full RAG pipeline:
    1. retrieve relevant chunks
    2.format as context
    3. send to claude api
    4.return generated answer"""

    print(f"\nQuestion:{question}")
    print("Retrieving relevant chunks...")

    chunks=retrieve_relevant_chunks(
        query=question,
        n_results=3,
        level_filter=level_filter
    )

    if not chunks:
        return {"answer":"Sorry I could not find relevant information in your study materials",
        "sources":[],
        "chunks_used":0}

    context=format_chunks_for_context(chunks)

    print(f"Found {len(chunks)} relevant chunks")
    print("Generating answer with Groq..")


    user_message=f"""Here is a relevant context from the study materials:

{context}

Based on this context , please answer the following question
{question}
""" 

    response=client.chat.completions.create( # sends reuqest to the groq api
        model="openai/gpt-oss-120b",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
             {"role":"user","content":user_message}
        ],
        max_tokens=1024, # maximum words for the answer
        temperature=0.3 # measures the creativity and randomness, 0.3 means slighly creative and mostly factual

    )
    answer=response.choices[0].message.content # choices[0] because v only want one answer
    sources=list(set([chunk['source'] for chunk in chunks]))

    return{
        "answer":answer,
        "sources":sources,
        "chunks_used":len(chunks)
    }

if __name__ =="__main__":
    try:
        test_questions=[
            "What is der die das in german?",
            "How do i introduce myself in german",
            "what are german numbers"
        ]
        for question in test_questions:
            print("\n"+"="*60)
            result=generate_answer(question)
            print(f"Question:{question}")
            print("-"*60)
            print(f"Answer:\n{result['answer']}")
            print("-"*60)
            print(f"Source used:{result['sources']}")
            print(f"chunks used:{result['chunks_used']}")
    except Exception as e:
        print(f"error:{e}")
        import traceback
        traceback.print_exc()

