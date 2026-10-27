import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: 'שלום! אני סוכן ה-AI שלך. איך אוכל לעזור לך היום בתרגול?' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);

  const [solution, setSolution] = useState('');
  const [gradeResult, setGradeResult] = useState(null);
  const [isGradingLoading, setIsGradingLoading] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isChatLoading) return;

    const userText = inputMessage;
    setInputMessage('');

    setMessages((prev) => [
      ...prev,
      { sender: 'user', text: userText },
      { sender: 'ai', text: '' }
    ]);
    setIsChatLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText }),
      });

      if (!response.ok) throw new Error('שגיאה בתקשורת עם השרת');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });

        setMessages((prev) => {
          const newMessages = [...prev];
          const lastIndex = newMessages.length - 1;
          newMessages[lastIndex].text += chunk;
          return newMessages;
        });
      }
    } catch (err) {
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        newMessages[lastIndex].text = 'אירעה שגיאה בקבלת התשובה. אנא נסה שוב.';
        return newMessages;
      });
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleGradeSubmit = async (e) => {
    e.preventDefault();
    if (!solution.trim() || isGradingLoading) return;

    setIsGradingLoading(true);
    setGradeResult(null);

    try {
      const response = await fetch('http://localhost:5000/api/grade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ solution }),
      });

      const data = await response.json();
      setGradeResult(data);
    } catch (err) {
      setGradeResult({
        grade: 0,
        feedback: 'שגיאה בחיבור לשרת הבדיקה.',
        improvements: ['ודא שהשרת פעיל ונסה שוב.']
      });
    } finally {
      setIsGradingLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>מערכת בדיקת תרגילים וצ'אט לימודי</h1>
      </header>

      <main className="main-content">
        {/* אזור הצ'אט */}
        <section className="card chat-card">
          <h2>💬 צ'אט לימודי</h2>
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div key={index} className={`message-bubble ${msg.sender}`}>
                <div className="message-sender">
                  {msg.sender === 'user' ? 'תלמיד/ה' : 'עוזר AI'}
                </div>
                <div className="message-text">
                  {msg.text || (isChatLoading && index === messages.length - 1 ? 'מקלד תשובה...' : '')}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="chat-input-form">
            <input
              type="text"
              placeholder="הקלד/י הודעה ל-AI..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={isChatLoading}
            />
            <button type="submit" disabled={isChatLoading || !inputMessage.trim()}>
              שליחה
            </button>
          </form>
        </section>

        {/* אזור בדיקת התרגילים */}
        <section className="card grading-card">
          <h2>📝 הגשת תרגיל לקבלת משוב</h2>
          <form onSubmit={handleGradeSubmit}>
            <textarea
              rows="5"
              placeholder="הדבק/י כאן את הפתרון או התשובה לתרגיל..."
              value={solution}
              onChange={(e) => setSolution(e.target.value)}
              disabled={isGradingLoading}
            ></textarea>
            <button type="submit" disabled={isGradingLoading || !solution.trim()}>
              {isGradingLoading ? 'בודק תרגיל...' : 'הגש תרגיל לבדיקה'}
            </button>
          </form>

          {gradeResult && (
            <div className="grade-result-box">
              <div className="grade-score">
                ציון: <span>{gradeResult.grade}</span>
              </div>
              <p className="grade-feedback">
                <strong>משוב:</strong> {gradeResult.feedback}
              </p>
              {gradeResult.improvements && gradeResult.improvements.length > 0 && (
                <div className="grade-improvements">
                  <strong>הצעות לשיפור:</strong>
                  <ul>
                    {gradeResult.improvements.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;