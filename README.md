Hi, 
This is a really good idea I hope it gets used.


Hope this AI-generated summary helps.
## Quick Start
### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Development Mode

Run the development script to start both backend and frontend:

```bash
./dev.sh
```

This will:
1. Create a Python virtual environment (in backend folder)
2. Install Python dependencies
3. Install Node.js dependencies
4. Start Flask backend on port 5001
5. Start Vite dev server on port 3000

Visit [http://localhost:3000](http://localhost:3000) to use the application.

### Manual Setup

If you prefer to run services separately:

#### Backend (Flask)
```bash
cd backend
source venv/bin/activate
python app.py
```

#### Frontend (Svelte + Vite)
```bash
npm install
npm run dev
```

## How It Works

1. **Daily Prompt**: The app loads a random prompt from `days.txt`
2. **User Input**: Users write responses to the prompt
3. **Grammar Check**: GPT-2 calculates perplexity to assess grammaticality
4. **Embedding**: SentenceTransformers creates semantic embeddings
5. **Distance Matrix**: Cosine similarity creates distance relationships
6. **Tree Generation**: DendroPy builds a neighbor-joining tree
7. **Visualization**: D3.js renders an interactive force-directed tree

## File Structure

```
sentence-tree/
├── dev.sh              # Development startup script
├── package.json        # Node.js dependencies
├── vite.config.js      # Vite configuration
├── index.html          # HTML entry point
├── src/                # Frontend source code
│   ├── main.js         # Svelte app entry
│   ├── App.svelte      # Main application component
│   ├── components/     # Svelte components
│   └── stores/         # Svelte stores
└── backend/            # Backend Flask application
    ├── app.py          # Flask server
    ├── models.py       # SQLAlchemy database models
    ├── utils.py        # ML utilities (embeddings, trees)
    ├── days.txt        # Daily prompts
    ├── requirements.txt # Python dependencies
    ├── venv/           # Python virtual environment
    └── README.md       # Backend documentation
```

## API Endpoints

- `GET /api/daily-prompt` - Get random daily prompt
- `POST /api/check-grammar` - Check text grammaticality
- `POST /api/submit-input` - Submit user response
- `GET /api/generate-tree` - Generate phylogenetic tree

## Technologies Used

- **Frontend**: Svelte, Vite, D3.js, Tailwind CSS
- **Backend**: Flask, SQLAlchemy
- **ML**: SentenceTransformers, Transformers (GPT-2), DendroPy
- **Database**: SQLite
