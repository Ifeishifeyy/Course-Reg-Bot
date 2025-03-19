class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };

        this.state = false;
        this.messages = [];
        this.program = null; // Track user's program
        this.level = null;   // Track user's level

        // Add the welcome message to the messages array
        this.messages.push({ name: "Sam", message: "Welcome! I am the Course Registration Advisor Chatbot. To assist you better, please tell me your level, program." });

        console.log("Chatbox button:", this.args.openButton);
        console.log("Send button:", this.args.sendButton);
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener('click', () => {
            this.toggleState(chatBox);
        });

        sendButton.addEventListener('click', () => this.onSendButton(chatBox));
        console.log("Send button event listener attached.");

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === 'Enter') {
                this.onSendButton(chatBox);
            }
        });

        // Display the initial welcome message
        this.updateChatText(chatBox);
    }

    toggleState(chatBox) {
        this.state = !this.state;
        console.log("Toggling chatbox state:", this.state); 
        if (this.state) {
            chatBox.classList.add('chatbox--active');
        } else {
            chatBox.classList.remove('chatbox--active');
        }
    }

    onSendButton(chatBox) {
        var textField = chatBox.querySelector('input');
        let text1 = textField.value;

        if (text1 === "") {
            console.log("Empty input.");
            return;
        }

        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);

        // Extract program and level from the message
        let program = this.extractProgram(text1);
        let level = this.extractLevel(text1);

        console.log("Extracted Program:", program);
        console.log("Extracted Level:", level);

        // Update program and level if found
        if (program) this.program = program;
        if (level) this.level = level;

        fetch($SCRIPT_ROOT + '/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1, program: this.program, level: this.level }),
            mode: 'cors',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(response => {
            let msg2 = { name: "Sam", message: response.response };
            this.messages.push(msg2);
            this.updateChatText(chatBox);
            textField.value = '';
        })
        .catch(error => {
            console.error('Error:', error);
            this.updateChatText(chatBox);
            textField.value = '';
        });
    }

    extractProgram(text) {
        const lowerText = text.toLowerCase();
        
        if (lowerText.includes("industrial mathematics")|| lowerText.includes("maths") || lowerText.includes("mathematics")|| lowerText.includes("ind maths")||lowerText.includes("industrial maths")) {
            return "Industrial Mathematics";
        } else if (lowerText.includes("computer science")|| lowerText.includes("cs")|| lowerText.includes("comp science")|| lowerText.includes("comp sci")) {
            return "Computer Science";
        } 
        
        return null;
    }
    

    extractLevel(text) {
        const lowerText = text.toLowerCase();
        const words = lowerText.match(/\b(\d{3})\s*-?\s*(l|lvl|level)?\b/); // Finds three-digit numbers (e.g., 100, 200, 300...)
        
        if (words) {
            let level = parseInt(words[0]); // Convert to number
            if (level >= 100 && level <= 400) {
                return level.toString(); // Return as a string
            }
        }
        if (lowerText.includes("penultimate")) {
            return "300";
        } else if (lowerText.includes("final")) {
            return "400";
        }else if (lowerText.includes("fresher")||lowerText.includes("freshman")){
            return "100";
        } else if (lowerText.includes("sophomore")){
            return "200";
        }
        
        return null;
    }
    

    updateChatText(chatBox) {
        var html = '';
        this.messages.slice().reverse().forEach(item => {
            if (item.name === "User") {
                html += `<div class="messages__item messages__item--operator">${item.message}</div>`;
            } else if (item.name === "Sam") {
                html += `<div class="messages__item messages__item--visitor">${item.message.replace(/\n/g,"<br>")}</div>`;
            }
        });

        const chatMessage = chatBox.querySelector('.chatbox__messages');
        chatMessage.innerHTML = html;
    }
}

const chatbox = new Chatbox();
chatbox.display();