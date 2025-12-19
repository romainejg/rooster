# 🐓 Rooster - Daily Bible Verse WhatsApp App

A Streamlit-based application that sends daily Bible verses via Twilio WhatsApp with AI-generated reflections powered by OpenAI. Features two-way WhatsApp communication for answering Bible questions from your church's doctrinal perspective.

## ✨ Features

- 📖 **Bible Verse Selection**: Choose any book, chapter, and verse range
- 🤖 **AI Reflections**: OpenAI generates brief, meaningful reflections on selected verses
- 📱 **WhatsApp Delivery**: Send formatted verses via Twilio WhatsApp
- 📅 **Scheduling**: Schedule daily verse delivery at specific times
- 💬 **Two-Way Q&A**: Reply to WhatsApp messages and get AI-powered answers
- 🏛️ **Doctrinal Context**: AI answers reflect your church's theological perspective
- 📊 **Conversation History**: Track all WhatsApp conversations and sent verses
- 💾 **Persistent Memory**: App remembers your selections and preferences across sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API account
- Twilio account with WhatsApp-enabled number
- (Optional) Bible API key from api.bible

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/romainejg/rooster.git
cd rooster
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
# Your WhatsApp-enabled Twilio number (numbers will be auto-formatted for WhatsApp)
TWILIO_PHONE_NUMBER=+1234567890

# Application Configuration
# Recipient WhatsApp number (numbers will be auto-formatted for WhatsApp)
RECIPIENT_PHONE_NUMBER=+1234567890
CHURCH_DOCTRINE=Protestant Christian perspective with emphasis on grace, faith, and scripture

