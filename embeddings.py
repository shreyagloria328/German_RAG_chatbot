import sys
import os
import functools
from sentence_transformers import SentenceTransformer
import chromadb
from pdf_extractor import extract_all_pdfs

print=functools.partial(print,flush=True)
sys.stdout.reconfigure(encoding='utf-8')


print("Loading embedding model")
model=SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("model loaded!")

print("Initializing chromadb")
client=chromadb.PersistentClient(path="chroma_db")

collection=client.get_or_create_collection(
    name="german_study",
    metadata={"hnsw:space":"cosine"}
)
print("ready")

def create_and_store_embeddings(chunks):
    """convert chunks to embeddings and store in ChromaDB"""

    print(f"\nCreating embeddings for {len(chunks)} chunks")

    texts=[chunk['text'] for chunk in chunks]
    ids=[chunk['chunk_id'] for chunk in chunks]

    metadatas=[
        {
            "source":chunk['source'],
            "level":chunk['level']
        }
        for chunk in chunks
    ]
    batch_size=10
    total_batches=(len(chunks)+batch_size-1) // batch_size
    for i in range(0,len(chunks),batch_size):
        batch_num=(i//batch_size) +1
        batch_texts=texts[i:i+batch_size]
        batch_ids=ids[i:i+batch_size]
        batch_metadatas=metadatas[i:i+batch_size]
        print(f"processing batch {batch_num}/{total_batches} ")
        prefixed_texts=batch_texts
        embeddings=model.encode(prefixed_texts).tolist()
        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=embeddings,
            metadatas=batch_metadatas
        )

    print(f"\nAll {len(chunks)} chunks stored in ChromaDB")
    return True


def verify_storage():
    """Check how many chunks are stored in chromadb"""

    count=collection.count()
    print(f"Total chunks in chromadb:{count}")


    sample=collection.peek(limit=1)
    if sample['documents']:
        print(f"\nSample stored document:")
        print(f"ID:{sample['ids'][0]}")
        print(f"Source:{sample['metadatas'][0]['source']}")
        print(f"Level:{sample['metadatas'][0]['level']}")
        print(f"Text preview : {sample['documents'][0][:150]}")

    return count


if __name__=="__main__":
    try:
        existing_count=collection.count()

        if existing_count>0:
            print(f"ChromaDB already has {existing_count}chunks")
            print("Skipping embedding creation")
            verify_storage()
        else:
            print(f"Extracting text from PDFs..")
            chunks=extract_all_pdfs("data")

            if not chunks:
                print("No chunks found.")
            else:
                create_and_store_embeddings(chunks)

                verify_storage()

                print("embedding created successfully")
    except Exception as e:
        print(f"ERROR:{e}")
        import traceback
        traceback.print_exc()
