import streamlit as st
import uuid
import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json

# Function to get the public IP address
def get_public_ip():
    url = "https://api.ipify.org?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('ip')
    else:
        return "Error: Unable to fetch IP"

# Generate session ID based on public IP
def generate_session_id(ip):
    return ip  # Using public IP as the session ID

# Encryption functions
def generate_key():
    return get_random_bytes(16)

def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

def decrypt_message(key, encrypted_message):
    data = base64.b64decode(encrypted_message)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode('utf-8')

# Main application
def main():
    st.title("P2P File Sharing & Chat System")
    
    # Initialize session state
    if 'session_id' not in st.session_state:
        public_ip = get_public_ip()  # Get the public IP
        st.session_state.session_id = generate_session_id(public_ip)  # Use IP as session ID
    if 'key' not in st.session_state:
        st.session_state.key = generate_key()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_info' not in st.session_state:
        st.session_state.file_info = None
    
    # Sidebar for connection
    with st.sidebar:
        st.header("Connection")
        st.write("Your Session ID (Public IP):")
        st.code(st.session_state.session_id)  # Display public IP as session ID
        
        peer_id = st.text_input("Enter Peer's Session ID to connect:")
        if st.button("Connect"):
            st.session_state.peer_id = peer_id
            st.success(f"Attempting to connect to {peer_id}")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("File Sharing")
        uploaded_file = st.file_uploader("Choose a file to share", type=None)
        if uploaded_file is not None:
            file_details = {
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "size": uploaded_file.size
            }
            st.session_state.file_info = file_details
            st.success(f"File '{uploaded_file.name}' ready to share!")
        
        if st.session_state.file_info:
            st.write("File ready to send:")
            st.json(st.session_state.file_info)
    
    with col2:
        st.header("Chat")
        
        # Display chat messages
        for message in st.session_state.messages:
            st.chat_message(message["role"]).write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message"):
            encrypted_msg = encrypt_message(st.session_state.key, prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()  # Updated from experimental_rerun()
    
    # WebRTC JavaScript integration (Updated to reflect changes)
    st.markdown(
        f"""
        <script src="https://unpkg.com/peerjs@1.4.7/dist/peerjs.min.js"></script>
        <script>
        const peer = new Peer('{st.session_state.session_id}');
        
        peer.on('connection', (conn) => {{
            conn.on('data', (data) => {{
                try {{
                    const message = JSON.parse(data);
                    if (message.type === 'chat') {{
                        // Display received message
                        const chatContainer = document.querySelector('.stChatMessage');
                        if (chatContainer) {{
                            const messageElement = document.createElement('div');
                            messageElement.className = 'stChatMessage';
                            messageElement.innerHTML = `
                                <div class="stChatMessageContent">
                                    <div class="stChatMessageRole">peer</div>
                                    <div class="stChatMessageText">${{message.content}}</div>
                                </div>
                            `;
                            chatContainer.appendChild(messageElement);
                        }}
                    }}
                }} catch (e) {{
                    console.error('Error processing message:', e);
                }}
            }});
        }});
        
        function connectToPeer(peerId) {{
            const conn = peer.connect(peerId);
            return conn;
        }}
        
        // Auto-connect if peer ID is set
        {f"if ('{st.session_state.get('peer_id', '')}') connectToPeer('{st.session_state.peer_id}');" if st.session_state.get('peer_id') else ""}
        </script>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
