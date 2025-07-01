import { useState } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [notes, setNotes] = useState([]);

  const addNote = () => {
    if (text.trim() === '') return;
    setNotes([...notes, text]);
    setText('');
  };

  return (
    <div className="app">
      <h1>פתקים</h1>
      <div className="input-area">
        <input
          type="text"
          placeholder="הכנס טקסט לפתק"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button onClick={addNote}>צור</button>
      </div>
      <div className="notes">
        {notes.map((note, index) => (
          <div className="note" key={index}>
            {note}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
