# Sentence Tree Backend

Flask API server for the Sentence Tree application.

## Structure

- `app.py` - Main Flask application
- `models.py` - Database models (SQLAlchemy)
- `utils.py` - Utility functions for NLP and tree generation
- `requirements.txt` - Python dependencies
- `days.txt` - Daily writing prompts
- `venv/` - Python virtual environment
- `distances.csv` - Generated distance matrix (auto-created)
- `sentence_tree.db` - SQLite database (auto-created)

## API Endpoints

- `GET /api/daily-prompt` - Get a random writing prompt
- `POST /api/check-grammar` - Check grammaticality of text
- `POST /api/submit-input` - Submit user input and store with embedding
- `GET /api/generate-tree` - Generate phylogenetic tree from all inputs

## Development

The backend runs on port 5001 and is started automatically by the main dev.sh script.

To run just the backend:
```bash
cd backend
source venv/bin/activate
python3 app.py
```
