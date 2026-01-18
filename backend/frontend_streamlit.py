import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd

# UI styling
st.set_page_config(page_title="Policy Classifier", page_icon="🔐", layout="centered")
st.markdown(
    """
    <style>
        .main {background-color: #f6f8fa;}
        .stTextArea textarea {
            background-color: #eaf1fb; 
            font-size: 1.1em;
            color: #000000;
            border: 2px solid #0057b7;
            border-radius: 5px;
        }
        .stButton button {
            background-color: #0057b7; 
            color: white; 
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        .stButton button:hover {
            background-color: #003d82;
        }
        .risk-high {color: #D7263D; font-weight: bold;}
        .risk-medium {color: #F6C85F; font-weight: bold;}
        .risk-low {color: #2ECC71; font-weight: bold;}
        .dataframe {
            border-collapse: collapse;
            width: 100%;
        }
        .dataframe td, .dataframe th {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        .dataframe th {
            background-color: #0057b7;
            color: white;
            font-weight: bold;
        }
        .dataframe tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("🔐 Privacy Policy Clause Classifier")
st.subheader("Analyze and classify ToS / Privacy Policy content using AI")

col1, col2 = st.columns([3, 1])
with col1:
    selected_model = st.selectbox(
        "Select Model:",
        options=["bert", "deberta", "deberta-v2"],
        format_func=lambda x: f"BERT (Uncased)" if x == "bert" else ("DeBERTa v3 (Base)" if x == "deberta" else "DeBERTa v3 (Base v2)"),
        help="Choose between BERT and DeBERTa models for classification"
    )
with col2:
    st.info(f"📊 Model: {selected_model.upper()}")


# Defines global LABELS needed for both modes
LABELS = [
    "First Party Collection/Use", "Third Party Sharing/Collection", "User Choice/Control", 
    "User Access, Edit & Deletion", "Data Retention", "Data Security", "Policy Change", 
    "Do Not Track", "International & Specific Audiences", "Miscellaneous and Other", "Contact Information", 
    "User Choices/Consent Mechanisms"
]

RISK_MAPPING = {
    "First Party Collection/Use": "medium",
    "Third Party Sharing/Collection": "high",
    "User Choice/Control": "medium",
    "User Access, Edit & Deletion": "low",
    "Data Retention": "high",
    "Data Security": "low",
    "Policy Change": "medium",
    "Do Not Track": "high",
    "International & Specific Audiences": "medium",
    "Miscellaneous and Other": "medium",
    "Contact Information": "low",
    "User Choices/Consent Mechanisms": "low",
}


# UI State
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "Paste Text"

input_mode = st.radio("Input Mode:", ["Paste Text", "Enter URL"], horizontal=True)

if input_mode == "Enter URL":
    st.info("🌐 **URL Analysis Mode**: This will scrape the website, chunk the text, and analyze it.")
    url_input = st.text_input("Enter Privacy Policy URL:", placeholder="https://example.com/privacy-policy")
    
    if st.button("🔍 Analyze URL"):
        if not url_input.strip():
            st.warning("Please enter a valid URL.")
        else:
            with st.spinner("Scraping and analyzing... this may take a few seconds..."):
                try:
                    # Call the backend URL analysis endpoint
                    response = requests.post(
                        "http://localhost:8000/analyze-url", 
                        json={"url": url_input, "model": selected_model}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if "error" in result:
                            st.error(f"❌ Error: {result['error']}")
                        else:
                            # Store results in session state to persist across reruns
                            st.session_state.analysis_result = result
                            st.session_state.chat_chunks = result.get("chunks", [])
                            
                    else:
                        st.error(f"❌ Server returned error: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure FastAPI server is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    
    # Display analysis results if they exist in session state
    if "analysis_result" in st.session_state and st.session_state.analysis_result:
        result = st.session_state.analysis_result
        
        st.success(f"✅ Successfully analyzed {result.get('chunk_count', 0)} chunks from URL!")
        
        # Use backend predictions directly
        positive_labels = result.get("labels", [])
        risks = result.get("risks", [])
        scores = result.get("scores", [])
        risk_pct = result.get("risk_percentage", {})
        model_used = selected_model
                            
        # --- Display Results ---
        st.markdown("### 🧾 Prediction Results")
        
        if positive_labels:
            display_data = []
            for idx, lbl in enumerate(positive_labels):
                # Find the index of this label in the main LABELS list to get the correct score
                try:
                    label_index = LABELS.index(lbl)
                    score = scores[label_index]
                except (ValueError, IndexError):
                    score = 0
                
                risk_val = RISK_MAPPING.get(lbl, "medium")
                
                display_data.append({
                    "Category": lbl,
                    "Confidence": f"{score*100:.1f}%",
                    "Risk Level": f"🔴 {risk_val.upper()}" if risk_val == "high" else (f"🟡 {risk_val.upper()}" if risk_val == "medium" else f"🟢 {risk_val.upper()}")
                })
            
            st.success("✅ **The following privacy categories were detected:**")
            
            df_results = pd.DataFrame(display_data)
            st.dataframe(df_results, width="stretch", hide_index=True)
        else:
            st.info("ℹ️ No categories detected above the threshold.")

        # Bar chart for all categories
        st.markdown("#### 📈 Category Confidence Overview")
        chart_data = {lbl: score for lbl, score in zip(LABELS, scores)}
        st.bar_chart(chart_data)

        # Pie chart for Risks
        if positive_labels:
            st.markdown("#### 📊 Risk Level Summary")
            
            # Calculate risk summary locally to be 100% in sync with table
            local_risks = [RISK_MAPPING.get(lbl, "medium") for lbl in positive_labels]
            risk_counts = {lvl: local_risks.count(lvl) for lvl in ["high", "medium", "low"]}
            total_detected = len(local_risks)
            
            labels_chart = []
            sizes = []
            colors = ["#D7263D", "#F6C85F", "#2ECC71"] 
            for lvl in ["high", "medium", "low"]:
                count = risk_counts[lvl]
                if count > 0:
                    labels_chart.append(lvl.capitalize())
                    sizes.append(count)
            
            if sizes:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.pie(sizes, labels=labels_chart, colors=colors[:len(sizes)], autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
            else:
                st.info("No risks to summarize.")

        # --- Explanation & Summary ---
        st.divider()
        
        with st.expander("💡 **Analysis Explanation (AI Generated)**", expanded=True):
            if result.get("explanation"):
                st.markdown(result["explanation"])
            else:
                st.info("No detailed explanation available.")
        
        with st.expander("📝 **Policy Summary**", expanded=False):
            if result.get("summary"):
                st.markdown(result["summary"])
            else:
                st.info("No summary available.")

        st.divider()
        st.caption(f"✓ Model Used: **{model_used}**")

elif input_mode == "Paste Text":
    text_input = st.text_area(
        "Paste a section of Terms of Service or Privacy Policy here:",
        height=170,
        help="Works best on clear paragraphs or sections. Long documents will work, but may take longer to classify."
    )
    
    if st.button("🔎 Classify Section"):
        if len(text_input.strip()) < 12:
            st.warning("Please enter a substantial policy or ToS section.")
        else:
            try:
                # Change this URL if running FastAPI somewhere else
                response = requests.post(
                    "http://localhost:8000/predict", json={"text": text_input, "model": selected_model}
                )
                result = response.json()
                st.markdown("### 🧾 Prediction Results")
                
                # Use backend predictions directly (risks are already aligned with labels)
                positive_labels = result.get("labels", [])
                risks = result.get("risks", [])
                st.session_state.chat_chunks = result.get("chunks", []) # Update Chat Context
                
                # Get scores for positive labels
                if positive_labels:
                    display_data = []
                    # We need the full score list to map correctly if result has it,
                    # but /predict endpoint structure is a bit different, it returns "scores" as full list
                    scores = result.get("scores", [])
                    
                    for idx, lbl in enumerate(positive_labels):
                        try:
                            label_index = LABELS.index(lbl)
                            score = scores[label_index]
                        except (ValueError, IndexError):
                            score = 0
                            
                        risk_val = RISK_MAPPING.get(lbl, "medium")
                        
                        display_data.append({
                            "Category": lbl,
                            "Confidence": f"{score*100:.1f}%",
                            "Risk Level": f"🔴 {risk_val.upper()}" if risk_val == "high" else (f"🟡 {risk_val.upper()}" if risk_val == "medium" else f"🟢 {risk_val.upper()}")
                        })
                    
                    st.success("✅ **The following privacy categories were detected:**")
                    
                    df_results = pd.DataFrame(display_data)
                    st.dataframe(df_results, width="stretch", hide_index=True)
                else:
                    st.info("ℹ️ No categories detected above the threshold.")

                # Bar chart for all categories
                st.markdown("#### 📈 Category Confidence Overview")
                chart_data = {lbl: score for lbl, score in zip(LABELS, result["scores"])}
                st.bar_chart(chart_data)

                # PIE CHART RISK OVERVIEW AT THE BOTTOM
                if positive_labels:
                    st.markdown("#### 📊 Risk Level Summary")
                    
                    # Calculate risk summary locally
                    local_risks = [RISK_MAPPING.get(lbl, "medium") for lbl in positive_labels]
                    risk_counts = {lvl: local_risks.count(lvl) for lvl in ["high", "medium", "low"]}
                    
                    labels_chart = []
                    sizes = []
                    colors = ["#D7263D", "#F6C85F", "#2ECC71"] 
                    for lvl in ["high", "medium", "low"]:
                        count = risk_counts[lvl]
                        if count > 0:
                            labels_chart.append(lvl.capitalize())
                            sizes.append(count)
                            
                    if sizes:
                        fig, ax = plt.subplots(figsize=(8, 6))
                        wedges, texts, autotexts = ax.pie(
                            sizes, labels=labels_chart, colors=colors[:len(sizes)],
                            autopct='%1.1f%%', startangle=90, 
                            wedgeprops=dict(edgecolor='white', linewidth=2)
                        )
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_weight('bold')
                            autotext.set_fontsize(11)
                        ax.axis('equal')
                        st.pyplot(fig)
                        
                        summary_txt = ", ".join(f"**{labels_chart[i]}**: {(sizes[i]/len(local_risks))*100:.1f}%" for i in range(len(sizes)))
                        st.markdown(f"📌 Risk composition: {summary_txt}")
                    else:
                        st.info("No risk levels detected for selected input.")

                st.divider()
                st.caption(f"✓ Model Used: **{result['model_used']}**")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure FastAPI server is running on http://localhost:8000")
            except KeyError as e:
                st.error(f"❌ Unexpected response format from backend: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# --- Chatbot Integration (Sidebar) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_chunks" not in st.session_state:
    st.session_state.chat_chunks = []
if "chat_expanded" not in st.session_state:
    st.session_state.chat_expanded = True

with st.sidebar:
    # Collapsible chat interface
    with st.expander("💬 Policy Chat Assistant", expanded=st.session_state.chat_expanded):
        # Show context status
        chunk_count = len(st.session_state.chat_chunks)
        if chunk_count > 0:
            st.success(f"✅ {chunk_count} policy sections loaded")
        else:
            st.warning("⚠️ No policy loaded. Analyze a URL first!")
        
        st.caption("Ask questions about the privacy policy")
        st.divider()
        
        # Display chat history in a scrollable container
        chat_container = st.container(height=400)
        with chat_container:
            if not st.session_state.messages:
                st.info("👋 Hello! I can answer questions about privacy policies. Try asking:\n- What data do they collect?\n- How is my information shared?\n- Can I delete my data?")
            else:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        # Format based on message type
                        if msg["role"] == "assistant":
                            if msg.get("type") == "RAG":
                                st.markdown(f"**📄 Answer:**\n\n{msg['content']}")
                            elif msg.get("type") == "GUARDRAIL":
                                st.warning(msg["content"])
                            elif msg.get("type") == "INSTRUCTION":
                                st.info(msg["content"])
                            else:
                                st.write(msg["content"])
                        else:
                            st.write(msg["content"])

        # Chat input
        if prompt := st.chat_input("Ask about the policy...", key="sidebar_chat"):
            # Add user message to session state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Call Backend and get response
            try:
                with st.spinner("🤔 Thinking..."):
                    chat_response = requests.post(
                        "http://localhost:8000/chat",
                        json={
                            "message": prompt,
                            "chunks": st.session_state.chat_chunks
                        },
                        timeout=30
                    )
                    
                    if chat_response.status_code == 200:
                        data = chat_response.json()
                        answer = data.get("answer", "I couldn't generate an answer.")
                        response_type = data.get("type", "UNKNOWN")
                        
                        # Store message with type
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "type": response_type
                        })
                    else:
                        err_msg = f"❌ Server error: {chat_response.status_code}"
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": err_msg, 
                            "type": "ERROR"
                        })
            except requests.exceptions.Timeout:
                err_msg = "⏱️ Request timed out. Please try again."
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": err_msg, 
                    "type": "ERROR"
                })
            except requests.exceptions.ConnectionError:
                err_msg = "❌ Cannot connect to backend. Make sure FastAPI server is running."
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": err_msg, 
                    "type": "ERROR"
                })
            except Exception as e:
                err_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": err_msg, 
                    "type": "ERROR"
                })
            
            # Rerun to display new messages (this won't affect analysis results 
            # because they're already in session state and rendered above)
            st.rerun()
        
        # Clear chat button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("↻ Refresh", use_container_width=True):
                st.rerun()

st.markdown("---")
st.caption("Powered by Streamlit & FastAPI • Hugging Face Transformers")
