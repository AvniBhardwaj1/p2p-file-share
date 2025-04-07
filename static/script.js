// Get the session ID from the URL parameter
const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get('session_id') || 'default';

// Initialize PeerJS connection
const peer = new Peer(sessionId, {
    host: '0.peerjs.com',
    port: 443,
    path: '/',
    secure: true,
    debug: 3
});

let conn = null;
let dataChannel = null;

peer.on('open', (id) => {
    console.log('My peer ID is: ' + id);
});

// Handle incoming connection
peer.on('connection', (connection) => {
    console.log('Incoming connection from: ' + connection.peer);
    setupConnection(connection);
});

// Setup data channel and event handlers
function setupConnection(connection) {
    conn = connection;
    
    conn.on('open', () => {
        console.log('Connection established');
        
        // Create data channel for file transfer and chat
        dataChannel = conn.createDataChannel('fileTransfer');
        setupDataChannel(dataChannel);
    });
    
    conn.on('data', (data) => {
        console.log('Received data:', data);
        handleReceivedData(data);
    });
    
    conn.on('close', () => {
        console.log('Connection closed');
        alert('Peer disconnected');
    });
    
    conn.on('error', (err) => {
        console.error('Connection error:', err);
    });
}

// Setup data channel
function setupDataChannel(channel) {
    channel.onopen = () => {
        console.log('Data channel opened');
    };
    
    channel.onmessage = (event) => {
        console.log('Received message:', event.data);
        handleReceivedData(event.data);
    };
    
    channel.onclose = () => {
        console.log('Data channel closed');
    };
}

// Handle received data
function handleReceivedData(data) {
    try {
        const parsedData = JSON.parse(data);
        
        if (parsedData.type === 'chat') {
            // Display chat message
            const chatContainer = document.querySelector('.stChatMessage');
            if (chatContainer) {
                const messageElement = document.createElement('div');
                messageElement.className = 'stChatMessage';
                messageElement.innerHTML = `
                    <div class="stChatMessageContent">
                        <div class="stChatMessageRole">peer</div>
                        <div class="stChatMessageText">${parsedData.content}</div>
                    </div>
                `;
                chatContainer.appendChild(messageElement);
            }
        } else if (parsedData.type === 'file') {
            // Handle file metadata
            alert(`Incoming file: ${parsedData.name} (${formatFileSize(parsedData.size)})`);
            // Here you would implement the file transfer logic
        }
    } catch (e) {
        console.error('Error parsing received data:', e);
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Connect to peer
function connectToPeer(peerId) {
    if (conn) {
        conn.close();
    }
    
    conn = peer.connect(peerId, {
        reliable: true
    });
    
    setupConnection(conn);
}

// Send chat message
function sendChatMessage(message) {
    if (dataChannel && dataChannel.readyState === 'open') {
        const messageData = {
            type: 'chat',
            content: message,
            timestamp: new Date().toISOString()
        };
        dataChannel.send(JSON.stringify(messageData));
    } else {
        console.error('Data channel not ready');
    }
}

// Send file metadata
function sendFileMetadata(fileInfo) {
    if (dataChannel && dataChannel.readyState === 'open') {
        const fileData = {
            type: 'file',
            name: fileInfo.name,
            size: fileInfo.size,
            mimeType: fileInfo.type
        };
        dataChannel.send(JSON.stringify(fileData));
    } else {
        console.error('Data channel not ready');
    }
}

// Listen for Streamlit events
window.addEventListener('load', () => {
    // This would be enhanced to handle Streamlit events
    console.log('Page loaded, ready for P2P connections');
});
