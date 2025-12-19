# 🐓 Rooster - Daily Bible Verse Reader

A beautiful Streamlit-based application for reading and exploring Bible verses with AI-generated reflections powered by OpenAI. Features thoughtful Q&A and reading plan management for your daily devotional time.

## ✨ Features

- 📖 **Bible Verse Exploration**: Choose any book, chapter, and verse range to study
- 🤖 **AI Reflections**: OpenAI generates brief, meaningful reflections on selected verses
- 💭 **Theological Q&A**: Ask questions about faith, theology, or specific passages
- 📅 **Reading Plan Management**: Plan and organize your Bible reading journey in advance
- 🏛️ **Doctrinal Context**: AI answers reflect your church's theological perspective
- 🎨 **Inspirational Interface**: Warm, churchy colors with semi-transparent styling
- 💾 **Persistent Memory**: App remembers your selections and reading plan across sessions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API account
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
# OpenAI Configuration (Required)
OPENAI_API_KEY=sk-your-openai-api-key

# Application Configuration
CHURCH_DOCTRINE=Protestant Christian perspective with emphasis on grace, faith, and scripture

# Optional: Bible API (for full verse text)
BIBLE_API_KEY=your_bible_api_key
```

4. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📚 How to Use

### Browse and Read Bible Verses

1. Go to the **"Bible Verses & Q&A"** tab
2. Select book, chapter, and verse range
3. Check "Include AI-generated reflection" for a devotional message
4. Click **"View Verse & Reflection"** to see the formatted verse with optional reflection

### Ask Questions

1. In the **"Bible Verses & Q&A"** tab, scroll to the Q&A section
2. Enter your question about faith, theology, or specific verses
3. Click **"Get Answer"** to receive a thoughtful, doctrine-based response

### Manage Your Reading Plan

1. Go to the **"Reading Plan"** tab
2. Select verses you want to study
3. Optionally add notes about why you want to study this passage
4. Click **"Add to Plan"** to add it to your reading list
5. View and manage your reading plan
6. Remove completed readings as you progress

## 🌐 Deployment Options

### Deploy Streamlit App on Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit dashboard:
   ```toml
   # .streamlit/secrets.toml
   OPENAI_API_KEY = "sk-..."
   CHURCH_DOCTRINE = "Your church's theological perspective"
   BIBLE_API_KEY = "..." # Optional
   ```

### Alternative Deployment Platforms

- **Heroku**: Deploy with Procfile
- **Google Cloud Run**: Deploy as containerized app
- **AWS Elastic Beanstalk**: Deploy Python web app
- **Render**: Simple deployment for Streamlit apps

## 📖 API Documentation

### Bible Service (`bible_service.py`)
- Fetches verses from API.Bible
- Falls back to reference-only mode if API key not configured
- Supports all major Bible books

### OpenAI Service (`openai_service.py`)
- Formats verses with reflections using GPT-4
- Answers questions based on church doctrine
- Maintains conversation context

### Conversation Store (`conversation_store.py`)
- SQLite-based storage
- Tracks verse selections and reading plans
- Manages user preferences and state

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
├── bible_service.py          # Bible verse fetching
├── openai_service.py         # OpenAI integration
├── conversation_store.py     # SQLite storage for reading plans
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
├── .env.example             # Environment template
└── README.md                # This file
```

### Testing Locally

1. Set up all environment variables
2. Run Streamlit app: `streamlit run app.py`
3. Test verse selection and viewing
4. Test Q&A functionality
5. Test reading plan management

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **API.Bible** for Bible verse data
- **Streamlit** for the awesome framework

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the Setup tab in the application
- Review OpenAI API documentation

---

**Wake up to God's Word daily with Rooster! 🐓📖**