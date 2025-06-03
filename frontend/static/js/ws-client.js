const socket = new WebSocket("ws://localhost:8000/ws");

// Biến toàn cục
let targetLanguage = 'vi'; 

socket.onopen = () => {
    console.log("✅ Kết nối thành công!");
    updateConnectionStatus("Đã kết nối");
};

socket.onmessage = async function(event) {
    try {
        const message = JSON.parse(event.data);
        if (message.type === "translation") {
            // Hiển thị kết quả dịch
            document.getElementById("translationResult").innerText = message.text;
        }
        else if (message.type === "error") {
            console.error("Lỗi từ server:", message.data);
            document.getElementById("translationResult").innerText = `[Lỗi] ${message.text}`;
        }
    } catch (err) {
        console.error("Lỗi xử lý tin nhắn:", err);
        document.getElementById("translationResult").innerText = event.text;
    }
};

socket.onclose = (event) => {
    console.log("🔌 Đóng kết nối, mã:", event.code, "lý do:", event.reason);
    updateConnectionStatus("Mất kết nối", true);
    setTimeout(reconnectWebSocket, 3000);
};

socket.onerror = (error) => {
    console.error("Lỗi WebSocket:", error);
    updateConnectionStatus("Lỗi kết nối", true);
};

// Hàm kết nối lại
function reconnectWebSocket() {
    if (socket.readyState === WebSocket.CLOSED) {
        console.log("🔄 Đang kết nối lại...");
        socket = new WebSocket("ws://localhost:8000/ws");
    }
}

// Hàm cập nhật trạng thái kết nối
function updateConnectionStatus(text, isError = false) {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.textContent = text;
        statusElement.style.color = isError ? 'red' : 'green';
    }
}

// Hàm gửi văn bản cần dịch
window.sendText = function() {
    const text = document.getElementById("textInput").value.trim();
    if (!text) return;

    if (socket.readyState === WebSocket.OPEN) {
        const payload = {
            type: "translate",
            text: text,
            target_lang: targetLanguage
        };
        socket.send(JSON.stringify(payload));
        
        // Hiển thị trạng thái đang dịch
        document.getElementById("translationResult").innerText = "Đang dịch...";
    } else {
        console.warn("Không thể gửi - WebSocket chưa kết nối");
        updateConnectionStatus("Không thể gửi - Đang kết nối lại...", true);
        reconnectWebSocket();
    }
};

// Hàm thay đổi ngôn ngữ đích
window.changeLanguage = function(lang) {
    targetLanguage = lang;
    console.log(`Đã chọn ngôn ngữ đích: ${lang}`);
    document.getElementById("languageLabel").textContent = 
        `Đang dịch sang: ${getLanguageName(lang)}`;
};

// Helper: Lấy tên ngôn ngữ
function getLanguageName(code) {
    const languages = {
        'vi': 'Tiếng Việt',
        'en': 'Tiếng Anh',
        'fr': 'Tiếng Pháp',
        'ja': 'Tiếng Nhật',
    };
    return languages[code] || code;
}