# Optional: Bible API (for verse fetching)
BIBLE_API_KEY=your_bible_api_key
```

4. **Run the Streamlit app**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔧 Setting Up WhatsApp Webhooks

To enable two-way WhatsApp conversations (replying to messages), you need to set up the webhook handler:

### Development Setup (Using ngrok)

1. **Start the webhook handler**
```bash
python webhook_handler.py
```

2. **Expose with ngrok** (in a separate terminal)
```bash
ngrok http 5000
```

3. **Configure Twilio WhatsApp Sandbox (Development)**
- Go to your Twilio Console
- Navigate to Messaging → Try it out → Send a WhatsApp message
- Follow instructions to join your WhatsApp sandbox
- Once in sandbox, configure the webhook:
  - Go to Messaging → Settings → WhatsApp Sandbox Settings
  - Set "When a message comes in" webhook URL to:
    ```
    https://your-ngrok-url.ngrok.io/webhook/sms
    ```
  - Save changes

4. **Configure Twilio WhatsApp (Production)**
- After activating your WhatsApp Business account with Twilio:
  - Go to Messaging → Senders → WhatsApp senders
  - Select your WhatsApp number
  - Set the webhook URL to:
    ```
    https://your-production-url.com/webhook/sms
    ```
  - Save changes

### Production Setup

For production, deploy `webhook_handler.py` as a separate web service:

**Option 1: Railway**
```bash
# Add a Procfile
echo "web: python webhook_handler.py" > Procfile
# Push to Railway
```

**Option 2: Render**
- Create a new Web Service
- Point to your repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `python webhook_handler.py`

**Option 3: Heroku**
```bash
heroku create your-app-name
git push heroku main
```

Then update your Twilio webhook URL to your production URL.

## 📚 How to Use

### Send a Verse Immediately

1. Go to the **"Send Verse"** tab
2. Select book, chapter, and verse range
3. Check "Include AI-generated reflection" for a devotional message
4. Click **"Preview Message"** to see the formatted message
5. Click **"Send WhatsApp Now"** to send via Twilio WhatsApp

### Schedule Daily Verses

1. Go to the **"Schedule"** tab
2. Select your verse and preferred time
3. Click **"Add to Schedule"**
4. View and manage scheduled messages

⚠️ **Note**: Scheduled messages require a background scheduler. See deployment options below.

### View Conversation History

1. Go to the **"Conversations"** tab
2. View all sent and received messages
3. Test Q&A responses without sending SMS

### Configure Settings

1. Enter recipient phone number in the sidebar
2. View service configuration status
3. Check the **"Setup"** tab for deployment instructions

**Note:** Phone numbers are automatically formatted for WhatsApp (e.g., `+1234567890` becomes `whatsapp:+1234567890`)

## 🌐 Deployment Options

### Deploy Streamlit App on Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit dashboard:
   ```toml
   # .streamlit/secrets.toml
   OPENAI_API_KEY = "sk-..."
   TWILIO_ACCOUNT_SID = "AC..."
   TWILIO_AUTH_TOKEN = "..."
   TWILIO_PHONE_NUMBER = "+1..."
   RECIPIENT_PHONE_NUMBER = "+1..."
   CHURCH_DOCTRINE = "..."
   ```

### Deploy Webhook Handler Separately

The webhook handler needs to be always running to receive SMS replies:

- **Railway**: Connect repo, deploy `webhook_handler.py`
- **Render**: Create Web Service, deploy as Python app
- **Heroku**: Deploy with Procfile
- **AWS Lambda**: Use Zappa or Serverless framework

### Alternative: All-in-One Deployment

For production, you can combine the Streamlit app and webhook in a single deployment using tools like:
- **Docker**: Create a multi-process container
- **Supervisor**: Run both processes on a single server

## 📖 API Documentation

### Bible Service (`bible_service.py`)
- Fetches verses from API.Bible
- Falls back to reference-only mode if API key not configured
- Supports all major Bible books

### OpenAI Service (`openai_service.py`)
- Formats verses with reflections using GPT-4
- Answers questions based on church doctrine
- Maintains conversation context

### Twilio Service (`twilio_service.py`)
- Sends WhatsApp messages
- Automatically formats phone numbers for WhatsApp
- Creates webhook responses
- Parses incoming messages

### Conversation Store (`conversation_store.py`)
- SQLite-based storage
- Tracks message history
- Manages scheduled messages

## 🔐 Security Considerations

- Never commit `.env` file to version control
- Use Streamlit secrets for cloud deployment
- Rotate API keys regularly
- Validate webhook signatures in production
- Use HTTPS for webhook endpoints

## 📝 Configuration Options

### Church Doctrine

Customize the `CHURCH_DOCTRINE` environment variable to reflect your theological perspective:

```env
CHURCH_DOCTRINE="Reformed Baptist perspective emphasizing the sovereignty of God, justification by faith alone, and the authority of Scripture"
```

This influences how the AI answers questions about faith and doctrine.

### Bible API

The app uses API.Bible by default. Get a free API key:
1. Sign up at https://scripture.api.bible/
2. Create an API key
3. Add to `.env` as `BIBLE_API_KEY`

Without an API key, the app will show verse references only.

## 🛠️ Development

### Project Structure

```
rooster/
├── app.py                    # Main Streamlit application
├── webhook_handler.py        # Flask webhook for SMS replies
├── bible_service.py          # Bible verse fetching
├── openai_service.py         # OpenAI integration
├── twilio_service.py         # Twilio SMS handling
├── conversation_store.py     # SQLite conversation storage
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

### Testing Locally

1. Set up all environment variables
2. Run Streamlit app: `streamlit run app.py`
3. Run webhook handler: `python webhook_handler.py`
4. Use ngrok for webhook testing
5. Send test messages from the UI

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Twilio** for SMS services
- **API.Bible** for Bible verse data
- **Streamlit** for the awesome framework

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the Setup tab in the application
- Review Twilio WhatsApp and OpenAI documentation
- See [Twilio WhatsApp documentation](https://www.twilio.com/docs/whatsapp)

---

**Wake up to God's Word daily with Rooster! 🐓📖**