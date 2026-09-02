import sys # works with system level stuff
import os # for accessing the  files
import pdfplumber # for reading the pdf files and extracting text
import functools # utilty library 

# Fixing the  Windows output buffering:
print = functools.partial(print, flush=True) # creates a new version of print that fulshes immideately
sys.stdout.reconfigure(encoding='utf-8') # to check for spl characters v gotta do utf 8 encoding

print("Starting...", flush=True)


# Extracting the text from the pdfs 
def extract_text_from_pdf(pdf_path): # the input is the path ofthe pdf
    """Extract text from single PDF file"""
    text = "" # empty for now will add pdf texts 
    try: # using try and expect so that it protects against unreadable files

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages: # iterates thru every page 
                page_text = page.extract_text() # extracts all the text
                if page_text:
                    text += page_text + "\n" # add the text in the empty string
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}") # will tell the error giving file path and the error 

    return text

def split_into_chunks(text, filename, level, chunk_size=500):
    """Split text into smaller chunks for better retrieval"""
    words = text.split() # splitting the pages into words
    chunks = [] # will add the chunks into this 

    for i in range(0, len(words), chunk_size): # loop jumps 500 words at a time
        chunk_words = words[i:i+chunk_size]
        chunk_text = " ".join(chunk_words) # joining the words to form texts

        chunks.append({ # create a dictornary 
            "text": chunk_text, # content of 500 words
            "source": filename, # the filenmae where it was exrtracted
            "level": level, # a1 or a2 pr b1
            "chunk_id": f"{filename}_{i}"  # unique id to ondentify each chunk later for chroma db

        })
    return chunks

def extract_all_pdfs(data_folder):
    """Extract text from all PDFs in all subfolders"""
    all_chunks = [] # has all the chunks of all the pdfs


    for level in os.listdir(data_folder): # loops thru each level 
        level_path = os.path.join(data_folder, level) # creates full path eg  "dta"+"A1" data/A1"
        if not os.path.isdir(level_path): # to check if its a folder
            continue
        print(f"Processing level: {level}")

        for filename in os.listdir(level_path): # eg list all the files in A1 
            if filename.endswith('.pdf'): # only process such pdf files 
                pdf_path = os.path.join(level_path, filename) # now join the ful path to the pdf
                print(f"  Reading: {filename}")

                text = extract_text_from_pdf(pdf_path) # use the defined function to extract the text from that pdf path


                if text.strip(): # to check if text is there and it remoging whitespace
                    chunks = split_into_chunks(text, filename, level) # calling the function
                    all_chunks.extend(chunks) # extending it with the list all_chunks[]
                    print(f"  → {len(chunks)} chunks created")

    print(f"\nTotal chunks created: {len(all_chunks)}")
    return all_chunks

if __name__ == "__main__":
    try:
        data_folder = "data"
        chunks = extract_all_pdfs(data_folder)

        if chunks:
            print("\n=== SAMPLE CHUNK ===")
            print(f"Source: {chunks[0]['source']}")
            print(f"Level: {chunks[0]['level']}")
            print(f"Text preview: {chunks[0]['text'][:200]}")
        else:
            print("No chunks created!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
