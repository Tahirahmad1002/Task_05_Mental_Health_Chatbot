import streamlit as st
from transformers import pipeline, GenerationConfig

# 1. Page Configuration
st.set_page_config(page_title="EmpathyBot AI", page_icon="🌱", layout="wide")

# 2. Sidebar
with st.sidebar:
    st.title("🛠️ Project Technicals")
    st.info("""
    **Model:** Fine-tuned DistilGPT2  
    **Dataset:** EmpatheticDialogues  
    **Task:** Emotional Support & Listening  
    """)
    st.divider()
    st.warning("""
    **⚠️ Disclaimer:** This is an AI research project. It is not a substitute for professional mental health advice.
    """)
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# 3. Load Model
@st.cache_resource
def load_bot():
    return pipeline("text-generation", model="TahirAhmad1002/empathy-bot-distilgpt2")

chat_pipe = load_bot()

# 4. Main UI
st.title("🌱 EmpathyBot: Intent-Aware Mental Health Support Agent")
st.caption("Developed by Tahir Ahmad - AI Engineering Intern")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI companion. I'm here to listen. How are you feeling?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Input & Logic
# 5. Chat Input & Smart Logic
prompt = st.chat_input("Share your thoughts...")

if prompt:
    # We define user_input inside the block so it is guaranteed to exist
    user_input = str(prompt)
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        # A. SMART INTENT DETECTION
        q_words = ["what", "how", "who", "where", "why", "can you", "tell me"]
        is_question = any(user_input.lower().strip().startswith(w) for w in q_words)
        
# B. UPGRADED KEYWORD GUARDRAILS
        sad_words = ["upset", "sad", "worried", "lost", "lonely", "alone", "sick", "vet", "hospital", "nervous", "afraid", "fail", "presentation", "exam", "busy", "promotion"]
        is_sad = any(word in user_input.lower() for word in sad_words)
        
        # C. DYNAMIC PROMPT WRAPPING
        if is_question:
            formatted_input = f"Question: {user_input} Answer:"
        elif is_sad:
            formatted_input = f"Situation: {user_input} Emotional Context: Supportive Response: I am so sorry to hear that."
        else:
            formatted_input = f"Situation: {user_input} Emotional Context: Empathetic Response:"
        
        gen_config = GenerationConfig(
            max_new_tokens=50, 
            do_sample=True,
            temperature=0.3, 
            repetition_penalty=1.5, 
            no_repeat_ngram_size=3,
            pad_token_id=chat_pipe.tokenizer.eos_token_id
        )
        
        with st.spinner("Processing..."):
            result = chat_pipe(formatted_input, generation_config=gen_config)
            
        full_text = result[0]['generated_text']
        
        # Split logic
        if "Answer:" in full_text:
            response = full_text.split("Answer:")[-1].strip()
        else:
            response = full_text.split("Response:")[-1].strip()
        
        # Guardrail Reinforcement
        if is_sad and not response.lower().startswith("i am so sorry"):
            response = "I am so sorry to hear that. " + response
            
        # Cleanup
        response = response.replace("_comma_", ",").strip()
        if "." in response:
            response = response.rsplit(".", 1)[0] + "."
        
        # Fallback
        if len(response) < 10:
             response = "I'm here for you. Could you tell me more about how you're feeling?"
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})