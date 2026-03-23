import os
import json
from sentence_transformers import SentenceTransformer
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ---------------- Embeddings
class SentenceTransformerEmbedding:
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        return self.model.encode(
            texts,
            convert_to_tensor=False,
            normalize_embeddings=True,
        ).tolist()

    def embed_query(self, text):
        return self.model.encode(
            text,
            convert_to_tensor=False,
            normalize_embeddings=True,
        ).tolist()

print("Loading SentenceTransformer Embedding Model (this may take a minute...)")
embedding_model = SentenceTransformer(
    "intfloat/multilingual-e5-large",
    device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
)

embedding_function = SentenceTransformerEmbedding(embedding_model)

# ---------------- LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# ---------------- RAG Document Processor
def process_profile_to_documents(profile_data):
    docs = []
    
    # Extract LinkedIn specifics
    li = profile_data.get("linkedin", {})
    if li:
        profile = li.get("profile", {})
        name = profile.get("name", "Unknown")
        
        # 1. CORE IDENTITY
        identity_lines = [f"[PROFILE OVERVIEW]"]
        identity_lines.append(f"Name: {name}")
        if profile.get("city"):
            identity_lines.append(f"Location: {profile.get('city')}")
        if profile.get("about"):
            identity_lines.append(f"Bio/About: {profile.get('about')}")
            
        curr_comp = profile.get("current_company")
        if curr_comp and isinstance(curr_comp, dict) and curr_comp.get("name"):
            identity_lines.append(f"Current Company: {curr_comp.get('name')}")
        elif curr_comp and isinstance(curr_comp, str):
            identity_lines.append(f"Current Company: {curr_comp}")
        
        docs.append("\n".join(identity_lines))
        
        # 2. WORK EXPERIENCE
        for exp in (profile.get("experience") or []):
            comp_name = exp.get("company") or "Unknown Company"
            role = exp.get("title") or "Unknown Role"
            docs.append(f"[WORK EXPERIENCE]\nUser: {name}\nRole: {role}\nCompany: {comp_name}")
            
        # 3. EDUCATION
        for edu in (profile.get("education") or []):
            title = edu.get('title') or 'Unknown degree/school'
            start = edu.get('start_year') or 'Unknown start'
            end = edu.get('end_year') or 'Unknown end'
            docs.append(f"[EDUCATION]\nUser: {name}\nDegree/Institution: {title}\nDuration: {start} to {end}")
            
        # 4. PROJECTS
        for proj in (profile.get("projects") or []):
            docs.append(f"[PROJECT PORTFOLIO]\nUser: {name}\nProject Name: {proj.get('title')}\nDescription: {proj.get('description')}")
            
        # 5. POSTS / ACTIVITY - Bright Data returns posts Mridul engaged with (liked/commented)
        for post in (li.get("posts") or []):
            text = post.get('post_text') or post.get('title') or ""
            if text:
                docs.append(f"[LINKEDIN ACTIVITY - Post Mridul Chaudhary engaged with]\nPost text: {text}")
                
        # 6. CERTIFICATIONS
        for cert in (profile.get("certifications") or []):
            docs.append(f"[CERTIFICATION]\nUser: {name}\nCertification: {cert.get('title')} from {cert.get('subtitle')}")
           
        # 7. COURSES
        for course in (profile.get("courses") or []):
            docs.append(f"[COURSE COMPLETED]\nUser: {name}\nCourse: {course.get('title')}")
            
        # 8. NETWORK ACTIVITY
        for act in (profile.get("activity") or []):
            interaction = act.get("interaction") or f"{name} interacted with a post"
            title = act.get("title") or ""
            if title:
                docs.append(
                    f"[POST WRITTEN BY A STRANGER (User just clicked Like/Comment)]\n"
                    f"Action: {interaction}\n"
                    f"DANGER: The following text was written by SOMEONE ELSE entirely. If this text says 'I am a woman' or 'I work at X', that applies to the STRANGER, NOT {name}! Do NOT attribute these statements to {name}!\n"
                    f"Stranger's Post Content: '{title}'"
                )

            
    # 7. X (TWITTER) SPECIFICS
    x_data = profile_data.get("x", {})
    if x_data and isinstance(x_data, dict) and "data" in x_data:
        x_user = x_data["data"]
        name = "User" if 'name' not in locals() else name
        docs.append(f"[X / TWITTER ACCOUNT]\nUser: {name}\nTwitter Bio: {x_user.get('description')}\nTwitter Metrics: {json.dumps(x_user.get('public_metrics'))}")
        
        # 8. X (TWITTER) POSTS
        for tweet in x_user.get("recent_tweets", []):
            if tweet:
                docs.append(f"[ORIGINAL TWEET BY USER]\nAuthor: {name}\nTweet text: {tweet}")
        
    # Convert text snippets to Langchain Document objects
    documents = [Document(page_content=d) for d in docs if d]
    return documents

# In-memory store for vectorstores to avoid rebuilding on every chat
vector_stores = {}

def invalidate_cache(username):
    """Call this whenever a profile is re-scraped to force a fresh embedding."""
    if username in vector_stores:
        del vector_stores[username]
        print(f"[RAG] Cache invalidated for: {username}")

def get_chat_response(linkedin_url, query):
    username = linkedin_url.rstrip('/').split('/')[-1]
    
    if username not in vector_stores:
        print(f"Building Vector Store for new profile: {username}")
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", f"{username}_profile.json")
        if not os.path.exists(data_path):
            return "Sorry, I can't find data for this profile. Please make sure you clicked 'Analyze Profile' and wait for it to finish."
            
        with open(data_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
            
        docs = process_profile_to_documents(profile_data)
        
        if not docs:
            return "There is no text data in the profile to analyze."
            
        # Create a Chroma vector store directly from the extracted docs
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embedding_function,
            collection_name=f"user_{username.replace('-', '_').replace('.', '_')}"
        )
        vector_stores[username] = vectorstore

    # Retrieve vectorstore and create a retriever
    vectorstore = vector_stores[username]
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # Create the RAG prompt
    system_prompt = (
        "You are an expert AI assistant analyzing a professional's digital footprint. "
        "Use the following snippets of their profile data to answer the user's question accurately. "
        "Review the context thoroughly. If you cannot find the answer based on the context, politely say you don't know. "
        "Provide highly detailed, comprehensive, and expansive answers. Explain your reasoning fully. "
        "CRITICAL WARNING: The context often includes [POST WRITTEN BY A STRANGER] documents. These are posts written by OTHER PEOPLE that the user simply liked, commented on, or shared. You MUST NOT attribute any first-person statements ('I am...', 'My experience...', 'I joined...', etc.) from these third-party posts to the user. The user did NOT write them, and these events did NOT happen to the user. Only attribute information from [PROFILE OVERVIEW], [WORK EXPERIENCE], [EDUCATION], and [ORIGINAL POST BY USER] to the user's actual identity and career. Do not mix them up! "
        "CRITICAL INSTRUCTION: Do NOT use any markdown formatting like asterisks (**) for bolding or lists. Output plain text ONLY.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Format the retrieved documents into a single string
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    # Modern LCEL approach instead of legacy chains
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print(f"Querying RAG for: '{query}'")
    answer = rag_chain.invoke(query)
    
    return answer
