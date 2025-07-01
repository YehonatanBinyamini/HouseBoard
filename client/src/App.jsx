import React, { useState } from 'react';
import './App.css';

function App() {
  const [notes, setNotes] = useState([]);
  const [noteText, setNoteText] = useState('');

  const createNote = () => {
    if (noteText.trim() === '') return;
    
    const newNote = {
      id: Date.now(),
      text: noteText,
      createdAt: new Date()
    };
    
    setNotes([newNote, ...notes]);
    setNoteText('');
  };

  const deleteNote = (id) => {
    setNotes(notes.filter(note => note.id !== id));
  };

  const formatDate = (date) => {
    return new Intl.DateTimeFormat('he-IL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      createNote();
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">📝 הפתקים שלי</h1>
          <p className="subtitle">צור ונהל את הפתקים שלך בקלות</p>
        </header>

        <div className="note-creator">
          <div className="input-section">
            <textarea
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="כתוב את הפתק שלך כאן..."
              className="note-input"
              rows="4"
            />
            <button 
              onClick={createNote}
              className="create-btn"
              disabled={noteText.trim() === ''}
            >
              <span className="btn-icon">✨</span>
              צור פתק
            </button>
          </div>
        </div>

        <div className="notes-section">
          <div className="notes-header">
            <h2 className="notes-title">
              הפתקים שלי ({notes.length})
            </h2>
          </div>

          {notes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h3>אין פתקים עדיין</h3>
              <p>צור את הפתק הראשון שלך!</p>
            </div>
          ) : (
            <div className="notes-grid">
              {notes.map((note) => (
                <div key={note.id} className="note-card">
                  <div className="note-header">
                    <span className="note-date">
                      {formatDate(note.createdAt)}
                    </span>
                    <button 
                      onClick={() => deleteNote(note.id)}
                      className="delete-btn"
                      aria-label="מחק פתק"
                    >
                      ×
                    </button>
                  </div>
                  <div className="note-content">
                    {note.text}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;