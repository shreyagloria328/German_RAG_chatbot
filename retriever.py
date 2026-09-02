import sys
import functools
from sentence_transformers import SentenceTransformer
import chromadb

print=functools.partial(print,flush=True)
sys.stdout.reconfigure(encoding='utf-8')

print("Loading retriever model")
model=SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print('Model loaded')

client=chromadb.PersistentClient(path="chroma_db")
collection=client.get_or_create_collection(name="german_study",metadata={
    "hnsw:space":"cosine"
})
print(f"Connected to ChromaDB-{collection.count()} chunks available")



def retrieve_relevant_chunks(query,n_results=3,level_filter=None):
    """ 
    Search ChromaDB for chunks most relavant to the query
    
    query=user's question
    n_results=how many chunks to return(3 as default)
    level_filter=filter by A1,A2,B1"""

    print(f"\nSearching for :'{query}'")

    query_vector=model.encode(query).tolist()

    where_filter=None
    if level_filter:
        where_filter={"level":level_filter}

    if where_filter:
        results=collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=where_filter,
            include=["documents","metadatas","distances"]
            )
    else:
        results=collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=where_filter,
            include=["documents","metadatas","distances"]
            )

    chunks=[]
    for i in range(len(results['documents'][0])):
            chunk={
            "text": results['documents'][0][i],
            "source": results['metadatas'][0][i]['source'],
            "level": results['metadatas'][0][i]['level'],
            "similarity":1-results['distances'][0][i]
            }
            chunks.append(chunk)
    return chunks 
def format_chunks_for_context(chunks):
    """
    Combine retrieved chunks into one context string
    to send to Claude API"""

    context=""
    for i,chunk in enumerate(chunks):
        context+= f"\n--- Source {i+1}: {chunk['source']} (Level {chunk['level']}) ---\n"
        context+=chunk['text']
        context+="\n"
    return context

if __name__ =="__main__":
    try:
        test_questions=[
            "what is der die das in german?",
            "how do i introduce myself in german ",
            "what are german numbers"
        ]
        for question in test_questions:
            print("\n" + "="*50)
            print(f"Question:{question}")
            print("="*50)

            chunks=retrieve_relevant_chunks(query=question,
                                            n_results=3)
            print(f"Found {len(chunks)} relevant chunks:\n")

            for i,chunk in enumerate(chunks):
                print(f"Result{i+1}:")
                print(f"  Source:  {chunk['source']}")
                print(f"Level: {chunk['level']}")
                print(f"Similarity:{chunk['similarity']:.3f}")
                print(f"preview: {chunk['text'][:150]}")
                print()

    except Exception as e:
        print(f"ERROR:{e}")
        import traceback
        traceback.print_exc()


