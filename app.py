import streamlit as st
import requests
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Get public IP address
def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        return ip.replace('.', '-')  # Replace dot to make it PeerJS-friendly
    except:
        return "unknown"

# AES encryption/decryption
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

# Main UI
def main():
    st.set_page_config(layout="wide")
    st.title("🌐 P2P File Sharing & Chat (Distributed IP-Based)")

    # IP as session ID
    if 'ip_id' not in st.session_state:
        st.session_state.ip_id = get_public_ip()
    if 'key' not in st.session_state:
        st.session_state.key = generate_key()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'file_info' not in st.session_state:
        st.session_state.file_info = None

    # Sidebar for connection
    with st.sidebar:
        st.header("Connection Info")
        st.write("📡 Your Device ID (IP):")
        st.code(st.session_state.ip_id)

        peer_id = st.text_input("Enter Peer’s IP-based ID:")
        if st.button("Connect"):
            st.session_state.peer_id = peer_id.replace('.', '-')
            st.success(f"Connecting to {peer_id}")

    col1, col2 = st.columns(2)

    with col1:
        st.header("📁 File Sharing")
        file = st.file_uploader("Upload a file", type=None)
        if file:
            st.session_state.file_info = {
                "name": file.name,
                "type": file.type,
                "size": file.size
            }
            st.success(f"{file.name} ready to share!")

    with col2:
        st.header("💬 Chat")
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Send a message"):
            encrypted = encrypt_message(st.session_state.key, prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.experimental_rerun()

    # Inject JS
    peer_id_js = st.session_state.ip_id
    connect_id_js = st.session_state.get("peer_id", "")
    st.markdown(
        f"""
        <script src="https://unpkg.com/peerjs@1.4.7/dist/peerjs.min.js"></script>
        <script>
        const myId = "{peer_id_js}";
        const peer = new Peer(myId);

        peer.on('open', id => {{
            console.log("PeerJS ready with ID:", id);
        }});

        peer.on('connection', conn => {{
            conn.on('data', data => {{
                console.log("Received from peer:", data);
                alert("Peer says: " + data);
            }});
        }});

        function connectToPeer(peerId) {{
            const conn = peer.connect(peerId);
            conn.on('open', () => {{
                conn.send("Hello from " + myId);
            }});
        }}

        {"connectToPeer('" + connect_id_js + "');" if connect_id_js else ""}
        </script>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
