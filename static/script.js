function initPeer(myIP, peerIdToConnect) {
    const peer = new Peer(myIP, {
        host: '0.peerjs.com',
        port: 443,
        path: '/',
        secure: true
    });

    let conn;

    peer.on('open', id => {
        console.log("Connected with ID:", id);
    });

    peer.on('connection', connection => {
        conn = connection;
        setupConnection(conn);
    });

    if (peerIdToConnect) {
        const connOut = peer.connect(peerIdToConnect);
        connOut.on('open', () => {
            conn = connOut;
            setupConnection(conn);
        });
    }

    function setupConnection(connection) {
        connection.on('data', data => {
            const parsed = JSON.parse(data);
            if (parsed.type === 'chat') {
                appendChatMessage("peer", parsed.content);
            } else if (parsed.type === 'file') {
                alert(`Incoming File: ${parsed.name} (${formatSize(parsed.size)})`);
            }
        });

        connection.on('close', () => {
            alert("Peer Disconnected");
        });
    }

    function appendChatMessage(role, text) {
        const container = document.querySelector('.stChatMessage');
        if (container) {
            const div = document.createElement('div');
            div.className = 'stChatMessage';
            div.innerHTML = `
                <div class="stChatMessageContent">
                    <div class="stChatMessageRole">${role}</div>
                    <div class="stChatMessageText">${text}</div>
                </div>
            `;
            container.appendChild(div);
        }
    }

    function formatSize(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
    }
}
